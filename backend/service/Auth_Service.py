"""
Authentication Service - SQLite Version

Handles user authentication, JWT tokens, and session management.
Uses SQLAlchemy repositories instead of TempDb.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import bcrypt
import os
from dotenv import load_dotenv

from database.repositories.user_repository import UserRepository
from database.repositories.activity_repository import ActivityRepository

load_dotenv()


class AuthService:
    """
    Authentication service using SQLite database.
    
    Requires a SQLAlchemy Session to be passed in.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.activity_repo = ActivityRepository(db)
        
        # Load environment variables
        self.secret_key = os.getenv('SECRET_KEY', 'fsocitey-backup-key-change-this')
        self.algorithm = os.getenv('ALGORITHM', 'HS256')
        self.access_token_expire = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 2))
        self.refresh_token_expire = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Password hashing failed: {str(e)}")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password using bcrypt"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    def create_access_token(self, payload_data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        payload = payload_data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire)
        
        payload.update({'exp': expire, 'type': 'access'})
        access_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return access_token
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        payload = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire)
        payload.update({'exp': expire, 'type': 'refresh'})
        refresh_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return refresh_token
    
    def verify_token(self, token: str, token_type: str = 'access') -> Optional[dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get('type') != token_type:
                return None
            
            return payload
        except JWTError:
            return None
        
    def register_user(self, user_data: dict) -> dict:
        """Register new user"""
        # Check if user already exists
        existing_user = self.user_repo.get_by_email(user_data['email'])
        if existing_user:
            raise ValueError("User already exists")
        
        # Check username uniqueness
        existing_username = self.user_repo.get_by_username(user_data['username'])
        if existing_username:
            raise ValueError("Username already taken")
        
        # Hash password
        hashed_pass = self.hash_password(user_data['password'])

        # Create user via repository
        user = self.user_repo.create({
            'email': user_data['email'],
            'username': user_data['username'],
            'password_hash': hashed_pass,
            'full_name': user_data.get('full_name'),
            'phone': user_data.get('phone'),
            'company': user_data.get('company'),
            'bio': user_data.get('bio'),
            'role': 'user',  # SECURITY: Force role to 'user' to prevent privilege escalation
            'is_active': True,
        })
        
        # Log signup activity
        self.activity_repo.log_activity(
            user_id=user.id,
            action='signup',
            details={'email': user_data['email'], 'username': user_data['username']}
        )

        return {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'full_name': user.full_name,
            'phone': user.phone,
            'company': user.company,
            'bio': user.bio,
            'role': user.role,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
    
    def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate user"""
        user = self.user_repo.get_by_email(email)
        
        if not user:
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        # Check if user is disabled
        if not user.is_active:
            raise PermissionError("ACCOUNT_DISABLED")
        
        # Convert ORM model to dict
        return self._user_to_dict(user)
    
    def login_user(self, email: str, password: str) -> dict:
        """Login user and return tokens"""
        try:
            user = self.authenticate_user(email, password)
        except PermissionError as e:
            if str(e) == "ACCOUNT_DISABLED":
                raise PermissionError("ACCOUNT_DISABLED")
            raise
        
        if not user:
            raise ValueError("Invalid credentials")
        
        # Create token payload
        token_payload = {
            'sub': user['id'], 
            'email': user['email'],
            'role': user.get('role', 'user')
        }
        
        access_token = self.create_access_token(token_payload)
        refresh_token = self.create_refresh_token(token_payload)

        # Save refresh token to database
        expires_at = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire)
        self.user_repo.save_refresh_token(user['id'], refresh_token, expires_at)
        
        # Update last login
        self.user_repo.update_last_login(user['id'])
        
        # Log login activity
        self.activity_repo.log_activity(
            user_id=user['id'],
            action='login',
            details={'email': user['email'], 'username': user.get('username')}
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'username': user['username'],
                'full_name': user.get('full_name'),
                'phone': user.get('phone'),
                'company': user.get('company'),
                'bio': user.get('bio'),
                'role': user.get('role', 'user')
            }
        }
    
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token"""
        try:
            # Handle restart/stateless cases where token might be valid but not in DB (if using JWT only)
            # But here we enforce DB check for security (revoke capability)
            
            payload = self.verify_token(refresh_token, 'refresh')
            if not payload:
                print(" [AUTH] Refresh failed: Invalid token payload")
                return None
            
            user_id = payload.get('sub')
            if not user_id:
                return None
            
            # Verify stored token matches
            stored_token = self.user_repo.get_refresh_token(user_id)
            
            # Allow for some leeway or re-login if DB has no token but JWT is valid (optional, but strict is better)
            if not stored_token or stored_token != refresh_token:
                print(f" [AUTH] Refresh failed: Token mismatch for user {user_id}")
                return None
            
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return None
            
            # Create new access token
            payload_access_token = {
                'sub': user.id, 
                'email': user.email,
                'role': user.role or 'user'
            }
            new_access_token = self.create_access_token(payload_access_token)
            return new_access_token
            
        except Exception as e:
            print(f" [AUTH] Refresh error: {str(e)}")
            return None
    
    def logout(self, user_id: str, refresh_token: str):
        """Logout user by deleting refresh token"""
        payload = self.verify_token(refresh_token, 'refresh')
        if payload and payload.get('sub') == user_id:
            self.user_repo.delete_refresh_token(user_id)
            
            # Log logout activity
            self.activity_repo.log_activity(
                user_id=user_id,
                action='logout',
                details={}
            )

    def record_login_ip(self, user_id: str, ip_address: str):
        """Record user's login IP address"""
        if ip_address:
            self.user_repo.update_last_login(user_id, ip_address)

    def get_current_user(self, token: str) -> Optional[dict]:
        """Get current user from token"""
        payload = self.verify_token(token, 'access')
        if not payload:
            return None
        
        user_id = payload.get('sub')
        if not user_id:
            return None
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
            
        return self._user_to_dict(user)
    
    def _user_to_dict(self, user) -> dict:
        """Convert User ORM model to dictionary"""
        return {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'full_name': user.full_name,
            'phone': user.phone,
            'company': user.company,
            'bio': user.bio,
            'role': user.role or 'user',
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'password_changed_at': user.password_changed_at.isoformat() if user.password_changed_at else None,
            # Keep hashed_password for internal use (password verification)
            'hashed_password': user.password_hash,
        }

    # ==================== PASSWORD MANAGEMENT ====================

    def request_password_reset(self, email: str) -> bool:
        """Generate 6-digit OTP and print to console (Mock Email)"""
        user = self.user_repo.get_by_email(email)
        if not user:
            # Return True to prevent user enumeration
            return True
        
        import secrets
        import hashlib
        
        # Generate 6-digit OTP
        otp = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        # Store SHA256 hash for lookup/verification
        token_hash = hashlib.sha256(otp.encode()).hexdigest()
        
        # OTP expires in 10 minutes
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        
        self.user_repo.create_reset_token(user.id, token_hash, expires_at)
        
        # MOCK EMAIL SENDER
        print("\n" + "="*50)
        print(f" [EMAIL SERVICE] OTP Requested for {email}")
        print(f" [OTP CODE] {otp}")
        print("="*50 + "\n")
        
        return True

    def verify_otp_only(self, email: str, otp: str) -> None:
        """Verify OTP without resetting password (Internal check)"""
        import hashlib
        
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("Invalid Email or OTP")
            
        token_data = self.user_repo.get_user_reset_token(user.id)
        if not token_data:
            raise ValueError("No reset requested or expired")
            
        input_hash = hashlib.sha256(otp.encode()).hexdigest()
        if input_hash != token_data['token_hash']:
            raise ValueError("Invalid OTP")
            
        if token_data['expires_at'] < datetime.now(timezone.utc):
            raise ValueError("OTP has expired")

    def reset_password(self, email: str, otp: str, new_password: str) -> None:
        """Reset password using Email + OTP"""
        import hashlib
        
        # 1. Verify User
        user = self.user_repo.get_by_email(email)
        if not user:
            # Generic error to prevent enumeration? Or "Invalid OTP"?
            # If user doesn't exist, they can't have an OTP.
            raise ValueError("Invalid Email or OTP")

        # 2. Get User's Token
        token_data = self.user_repo.get_user_reset_token(user.id)
        if not token_data:
            raise ValueError("No reset requested or expired")
            
        # 3. Verify OTP Hash
        input_hash = hashlib.sha256(otp.encode()).hexdigest()
        if input_hash != token_data['token_hash']:
            raise ValueError("Invalid OTP")

        # 4. Check Expiry
        if token_data['expires_at'] < datetime.now(timezone.utc):
            self.user_repo.delete_reset_token(token_data['token_hash'])
            raise ValueError("OTP has expired")
            
        # Update password
        new_hash = self.hash_password(new_password)
        self.user_repo.update(user.id, {
            'password_hash': new_hash,
            'password_changed_at': datetime.now(timezone.utc)
        })
        
        # Invalidate token
        self.user_repo.delete_reset_token(token_data['token_hash'])

    def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        """Change password for authenticated user"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
            
        if not self.verify_password(current_password, user.password_hash):
            raise ValueError("Incorrect current password")
            
        new_hash = self.hash_password(new_password)
        self.user_repo.update(user_id, {
            'password_hash': new_hash,
            'password_changed_at': datetime.now(timezone.utc)
        })
