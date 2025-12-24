from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from datetime import datetime

# User Profile Update
class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v
    
    @validator('bio')
    def validate_bio(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('Bio must be less than 500 characters')
        return v

# Password Change
class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

# Activity Log Entry
class ActivityLog(BaseModel):
    id: str
    user_id: str
    action: str
    details: Optional[Dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: str

# User Statistics
class UserStats(BaseModel):
    total_scans: int = 0
    phishing_checks: int = 0
    vpn_configs: int = 0
    reports_generated: int = 0
    last_active: Optional[str] = None

# Response Models
class ActivityResponse(BaseModel):
    activities: List[ActivityLog]
    total: int
    page: int
    limit: int

class StatsResponse(BaseModel):
    stats: UserStats

class DeleteAccountRequest(BaseModel):
    password: str  # Require password for account deletion