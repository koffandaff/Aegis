"""
Rate Limiting for API endpoints
Prevents abuse of scanning endpoints
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
import time

class RateLimiter:
    def __init__(self):
        # Store request counts: {user_id: {endpoint: [timestamps]}}
        self.requests: Dict[str, Dict[str, list]] = {}
        
        # Rate limits (requests per minute)
        self.limits = {
            "scan_domain": 5,    # 5 domain scans per minute
            "scan_ip": 10,       # 10 IP scans per minute  
            "scan_ports": 3,     # 3 port scans per minute
            "scan_whois": 10,    # 10 WHOIS lookups per minute
            "scan_dns": 15,      # 15 DNS lookups per minute
            "scan_subdomains": 2, # 2 subdomain scans per minute
        }
        
        # Clean up interval (seconds)
        self.cleanup_interval = 300  # 5 minutes
    
    def is_allowed(self, user_id: str, endpoint: str) -> tuple:
        """
        Check if user is allowed to make a request
        Returns: (allowed: bool, remaining: int, reset_time: int)
        """
        now = time.time()
        
        # Initialize user data if not exists
        if user_id not in self.requests:
            self.requests[user_id] = {}
        
        if endpoint not in self.requests[user_id]:
            self.requests[user_id][endpoint] = []
        
        # Clean old timestamps (older than 1 minute)
        window_start = now - 60  # 1 minute window
        self.requests[user_id][endpoint] = [
            ts for ts in self.requests[user_id][endpoint] if ts > window_start
        ]
        
        # Get limit for endpoint
        limit = self.limits.get(endpoint, 10)  # Default 10 requests per minute
        
        # Check if under limit
        if len(self.requests[user_id][endpoint]) < limit:
            # Add current request timestamp
            self.requests[user_id][endpoint].append(now)
            
            remaining = limit - len(self.requests[user_id][endpoint])
            reset_in = 60 - int(now % 60)  # Seconds until minute resets
            
            return True, remaining, reset_in
        else:
            # Calculate reset time
            oldest_request = min(self.requests[user_id][endpoint])
            reset_in = int(60 - (now - oldest_request))
            
            return False, 0, reset_in
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get rate limit stats for a user"""
        stats = {}
        now = time.time()
        
        if user_id in self.requests:
            for endpoint, timestamps in self.requests[user_id].items():
                # Count requests in last minute
                window_start = now - 60
                recent_requests = [ts for ts in timestamps if ts > window_start]
                
                stats[endpoint] = {
                    'limit': self.limits.get(endpoint, 10),
                    'used': len(recent_requests),
                    'remaining': self.limits.get(endpoint, 10) - len(recent_requests),
                    'reset_in': 60 - int(now % 60)
                }
        
        return stats
    
    def cleanup_old_entries(self):
        """Clean up old entries to prevent memory leak"""
        now = time.time()
        users_to_delete = []
        
        for user_id, endpoints in list(self.requests.items()):
            # Remove empty users
            if not endpoints:
                users_to_delete.append(user_id)
                continue
            
            # Remove old timestamps (older than 5 minutes)
            for endpoint, timestamps in list(endpoints.items()):
                cutoff = now - 300  # 5 minutes
                self.requests[user_id][endpoint] = [
                    ts for ts in timestamps if ts > cutoff
                ]
                
                # Remove empty endpoint lists
                if not self.requests[user_id][endpoint]:
                    del self.requests[user_id][endpoint]
            
            # Remove user if no endpoints left
            if not self.requests[user_id]:
                users_to_delete.append(user_id)
        
        # Delete empty users
        for user_id in users_to_delete:
            del self.requests[user_id]

# Global instance
rate_limiter = RateLimiter()