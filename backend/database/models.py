"""
SQLAlchemy ORM Models

Defines all database tables based on the schema documentation.
These models map directly to SQL tables.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float,
    ForeignKey, DateTime, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from database.engine import Base

def get_utc_now():
    """Get current UTC time with timezone info"""
    return datetime.now(timezone.utc)


def generate_uuid():
    """Generate a new UUID string"""
    return str(uuid.uuid4())


# ============================================
# 1. USERS TABLE
# ============================================
class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    
    # Refresh token stored with user (merged from separate table)
    refresh_token = Column(Text, nullable=True)
    refresh_token_expires_at = Column(DateTime, nullable=True)
    
    # Profile fields
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    company = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Account status
    role = Column(String(20), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 compatible
    password_changed_at = Column(DateTime, nullable=True)
    
    # Relationships
    stats = relationship("UserStats", back_populates="user", uselist=False, cascade="all, delete-orphan")
    activities = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    network_scans = relationship("NetworkScan", back_populates="user", cascade="all, delete-orphan")
    security_scans = relationship("SecurityScan", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    footprint_scans = relationship("FootprintScan", back_populates="user", cascade="all, delete-orphan")
    vpn_configs = relationship("VPNConfig", back_populates="user", cascade="all, delete-orphan")
    malware_scans = relationship("MalwareScan", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary (excludes password)"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "phone": self.phone,
            "company": self.company,
            "bio": self.bio,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "password_changed_at": self.password_changed_at.isoformat() if self.password_changed_at else None,
        }


# ============================================
# 2. USER STATISTICS TABLE
# ============================================
class UserStats(Base):
    __tablename__ = "user_stats"
    
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    
    total_scans = Column(Integer, default=0)
    phishing_checks = Column(Integer, default=0)
    security_scans = Column(Integer, default=0)
    file_analysis = Column(Integer, default=0)
    vpn_configs = Column(Integer, default=0)
    reports_generated = Column(Integer, default=0)
    malware_detected = Column(Integer, default=0)
    last_active = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="stats")
    
    def to_dict(self):
        return {
            "total_scans": self.total_scans,
            "phishing_checks": self.phishing_checks,
            "security_scans": self.security_scans,
            "file_analysis": self.file_analysis,
            "vpn_configs": self.vpn_configs,
            "reports_generated": self.reports_generated,
            "malware_detected": self.malware_detected,
            "last_active": self.last_active.isoformat() if self.last_active else None,
        }


# ============================================
# 3. ACTIVITY LOGS TABLE
# ============================================
class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action = Column(String(50), nullable=False, index=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=get_utc_now, nullable=False, index=True)
    
    # Relationship
    user = relationship("User", back_populates="activities")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_email": self.user.email if self.user else None,
            "action": self.action,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


# ============================================
# 4. NETWORK SCANS TABLE
# ============================================
class NetworkScan(Base):
    __tablename__ = "network_scans"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_number = Column(Integer, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    scan_type = Column(String(30), nullable=False)
    target = Column(String(255), nullable=False)
    status = Column(String(20), default="pending")
    results = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    started_at = Column(DateTime, default=get_utc_now)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="network_scans")
    
    def to_dict(self):
        return {
            "id": self.id,
            "scan_number": self.scan_number,
            "user_id": self.user_id,
            "scan_type": self.scan_type,
            "target": self.target,
            "status": self.status,
            "results": self.results,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
        }


# ============================================
# 5. SECURITY SCANS TABLE
# ============================================
class SecurityScan(Base):
    __tablename__ = "security_scans"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    category = Column(String(30), nullable=False)  # ssl, headers, phishing
    target = Column(Text, nullable=False)
    risk_level = Column(String(20), nullable=True)
    results = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=get_utc_now)
    
    # Relationship
    user = relationship("User", back_populates="security_scans")


# ============================================
# 6. CHAT SESSIONS TABLE
# ============================================
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(100), default="New Chat")
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


# ============================================
# 7. CHAT MESSAGES TABLE
# ============================================
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=get_utc_now)
    
    # Relationship
    session = relationship("ChatSession", back_populates="messages")


# ============================================
# 8. FOOTPRINT SCANS TABLE
# ============================================
class FootprintScan(Base):
    __tablename__ = "footprint_scans"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    email_scanned = Column(String(255), nullable=True)
    username_scanned = Column(String(50), nullable=True)
    phone_scanned = Column(String(20), nullable=True)
    platforms_checked = Column(JSON, nullable=True)
    
    score = Column(Integer, default=100)
    status = Column(String(20), default="pending")
    progress = Column(Integer, default=0)
    recommendations = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    started_at = Column(DateTime, default=get_utc_now)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="footprint_scans")
    findings = relationship("FootprintFinding", back_populates="scan", cascade="all, delete-orphan")


# ============================================
# 9. FOOTPRINT FINDINGS TABLE
# ============================================
class FootprintFinding(Base):
    __tablename__ = "footprint_findings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_id = Column(String(36), ForeignKey("footprint_scans.id", ondelete="CASCADE"), nullable=False, index=True)
    
    category = Column(String(50), nullable=True)
    source = Column(String(50), nullable=True)
    severity = Column(String(20), nullable=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    found_at = Column(DateTime, default=get_utc_now)
    
    # Relationship
    scan = relationship("FootprintScan", back_populates="findings")


# ============================================
# 10. VPN SERVERS TABLE
# ============================================
class VPNServer(Base):
    __tablename__ = "vpn_servers"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    region = Column(String(50), nullable=True)
    is_online = Column(Boolean, default=True)
    current_load = Column(String(10), nullable=True)
    
    # Relationship
    configs = relationship("VPNConfig", back_populates="server")


# ============================================
# 11. VPN CONFIGURATIONS TABLE
# ============================================
class VPNConfig(Base):
    __tablename__ = "vpn_configs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    server_id = Column(String(50), ForeignKey("vpn_servers.id"), nullable=True)
    
    config_type = Column(String(20), default="openvpn")
    filename = Column(String(255), nullable=True)
    config_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    
    # Relationships
    user = relationship("User", back_populates="vpn_configs")
    server = relationship("VPNServer", back_populates="configs")


# ============================================
# 12. MALWARE SCANS TABLE
# ============================================
class MalwareScan(Base):
    __tablename__ = "malware_scans"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    filename = Column(String(255), nullable=True)
    file_hash = Column(String(64), nullable=False)
    risk_level = Column(String(20), nullable=True)
    is_malicious = Column(Boolean, nullable=True)
    results = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=get_utc_now)
    
    # Relationship
    user = relationship("User", back_populates="malware_scans")


# ============================================
# 13. REPORTS TABLE
# ============================================
class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=True)
    report_type = Column(String(50), nullable=True)
    file_path = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    
    # Relationship
    user = relationship("User", back_populates="reports")


# ============================================
# 14. PASSWORD RESET TOKENS TABLE
# ============================================
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=get_utc_now)
    
    # Relationship
    user = relationship("User")
