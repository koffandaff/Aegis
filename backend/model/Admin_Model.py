from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

# Admin User Management
class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

# Admin Stats
class PlatformStats(BaseModel):
    total_users: int
    active_users: int
    total_scans: int
    total_phishing_checks: int
    total_vpn_configs: int
    total_reports: int
    total_chat_sessions: int = 0
    total_chat_messages: int = 0

# User List Response
class AdminUserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    role: str
    is_active: bool
    created_at: str
    last_active: Optional[str]

class UserListResponse(BaseModel):
    users: List[AdminUserResponse]
    total: int
    page: int
    limit: int

# Activity Search
class ActivitySearch(BaseModel):
    user_id: Optional[str] = None
    action: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None