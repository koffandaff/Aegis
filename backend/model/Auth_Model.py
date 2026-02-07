from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, List
from datetime import datetime, timezone
from enum import Enum

# Role Enum
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

# All Validation fields 
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    role: UserRole = UserRole.USER  # Default role is user

    @validator('password')
    def password_strength(cls, v):
        import re
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('username')
    def username_length(cls, v):
        import re
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('bio')
    def bio_length(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('Bio must be less than 500 characters')
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TokenData(BaseModel):
    email: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    otp: str # 6-digit code
    new_password: str
    
    @validator('new_password')
    def password_strength(cls, v):
        import re
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('Password must contain at least one special character')
        return v
    
class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str

    @validator('new_password')
    def password_strength(cls, v):
        import re
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('Password must contain at least one special character')
        return v
   
class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    role: str = "user"
    created_at: str
    updated_at: Optional[str] = None
    password_changed_at: Optional[str] = None

# Our mock database for testing
class TempDb:
    def __init__(self):
        self.users = {}
        self.refresh_tokens = {}
        self.token_metadata = {}
        self.user_activities = {}    # Store user activities
        self.user_stats = {}         # Store user statistics
        self.scans = {}  # NEW: Store scan results
        self.scan_counter = 0
    
    def save_user(self, user_data: dict) -> str:
        from datetime import datetime
        import uuid

        user_id = str(uuid.uuid4())
        user_data['id'] = user_id
        user_data['created_at'] = datetime.now(timezone.utc).isoformat()
        user_data['is_active'] = True
        # Ensure role is saved
        if 'role' not in user_data:
            user_data['role'] = 'user'
        self.users[user_id] = user_data
        return user_id
    
    def get_userby_email(self, email: str) -> Optional[dict]:
        for user in self.users.values():
            if user.get('email') == email:
                return user
        return None
    
    def get_userby_id(self, user_id: str) -> Optional[dict]:
        return self.users.get(user_id)
    
    def save_refresh_token(self, user_id: str, token: str):
        self.refresh_tokens[user_id] = token
    
    def get_refresh_token(self, user_id: str) -> Optional[str]:
        return self.refresh_tokens.get(user_id)
    
    def delete_refresh_token(self, user_id: str):
        if user_id in self.refresh_tokens:
            del self.refresh_tokens[user_id]
    
    # Token metadata methods
    def save_token_metadata(self, token: str, metadata: dict):
        self.token_metadata[token] = metadata
    
    def get_token_metadata(self, token: str) -> Optional[dict]:
        return self.token_metadata.get(token)
    
    def delete_token_metadata(self, token: str):
        if token in self.token_metadata:
            del self.token_metadata[token]
    
    def get_all_users(self) -> list:
        return list(self.users.values())
    
    # Activity logging methods
    def log_activity(self, user_id: str, action: str, details: Optional[Dict] = None,
                     ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        import uuid
        from datetime import datetime
        
        activity_id = str(uuid.uuid4())
        activity = {
            'id': activity_id,
            'user_id': user_id,
            'action': action,
            'details': details or {},
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if user_id not in self.user_activities:
            self.user_activities[user_id] = []
        
        self.user_activities[user_id].append(activity)
        
        # Keep only last 100 activities per user
        if len(self.user_activities[user_id]) > 100:
            self.user_activities[user_id] = self.user_activities[user_id][-100:]
        
        return activity_id
    
    def get_user_activities(self, user_id: str, limit: int = 20, skip: int = 0) -> List[Dict]:
        if user_id not in self.user_activities:
            return []
        
        activities = self.user_activities[user_id][::-1]  # Reverse for newest first
        return activities[skip:skip + limit]
    
    def get_user_activity_count(self, user_id: str) -> int:
        if user_id not in self.user_activities:
            return 0
        return len(self.user_activities[user_id])
    
    # User statistics methods
    def update_user_stats(self, user_id: str, stats_update: Dict):
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                'total_scans': 0,
                'phishing_checks': 0,
                'vpn_configs': 0,
                'reports_generated': 0,
                'last_active': None
            }
        
        for key, value in stats_update.items():
            if key in self.user_stats[user_id]:
                if key.endswith('_scans') or key.endswith('_checks') or key.endswith('_configs') or key.endswith('_generated'):
                    self.user_stats[user_id][key] += value
                else:
                    self.user_stats[user_id][key] = value
    
    def get_user_stats(self, user_id: str) -> Dict:
        if user_id not in self.user_stats:
            return {
                'total_scans': 0,
                'phishing_checks': 0,
                'vpn_configs': 0,
                'reports_generated': 0,
                'last_active': None
            }
        return self.user_stats[user_id].copy()
    
    def create_scan(self, user_id: str, scan_type: str, target: str) -> str:
        import uuid
        from datetime import datetime
        
        scan_id = str(uuid.uuid4())
        self.scan_counter += 1
        
        scan = {
            'id': scan_id,
            'scan_number': self.scan_counter,
            'user_id': user_id,
            'scan_type': scan_type,
            'target': target,
            'status': 'pending',
            'results': None,
            'error': None,
            'started_at': datetime.now(timezone.utc).isoformat(),
            'completed_at': None,
            'duration_ms': None
        }
        
        self.scans[scan_id] = scan
        return scan_id
    
    def update_scan(self, scan_id: str, updates: Dict):
        if scan_id in self.scans:
            self.scans[scan_id].update(updates)
    
    def get_scan(self, scan_id: str) -> Optional[Dict]:
        return self.scans.get(scan_id)
    
    def get_user_scans(self, user_id: str, limit: int = 20, skip: int = 0) -> List[Dict]:
        user_scans = []
        for scan in self.scans.values():
            if scan['user_id'] == user_id:
                user_scans.append(scan)
        
        # Sort by started_at (newest first)
        user_scans.sort(key=lambda x: x['started_at'], reverse=True)
        return user_scans[skip:skip + limit]
    
    def get_user_scan_count(self, user_id: str) -> int:
        count = 0
        for scan in self.scans.values():
            if scan['user_id'] == user_id:
                count += 1
        return count
    
    def delete_scan(self, scan_id: str):
        if scan_id in self.scans:
            del self.scans[scan_id]
    
    def get_all_scans(self, limit: int = 50, skip: int = 0) -> List[Dict]:
        """Get all scans (for admin)"""
        all_scans = list(self.scans.values())
        all_scans.sort(key=lambda x: x['started_at'], reverse=True)
        return all_scans[skip:skip + limit]

# Global database instance
db = TempDb()