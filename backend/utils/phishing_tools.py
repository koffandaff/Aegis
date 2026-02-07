"""
Phishing URL detection and analysis tools - Simplified version
"""
import re
import socket
import time
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from urllib.parse import urlparse
import httpx
from dns import resolver

from config.settings import settings
from config.constants import PhishingIndicator, RiskLevel

class PhishingTools:
    def __init__(self):
        self.timeout = 10
        self.user_agent = settings.USER_AGENT
        self.suspicious_tlds = settings.SUSPICIOUS_TLDS
        self.suspicious_keywords = settings.SUSPICIOUS_KEYWORDS
        self.phishing_threshold = settings.PHISHING_THRESHOLD
        
        # High-trust whitelist
        self.trusted_domains = [
            'google.com', 'google.co.in', 'youtube.com', 'facebook.com', 
            'instagram.com', 'whatsapp.com', 'microsoft.com', 'apple.com',
            'amazon.com', 'amazon.in', 'netflix.com', 'linkedin.com',
            'twitter.com', 'x.com', 'github.com', 'gmail.com', 'yahoo.com',
            'outlook.com', 'paypal.com', 'ajays.co.in'
        ]
        
        # Brand to official domain mapping
        self.brand_domains = {
            'google': 'google.com',
            'paypal': 'paypal.com',
            'apple': 'apple.com',
            'microsoft': 'microsoft.com',
            'amazon': 'amazon.com',
            'facebook': 'facebook.com',
            'netflix': 'netflix.com'
        }
        
    def check_phishing(self, url: str, deep_analysis: bool = False) -> Dict:
        """
        Check if a URL is potentially phishing
        """
        start_time = time.time()
        results = {
            'url': url,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'domain': None,
            'final_url': None,
            'risk_score': 0.0,
            'is_phishing': False,
            'indicators': [],
            'ssl_valid': None,
            'domain_age_days': None,
            'reputation': None,
            'virustotal': None,
            'error': None
        }
        
        try:
            # Parse URL
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
            
            parsed = urlparse(url)
            domain = parsed.netloc.split(':')[0].lower()
            results['domain'] = domain
            
            # Follow redirects to get final URL
            final_url = self._get_final_url(url)
            results['final_url'] = final_url
            
            # Extract domain parts
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                base_domain = '.'.join(domain_parts[-2:])
                tld = f".{domain_parts[-1]}"
            else:
                base_domain = domain
                tld = ""

            # Check Whitelist
            is_trusted = any(domain == trusted or domain.endswith('.' + trusted) for trusted in self.trusted_domains)
            
            # Calculate indicators
            indicators = self._calculate_indicators(url, domain, base_domain, tld, is_trusted)
            results['indicators'] = indicators
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(indicators)
            
            # Trusted domains get a massive bonus (reduction in risk)
            if is_trusted:
                risk_score = risk_score * 0.1
            
            # VirusTotal URL Check (if API key is available)
            vt_result = self._check_virustotal_url(url)
            if vt_result:
                results['virustotal'] = vt_result
                # If VT detected malicious, boost risk score
                if vt_result.get('positives', 0) > 0:
                    vt_boost = min(0.5, vt_result['positives'] / 20)
                    risk_score = min(1.0, risk_score + vt_boost)
                    results['indicators'].append({
                        'indicator': PhishingIndicator.VIRUSTOTAL_DETECTION,
                        'present': True,
                        'score': vt_boost,
                        'details': f"VirusTotal: {vt_result['positives']}/{vt_result['total']} engines flagged this URL"
                    })
            
            results['risk_score'] = round(risk_score, 2)
            results['is_phishing'] = risk_score >= self.phishing_threshold
            
            # SSL validation
            results['ssl_valid'] = self._check_ssl_validity(domain)
            
            # Domain age (actual WHOIS check)
            results['domain_age_days'] = self._get_actual_domain_age(domain)
            
            # Reputation
            results['reputation'] = self._get_domain_reputation(domain)
            
        except Exception as e:
            results['error'] = str(e)
        
        results['scan_duration_ms'] = int((time.time() - start_time) * 1000)
        return results

    def _check_virustotal_url(self, url: str) -> Optional[Dict]:
        """Check URL against VirusTotal API"""
        try:
            vt_key = settings.VIRUSTOTAL_API_KEY
            if not vt_key:
                return None
            
            # VirusTotal v3 API - Get URL ID first
            import base64
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            
            headers = {
                'x-apikey': vt_key,
                'Accept': 'application/json'
            }
            
            with httpx.Client(timeout=15) as client:
                response = client.get(
                    f'https://www.virustotal.com/api/v3/urls/{url_id}',
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                    return {
                        'positives': stats.get('malicious', 0) + stats.get('phishing', 0),
                        'total': sum(stats.values()),
                        'categories': data.get('data', {}).get('attributes', {}).get('categories', {}),
                        'permalink': f"https://www.virustotal.com/gui/url/{url_id}"
                    }
                elif response.status_code == 404:
                    # URL not in VT database - submit it
                    return {'positives': 0, 'total': 0, 'note': 'URL not yet scanned by VirusTotal'}
        except Exception as e:
            return {'error': str(e)}
        
        return None

    def _get_actual_domain_age(self, domain: str) -> Optional[int]:
        """Fetch real domain age in days using WHOIS"""
        try:
            import whois
            w = whois.whois(domain)
            creation_date = w.creation_date
            
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if creation_date:
                delta = datetime.now() - creation_date
                return delta.days
        except:
            pass
        return None

    def _detect_impersonation(self, url: str, domain: str, is_trusted: bool) -> Optional[str]:
        """Detect if a brand is being impersonated on a different domain"""
        url_lower = url.lower()
        
        for brand, official in self.brand_domains.items():
            if brand.lower() in url_lower:
                # If this domain is NOT the official domain (or its subdomains/trusted variants)
                if not domain == official and not domain.endswith('.' + official):
                    return f"Suspected impersonation of {brand.upper()} on unauthorized domain: {domain}"
        
        # Generic suspicious keywords
        generic_keywords = ['banking', 'secure', 'login', 'verify', 'update']
        if not is_trusted:
            for kw in generic_keywords:
                if kw in url_lower:
                    return f"Suspicious keyword '{kw}' found on unverified domain"
        
        return None
    
    def _get_final_url(self, url: str, max_redirects: int = 5) -> str:
        """Follow redirects to get final URL"""
        try:
            headers = {'User-Agent': self.user_agent}
            
            with httpx.Client(
                timeout=self.timeout,
                follow_redirects=False,
                verify=False
            ) as client:
                response = client.get(url, headers=headers)
                
                redirect_count = 0
                current_url = url
                
                while 300 <= response.status_code < 400 and redirect_count < max_redirects:
                    if 'location' in response.headers:
                        next_url = response.headers['location']
                        # Handle relative URLs
                        if not next_url.startswith(('http://', 'https://')):
                            parsed = urlparse(current_url)
                            next_url = f"{parsed.scheme}://{parsed.netloc}{next_url}"
                        
                        response = client.get(next_url, headers=headers)
                        current_url = next_url
                        redirect_count += 1
                    else:
                        break
                
                return str(response.url)
        
        except:
            return url
    
    def _calculate_indicators(self, url: str, domain: str, 
                             base_domain: str, tld: str, is_trusted: bool) -> List[Dict]:
        """Calculate phishing indicators with brand awareness"""
        indicators = []
        
        # 1. Suspicious TLD
        is_suspicious_tld = not is_trusted and tld.lower() in self.suspicious_tlds
        indicators.append({
            'indicator': PhishingIndicator.SUSPICIOUS_TLD,
            'present': is_suspicious_tld,
            'score': 0.8 if is_suspicious_tld else 0.0,
            'details': f"TLD {tld} is frequently used for malicious activity" if is_suspicious_tld else None
        })
        
        # 2. IP in URL
        is_ip_url = self._contains_ip_address(domain)
        indicators.append({
            'indicator': PhishingIndicator.IP_IN_URL,
            'present': is_ip_url,
            'score': 0.9 if is_ip_url else 0.0,
            'details': "Uses IP address instead of domain name" if is_ip_url else None
        })
        
        # 3. Impersonation/Suspicious Keywords
        impersonation_info = self._detect_impersonation(url, domain, is_trusted)
        indicators.append({
            'indicator': PhishingIndicator.SUSPICIOUS_KEYWORD,
            'present': impersonation_info is not None,
            'score': 0.7 if impersonation_info else 0.0,
            'details': impersonation_info
        })
        
        # 4. URL Length
        is_long_url = len(url) > 100 and not is_trusted
        indicators.append({
            'indicator': PhishingIndicator.LONG_URL,
            'present': is_long_url,
            'score': 0.4 if is_long_url else 0.0,
            'details': f"Excessive URL length ({len(url)} characters)" if is_long_url else None
        })
        
        # 5. URL Shortening
        is_shortened = self._is_shortened_url(domain)
        indicators.append({
            'indicator': PhishingIndicator.SHORTENED_URL,
            'present': is_shortened,
            'score': 0.5 if is_shortened else 0.0,
            'details': "Uses URL shortening service to hide destination" if is_shortened else None
        })
        
        # 6. Non-standard Port
        is_non_standard_port = self._has_non_standard_port(url)
        indicators.append({
            'indicator': PhishingIndicator.NON_STANDARD_PORT,
            'present': is_non_standard_port,
            'score': 0.6 if is_non_standard_port else 0.0,
            'details': "Uses non-standard web service port" if is_non_standard_port else None
        })
        
        # 7. HTTPS
        has_https = url.startswith('https://')
        indicators.append({
            'indicator': PhishingIndicator.HTTPS_MISSING,
            'present': not has_https,
            'score': 0.5 if not has_https else 0.0,
            'details': "Insecure connection detected" if not has_https else None
        })
        
        return indicators
    
    def _contains_ip_address(self, domain: str) -> bool:
        """Check if domain contains an IP address"""
        # Check for IPv4
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ipv4_pattern, domain):
            # Validate IP range
            parts = domain.split('.')
            if all(0 <= int(part) <= 255 for part in parts):
                return True
        
        # Check for IPv6 (simplified)
        if '[' in domain and ']' in domain:
            return True
        
        return False
    
    
    def _is_shortened_url(self, domain: str) -> bool:
        """Check if domain is a URL shortening service"""
        shorteners = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 'is.gd',
            'buff.ly', 'adf.ly', 'shorte.st', 'bc.vc', 'tiny.cc',
            'tr.im', 'ow.ly', 't.co', 'lnkd.in', 'db.tt', 'qr.ae',
            'cur.lv', 'po.st', 'ity.im', 'u.to', 'j.mp', 'v.gd'
        ]
        
        return any(domain.endswith(shortener) for shortener in shorteners)
    
    def _has_non_standard_port(self, url: str) -> bool:
        """Check if URL uses non-standard port"""
        parsed = urlparse(url)
        if parsed.port:
            standard_ports = [80, 443, 8080, 8443]
            return parsed.port not in standard_ports
        return False
    
    def _calculate_risk_score(self, indicators: List[Dict]) -> float:
        """
        Calculate overall phishing risk score using an Additive Model.
        Unlike weighted average, this ensures that specific critical flaws 
        directly increase the risk, rather than being diluted by 'good' factors.
        """
        if not indicators:
            return 0.0
        
        # Base Score Sum
        total_risk = 0.0
        
        # Track specific indicators for combo detection
        has_https_issues = False
        has_suspicious_keyword = False
        has_ip_url = False
        has_suspicious_tld = False
        
        for indicator in indicators:
            if indicator['present']:
                # Add weighted score directly
                weight = self._get_indicator_weight(indicator['indicator'])
                # indicator['score'] is already 0.0-1.0 representing severity
                total_risk += indicator['score'] * weight
                
                # Flag tracking
                if indicator['indicator'] == PhishingIndicator.HTTPS_MISSING:
                    has_https_issues = True
                elif indicator['indicator'] == PhishingIndicator.SUSPICIOUS_KEYWORD:
                    has_suspicious_keyword = True
                elif indicator['indicator'] == PhishingIndicator.IP_IN_URL:
                    has_ip_url = True
                elif indicator['indicator'] == PhishingIndicator.SUSPICIOUS_TLD:
                    has_suspicious_tld = True

        # --- COMPOUND RISK MULTIPLIERS ---
        
        # 1. The "Login on HTTP" Trap
        # If site asks for login/secure info but has no encryption -> AUTO HIGH RISK
        if has_https_issues and has_suspicious_keyword:
            total_risk += 0.35
            
        # 2. IP Address with no SSL -> Likely malware/botnet hosting
        if has_ip_url and has_https_issues:
            total_risk += 0.25
            
        # 3. Suspicious TLD + Keyword -> Targeted Phishing
        if has_suspicious_tld and has_suspicious_keyword:
            total_risk += 0.20

        return min(total_risk, 1.0)
    
    def _get_indicator_weight(self, indicator: PhishingIndicator) -> float:
        """Get weight for an indicator based on importance (0.0 - 1.0)"""
        # Weights determine how much an individual factor contributes to the total 1.0 cap
        weights = {
            PhishingIndicator.HTTPS_MISSING: 0.3,     # Base penalty for HTTP
            PhishingIndicator.IP_IN_URL: 0.8,         # Very high indicator
            PhishingIndicator.SUSPICIOUS_TLD: 0.4,    # Moderate
            PhishingIndicator.SUSPICIOUS_KEYWORD: 0.4, # Moderate
            PhishingIndicator.SHORTENED_URL: 0.3,     # Contextual
            PhishingIndicator.LONG_URL: 0.1,          # Weak indicator
            PhishingIndicator.NON_STANDARD_PORT: 0.2, # Contextual
            PhishingIndicator.SHORT_DOMAIN_AGE: 0.2   # Contextual
        }
        
        return weights.get(indicator, 0.2)
    
    def _check_ssl_validity(self, domain: str) -> Optional[bool]:
        """Check if SSL certificate is valid"""
        try:
            import ssl
            context = ssl.create_default_context()
            
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    return cert is not None
        except:
            return None
    
    
    def _get_domain_reputation(self, domain: str) -> Dict:
        """Get domain reputation (placeholder for future API integration)"""
        return {
            'note': 'Reputation checking requires external API integration',
            'suggested_apis': ['Google Safe Browsing', 'PhishTank', 'URLhaus']
        }

# Global instance
phishing_tools = PhishingTools()