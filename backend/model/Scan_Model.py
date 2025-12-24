from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class ScanType(str, Enum):
    DOMAIN = "domain"
    IP = "ip"
    WHOIS = "whois"
    DNS = "dns"
    SUBDOMAINS = "subdomains"
    PORTS = "ports"
    FULL = "full"

class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# Scan Request Models
class DomainScanRequest(BaseModel):
    domain: str
    scan_type: ScanType = ScanType.FULL
    deep_scan: bool = False

class IPScanRequest(BaseModel):
    ip: str
    scan_ports: bool = True
    ports: Optional[List[int]] = None

class WhoisRequest(BaseModel):
    domain: str

class DNSRequest(BaseModel):
    domain: str
    record_types: List[str] = ["A", "AAAA", "MX", "NS", "TXT"]

class SubdomainRequest(BaseModel):
    domain: str
    use_wordlist: bool = True
    custom_wordlist: Optional[List[str]] = None

class PortScanRequest(BaseModel):
    target: str  # Can be domain or IP
    ports: List[int] = Field(default=[80, 443, 22, 21, 25, 53, 8080, 8443])
    timeout: int = Field(default=1, ge=1, le=10)

# Scan Result Models
class ScanResult(BaseModel):
    id: str
    user_id: str
    scan_type: ScanType
    target: str
    status: ScanStatus
    results: Optional[Dict] = None
    error: Optional[str] = None
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None

class ScanHistoryResponse(BaseModel):
    scans: List[ScanResult]
    total: int
    page: int
    limit: int

# Validation
class ScanValidator:
    @staticmethod
    def validate_domain(domain: str) -> bool:
        import re
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, domain))
    
    @staticmethod
    def validate_ip(ip: str) -> bool:
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except:
            return False