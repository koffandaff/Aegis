"""
Scan Service with Security Features
"""
from typing import Dict, Optional, List
from datetime import datetime
import time
from model.Scan_Model import ScanType, ScanStatus, ScanValidator
from utils.ssrf_guard import ssrf_guard
from utils.network_tools import network_tools
from utils.rate_limiter import rate_limiter
from model.Auth_Model import db

class ScanService:
    def __init__(self):
        self.db = db
    
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
        
        # Create scan record
        scan_id = self.db.create_scan(user_id, scan_type, sanitized_target)
        
        return scan_id
    
    def perform_scan(self, scan_id: str) -> Dict:
        """Perform the actual scan (synchronous for now)"""
        scan = self.db.get_scan(scan_id)
        if not scan:
            raise ValueError("Scan not found")
        
        start_time = time.time()
        
        try:
            # Update scan status
            self.db.update_scan(scan_id, {
                'status': 'running',
                'started_at': datetime.utcnow().isoformat()
            })
            
            # Perform scan based on type
            results = {}
            
            if scan['scan_type'] == 'domain':
                results = network_tools.full_domain_scan(scan['target'])
            
            elif scan['scan_type'] == 'whois':
                results = network_tools.get_whois(scan['target'])
            
            elif scan['scan_type'] == 'dns':
                results = network_tools.get_dns_records(scan['target'])
            
            elif scan['scan_type'] == 'subdomains':
                results = network_tools.find_subdomains(scan['target'])
            
            elif scan['scan_type'] == 'ip':
                results = network_tools.get_ip_info(scan['target'])
            
            elif scan['scan_type'] == 'ports':
                # For domain targets, get IP first
                if ScanValidator.validate_domain(scan['target']):
                    dns_results = network_tools.get_dns_records(scan['target'])
                    if dns_results.get('a_records'):
                        target_ip = dns_results['a_records'][0]
                        results = network_tools.scan_ports(target_ip)
                        results['domain'] = scan['target']
                    else:
                        raise ValueError("Could not resolve domain to IP")
                else:
                    results = network_tools.scan_ports(scan['target'])
            
            else:
                raise ValueError(f"Unsupported scan type: {scan['scan_type']}")
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Update scan with results
            self.db.update_scan(scan_id, {
                'status': 'completed',
                'results': results,
                'completed_at': datetime.utcnow().isoformat(),
                'duration_ms': duration_ms
            })
            
            # Update user stats
            self._update_user_stats(scan['user_id'], scan['scan_type'])
            
            return results
            
        except Exception as e:
            # Update scan with error
            duration_ms = int((time.time() - start_time) * 1000)
            
            self.db.update_scan(scan_id, {
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.utcnow().isoformat(),
                'duration_ms': duration_ms
            })
            
            raise
    
    def _update_user_stats(self, user_id: str, scan_type: str):
        """Update user statistics after scan"""
        stats_key = ''
        
        if scan_type == 'domain':
            stats_key = 'total_scans'
        elif scan_type == 'ip':
            stats_key = 'total_scans'  # Count as scan
        elif scan_type == 'ports':
            stats_key = 'total_scans'
        elif scan_type == 'whois':
            stats_key = 'total_scans'
        elif scan_type == 'dns':
            stats_key = 'total_scans'
        elif scan_type == 'subdomains':
            stats_key = 'total_scans'
        
        if stats_key:
            self.db.update_user_stats(user_id, {stats_key: 1})
    
    def check_rate_limit(self, user_id: str, endpoint: str) -> tuple:
        """Check rate limit for user"""
        return rate_limiter.is_allowed(user_id, endpoint)
    
    def get_scan(self, scan_id: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """Get scan by ID with optional ownership check"""
        scan = self.db.get_scan(scan_id)
        
        if not scan:
            return None
        
        # If user_id provided, check ownership
        if user_id and scan['user_id'] != user_id:
            # Check if user is admin
            user = self.db.get_userby_id(user_id)
            if not user or user.get('role') != 'admin':
                return None
        
        return scan
    
    def get_user_scans(self, user_id: str, limit: int = 20, page: int = 1) -> Dict:
        """Get scans for a specific user"""
        skip = (page - 1) * limit
        scans = self.db.get_user_scans(user_id, limit, skip)
        total = self.db.get_user_scan_count(user_id)
        
        return {
            'scans': scans,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit
        }
    
    def delete_scan(self, scan_id: str, user_id: str) -> bool:
        """Delete scan if user owns it or is admin"""
        scan = self.db.get_scan(scan_id)
        if not scan:
            return False
        
        # Check ownership
        if scan['user_id'] != user_id:
            # Check if user is admin
            user = self.db.get_userby_id(user_id)
            if not user or user.get('role') != 'admin':
                return False
        
        self.db.delete_scan(scan_id)
        return True

# Global instance
scan_service = ScanService()