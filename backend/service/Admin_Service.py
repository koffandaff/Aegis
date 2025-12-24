from typing import Optional, Dict, List
from datetime import datetime, timedelta

class AdminService:
    def __init__(self, db):
        self.db = db
    
    def get_all_users(self, limit: int = 20, skip: int = 0, 
                      role: Optional[str] = None, 
                      active_only: bool = False) -> Dict:
        """Get all users with filtering (admin only)"""
        users_list = []
        
        # FIXED: Use self.db.users.values() instead of self.db.values()
        for user in self.db.users.values():
            # Apply filters
            if role and user.get('role') != role:
                continue
            
            if active_only and not user.get('is_active', True):
                continue
            
            # Get user stats for last_active
            stats = self.db.get_user_stats(user['id'])
            
            users_list.append({
                'id': user['id'],
                'email': user['email'],
                'username': user.get('username'),
                'full_name': user.get('full_name'),
                'phone': user.get('phone'),
                'company': user.get('company'),
                'role': user.get('role', 'user'),
                'is_active': user.get('is_active', True),
                'created_at': user.get('created_at'),
                'last_active': stats.get('last_active')
            })
        
        # Simple sorting by creation date (newest first)
        users_list.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Apply pagination
        paginated_users = users_list[skip:skip + limit]
        
        return {
            'users': paginated_users,
            'total': len(users_list),
            'page': (skip // limit) + 1,
            'limit': limit
        }
    
    def update_user(self, user_id: str, update_data: Dict) -> Dict:
        """Update any user (admin only)"""
        user = self.db.get_userby_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Fields that admin can update
        allowed_fields = ['username', 'full_name', 'phone', 'company', 'role', 'is_active']
        
        for field in allowed_fields:
            if field in update_data and update_data[field] is not None:
                user[field] = update_data[field]
        
        user['updated_at'] = datetime.utcnow().isoformat()
        
        return {
            'id': user_id,
            'email': user['email'],
            'username': user.get('username'),
            'full_name': user.get('full_name'),
            'phone': user.get('phone'),
            'company': user.get('company'),
            'role': user.get('role', 'user'),
            'is_active': user.get('is_active', True),
            'created_at': user.get('created_at'),
            'updated_at': user.get('updated_at')
        }
    
    def delete_user(self, user_id: str):
        """Delete any user (admin only)"""
        user = self.db.get_userby_id(user_id)
        if not user:
            raise ValueError("User not found")
        
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
    
    def get_platform_stats(self) -> Dict:
        """Get platform statistics (admin only)"""
        # FIXED: Use len(self.db.users) instead of self.db.values()
        total_users = len(self.db.users)
        
        # Count active users correctly
        active_users = 0
        for user in self.db.users.values():
            if user.get('is_active', True):
                active_users += 1
        
        # Sum all user stats
        total_scans = 0
        total_phishing_checks = 0
        total_vpn_configs = 0
        total_reports = 0
        
        for user_id in self.db.users:
            stats = self.db.get_user_stats(user_id)
            total_scans += stats.get('total_scans', 0)
            total_phishing_checks += stats.get('phishing_checks', 0)
            total_vpn_configs += stats.get('vpn_configs', 0)
            total_reports += stats.get('reports_generated', 0)
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_scans': total_scans,
            'total_phishing_checks': total_phishing_checks,
            'total_vpn_configs': total_vpn_configs,
            'total_reports': total_reports
        }
    
    def search_activities(self, user_id: Optional[str] = None, 
                         action: Optional[str] = None,
                         date_from: Optional[str] = None,
                         date_to: Optional[str] = None,
                         limit: int = 50) -> List[Dict]:
        """Search activities across all users (admin only)"""
        all_activities = []
        
        # Collect all activities
        for uid, activities in self.db.user_activities.items():
            for activity in activities:
                activity_with_user = activity.copy()
                # Get user email for display
                user = self.db.get_userby_id(uid)
                activity_with_user['user_email'] = user.get('email', 'Unknown') if user else 'Unknown'
                all_activities.append(activity_with_user)
        
        # Apply filters
        filtered_activities = []
        
        for activity in all_activities:
            # User filter
            if user_id and activity['user_id'] != user_id:
                continue
            
            # Action filter
            if action and activity['action'] != action:
                continue
            
            # Date filters
            if date_from:
                try:
                    activity_date = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
                    filter_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                    if activity_date < filter_date:
                        continue
                except:
                    pass
            
            if date_to:
                try:
                    activity_date = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
                    filter_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                    if activity_date > filter_date:
                        continue
                except:
                    pass
            
            filtered_activities.append(activity)
        
        # Sort by timestamp (newest first)
        filtered_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return filtered_activities[:limit]