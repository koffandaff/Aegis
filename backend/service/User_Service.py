"""
User Service - SQLite Version

Handles user profile management, password changes, and activity logging.
Uses SQLAlchemy repositories instead of TempDb.
"""
from typing import Optional, Dict, List
from datetime import datetime, timezone
from fastapi import Request
from sqlalchemy.orm import Session

from database.repositories.user_repository import UserRepository
from database.repositories.activity_repository import ActivityRepository
from service.Auth_Service import AuthService


class UserService:
    """User service using SQLite database."""
    
    def __init__(self, db: Session, auth_service: AuthService = None):
        self.db = db
        self.user_repo = UserRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.auth_service = auth_service or AuthService(db)
    
    def update_profile(self, user_id: str, profile_data: Dict) -> Dict:
        """Update user profile"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Build update dict with only provided fields
        update_dict = {}
        for field in ['username', 'full_name', 'phone', 'company', 'bio']:
            if field in profile_data and profile_data[field] is not None:
                update_dict[field] = profile_data[field]
        
        # Update via repository
        updated_user = self.user_repo.update(user_id, update_dict)
        
        return {
            'id': updated_user.id,
            'email': updated_user.email,
            'username': updated_user.username,
            'full_name': updated_user.full_name,
            'phone': updated_user.phone,
            'company': updated_user.company,
            'bio': updated_user.bio,
            'role': updated_user.role or 'user',
            'created_at': updated_user.created_at.isoformat() if updated_user.created_at else None,
            'updated_at': updated_user.updated_at.isoformat() if updated_user.updated_at else None
        }
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not self.auth_service.verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Hash new password and update
        new_hashed_password = self.auth_service.hash_password(new_password)
        
        self.user_repo.update(user_id, {
            'password_hash': new_hashed_password,
            'password_changed_at': datetime.now(timezone.utc)
        })
        
        # Log activity
        self.activity_repo.log_activity(
            user_id=user_id,
            action='password_change',
            details={'status': 'success'}
        )
        
        return True
    
    def delete_account(self, user_id: str, password: str) -> bool:
        """Delete user account after password verification"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify password
        if not self.auth_service.verify_password(password, user.password_hash):
            raise ValueError("Password is incorrect")
        
        # Delete via repository (cascades to related data)
        self.user_repo.delete(user_id)
        
        return True
    
    def get_user_activities(self, user_id: str, limit: int = 20, page: int = 1) -> Dict:
        """Get user activity logs"""
        skip = (page - 1) * limit
        
        # Get activities from repository
        activities = self.activity_repo.get_by_user(user_id, limit=limit, offset=skip)
        total = self.activity_repo.count_by_user(user_id)
        
        # Convert to dicts
        activities_list = []
        for activity in activities:
            activities_list.append({
                'id': activity.id,
                'action': activity.action,
                'details': activity.details,
                'ip_address': activity.ip_address,
                'user_agent': activity.user_agent,
                'timestamp': activity.timestamp.isoformat() if activity.timestamp else None
            })
        
        return {
            'activities': activities_list,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit if limit > 0 else 1
        }
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics"""
        stats = self.user_repo.get_stats(user_id)
        
        if not stats:
            return {
                'total_scans': 0,
                'phishing_checks': 0,
                'security_scans': 0,
                'vpn_configs': 0,
                'reports_generated': 0,
                'file_analysis': 0,
                'malware_detected': 0,
                'last_active': None
            }
        
        return {
            'total_scans': stats.total_scans or 0,
            'phishing_checks': stats.phishing_checks or 0,
            'security_scans': stats.security_scans or 0,
            'vpn_configs': stats.vpn_configs or 0,
            'reports_generated': stats.reports_generated or 0,
            'file_analysis': stats.file_analysis or 0,
            'malware_detected': stats.malware_detected or 0,
            'last_active': stats.last_active.isoformat() if stats.last_active else None
        }
    
    def log_activity(self, user_id: str, action: str, details: Optional[Dict] = None,
                     request: Optional[Request] = None):
        """Log user activity"""
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get('user-agent')
        
        # Update last active
        self.user_repo.update_stats(user_id, {'last_active': datetime.now(timezone.utc)})
        
        # Log the activity
        return self.activity_repo.log_activity(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def increment_stat(self, user_id: str, stat_name: str, increment: int = 1):
        """Increment a specific user statistic"""
        stats = self.user_repo.get_stats(user_id)
        if stats:
            current_value = getattr(stats, stat_name, 0) or 0
            self.user_repo.update_stats(user_id, {stat_name: current_value + increment})