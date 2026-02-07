"""
Background worker for async scanning tasks
"""
import asyncio
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from model.Auth_Model import db
from utils.network_tools import network_tools
from utils.security_tools import security_tools
from utils.phishing_tools import phishing_tools
from utils.file_tools import file_tools
from utils.cache_tools import cache_tools
from service.Scan_Service import scan_service
from service.Security_Service import security_service
from service.File_Service import file_service

class ScanWorker:
    def __init__(self):
        self.db = db
        self.active_scans = {}
    
    async def perform_async_scan(self, scan_id: str, scan_type: str, target: str, user_id: str, params: Dict = None) -> Dict:
        """Perform scan asynchronously"""
        try:
            # Update scan status
            self.db.update_scan(scan_id, {
                'status': 'running',
                'started_at': datetime.now(timezone.utc).isoformat()
            })
            
            # Perform scan based on type
            results = {}
            start_time = time.time()
            
            if scan_type in ['domain', 'whois', 'dns', 'subdomains', 'ip', 'ports']:
                # Use existing scan service
                results = await asyncio.to_thread(
                    scan_service.perform_scan, scan_id
                )
            
            elif scan_type == 'ssl':
                # SSL/TLS scan
                from model.Security_Model import SSLScanRequest
                request = SSLScanRequest(
                    domain=target,
                    port=params.get('port', 443) if params else 443
                )
                results = await asyncio.to_thread(
                    security_service.scan_ssl, user_id, request
                )
            
            elif scan_type == 'headers':
                # HTTP headers scan
                from model.Security_Model import HeaderScanRequest
                request = HeaderScanRequest(
                    url=target,
                    follow_redirects=params.get('follow_redirects', True) if params else True
                )
                results = await asyncio.to_thread(
                    security_service.scan_headers, user_id, request
                )
            
            elif scan_type == 'phishing':
                # Phishing check
                from model.Security_Model import PhishingCheckRequest
                request = PhishingCheckRequest(
                    url=target,
                    deep_analysis=params.get('deep_analysis', False) if params else False
                )
                results = await asyncio.to_thread(
                    security_service.check_phishing, user_id, request
                )
            
            elif scan_type == 'hash_check':
                # Hash check
                from model.File_Model import HashCheckRequest
                from config.constants import HashType
                request = HashCheckRequest(
                    hash=target,
                    hash_type=HashType(params.get('hash_type', 'sha256')) if params else HashType.SHA256
                )
                results = await asyncio.to_thread(
                    file_service.check_hash, user_id, request
                )
            
            else:
                raise ValueError(f"Unsupported async scan type: {scan_type}")
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Update scan with results
            self.db.update_scan(scan_id, {
                'status': 'completed',
                'results': results,
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'duration_ms': duration_ms
            })
            
            # Update user stats
            self._update_user_stats(user_id, scan_type)
            
            return results
            
        except Exception as e:
            # Update scan with error
            duration_ms = int((time.time() - start_time) * 1000)
            
            self.db.update_scan(scan_id, {
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'duration_ms': duration_ms
            })
            
            raise
    
    def _update_user_stats(self, user_id: str, scan_type: str):
        """Update user statistics after scan"""
        stats_key = ''
        
        # Map scan types to stat keys
        stat_mapping = {
            'ssl': 'security_scans',
            'headers': 'security_scans',
            'phishing': 'phishing_checks',
            'hash_check': 'file_analysis',
            'domain': 'total_scans',
            'ip': 'total_scans',
            'ports': 'total_scans',
            'whois': 'total_scans',
            'dns': 'total_scans',
            'subdomains': 'total_scans'
        }
        
        stats_key = stat_mapping.get(scan_type, 'total_scans')
        
        if stats_key:
            self.db.update_user_stats(user_id, {stats_key: 1})
    
    async def batch_process(self, scan_tasks: List[Dict]) -> Dict:
        """Process multiple scans in batch"""
        results = {
            'total': len(scan_tasks),
            'completed': 0,
            'failed': 0,
            'results': [],
            'start_time': datetime.now(timezone.utc).isoformat()
        }
        
        # Process tasks concurrently
        tasks = []
        for task in scan_tasks:
            task_obj = asyncio.create_task(
                self.perform_async_scan(
                    task['scan_id'],
                    task['scan_type'],
                    task['target'],
                    task['user_id'],
                    task.get('params')
                )
            )
            tasks.append(task_obj)
        
        # Wait for all tasks to complete
        scan_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(scan_results):
            if isinstance(result, Exception):
                results['failed'] += 1
                results['results'].append({
                    'scan_id': scan_tasks[i]['scan_id'],
                    'status': 'failed',
                    'error': str(result)
                })
            else:
                results['completed'] += 1
                results['results'].append({
                    'scan_id': scan_tasks[i]['scan_id'],
                    'status': 'completed',
                    'results': result
                })
        
        results['end_time'] = datetime.now(timezone.utc).isoformat()
        results['success_rate'] = results['completed'] / results['total'] if results['total'] > 0 else 0
        
        return results
    
    def get_worker_status(self) -> Dict:
        """Get worker status"""
        return {
            'status': 'active',
            'active_scans': len(self.active_scans),
            'memory_usage': 'N/A',  # Would use psutil in production
            'uptime': 'N/A',  # Would track in production
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def cleanup_old_scans(self, hours: int = 24):
        """Clean up old scan records"""
        import time
        cutoff_time = time.time() - (hours * 3600)
        
        scans_to_delete = []
        for scan_id, scan in list(self.db.scans.items()):
            # Check if scan is old and completed/failed
            if 'started_at' in scan:
                try:
                    scan_time = time.mktime(datetime.fromisoformat(scan['started_at']).timetuple())
                    if scan_time < cutoff_time and scan.get('status') in ['completed', 'failed']:
                        scans_to_delete.append(scan_id)
                except:
                    continue
        
        # Delete old scans
        for scan_id in scans_to_delete:
            del self.db.scans[scan_id]
        
        return {
            'deleted': len(scans_to_delete),
            'remaining': len(self.db.scans),
            'message': f'Cleaned up {len(scans_to_delete)} scans older than {hours} hours'
        }

# Global instance
scan_worker = ScanWorker()