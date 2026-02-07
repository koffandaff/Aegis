"""
Footprint Models - Digital Footprint Scanner
Pydantic models for OSINT-based digital footprint analysis
"""
import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingCategory(str, Enum):
    EMAIL_EXPOSURE = "email_exposure"
    USERNAME_FOUND = "username_found"
    SOCIAL_MEDIA = "social_media"
    DATA_BREACH = "data_breach"
    PUBLIC_INFO = "public_info"


# ========================
# Request/Response Models
# ========================

class FootprintScanRequest(BaseModel):
    """Request to start a digital footprint scan"""
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)
    phone_number: Optional[str] = Field(None, description="Optional phone number with country code")
    platforms: List[str] = Field(default_factory=list, description="Selected social platforms")
    reuses_passwords: bool = False
    email_in_directories: Optional[str] = "unsure"  # yes, no, unsure
    consent_given: bool = Field(..., description="User must consent to scan")


class FindingItem(BaseModel):
    """Individual finding from the scan"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    category: FindingCategory
    source: str  # e.g., "Twitter", "GitHub", etc.
    severity: SeverityLevel
    title: str
    description: str
    url: Optional[str] = None
    found_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FootprintScanResult(BaseModel):
    """Complete scan result"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    email_scanned: str
    username_scanned: str
    phone_scanned: Optional[str] = None
    platforms_checked: List[str]
    
    # Results
    score: int = Field(ge=0, le=100, default=100)
    findings: List[FindingItem] = []
    recommendations: List[str] = []
    
    # Metadata
    status: str = "pending"  # pending, running, completed, failed
    progress: int = 0  # 0-100
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class FootprintScanSummary(BaseModel):
    """Summary for history listing"""
    id: str
    email_scanned: str
    username_scanned: str
    score: int
    findings_count: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None


# ========================
# JSON File Database
# ========================

class FootprintDatabase:
    def __init__(self, db_path: str = "data/footprint_scans.json"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file and directory exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            self._save_data({"scans": []})
    
    def _load_data(self) -> Dict:
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except:
            return {"scans": []}
    
    def _save_data(self, data: Dict):
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def create_scan(self, user_id: str, request: FootprintScanRequest) -> FootprintScanResult:
        """Create a new scan record"""
        scan = FootprintScanResult(
            user_id=user_id,
            email_scanned=request.email,
            username_scanned=request.username,
            phone_scanned=request.phone_number,
            platforms_checked=request.platforms,
            status="pending"
        )
        
        data = self._load_data()
        data["scans"].append(scan.dict())
        self._save_data(data)
        
        return scan
    
    def get_scan(self, scan_id: str, user_id: str) -> Optional[FootprintScanResult]:
        """Get a specific scan by ID"""
        data = self._load_data()
        
        for s in data["scans"]:
            if s["id"] == scan_id and s.get("user_id") == user_id:
                return FootprintScanResult(**s)
        
        return None
    
    def update_scan(self, scan_id: str, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update a scan record"""
        data = self._load_data()
        
        for s in data["scans"]:
            if s["id"] == scan_id and s.get("user_id") == user_id:
                s.update(updates)
                self._save_data(data)
                return True
        
        return False
    
    def get_user_scans(self, user_id: str) -> List[FootprintScanSummary]:
        """Get all scans for a user (summary only)"""
        data = self._load_data()
        user_scans = [s for s in data["scans"] if s.get("user_id") == user_id]
        
        # Sort by started_at descending
        user_scans.sort(key=lambda x: x.get("started_at", ""), reverse=True)
        
        return [
            FootprintScanSummary(
                id=s["id"],
                email_scanned=s.get("email_scanned", ""),
                username_scanned=s.get("username_scanned", ""),
                score=s.get("score", 0),
                findings_count=len(s.get("findings", [])),
                status=s.get("status", "unknown"),
                started_at=s.get("started_at", datetime.now(timezone.utc)),
                completed_at=s.get("completed_at")
            )
            for s in user_scans
        ]
    
    def delete_scan(self, scan_id: str, user_id: str) -> bool:
        """Delete a scan record"""
        data = self._load_data()
        original_length = len(data["scans"])
        
        data["scans"] = [
            s for s in data["scans"]
            if not (s["id"] == scan_id and s.get("user_id") == user_id)
        ]
        
        if len(data["scans"]) < original_length:
            self._save_data(data)
            return True
        
        return False


# Global database instance
footprint_db = FootprintDatabase()
