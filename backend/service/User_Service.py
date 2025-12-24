from typing import Optional, Dict, List
import uuid
from datetime import datetime
from fastapi import Request

class UserService:
    def __init__(self, db, auth_service):
        self.db = db
        self.auth_service = auth_service
    
    def update_profile(self, user_id: str, profile_data: Dict) -> Dict:
        """Update user profile"""
        user = self.db.get_userby_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Update only provided fields
        for field in ['username', 'full_name', 'phone', 'company', 'bio']:
            if field in profile_data and profile_data[field] is not None:
                user[field] = profile_data[field]
        
        # Update timestamp
        user['updated_at'] = datetime.utcnow().isoformat()
        
        return {
            'id': user_id,
            'email': user['email'],
            'username': user.get('username'),
            'full_name': user.get('full_name'),
            'phone': user.get('phone'),
            'company': user.get('company'),
            'bio': user.get('bio'),
            'role': user.get('role', 'user'),
            'created_at': user.get('created_at'),
            'updated_at': user.get('updated_at')
        }
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.db.get_userby_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not self.auth_service.verify_password(current_password, user['hashed_password']):
            raise ValueError("Current password is incorrect")
        
        # Hash new password
        new_hashed_password = self.auth_service.hash_password(new_password)
        
        # Update password
        user['hashed_password'] = new_hashed_password
        user['password_changed_at'] = datetime.utcnow().isoformat()
        
        return True
    
    def delete_account(self, user_id: str, password: str) -> bool:
        """Delete user account after password verification"""
        user = self.db.get_userby_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify password
        if not self.auth_service.verify_password(password, user['hashed_password']):
            raise ValueError("Password is incorrect")
        
        # Delete user data
        if user_id in self.db.users:
            del self.db.users[user_id]
        
        # Delete refresh token
        if user_id in self.db.refresh_tokens:
            del self.db.refresh_tokens[user_id]
        
        # Delete activities
        if user_id in self.db.user_activities:
            del self.db.user_activities[user_id]
        
        # Delete stats
        if user_id in self.db.user_stats:
            del self.db.user_stats[user_id]
        
        return True
    
    def get_user_activities(self, user_id: str, limit: int = 20, page: int = 1) -> Dict:
        """Get user activity logs"""
        skip = (page - 1) * limit
        activities = self.db.get_user_activities(user_id, limit, skip)
        total = self.db.get_user_activity_count(user_id)
        
        return {
            'activities': activities,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit  # Ceiling division
        }
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics"""
        return self.db.get_user_stats(user_id)
    
    def log_activity(self, user_id: str, action: str, details: Optional[Dict] = None,
                     request: Optional[Request] = None):
        """Log user activity"""
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get('user-agent')
        
        # Update last active
        self.db.update_user_stats(user_id, {'last_active': datetime.utcnow().isoformat()})
        
        # Log the activity
        return self.db.log_activity(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )