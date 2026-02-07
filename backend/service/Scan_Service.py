"""
Scan Service - SQLite Version

Handles network scanning with security features.
Uses SQLAlchemy repositories instead of TempDb.
"""
from typing import Dict, Optional, List
from datetime import datetime, timezone
import time
from sqlalchemy.orm import Session

from model.Scan_Model import ScanType, ScanStatus, ScanValidator
from utils.ssrf_guard import ssrf_guard
from utils.network_tools import network_tools
from utils.rate_limiter import rate_limiter

from database.repositories.scan_repository import ScanRepository
from database.repositories.user_repository import UserRepository
from database.repositories.activity_repository import ActivityRepository


class ScanService:
    """Scan service using SQLite database."""
    
    def __init__(self, db: Session):
        self.db = db
        self.scan_repo = ScanRepository(db)
        self.user_repo = UserRepository(db)
        self.activity_repo = ActivityRepository(db)
    
    def validate_and_create_scan(self, user_id: str, scan_type: str, target: str) -> str:
        """Validate scan request and create scan entry"""
        # Validate target based on scan type
        if scan_type in ["domain", "whois", "dns", "subdomains", "full"]:
            if not ScanValidator.validate_domain(target):
                raise ValueError("Invalid domain format")
            
            # SSRF protection
            if not ssrf_guard.validate_target(target, "domain"):
                raise ValueError("Scan target not allowed for security reasons")
        
        elif scan_type == "ip":
            if not ScanValidator.validate_ip(target):
                raise ValueError("Invalid IP address format")
            
            # SSRF protection
            if not ssrf_guard.validate_target(target, "ip"):
                raise ValueError("IP scanning not allowed for security reasons")
        
        elif scan_type == "ports":
            # Check if target is IP or domain
            if ScanValidator.validate_ip(target):
                if not ssrf_guard.validate_target(target, "ip"):
                    raise ValueError("Port scanning not allowed for security reasons")
            elif ScanValidator.validate_domain(target):
                if not ssrf_guard.validate_target(target, "domain"):
                    raise ValueError("Domain not allowed for security reasons")
            else:
                raise ValueError("Invalid target for port scan")
        
        else:
            raise ValueError(f"Unknown scan type: {scan_type}")
        
        # Sanitize target
        sanitized_target = ssrf_guard.sanitize_input(target)
        
        # Create scan record via repository
        scan = self.scan_repo.create({
            "user_id": user_id,
            "scan_type": scan_type,
            "target": sanitized_target,
            "status": "pending"
        })
        
        return scan.id
    
    def perform_scan(self, scan_id: str) -> Dict:
        """Perform the actual scan (synchronous for now)"""
        scan = self.scan_repo.get_by_id(scan_id)
        if not scan:
            raise ValueError("Scan not found")
        
        start_time = time.time()
        
        try:
            # Update scan status
            self.scan_repo.update(scan_id, {
                'status': 'running',
                'started_at': datetime.now(timezone.utc)
            })
            
            # Perform scan based on type
            results = {}
            print(f"[DEBUG] Initiating {scan.scan_type} scan for target: {scan.target} (User: {scan.user_id})")
            
            if scan.scan_type == 'domain':
                results = network_tools.full_domain_scan(scan.target)
            
            elif scan.scan_type == 'whois':
                results = network_tools.get_whois(scan.target)
            
            elif scan.scan_type == 'dns':
                results = network_tools.get_dns_records(scan.target)
            
            elif scan.scan_type == 'subdomains':
                results = network_tools.find_subdomains(scan.target)
            
            elif scan.scan_type == 'ip':
                results = network_tools.get_ip_info(scan.target)
            
            elif scan.scan_type == 'ports':
                # For domain targets, get IP first
                if ScanValidator.validate_domain(scan.target):
                    print(f"[DEBUG] Resolving domain {scan.target} to IP for port scan...")
                    dns_results = network_tools.get_dns_records(scan.target)
                    if dns_results.get('a_records'):
                        target_ip = dns_results['a_records'][0]
                        print(f"[DEBUG] Resolved to {target_ip}. Starting port scan...")
                        results = network_tools.scan_ports(target_ip)
                        results['domain'] = scan.target
                    else:
                        print(f"[ERROR] Could not resolve {scan.target}")
                        raise ValueError("Could not resolve domain to IP")
                else:
                    print(f"[DEBUG] Starting direct IP port scan on {scan.target}")
                    results = network_tools.scan_ports(scan.target)
            
            else:
                print(f"[ERROR] Unsupported scan type: {scan.scan_type}")
                raise ValueError(f"Unsupported scan type: {scan.scan_type}")
            
            # Generate Intelligent Summary
            scan_summary = network_tools.generate_scan_summary(scan.scan_type, scan.target, results)
            results['analysis_summary'] = scan_summary
            
            print(f"[DEBUG] Scan {scan_id} completed successfully. Results size: {len(str(results))} bytes")
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Update scan with results
            self.scan_repo.update(scan_id, {
                'status': 'completed',
                'results': results,
                'completed_at': datetime.now(timezone.utc),
                'duration_ms': duration_ms
            })
            
            # Log scan activity
            self.activity_repo.log_activity(
                user_id=scan.user_id,
                action='scan',
                details={'scan_type': scan.scan_type, 'target': scan.target, 'duration_ms': duration_ms}
            )
            
            # Update user stats
            self._update_user_stats(scan.user_id, scan.scan_type)
            
            return results
            
        except Exception as e:
            # Update scan with error
            duration_ms = int((time.time() - start_time) * 1000)
            
            self.scan_repo.update(scan_id, {
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.now(timezone.utc),
                'duration_ms': duration_ms
            })
            
            raise
    
    def _update_user_stats(self, user_id: str, scan_type: str):
        """Update user statistics after scan"""
        # All scan types count as total_scans
        stats = self.user_repo.get_stats(user_id)
        if stats:
            current_scans = stats.total_scans or 0
            self.user_repo.update_stats(user_id, {'total_scans': current_scans + 1})
    
    def check_rate_limit(self, user_id: str, endpoint: str) -> tuple:
        """Check rate limit for user"""
        return rate_limiter.is_allowed(user_id, endpoint)
    
    def get_scan(self, scan_id: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """Get scan by ID with optional ownership check"""
        scan = self.scan_repo.get_by_id(scan_id)
        
        if not scan:
            return None
        
        # If user_id provided, check ownership
        if user_id and scan.user_id != user_id:
            # Check if user is admin
            user = self.user_repo.get_by_id(user_id)
            if not user or user.role != 'admin':
                return None
        
        # Convert to dict
        return self._scan_to_dict(scan)
    
    def get_user_scans(self, user_id: str, limit: int = 20, page: int = 1) -> Dict:
        """Get scans for a specific user"""
        skip = (page - 1) * limit
        scans = self.scan_repo.get_by_user(user_id, limit, skip)
        total = self.scan_repo.count_by_user(user_id)
        
        return {
            'scans': [self._scan_to_dict(s) for s in scans],
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit if limit > 0 else 1
        }
    
    def delete_scan(self, scan_id: str, user_id: str) -> bool:
        """Delete scan if user owns it or is admin"""
        scan = self.scan_repo.get_by_id(scan_id)
        if not scan:
            return False
        
        # Check ownership
        if scan.user_id != user_id:
            # Check if user is admin
            user = self.user_repo.get_by_id(user_id)
            if not user or user.role != 'admin':
                return False
        
        self.scan_repo.delete(scan_id)
        return True
    
    def _scan_to_dict(self, scan) -> Dict:
        """Convert NetworkScan model to dictionary"""
        return {
            'id': scan.id,
            'user_id': scan.user_id,
            'scan_type': scan.scan_type,
            'target': scan.target,
            'status': scan.status,
            'results': scan.results,
            'error': scan.error,
            'started_at': scan.started_at.isoformat() if scan.started_at else None,
            'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
            'duration_ms': scan.duration_ms,
            'scan_number': scan.scan_number
        }