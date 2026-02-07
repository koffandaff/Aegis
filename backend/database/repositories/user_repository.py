"""
User Repository - Database operations for users, stats, and tokens

Handles all user-related database operations including:
- User CRUD
- Authentication (password, tokens)
- User statistics
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database.repositories.base import BaseRepository
from database.models import User, UserStats


class UserRepository(BaseRepository[User]):
    """
    Repository for User operations.
    Includes stats management since User and UserStats are 1:1.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    # ==================== CRUD ====================
    
    def create(self, data: Dict[str, Any]) -> User:
        """Create a new user with stats"""
        user = User(
            email=data.get("email"),
            username=data.get("username"),
            password_hash=data.get("password_hash"),
            full_name=data.get("full_name"),
            phone=data.get("phone"),
            company=data.get("company"),
            bio=data.get("bio"),
            role=data.get("role", "user"),
            is_active=data.get("is_active", True),
        )
        self.db.add(user)
        self.db.flush()  # Get the ID without committing
        
        # Create associated stats
        stats = UserStats(user_id=user.id)
        self.db.add(stats)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_all(self, limit: int = 100, skip: int = 0) -> List[User]:
        """Get all users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def search(self, query: str = None, role: str = None, is_active: bool = None, 
               limit: int = 100, skip: int = 0) -> List[User]:
        """Search users with filters"""
        q = self.db.query(User)
        
        if query:
            q = q.filter(
                or_(
                    User.email.ilike(f"%{query}%"),
                    User.username.ilike(f"%{query}%"),
                    User.full_name.ilike(f"%{query}%")
                )
            )
        
        if role:
            q = q.filter(User.role == role)
        
        if is_active is not None:
            q = q.filter(User.is_active == is_active)
        
        return q.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    def count(self, is_active: bool = None) -> int:
        """Count users"""
        q = self.db.query(User)
        if is_active is not None:
            q = q.filter(User.is_active == is_active)
        return q.count()
    
    def update(self, id: str, data: Dict[str, Any]) -> Optional[User]:
        """Update user by ID"""
        user = self.get_by_id(id)
        if not user:
            return None
        
        for key, value in data.items():
            if hasattr(user, key) and key not in ["id", "created_at"]:
                setattr(user, key, value)
        
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, id: str) -> bool:
        """Delete user by ID (cascades to stats, activities, etc.)"""
        user = self.get_by_id(id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    # ==================== AUTHENTICATION ====================
    
    def save_refresh_token(self, user_id: str, token: str, expires_at: datetime) -> bool:
        """Save refresh token for user"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.refresh_token = token
        user.refresh_token_expires_at = expires_at
        self.db.commit()
        return True
    
    def get_refresh_token(self, user_id: str) -> Optional[str]:
        """Get refresh token for user"""
        user = self.get_by_id(user_id)
        return user.refresh_token if user else None
    
    def delete_refresh_token(self, user_id: str) -> bool:
        """Delete refresh token (logout)"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.refresh_token = None
        user.refresh_token_expires_at = None
        self.db.commit()
        return True
    
    def update_last_login(self, user_id: str, ip_address: str = None) -> bool:
        """Update last login timestamp and IP"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.last_login_at = datetime.now(timezone.utc)
        if ip_address:
            user.last_login_ip = ip_address
        self.db.commit()
        return True
    
    # ==================== STATISTICS ====================
    
    def get_stats(self, user_id: str) -> Optional[UserStats]:
        """Get user statistics"""
        return self.db.query(UserStats).filter(UserStats.user_id == user_id).first()
    
    def update_stats(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user statistics (increments numeric fields)"""
        stats = self.get_stats(user_id)
        if not stats:
            # Create stats if they don't exist
            stats = UserStats(user_id=user_id)
            self.db.add(stats)
        
        for key, value in updates.items():
            if hasattr(stats, key):
                if key == "last_active":
                    setattr(stats, key, value if isinstance(value, datetime) else datetime.fromisoformat(value))
                elif isinstance(value, int):
                    # Increment numeric fields
                    current = getattr(stats, key) or 0
                    setattr(stats, key, current + value)
                else:
                    setattr(stats, key, value)
        
        self.db.commit()
        return True
    
    def get_all_stats_sum(self) -> Dict[str, int]:
        """Get aggregated stats for all users (admin dashboard)"""
        from sqlalchemy import func
        
        result = self.db.query(
            func.sum(UserStats.total_scans).label("total_scans"),
            func.sum(UserStats.phishing_checks).label("total_phishing_checks"),
            func.sum(UserStats.vpn_configs).label("total_vpn_configs"),
            func.sum(UserStats.reports_generated).label("total_reports"),
            func.sum(UserStats.security_scans).label("total_security_scans"),
            func.sum(UserStats.malware_detected).label("total_malware_detected"),
        ).first()
        
        return {
            "total_scans": result.total_scans or 0,
            "total_phishing_checks": result.total_phishing_checks or 0,
            "total_vpn_configs": result.total_vpn_configs or 0,
            "total_reports": result.total_reports or 0,
            "total_security_scans": result.total_security_scans or 0,
            "total_malware_detected": result.total_malware_detected or 0,
        }

    # ==================== PASSWORD RESET ====================

    def create_reset_token(self, user_id: str, token_hash: str, expires_at: datetime) -> bool:
        """Create a password reset token"""
        from database.models import PasswordResetToken
        
        # Delete any existing tokens for this user
        self.db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user_id).delete()
        
        token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        self.db.add(token)
        self.db.commit()
        return True

    def get_reset_token(self, token_hash: str) -> Optional[dict]:
        """Get reset token by hash"""
        from database.models import PasswordResetToken
        
        token = self.db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()
        if not token:
            return None
            
        return {
            'user_id': token.user_id,
            'expires_at': token.expires_at,
            'token_hash': token.token_hash
        }

    def get_user_reset_token(self, user_id: str) -> Optional[dict]:
        """Get active reset token for user"""
        from database.models import PasswordResetToken
        
        token = self.db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user_id).first()
        if not token:
            return None
            
        return {
            'user_id': token.user_id,
            'expires_at': token.expires_at,
            'token_hash': token.token_hash
        }

    def delete_reset_token(self, token_hash: str) -> bool:
        """Delete used reset token"""
        from database.models import PasswordResetToken
        
        self.db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).delete()
        self.db.commit()
        return True
