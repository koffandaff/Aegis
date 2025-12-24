"""
SSRF (Server-Side Request Forgery) Protection
Prevents internal network scanning and SSRF attacks
"""
import re
import ipaddress
from urllib.parse import urlparse

class SSRFGuard:
    def __init__(self):
        # List of blocked/internal IP ranges
        self.blocked_ranges = [
            "127.0.0.0/8",      # Localhost
            "10.0.0.0/8",       # Private A
            "172.16.0.0/12",    # Private B
            "192.168.0.0/16",   # Private C
            "169.254.0.0/16",   # Link-local
            "::1/128",          # IPv6 localhost
            "fc00::/7",         # IPv6 private
            "fe80::/10",        # IPv6 link-local
        ]
        
        # Blocked domains/hosts
        self.blocked_hosts = [
            "localhost",
            "localdomain",
            "*.local",
            "*.internal",
            "metadata.google.internal",  # Cloud metadata
            "169.254.169.254",           # AWS/Azure/GCP metadata
            "metadata.google.internal",
            "instance-data",
        ]
        
        # Blocked URL schemes
        self.blocked_schemes = [
            "file://",
            "gopher://",
            "jar://",
            "mailto://",
            "ftp://",
            "sftp://",
        ]
    
    def is_blocked_ip(self, ip: str) -> bool:
        """Check if IP is in blocked/internal range"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check against blocked ranges
            for blocked_range in self.blocked_ranges:
                if ip_obj in ipaddress.ip_network(blocked_range):
                    return True
            
            # Block multicast
            if ip_obj.is_multicast:
                return True
            
            # Block broadcast
            if ip_obj.is_global is False and not ip_obj.is_private:
                return True
                
            return False
        except ValueError:
            return True  # Invalid IP = blocked
    
    def is_blocked_host(self, hostname: str) -> bool:
        """Check if hostname is blocked"""
        hostname = hostname.lower()
        
        # Check exact matches
        if hostname in self.blocked_hosts:
            return True
        
        # Check wildcard matches
        for blocked in self.blocked_hosts:
            if '*' in blocked:
                pattern = blocked.replace('*', '.*')
                if re.match(pattern, hostname):
                    return True
        
        # Check for internal/local domains
        if hostname.endswith('.local') or hostname.endswith('.internal'):
            return True
        
        return False
    
    def is_blocked_url(self, url: str) -> bool:
        """Check if URL is blocked"""
        # Check schemes
        for scheme in self.blocked_schemes:
            if url.startswith(scheme):
                return True
        
        # Parse URL
        try:
            parsed = urlparse(url)
            
            # Check hostname
            if parsed.hostname:
                if self.is_blocked_host(parsed.hostname):
                    return True
                
                # Try to resolve hostname to IP and check
                # (We'll implement DNS resolution separately)
            
            return False
        except:
            return True  # Invalid URL = blocked
    
    def validate_target(self, target: str, target_type: str = "domain") -> bool:
        """
        Validate scanning target
        target_type: "domain", "ip", "url"
        """
        target = target.strip()
        
        if not target:
            return False
        
        if target_type == "ip":
            return not self.is_blocked_ip(target)
        
        elif target_type == "domain":
            # Basic domain validation
            if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', target):
                return False
            
            return not self.is_blocked_host(target)
        
        elif target_type == "url":
            return not self.is_blocked_url(target)
        
        return False
    
    def sanitize_input(self, input_str: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1F\x7F]', '', input_str)
        
        # Limit length
        sanitized = sanitized[:255]
        
        # Remove multiple dots (path traversal)
        sanitized = re.sub(r'\.{2,}', '.', sanitized)
        
        return sanitized.strip()

# Global instance
ssrf_guard = SSRFGuard()