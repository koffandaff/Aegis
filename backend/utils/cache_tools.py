"""
Caching utilities for scan results
"""
import time
import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from collections import OrderedDict

from config.settings import settings

class CacheTools:
    """Simple in-memory cache with TTL and size limits"""
    
    def __init__(self):
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.max_size = settings.MAX_CACHE_SIZE
        self.ttl = settings.CACHE_TTL
        
    def get_key(self, scan_type: str, target: str, params: Dict = None) -> str:
        """Generate cache key from scan parameters"""
        key_data = {
            'scan_type': scan_type,
            'target': target,
            'params': params or {}
        }
        
        # Sort params for consistent keys
        if key_data['params']:
            key_data['params'] = dict(sorted(key_data['params'].items()))
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Dict]:
        """Get value from cache"""
        if not settings.CACHE_ENABLED:
            return None
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if time.time() - entry['timestamp'] > self.ttl:
                del self.cache[key]
                self.misses += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return entry['value']
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Dict) -> None:
        """Set value in cache"""
        if not settings.CACHE_ENABLED:
            return
        
        # Remove expired entries
        self._cleanup()
        
        # Add new entry
        entry = {
            'value': value,
            'timestamp': time.time(),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        self.cache[key] = entry
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        
        # Enforce size limit
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)  # Remove first (oldest)
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self, cache_type: str = None) -> Dict:
        """Clear cache or specific type"""
        if cache_type:
            # Clear entries of specific type
            keys_to_delete = []
            for key, entry in self.cache.items():
                if cache_type in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.cache[key]
            
            return {
                'cleared': len(keys_to_delete),
                'type': cache_type
            }
        else:
            # Clear all
            cleared_count = len(self.cache)
            self.cache.clear()
            
            return {
                'cleared': cleared_count,
                'type': 'all'
            }
    
    def _cleanup(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time - entry['timestamp'] > self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = len(self.cache)
        hits = self.hits
        misses = self.misses
        total_requests = hits + misses
        
        hit_rate = hits / total_requests if total_requests > 0 else 0
        miss_rate = misses / total_requests if total_requests > 0 else 0
        
        # Calculate memory usage estimate
        memory_estimate = sum(
            len(json.dumps(entry).encode()) 
            for entry in self.cache.values()
        )
        
        # Oldest and newest entries
        oldest = None
        newest = None
        if self.cache:
            oldest_key = next(iter(self.cache))
            newest_key = next(reversed(self.cache))
            oldest = self.cache[oldest_key]['created_at']
            newest = self.cache[newest_key]['created_at']
        
        return {
            'enabled': settings.CACHE_ENABLED,
            'total_entries': total,
            'max_size': self.max_size,
            'ttl_seconds': self.ttl,
            'hits': hits,
            'misses': misses,
            'hit_rate': round(hit_rate, 3),
            'miss_rate': round(miss_rate, 3),
            'memory_bytes': memory_estimate,
            'oldest_entry': oldest,
            'newest_entry': newest,
            'size_percentage': round((total / self.max_size) * 100, 1)
        }
    
    def get_entries(self, limit: int = 50) -> List[Dict]:
        """Get cache entries for inspection"""
        entries = []
        
        for key, entry in list(self.cache.items())[:limit]:
            entries.append({
                'key': key,
                'created_at': entry['created_at'],
                'age_seconds': int(time.time() - entry['timestamp']),
                'value_size': len(json.dumps(entry['value']).encode())
            })
        
        return entries

# Global cache instance
cache_tools = CacheTools()