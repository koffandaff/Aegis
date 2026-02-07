"""
File analysis service for hash checking, malware detection, etc.
"""
from typing import Dict, Optional, List
from datetime import datetime, timezone
import time
import httpx
from sqlalchemy.orm import Session

from model.File_Model import (
    HashCheckRequest, BatchHashCheckRequest, FileUploadRequest,
    HashCheckResult, BatchHashCheckResult, FileAnalysisResult,
    VirusTotalCheckRequest, VirusTotalReport
)
from utils.ssrf_guard import ssrf_guard
from utils.file_tools import file_tools
from utils.cache_tools import cache_tools
from utils.rate_limiter import rate_limiter
from config.settings import settings
from database.repositories.user_repository import UserRepository
from database.repositories.activity_repository import ActivityRepository

class FileService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.virustotal_api_key = settings.VIRUSTOTAL_API_KEY
        self.virustotal_enabled = settings.VIRUSTOTAL_ENABLED
    
    # ========== HASH CHECKING ==========
    
    def check_hash(self, user_id: str, request: HashCheckRequest) -> Dict:
        """Check hash against malware databases"""
        # Rate limiting
        allowed, remaining, reset_in = rate_limiter.is_allowed(user_id, "scan_file_hash")
        if not allowed:
            raise ValueError(f"Rate limit exceeded. Try again in {reset_in} seconds")
        
        # Check cache
        cache_key = cache_tools.get_key("hash_check", request.hash, {"hash_type": request.hash_type})
        cached = cache_tools.get(cache_key)
        
        if cached:
            cached['user_id'] = user_id
            cached['cached'] = True
            cached['cache_hit'] = True
            return cached
        
        # Perform check
        start_time = time.time()
        
        try:
            # Validate hash format
            if not request.hash or len(request.hash.strip()) == 0:
                raise ValueError("Hash cannot be empty")
            
            # Check hash
            scan_results = file_tools.check_hash(request.hash, request.hash_type)
            
            # Add metadata
            scan_results['user_id'] = user_id
            scan_results['scan_type'] = 'hash_check'
            scan_results['request'] = request.dict()
            scan_results['cached'] = False
            scan_results['cache_hit'] = False
            scan_results['total_duration_ms'] = int((time.time() - start_time) * 1000)
            
            # Cache results
            cache_tools.set(cache_key, scan_results)
            
            # Log activity
            self.activity_repo.log_activity(
                user_id=user_id,
                action="hash_check",
                details={
                    'hash': request.hash[:8] + '...',  # Truncate for privacy
                    'hash_type': request.hash_type.value,
                    'is_malicious': scan_results['reputation']['known_malicious']
                }
            )
            
            # Update stats
            if scan_results['reputation']['known_malicious']:
                self._update_stat(user_id, {'malware_detected': 1})
            self._update_stat(user_id, {'hash_checks': 1})
            
            return scan_results
            
        except Exception as e:
            raise ValueError(f"Hash check failed: {str(e)}")
    
    def check_hash_batch(self, user_id: str, request: BatchHashCheckRequest) -> Dict:
        """Check multiple hashes in batch"""
        # Rate limiting
        allowed, remaining, reset_in = rate_limiter.is_allowed(user_id, "scan_hash_batch")
        if not allowed:
            raise ValueError(f"Rate limit exceeded. Try again in {reset_in} seconds")
        
        # Check cache for each hash
        all_cached = True
        batch_results = []
        
        for hash_str in request.hashes:
            cache_key = cache_tools.get_key("hash_check", hash_str, {"hash_type": request.hash_type})
            cached = cache_tools.get(cache_key)
            
            if cached:
                batch_results.append(cached)
            else:
                all_cached = False
                break
        
        if all_cached and batch_results:
            # All results were cached
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_hashes': len(request.hashes),
                'malicious_count': sum(1 for r in batch_results if r['reputation']['known_malicious']),
                'clean_count': sum(1 for r in batch_results if r['reputation']['known_clean']),
                'unknown_count': sum(1 for r in batch_results if not r['reputation']['known_malicious'] and not r['reputation']['known_clean']),
                'results': batch_results,
                'cached': True,
                'cache_hit': True,
                'total_duration_ms': 0
            }
        
        # Perform batch check
        start_time = time.time()
        
        try:
            # Validate all hashes
            for hash_str in request.hashes:
                if not hash_str or len(hash_str.strip()) == 0:
                    raise ValueError("Hash cannot be empty")
            
            # Check hashes
            scan_results = file_tools.check_hash_batch(request.hashes, request.hash_type)
            
            # Add metadata
            scan_results['user_id'] = user_id
            scan_results['scan_type'] = 'hash_batch_check'
            scan_results['request'] = request.dict()
            scan_results['cached'] = False
            scan_results['cache_hit'] = False
            scan_results['total_duration_ms'] = int((time.time() - start_time) * 1000)
            
            # Cache individual results
            for i, hash_str in enumerate(request.hashes):
                if i < len(scan_results['results']):
                    cache_key = cache_tools.get_key("hash_check", hash_str, {"hash_type": request.hash_type})
                    cache_tools.set(cache_key, scan_results['results'][i])
            
            # Log activity
            self.activity_repo.log_activity(
                user_id=user_id,
                action="hash_batch_check",
                details={
                    'hash_count': len(request.hashes),
                    'malicious_count': scan_results['malicious_count']
                }
            )
            
            # Update stats
            self._update_stat(user_id, {'hash_checks': len(request.hashes)})
            if scan_results['malicious_count'] > 0:
                self._update_stat(user_id, {'malware_detected': scan_results['malicious_count']})
            
            return scan_results
            
        except Exception as e:
            raise ValueError(f"Batch hash check failed: {str(e)}")
    
    # ========== FILE UPLOAD ANALYSIS ==========
    
    def analyze_file(self, user_id: str, file_content: bytes, filename: str, 
                     request: Optional[FileUploadRequest] = None,
                     use_virustotal: bool = True) -> Dict:
        """Analyze uploaded file"""
        start_time = time.time()
        
        try:
            # Check file size
            max_size = settings.MAX_FILE_SIZE
            if len(file_content) > max_size:
                raise ValueError(f"File too large (max {max_size // 1024 // 1024}MB)")
            
            if len(file_content) == 0:
                raise ValueError("Empty file")
            
            # Analyze file
            scan_results = file_tools.analyze_file(file_content, filename)
            
            # Add metadata
            scan_results['user_id'] = user_id
            scan_results['scan_type'] = 'file_analysis'
            scan_results['filename'] = filename
            scan_results['file_size'] = len(file_content)
            scan_results['request'] = request.dict() if request else {}
            scan_results['cached'] = False
            scan_results['cache_hit'] = False
            
            # VirusTotal cross-reference
            if use_virustotal and self.virustotal_enabled and self.virustotal_api_key:
                try:
                    sha256_hash = scan_results.get('hash_sha256')
                    if sha256_hash:
                        vt_result = self._query_virustotal(sha256_hash)
                        scan_results['virustotal'] = {
                            'positives': vt_result.get('positives', 0),
                            'total': vt_result.get('total', 0),
                            'permalink': vt_result.get('permalink'),
                            'scan_date': vt_result.get('scan_date'),
                            'meaningful_name': vt_result.get('meaningful_name')
                        }
                        
                        # Update risk level based on VT results
                        if vt_result.get('positives', 0) > 0:
                            scan_results['reputation']['known_malicious'] = True
                            scan_results['reputation']['detection_count'] = vt_result['positives']
                            from config.constants import RiskLevel
                            if vt_result['positives'] > 10:
                                scan_results['risk_level'] = RiskLevel.CRITICAL
                            elif vt_result['positives'] > 5:
                                scan_results['risk_level'] = RiskLevel.HIGH
                            scan_results['warnings'].append(f"VirusTotal: {vt_result['positives']}/{vt_result['total']} engines detected this file")
                except Exception as vt_error:
                    scan_results['virustotal_error'] = str(vt_error)
            
            scan_results['total_duration_ms'] = int((time.time() - start_time) * 1000)
            
            # Log activity
            self.activity_repo.log_activity(
                user_id=user_id,
                action="file_analysis",
                details={
                    'filename': filename,
                    'file_size': len(file_content),
                    'is_malicious': scan_results['reputation']['known_malicious'] if scan_results['reputation'] else False,
                    'risk_level': scan_results['risk_level'].value
                }
            )
            
            # Update stats
            self._update_stat(user_id, {'file_analysis': 1})
            if scan_results['reputation'] and scan_results['reputation']['known_malicious']:
                self._update_stat(user_id, {'malware_detected': 1})
            
            return scan_results
            
        except Exception as e:
            raise ValueError(f"File analysis failed: {str(e)}")
    
    # ========== VIRUSTOTAL INTEGRATION ==========
    
    def check_virustotal(self, user_id: str, request: VirusTotalCheckRequest) -> Dict:
        """Check hash on VirusTotal (requires API key)"""
        if not self.virustotal_enabled or not self.virustotal_api_key:
            raise ValueError("VirusTotal integration is not enabled. Set VIRUSTOTAL_API_KEY in .env")
        
        # Rate limiting (strict for VirusTotal)
        allowed, remaining, reset_in = rate_limiter.is_allowed(user_id, "scan_virustotal")
        if not allowed:
            raise ValueError(f"Rate limit exceeded. Try again in {reset_in} seconds")
        
        # Check cache
        cache_key = cache_tools.get_key("virustotal", request.hash, {})
        cached = cache_tools.get(cache_key)
        
        if cached:
            cached['user_id'] = user_id
            cached['cached'] = True
            cached['cache_hit'] = True
            return cached
        
        # Perform VirusTotal check
        start_time = time.time()
        
        try:
            # Validate hash
            if not request.hash or len(request.hash.strip()) == 0:
                raise ValueError("Hash cannot be empty")
            
            # Check VirusTotal
            vt_results = self._query_virustotal(request.hash)
            
            # Add metadata
            vt_results['user_id'] = user_id
            vt_results['scan_type'] = 'virustotal'
            vt_results['request'] = request.dict()
            vt_results['cached'] = False
            vt_results['cache_hit'] = False
            vt_results['total_duration_ms'] = int((time.time() - start_time) * 1000)
            
            # Cache results
            cache_tools.set(cache_key, vt_results)
            
            # Log activity
            self.activity_repo.log_activity(
                user_id=user_id,
                action="virustotal_check",
                details={
                    'hash': request.hash[:8] + '...',
                    'positives': vt_results.get('positives', 0),
                    'total': vt_results.get('total', 0)
                }
            )
            
            # Update stats
            self._update_stat(user_id, {'virustotal_checks': 1})
            if vt_results.get('positives', 0) > 0:
                self._update_stat(user_id, {'malware_detected': 1})
            
            return vt_results
            
        except Exception as e:
            raise ValueError(f"VirusTotal check failed: {str(e)}")
    
    def _query_virustotal(self, hash_str: str) -> Dict:
        """Query VirusTotal API"""
        try:
            headers = {
                'x-apikey': self.virustotal_api_key,
                'Accept': 'application/json'
            }
            
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f'https://www.virustotal.com/api/v3/files/{hash_str}',
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    attributes = data.get('data', {}).get('attributes', {})
                    
                    return {
                        'hash': hash_str,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'permalink': f"https://www.virustotal.com/gui/file/{hash_str}",
                        'positives': attributes.get('last_analysis_stats', {}).get('malicious', 0),
                        'total': sum(attributes.get('last_analysis_stats', {}).values()),
                        'scan_date': attributes.get('last_analysis_date'),
                        'scans': attributes.get('last_analysis_results', {}),
                        'md5': attributes.get('md5'),
                        'sha1': attributes.get('sha1'),
                        'sha256': attributes.get('sha256'),
                        'meaningful_name': attributes.get('meaningful_name'),
                        'tags': attributes.get('tags', []),
                        'times_submitted': attributes.get('times_submitted'),
                        'last_analysis_date': attributes.get('last_analysis_date')
                    }
                elif response.status_code == 404:
                    return {
                        'hash': hash_str,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'note': 'Hash not found in VirusTotal database',
                        'positives': 0,
                        'total': 0
                    }
                else:
                    raise ValueError(f"VirusTotal API error: {response.status_code}")
        
        except httpx.RequestError as e:
            raise ValueError(f"VirusTotal request failed: {str(e)}")
        except Exception as e:
            raise ValueError(f"VirusTotal processing failed: {str(e)}")
    
    # ========== MALWARE DATABASE MANAGEMENT ==========
    
    def get_malware_database_info(self, user_id: str) -> Dict:
        """Get information about the local malware database"""
        # Only admin can view database info
        user = self.user_repo.get_by_id(user_id)
        if not user or user.role != 'admin':
            raise ValueError("Admin access required")
        
        db_path = settings.LOCAL_MALWARE_DB_PATH
        
        info = {
            'name': 'Fsociety Local Malware Database',
            'version': '1.0.0',
            'hash_count': len(file_tools.malware_hashes),
            'updated_at': None,
            'source': 'Internal + Community Contributions',
            'path': db_path,
            'exists': False
        }
        
        try:
            import os
            if os.path.exists(db_path):
                import json
                with open(db_path, 'r') as f:
                    data = json.load(f)
                    info['updated_at'] = data.get('updated_at')
                    info['exists'] = True
        except:
            pass
        
        return info
    
    def update_malware_database(self, user_id: str, hashes: List[Dict]) -> Dict:
        """Update local malware database (admin only)"""
        # Only admin can update database
        user = self.user_repo.get_by_id(user_id)
        if not user or user.role != 'admin':
            raise ValueError("Admin access required")
        
        try:
            # Load existing database
            db_path = settings.LOCAL_MALWARE_DB_PATH
            existing_data = {'hashes': [], 'updated_at': None}
            
            import os
            import json
            from datetime import datetime
            
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    existing_data = json.load(f)
            
            # Add new hashes
            existing_hashes = existing_data['hashes']
            hash_dict = {h['sha256']: h for h in existing_hashes}
            
            added = 0
            updated = 0
            
            for new_hash in hashes:
                sha256 = new_hash.get('sha256')
                if sha256:
                    if sha256 in hash_dict:
                        # Update existing entry
                        hash_dict[sha256].update(new_hash)
                        updated += 1
                    else:
                        # Add new entry
                        hash_dict[sha256] = new_hash
                        added += 1
            
            # Save updated database
            existing_data['hashes'] = list(hash_dict.values())
            existing_data['updated_at'] = datetime.now(timezone.utc).isoformat()
            existing_data['total_entries'] = len(existing_data['hashes'])
            
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            with open(db_path, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            # Reload in memory
            file_tools.malware_hashes = file_tools._load_malware_database()
            
            # Log activity
            self.activity_repo.log_activity(
                user_id=user_id,
                action="malware_db_update",
                details={
                    'added': added,
                    'updated': updated,
                    'total': len(existing_data['hashes'])
                }
            )
            
            return {
                'success': True,
                'added': added,
                'updated': updated,
                'total': len(existing_data['hashes']),
                'updated_at': existing_data['updated_at']
            }
            
        except Exception as e:
            raise ValueError(f"Failed to update malware database: {str(e)}")
    
    def _update_stat(self, user_id: str, stat_updates: dict):
        """Update user statistics via repository"""
        stats = self.user_repo.get_stats(user_id)
        if stats:
            for key, increment in stat_updates.items():
                current_value = getattr(stats, key, 0) or 0
                self.user_repo.update_stats(user_id, {key: current_value + increment})
