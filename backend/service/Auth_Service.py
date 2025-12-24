from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt, JWTError
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

class AuthService:
    def __init__(self, db):
        self.db = db
        # Load environment variables
        self.secret_key = os.getenv('SECRET_KEY', 'fsocitey-backup-key-change-this')
        self.algorithm = os.getenv('ALGORITHM', 'HS256')
        self.access_token_expire = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 15))
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
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)
        
        payload.update({'exp': expire, 'type': 'access'})
        access_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return access_token
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        payload = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire)
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
        """Register new user with additional fields"""
        existing_user = self.db.get_userby_email(user_data['email'])
        if existing_user:
            raise ValueError("User already exists")
        
        hashed_pass = self.hash_password(user_data['password'])

        user_save = {
            'email': user_data['email'],
            'username': user_data['username'],
            'hashed_password': hashed_pass,
            'full_name': user_data.get('full_name'),
            'phone': user_data.get('phone'),
            'company': user_data.get('company'),
            'bio': user_data.get('bio'),
            'role': user_data.get('role', 'user'),  # Add role, default to 'user'
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        }

        user_id = self.db.save_user(user_save)

        return {
            'id': user_id,
            'email': user_data['email'],
            'username': user_data['username'],
            'full_name': user_data.get('full_name'),
            'phone': user_data.get('phone'),
            'company': user_data.get('company'),
            'bio': user_data.get('bio'),
            'role': user_data.get('role', 'user'),
            'created_at': user_save['created_at']
        }
    
    def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate user"""
        user = self.db.get_userby_email(email)
        
        if not user:
            return None
        
        if not self.verify_password(password, user['hashed_password']):
            return None
        
        if not user.get('is_active', True):
            return None
        
        return user
    
    def login_user(self, email: str, password: str) -> dict:
        """Login user and return tokens"""
        user = self.authenticate_user(email, password)
        if not user:
            raise ValueError("Invalid credentials")
        
        # Include role in token payload
        token_payload = {
            'sub': user['id'], 
            'email': user['email'],
            'role': user.get('role', 'user')  # Include role in JWT
        }
        
        access_token = self.create_access_token(token_payload)
        refresh_token = self.create_refresh_token(token_payload)

        self.db.save_refresh_token(user['id'], refresh_token)

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
        payload = self.verify_token(refresh_token, 'refresh')
        if not payload:
            return None
        
        user_id = payload.get('sub')
        if not user_id:
            return None
        
        stored_token = self.db.get_refresh_token(user_id)
        if stored_token != refresh_token:
            return None
        
        user = self.db.get_userby_id(user_id)
        if not user:
            return None
        
        # Include role when refreshing token
        payload_access_token = {
            'sub': user['id'], 
            'email': user['email'],
            'role': user.get('role', 'user')
        }
        new_access_token = self.create_access_token(payload_access_token)
        return new_access_token
    
    def logout(self, user_id: str, refresh_token: str):
        """Logout user by deleting refresh token"""
        # Verify the refresh token before deleting
        payload = self.verify_token(refresh_token, 'refresh')
        if payload and payload.get('sub') == user_id:
            self.db.delete_refresh_token(user_id)

    def get_current_user(self, token: str) -> Optional[dict]:
        """Get current user from token"""
        payload = self.verify_token(token, 'access')
        if not payload:
            return None
        
        user_id = payload.get('sub')
        if not user_id:
            return None
        
        user = self.db.get_userby_id(user_id)
        return user