"""
Activity Repository - Database operations for activity logs

Handles all activity logging and retrieval operations.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.repositories.base import BaseRepository
from database.models import ActivityLog, User


class ActivityRepository(BaseRepository[ActivityLog]):
    """
    Repository for ActivityLog operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    # ==================== CRUD ====================
    
    def create(self, data: Dict[str, Any]) -> ActivityLog:
        """Create a new activity log"""
        activity = ActivityLog(
            user_id=data.get("user_id"),
            action=data.get("action"),
            details=data.get("details"),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            timestamp=data.get("timestamp", datetime.now(timezone.utc)),
        )
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity
    
    def get_by_id(self, id: str) -> Optional[ActivityLog]:
        """Get activity by ID"""
        return self.db.query(ActivityLog).filter(ActivityLog.id == id).first()
    
    def get_all(self, limit: int = 100, skip: int = 0) -> List[ActivityLog]:
        """Get all activities (newest first)"""
        return (
            self.db.query(ActivityLog)
            .order_by(desc(ActivityLog.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_user(self, user_id: str, limit: int = 20, skip: int = 0) -> List[ActivityLog]:
        """Get activities for a specific user"""
        return (
            self.db.query(ActivityLog)
            .filter(ActivityLog.user_id == user_id)
            .order_by(desc(ActivityLog.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_action(self, action: str, limit: int = 50, skip: int = 0) -> List[ActivityLog]:
        """Get activities by action type"""
        return (
            self.db.query(ActivityLog)
            .filter(ActivityLog.action == action)
            .order_by(desc(ActivityLog.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search(
        self,
        user_id: str = None,
        action: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict]:
        """Search activities with filters"""
        q = self.db.query(ActivityLog).join(User, ActivityLog.user_id == User.id, isouter=True)
        
        if user_id:
            q = q.filter(ActivityLog.user_id == user_id)
        
        if action:
            q = q.filter(ActivityLog.action == action)
        
        if date_from:
            q = q.filter(ActivityLog.timestamp >= date_from)
        
        if date_to:
            q = q.filter(ActivityLog.timestamp <= date_to)
        
        activities = q.order_by(desc(ActivityLog.timestamp)).offset(skip).limit(limit).all()
        
        return [a.to_dict() for a in activities]
    
    def count_by_user(self, user_id: str) -> int:
        """Count activities for a user"""
        return self.db.query(ActivityLog).filter(ActivityLog.user_id == user_id).count()
    
    def update(self, id: str, data: Dict[str, Any]) -> Optional[ActivityLog]:
        """Update activity (rarely used - logs are usually immutable)"""
        activity = self.get_by_id(id)
        if not activity:
            return None
        
        for key, value in data.items():
            if hasattr(activity, key):
                setattr(activity, key, value)
        
        self.db.commit()
        self.db.refresh(activity)
        return activity
    
    def delete(self, id: str) -> bool:
        """Delete activity by ID"""
        activity = self.get_by_id(id)
        if not activity:
            return False
        
        self.db.delete(activity)
        self.db.commit()
        return True
    
    def delete_by_user(self, user_id: str) -> int:
        """Delete all activities for a user (GDPR compliance)"""
        count = self.db.query(ActivityLog).filter(ActivityLog.user_id == user_id).delete()
        self.db.commit()
        return count
    
    # ==================== CONVENIENCE ====================
    
    def log_activity(
        self,
        user_id: str,
        action: str,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ActivityLog:
        """Convenience method to log an activity"""
        return self.create({
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
        })
