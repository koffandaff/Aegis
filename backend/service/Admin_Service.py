"""
Admin Service - SQLite Version

Provides administrative functions for user management and platform statistics.
Uses SQLAlchemy repositories instead of TempDb.
"""
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from database.repositories.user_repository import UserRepository
from database.repositories.activity_repository import ActivityRepository
from model.Chat_Model import chat_db


class AdminService:
    """Admin service using SQLite database."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.activity_repo = ActivityRepository(db)
    
    def get_all_users(self, limit: int = 20, skip: int = 0, 
                      role: Optional[str] = None, 
                      active_only: bool = False,
                      search: Optional[str] = None) -> Dict:
        """Get all users with filtering and pagination"""
        # Get all users from repository
        all_users = self.user_repo.get_all()
        
        users_list = []
        for user in all_users:
            # Apply filters
            if role and user.role != role:
                continue
            
            if active_only and not user.is_active:
                continue
            
            if search:
                search_lower = search.lower()
                username = (user.username or "").lower()
                email = (user.email or "").lower()
                full_name = (user.full_name or "").lower()
                if search_lower not in username and \
                   search_lower not in email and \
                   search_lower not in full_name:
                    continue
            
            # Get user stats for last_active
            stats = user.stats
            last_active = None
            if stats:
                last_active = stats.last_active.isoformat() if stats.last_active else None
            
            users_list.append({
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.full_name,
                'phone': user.phone,
                'company': user.company,
                'role': user.role or 'user',
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_active': last_active
            })
        
        # Sort by creation date (newest first)
        users_list.sort(key=lambda x: x['created_at'] or '', reverse=True)
        
        # Apply pagination
        paginated_users = users_list[skip:skip + limit]
        
        return {
            'users': paginated_users,
            'total': len(users_list),
            'page': (skip // limit) + 1 if limit > 0 else 1,
            'limit': limit
        }
    
    def update_user(self, user_id: str, update_data: Dict) -> Dict:
        """Update any user (admin only)"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Fields that admin can update
        allowed_fields = ['username', 'full_name', 'phone', 'company', 'role', 'is_active']
        
        update_dict = {}
        for field in allowed_fields:
            if field in update_data and update_data[field] is not None:
                update_dict[field] = update_data[field]
        
        # Update via repository
        updated_user = self.user_repo.update(user_id, update_dict)
        
        return {
            'id': updated_user.id,
            'email': updated_user.email,
            'username': updated_user.username,
            'full_name': updated_user.full_name,
            'phone': updated_user.phone,
            'company': updated_user.company,
            'role': updated_user.role or 'user',
            'is_active': updated_user.is_active,
            'created_at': updated_user.created_at.isoformat() if updated_user.created_at else None,
            'updated_at': updated_user.updated_at.isoformat() if updated_user.updated_at else None
        }
    
    def delete_user(self, user_id: str):
        """Delete any user (admin only)"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Delete via repository (cascades to related data)
        self.user_repo.delete(user_id)
        return True
    
    def get_platform_stats(self) -> Dict:
        """Get platform statistics"""
        # Get all users
        all_users = self.user_repo.get_all()
        
        total_users = len(all_users)
        active_users = sum(1 for user in all_users if user.is_active)
        
        # Sum all user stats
        total_scans = 0
        total_phishing_checks = 0
        total_vpn_configs = 0
        total_reports = 0
        
        for user in all_users:
            if user.stats:
                total_scans += user.stats.total_scans or 0
                total_phishing_checks += user.stats.phishing_checks or 0
                total_vpn_configs += user.stats.vpn_configs or 0
                total_reports += user.stats.reports_generated or 0
        
        # Get chat stats
        chat_stats = chat_db.get_global_stats()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_scans': total_scans,
            'total_phishing_checks': total_phishing_checks,
            'total_vpn_configs': total_vpn_configs,
            'total_reports': total_reports,
            'total_chat_sessions': chat_stats.get('total_sessions', 0),
            'total_chat_messages': chat_stats.get('total_messages', 0)
        }
    
    def search_activities(self, user_id: Optional[str] = None, 
                         action: Optional[str] = None,
                         date_from: Optional[str] = None,
                         date_to: Optional[str] = None,
                         limit: int = 50,
                         skip: int = 0) -> List[Dict]:
        """Search activities across all users"""
        # Parse dates for repository
        d_from = None
        if date_from:
            try:
                d_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            except:
                pass
                
        d_to = None
        if date_to:
            try:
                d_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            except:
                pass

        # Use repository search which returns List[Dict] (to_dict already called)
        activities = self.activity_repo.search(
            user_id=user_id,
            action=action,
            date_from=d_from,
            date_to=d_to,
            limit=limit,
            skip=skip
        )
        
        return activities
