"""
File analysis and hash checking utilities
"""
import hashlib
import os
import re
import math
import time
import json
from typing import Dict, List, Optional, Tuple, BinaryIO
from datetime import datetime, timezone
from pathlib import Path

from config.settings import settings
from config.constants import HashType, RiskLevel

class FileTools:
    def __init__(self):
        self.max_file_size = settings.MAX_FILE_SIZE
        self.supported_hash_types = settings.SUPPORTED_HASH_TYPES
        self.malware_db_path = settings.LOCAL_MALWARE_DB_PATH
        self.malware_hashes = self._load_malware_database()
        self.magic_available = False
        
        # Try to initialize magic (file type detection)
        try:
            # Try python-magic-bin first (Windows)
            import magic
            self.magic_available = True
            self.magic_instance = magic.Magic(mime=True)
        except ImportError:
            try:
                # Try python-magic (Linux/macOS)
                import magic
                self.magic_available = True
                self.magic_instance = magic.Magic(mime=True)
            except (ImportError, AttributeError):
                self.magic_available = False
                print("Warning: python-magic not available. File type detection will be limited.")
        
    def _load_malware_database(self) -> Dict:
        """Load local malware hash database"""
        try:
            if os.path.exists(self.malware_db_path):
                with open(self.malware_db_path, 'r') as f:
                    data = json.load(f)
                    # Convert to dict for faster lookups
                    malware_dict = {}
                    for entry in data.get('hashes', []):
                        for hash_type in ['md5', 'sha1', 'sha256']:
                            if hash_type in entry:
                                malware_dict[entry[hash_type].lower()] = entry
                    return malware_dict
        except:
            pass
        
        # Return empty dict if database doesn't exist or can't be loaded
        return {}
    
    def _save_malware_database(self, data: Dict):
        """Save malware hash database"""
        try:
            os.makedirs(os.path.dirname(self.malware_db_path), exist_ok=True)
            with open(self.malware_db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    # ========== HASH CHECKING ==========
    
    def check_hash(self, hash_str: str, hash_type: HashType = HashType.SHA256) -> Dict:
        """
        Check hash against malware database
        
        Args:
            hash_str: Hash to check
            hash_type: Type of hash
            
        Returns:
            Dictionary with hash check results
        """
        start_time = time.time()
        hash_str = hash_str.lower().strip()
        
        results = {
            'hash': hash_str,
            'hash_type': hash_type.value,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'reputation': {
                'known_malicious': False,
                'known_clean': False,
                'detection_count': 0,
                'detection_names': [],
                'first_seen': None,
                'last_seen': None,
                'file_type': None,
                'file_size': None,
                'tags': []
            },
            'risk_level': RiskLevel.INFO,
            'confidence': 0.0,
            'sources_checked': ['local_database'],
            'recommendations': [],
            'error': None
        }
        
        try:
            # Check local malware database
            malware_info = self.malware_hashes.get(hash_str)
            
            if malware_info:
                results['reputation']['known_malicious'] = True
                results['reputation']['detection_count'] = malware_info.get('detections', 1)
                results['reputation']['detection_names'] = malware_info.get('names', ['Unknown'])
                results['reputation']['first_seen'] = malware_info.get('first_seen')
                results['reputation']['last_seen'] = malware_info.get('last_seen')
                results['reputation']['file_type'] = malware_info.get('file_type')
                results['reputation']['file_size'] = malware_info.get('file_size')
                results['reputation']['tags'] = malware_info.get('tags', [])
                
                results['risk_level'] = RiskLevel.HIGH
                results['confidence'] = 0.9
                results['recommendations'].append('Hash matches known malware - DO NOT EXECUTE')
            
            else:
                # Check if hash looks like a common/clean file
                is_common_hash = self._check_common_hashes(hash_str, hash_type)
                
                if is_common_hash:
                    results['reputation']['known_clean'] = True
                    results['risk_level'] = RiskLevel.LOW
                    results['confidence'] = 0.8
                    results['recommendations'].append('Hash matches known clean file')
                else:
                    results['risk_level'] = RiskLevel.MEDIUM
                    results['confidence'] = 0.3
                    results['recommendations'].append('Hash not in database - exercise caution')
                    results['recommendations'].append('Submit file for analysis if suspicious')
            
            # Check hash format
            if not self._validate_hash_format(hash_str, hash_type):
                results['error'] = f'Invalid {hash_type.value} hash format'
                results['confidence'] = 0.0
            
        except Exception as e:
            results['error'] = str(e)
        
        results['scan_duration_ms'] = int((time.time() - start_time) * 1000)
        return results
    
    def check_hash_batch(self, hashes: List[str], hash_type: HashType = HashType.SHA256) -> Dict:
        """
        Check multiple hashes in batch
        
        Args:
            hashes: List of hashes to check
            hash_type: Type of hashes
            
        Returns:
            Dictionary with batch check results
        """
        start_time = time.time()
        
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_hashes': len(hashes),
            'malicious_count': 0,
            'clean_count': 0,
            'unknown_count': 0,
            'results': [],
            'scan_duration_ms': 0
        }
        
        # Process each hash
        for hash_str in hashes:
            hash_result = self.check_hash(hash_str, hash_type)
            results['results'].append(hash_result)
            
            # Update counters
            if hash_result['reputation']['known_malicious']:
                results['malicious_count'] += 1
            elif hash_result['reputation']['known_clean']:
                results['clean_count'] += 1
            else:
                results['unknown_count'] += 1
        
        results['scan_duration_ms'] = int((time.time() - start_time) * 1000)
        return results
    
    def _check_common_hashes(self, hash_str: str, hash_type: HashType) -> bool:
        """Check if hash matches common/clean files"""
        # Common Windows system files (example hashes)
        common_hashes = {
            'md5': [
                'd41d8cd98f00b204e9800998ecf8427e',  # Empty file
                '098f6bcd4621d373cade4e832627b4f6',  # "test"
            ],
            'sha1': [
                'da39a3ee5e6b4b0d3255bfef95601890afd80709',  # Empty file
                'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3',  # "test"
            ],
            'sha256': [
                'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',  # Empty file
                '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',  # "test"
            ]
        }
        
        hash_list = common_hashes.get(hash_type.value, [])
        return hash_str in hash_list
    
    def _validate_hash_format(self, hash_str: str, hash_type: HashType) -> bool:
        """Validate hash format"""
        # Expected lengths for each hash type
        expected_lengths = {
            HashType.MD5: 32,
            HashType.SHA1: 40,
            HashType.SHA256: 64,
            HashType.SHA512: 128
        }
        
        expected_len = expected_lengths.get(hash_type)
        if expected_len and len(hash_str) != expected_len:
            return False
        
        # Check hex characters
        hex_pattern = re.compile(r'^[0-9a-f]+$', re.IGNORECASE)
        return bool(hex_pattern.match(hash_str))
    
    # ========== FILE ANALYSIS ==========
    
    def analyze_file(self, file_content: bytes, filename: str) -> Dict:
        """
        Analyze uploaded file
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Dictionary with file analysis results
        """
        start_time = time.time()
        
        results = {
            'filename': filename,
            'file_size': len(file_content),
            'mime_type': None,
            'hash_md5': None,
            'hash_sha1': None,
            'hash_sha256': None,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'is_executable': False,
            'is_archive': False,
            'is_encrypted': False,
            'contains_macros': False,
            'entropy': 0.0,
            'strings_found': [],
            'magic_bytes': None,
            'reputation': None,
            'risk_level': RiskLevel.INFO,
            'warnings': [],
            'error': None
        }
        
        try:
            # Check file size
            if len(file_content) > self.max_file_size:
                raise ValueError(f'File too large (max {self.max_file_size // 1024 // 1024}MB)')
            
            if len(file_content) == 0:
                raise ValueError('Empty file')
            
            # Calculate hashes
            results['hash_md5'] = self._calculate_hash(file_content, HashType.MD5)
            results['hash_sha1'] = self._calculate_hash(file_content, HashType.SHA1)
            results['hash_sha256'] = self._calculate_hash(file_content, HashType.SHA256)
            
            # Detect MIME type
            results['mime_type'] = self._detect_mime_type(file_content, filename)
            
            # Check file type
            results['is_executable'] = self._is_executable(file_content, results['mime_type'])
            results['is_archive'] = self._is_archive(results['mime_type'], filename)
            results['is_encrypted'] = self._is_encrypted(file_content)
            results['contains_macros'] = self._contains_macros(file_content, filename)
            
            # Calculate entropy
            results['entropy'] = self._calculate_entropy(file_content)
            
            # Extract strings
            results['strings_found'] = self._extract_strings(file_content)
            
            # Get magic bytes
            results['magic_bytes'] = file_content[:4].hex() if len(file_content) >= 4 else None
            
            # Check hash reputation
            hash_result = self.check_hash(results['hash_sha256'], HashType.SHA256)
            results['reputation'] = hash_result['reputation']
            results['risk_level'] = hash_result['risk_level']
            
            # Generate warnings
            results['warnings'] = self._generate_file_warnings(results)
            
        except Exception as e:
            results['error'] = str(e)
        
        results['scan_duration_ms'] = int((time.time() - start_time) * 1000)
        return results
    
    def _calculate_hash(self, data: bytes, hash_type: HashType) -> str:
        """Calculate hash of data"""
        hash_funcs = {
            HashType.MD5: hashlib.md5,
            HashType.SHA1: hashlib.sha1,
            HashType.SHA256: hashlib.sha256,
            HashType.SHA512: hashlib.sha512
        }
        
        hash_func = hash_funcs.get(hash_type)
        if hash_func:
            return hash_func(data).hexdigest()
        return ''
    
    def _detect_mime_type(self, data: bytes, filename: str) -> str:
        """Detect MIME type of file"""
        # Try using magic if available
        if self.magic_available:
            try:
                return self.magic_instance.from_buffer(data)
            except:
                pass
        
        # Fallback based on extension
        ext = Path(filename).suffix.lower()
        mime_map = {
            '.exe': 'application/x-msdownload',
            '.dll': 'application/x-msdownload',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.7z': 'application/x-7z-compressed',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip',
            '.bz2': 'application/x-bzip2',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.ico': 'image/x-icon',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.wmv': 'video/x-ms-wmv'
        }
        
        return mime_map.get(ext, 'application/octet-stream')
    
    def _is_executable(self, data: bytes, mime_type: str) -> bool:
        """Check if file is executable"""
        # Check MIME type
        exec_mimes = [
            'application/x-msdownload',  # Windows EXE/DLL
            'application/x-dosexec',     # DOS executable
            'application/x-executable',  # Linux executable
            'application/x-mach-binary', # macOS executable
            'application/x-sharedlib',   # Shared library
        ]
        
        if mime_type in exec_mimes:
            return True
        
        # Check magic bytes
        if len(data) >= 2:
            # MZ header (Windows/DOS)
            if data[:2] == b'MZ':
                return True
            
            # ELF header (Linux)
            if data[:4] == b'\x7fELF':
                return True
            
            # Mach-O header (macOS)
            if data[:4] in [b'\xfe\xed\xfa\xce', b'\xfe\xed\xfa\xcf', 
                           b'\xce\xfa\xed\xfe', b'\xcf\xfa\xed\xfe']:
                return True
        
        return False
    
    def _is_archive(self, mime_type: str, filename: str) -> bool:
        """Check if file is an archive"""
        archive_mimes = [
            'application/zip',
            'application/x-rar-compressed',
            'application/x-7z-compressed',
            'application/x-tar',
            'application/gzip',
            'application/x-bzip2',
            'application/x-lzma',
            'application/x-xz'
        ]
        
        if mime_type in archive_mimes:
            return True
        
        # Check extension
        ext = Path(filename).suffix.lower()
        archive_exts = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.lzma']
        return ext in archive_exts
    
    def _is_encrypted(self, data: bytes) -> bool:
        """Check if file appears to be encrypted (high entropy)"""
        entropy = self._calculate_entropy(data)
        return entropy > 7.5  # High entropy often indicates encryption
    
    def _contains_macros(self, data: bytes, filename: str) -> bool:
        """Check if Office file contains macros"""
        ext = Path(filename).suffix.lower()
        
        # Check for macro-enabled extensions
        macro_exts = ['.docm', '.dotm', '.xlsm', '.xltm', '.pptm', '.potm', '.ppam']
        if ext in macro_exts:
            return True
        
        # Check for VBA project in Office files
        if ext in ['.doc', '.xls', '.ppt']:
            # Look for VBA project signature
            vba_signatures = [b'VBA', b'Macros', b'PROJECT', b'VERSION']
            for sig in vba_signatures:
                if sig in data:
                    return True
        
        return False
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0
        
        entropy = 0.0
        size = len(data)
        
        # Count byte frequencies
        freq = [0] * 256
        for byte in data:
            freq[byte] += 1
        
        # Calculate entropy
        for count in freq:
            if count > 0:
                probability = count / size
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _extract_strings(self, data: bytes, min_length: int = 4) -> List[str]:
        """Extract ASCII strings from binary data"""
        strings = []
        current_string = []
        
        for byte in data:
            if 32 <= byte <= 126:  # Printable ASCII
                current_string.append(chr(byte))
            else:
                if len(current_string) >= min_length:
                    strings.append(''.join(current_string))
                current_string = []
        
        # Add last string if any
        if len(current_string) >= min_length:
            strings.append(''.join(current_string))
        
        # Return unique strings, sorted by length
        unique_strings = list(set(strings))
        unique_strings.sort(key=len, reverse=True)
        
        return unique_strings[:50]  # Limit to 50 strings
    
    def _generate_file_warnings(self, file_info: Dict) -> List[str]:
        """Generate warnings based on file analysis"""
        warnings = []
        
        # Executable warnings
        if file_info['is_executable']:
            warnings.append('File is an executable - may contain malware')
        
        # Archive warnings
        if file_info['is_archive']:
            warnings.append('File is an archive - may contain multiple files')
        
        # Encrypted warnings
        if file_info['is_encrypted']:
            warnings.append('File appears to be encrypted - cannot inspect contents')
        
        # Macro warnings
        if file_info['contains_macros']:
            warnings.append('Office file contains macros - may be malicious')
        
        # High entropy warning
        if file_info['entropy'] > 7.0:
            warnings.append('High entropy detected - file may be encrypted or packed')
        
        # Malware hash match
        if file_info['reputation'] and file_info['reputation']['known_malicious']:
            warnings.append('File hash matches known malware - DO NOT EXECUTE')
        
        # Large file warning
        if file_info['file_size'] > 5 * 1024 * 1024:  # 5MB
            warnings.append('Large file size - may take time to analyze')
        
        return warnings[:5]  # Limit to 5 warnings

# Global instance
file_tools = FileTools()