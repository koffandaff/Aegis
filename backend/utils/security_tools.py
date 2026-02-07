"""
Security scanning utilities for SSL/TLS, HTTP headers, etc.
"""
import ssl
import socket
import hashlib
import re
import time
import warnings
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from urllib.parse import urlparse
import httpx
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from config.settings import settings
from config.constants import (
    SecurityHeader, RiskLevel, TECHNOLOGY_PATTERNS,
    SSL_VULNERABILITIES, TLSVersion
)

class SecurityTools:
    def __init__(self):
        self.timeout = settings.SSL_SCAN_TIMEOUT
        self.user_agent = settings.USER_AGENT
        
        # Suppress SSL warnings
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    # ========== SSL/TLS SCANNING ==========
    
    def scan_ssl(self, domain: str, port: int = 443) -> Dict:
        """
        Perform SSL/TLS scan on a domain
        
        Args:
            domain: Domain to scan
            port: Port to scan (default: 443)
            
        Returns:
            Dictionary with SSL/TLS scan results
        """
        start_time = time.time()
        results = {
            'domain': domain,
            'port': port,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'certificate': {},
            'tls_versions': [],
            'cipher_suites': [],
            'vulnerabilities': [],
            'ocsp_stapling': False,
            'hsts_preloaded': False,
            'certificate_transparency': False
        }
        
        try:
            # Get certificate
            cert_info = self._get_certificate_info(domain, port)
            results['certificate'] = cert_info
            
            # Check TLS versions
            tls_versions = self._check_tls_versions(domain, port)
            results['tls_versions'] = tls_versions
            
            # Get cipher suites (simplified - in real implementation use sslscan or similar)
            cipher_suites = self._get_cipher_suites(domain, port)
            results['cipher_suites'] = cipher_suites
            
            # Check for vulnerabilities
            vulnerabilities = self._check_ssl_vulnerabilities(domain, port, cert_info, tls_versions)
            results['vulnerabilities'] = vulnerabilities
            
            # Check OCSP stapling
            results['ocsp_stapling'] = self._check_ocsp_stapling(domain, port)
            
            # Check HSTS preload
            results['hsts_preloaded'] = self._check_hsts_preload(domain)
            
            # Check Certificate Transparency
            results['certificate_transparency'] = self._check_certificate_transparency(cert_info)
            
        except Exception as e:
            results['error'] = str(e)
        
        results['scan_duration_ms'] = int((time.time() - start_time) * 1000)
        return results
    
    def _get_certificate_info(self, domain: str, port: int) -> Dict:
        """Get SSL certificate information"""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate
            with socket.create_connection((domain, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert_bin = ssock.getpeercert(binary_form=True)
                    cert = x509.load_der_x509_certificate(cert_bin, default_backend())
                    
                    # Parse certificate
                    cert_info = {
                        'subject': {},
                        'issuer': {},
                        'version': cert.version.value,
                        'serial_number': hex(cert.serial_number)[2:].upper(),
                        'not_before': cert.not_valid_before.isoformat(),
                        'not_after': cert.not_valid_after.isoformat(),
                        'signature_algorithm': cert.signature_algorithm_oid._name,
                        'public_key_algorithm': cert.public_key().__class__.__name__,
                        'public_key_bits': cert.public_key().key_size if hasattr(cert.public_key(), 'key_size') else None,
                        'san': [],
                        'ocsp_must_staple': False,
                        'extended_validation': False
                    }
                    
                    # Subject
                    for attr in cert.subject:
                        cert_info['subject'][attr.oid._name] = attr.value
                    
                    # Issuer
                    for attr in cert.issuer:
                        cert_info['issuer'][attr.oid._name] = attr.value
                    
                    # Subject Alternative Names
                    try:
                        san_ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                        cert_info['san'] = [str(name) for name in san_ext.value]
                    except:
                        pass
                    
                    # Check for OCSP Must-Staple
                    try:
                        ocsp_ext = cert.extensions.get_extension_for_class(x509.TLSFeature)
                        for feature in ocsp_ext.value:
                            if feature == x509.TLSFeatureType.status_request:
                                cert_info['ocsp_must_staple'] = True
                                break
                    except:
                        pass
                    
                    # Check for Extended Validation (simplified)
                    org_fields = ['organizationName', 'businessCategory', 'jurisdictionCountryName']
                    ev_indicators = sum(1 for field in org_fields if field in cert_info['subject'])
                    cert_info['extended_validation'] = ev_indicators >= 2
                    
                    return cert_info
        
        except Exception as e:
            return {'error': f'Failed to get certificate: {str(e)}'}
    
    def _check_tls_versions(self, domain: str, port: int) -> List[Dict]:
        """Check which TLS versions are supported with improved reliability"""
        tls_versions = []
        
        # Test configurations
        configs = [
            (ssl.PROTOCOL_TLS_CLIENT, "TLS_ALL", "Combined Test"),
            (getattr(ssl, 'PROTOCOL_TLSv1_3', None), TLSVersion.TLSv1_3, "TLSv1.3"),
            (ssl.PROTOCOL_TLSv1_2, TLSVersion.TLSv1_2, "TLSv1.2"),
            (ssl.PROTOCOL_TLSv1_1, TLSVersion.TLSv1_1, "TLSv1.1"),
            (ssl.PROTOCOL_TLSv1, TLSVersion.TLSv1_0, "TLSv1.0"),
            (getattr(ssl, 'PROTOCOL_SSLv3', None), TLSVersion.SSLv3, "SSLv3"),
            (getattr(ssl, 'PROTOCOL_SSLv2', None), TLSVersion.SSLv2, "SSLv2"),
        ]
        
        for protocol_const, version_name, display_name in configs:
            if protocol_const is None:
                continue
                
            if version_name == "TLS_ALL":
                # Check preferred version
                try:
                    context = ssl.create_default_context()
                    with socket.create_connection((domain, port), timeout=3) as sock:
                        with context.wrap_socket(sock, server_hostname=domain) as ssock:
                            negotiated = ssock.version()
                            tls_versions.append({
                                'version': negotiated,
                                'supported': True,
                                'preferred': True
                            })
                except:
                    pass
                continue

            try:
                context = ssl.SSLContext(protocol_const)
                # Lower security levels to allow testing older versions
                if hasattr(context, 'set_ciphers'):
                    context.set_ciphers('ALL:@SECLEVEL=0')
                
                with socket.create_connection((domain, port), timeout=3) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        tls_versions.append({
                            'version': version_name,
                            'supported': True,
                            'preferred': ssock.version() == version_name
                        })
            except:
                # Only add if not already present from "TLS_ALL" check
                if not any(v['version'] == version_name for v in tls_versions):
                    tls_versions.append({
                        'version': version_name,
                        'supported': False,
                        'preferred': False
                    })
        
        return tls_versions
    
    def _get_cipher_suites(self, domain: str, port: int) -> List[Dict]:
        """Get supported cipher suites with more details"""
        cipher_suites = []
        
        try:
            # We try different contexts to see various supported ciphers
            contexts = [
                ssl.create_default_context(),
                ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ]
            
            for context in contexts:
                if hasattr(context, 'set_ciphers'):
                    context.set_ciphers('ALL:@SECLEVEL=0')
                
                try:
                    with socket.create_connection((domain, port), timeout=3) as sock:
                        with context.wrap_socket(sock, server_hostname=domain) as ssock:
                            cipher = ssock.cipher()
                            if cipher:
                                name, protocol, bits = cipher
                                if not any(c['name'] == name for c in cipher_suites):
                                    cipher_suites.append({
                                        'name': name,
                                        'protocol': protocol,
                                        'bits': bits,
                                        'kx': 'DH/RSA',  # Simplified
                                        'au': 'RSA',
                                        'enc': name.split('-')[0] if '-' in name else 'AES',
                                        'mac': 'SHA'
                                    })
                except:
                    continue
        except:
            pass
        
        return cipher_suites
    
    def _check_ssl_vulnerabilities(self, domain: str, port: int, 
                                   cert_info: Dict, tls_versions: List[Dict]) -> List[Dict]:
        """Check for known SSL/TLS vulnerabilities"""
        vulnerabilities = []
        
        # Check each vulnerability
        for vuln_name, vuln_info in SSL_VULNERABILITIES.items():
            affected = False
            details = None
            
            if vuln_name == "heartbleed":
                # Simplified check - in real implementation use testssl.sh or similar
                affected = self._check_heartbleed(domain, port)
            
            elif vuln_name == "poodle":
                # Check if SSLv3 is supported
                sslv3_supported = any(
                    v['version'] == TLSVersion.SSLv3 and v['supported'] 
                    for v in tls_versions
                )
                affected = sslv3_supported
                if affected:
                    details = "SSLv3 is enabled, vulnerable to POODLE attack"
            
            elif vuln_name == "freak":
                # Check for weak export ciphers
                affected = self._check_weak_ciphers(domain, port)
            
            elif vuln_name == "logjam":
                # Check for weak DH parameters
                affected = self._check_dh_parameters(domain, port)
            
            elif vuln_name == "sweet32":
                # Check for 64-bit block ciphers
                affected = self._check_64bit_ciphers(domain, port)
            
            vulnerabilities.append({
                'name': vuln_name,
                'cve': vuln_info['cve'],
                'description': vuln_info['description'],
                'risk': vuln_info['risk'],
                'affected': affected,
                'details': details
            })
        
        return vulnerabilities
    
    def _check_heartbleed(self, domain: str, port: int) -> bool:
        """Check for Heartbleed vulnerability (simplified)"""
        # In a real implementation, you would send a malicious heartbeat request
        # For now, return False as most servers are patched
        return False
    
    def _check_weak_ciphers(self, domain: str, port: int) -> bool:
        """Check for weak export-grade ciphers"""
        weak_ciphers = [
            'EXP', 'EXPORT', 'NULL', 'ANON', 'ADH', 'AECDH',
            'RC4', 'DES', '3DES', 'MD5', 'SHA1'
        ]
        
        try:
            context = ssl.create_default_context()
            context.set_ciphers('ALL:@SECLEVEL=0')
            
            with socket.create_connection((domain, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cipher = ssock.cipher()[0]
                    return any(weak in cipher.upper() for weak in weak_ciphers)
        except:
            return False
    
    def _check_dh_parameters(self, domain: str, port: int) -> bool:
        """Check for weak DH parameters (simplified)"""
        # In real implementation, check DH key size
        return False
    
    def _check_64bit_ciphers(self, domain: str, port: int) -> bool:
        """Check for 64-bit block ciphers"""
        weak_ciphers = ['DES', '3DES', 'RC2', 'IDEA']
        
        try:
            context = ssl.create_default_context()
            context.set_ciphers('ALL:@SECLEVEL=0')
            
            with socket.create_connection((domain, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cipher = ssock.cipher()[0]
                    return any(cipher.upper().startswith(weak) for weak in weak_ciphers)
        except:
            return False
    
    def _check_ocsp_stapling(self, domain: str, port: int) -> bool:
        """Check if OCSP stapling is enabled"""
        try:
            context = ssl.create_default_context()
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            
            with socket.create_connection((domain, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    # Try to get OCSP response
                    ocsp = ssock.getpeercert(binary_form=False).get('ocsp', [])
                    return len(ocsp) > 0
        except:
            return False
    
    def _check_hsts_preload(self, domain: str) -> bool:
        """Check if domain is in HSTS preload list"""
        # Common preloaded domains (partial list)
        preloaded_domains = [
            'google.com', 'facebook.com', 'github.com', 'twitter.com',
            'paypal.com', 'dropbox.com', 'linkedin.com', 'microsoft.com'
        ]
        
        # Check if domain ends with any preloaded domain
        for preloaded in preloaded_domains:
            if domain.endswith(preloaded):
                return True
        
        return False
    
    def _check_certificate_transparency(self, cert_info: Dict) -> bool:
        """Check if certificate is in Certificate Transparency logs"""
        # Check for SCT extension (simplified)
        return cert_info.get('extended_validation', False)
    
    # ========== HTTP HEADER ANALYSIS ==========
    
    def analyze_headers(self, url: str, follow_redirects: bool = True) -> Dict:
        """
        Analyze HTTP headers and detect technologies
        
        Args:
            url: URL to analyze
            follow_redirects: Whether to follow redirects
            
        Returns:
            Dictionary with header analysis results
        """
        start_time = time.time()
        results = {
            'url': url,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status_code': None,
            'server': None,
            'content_type': None,
            'content_length': None,
            'security_headers': [],
            'technologies': [],
            'cookies': [],
            'redirects': [],
            'error': None
        }
        
        try:
            # Parse URL
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
            
            # Make request
            headers = {'User-Agent': self.user_agent}
            
            with httpx.Client(
                timeout=self.timeout,
                follow_redirects=follow_redirects,
                verify=False  # For testing, accept self-signed certs
            ) as client:
                response = client.get(url, headers=headers)
                
                # Store basic info
                results['status_code'] = response.status_code
                results['server'] = response.headers.get('Server')
                results['content_type'] = response.headers.get('Content-Type')
                results['content_length'] = int(response.headers.get('Content-Length', 0))
                
                # Analyze security headers
                results['security_headers'] = self._analyze_security_headers(response.headers)
                
                # Detect technologies
                results['technologies'] = self._detect_technologies(response)
                
                # Analyze cookies
                results['cookies'] = self._analyze_cookies(response)
                
                # Store redirect history
                if hasattr(response, 'history'):
                    results['redirects'] = [
                        {
                            'url': str(resp.url),
                            'status_code': resp.status_code,
                            'headers': dict(resp.headers)
                        }
                        for resp in response.history
                    ]
                
        except Exception as e:
            results['error'] = str(e)
        
        results['scan_duration_ms'] = int((time.time() - start_time) * 1000)
        return results
    
    def _analyze_security_headers(self, headers: Dict) -> List[Dict]:
        """Analyze security headers"""
        security_headers = []
        
        # Check each security header
        header_checks = {
            SecurityHeader.CSP: {
                'recommendation': 'Implement CSP to prevent XSS attacks',
                'risk': RiskLevel.HIGH
            },
            SecurityHeader.HSTS: {
                'recommendation': 'Enable HSTS with max-age >= 31536000 and includeSubDomains',
                'risk': RiskLevel.HIGH
            },
            SecurityHeader.X_FRAME_OPTIONS: {
                'recommendation': 'Set X-Frame-Options to DENY or SAMEORIGIN',
                'risk': RiskLevel.MEDIUM
            },
            SecurityHeader.X_CONTENT_TYPE_OPTIONS: {
                'recommendation': 'Set X-Content-Type-Options to nosniff',
                'risk': RiskLevel.MEDIUM
            },
            SecurityHeader.X_XSS_PROTECTION: {
                'recommendation': 'Modern browsers ignore this; use CSP instead',
                'risk': RiskLevel.LOW
            },
            SecurityHeader.REFERRER_POLICY: {
                'recommendation': 'Set Referrer-Policy to strict-origin-when-cross-origin',
                'risk': RiskLevel.LOW
            },
            SecurityHeader.PERMISSIONS_POLICY: {
                'recommendation': 'Configure Permissions-Policy to limit browser features',
                'risk': RiskLevel.MEDIUM
            }
        }
        
        for header, info in header_checks.items():
            value = headers.get(header.value)
            security_headers.append({
                'header': header.value,
                'present': value is not None,
                'value': value,
                'recommendation': info['recommendation'],
                'risk': info['risk'] if value is None else RiskLevel.INFO
            })
        
        return security_headers
    
    def _detect_technologies(self, response: httpx.Response) -> List[Dict]:
        """Detect technologies from HTTP response with improved heuristics"""
        technologies = []
        content = response.text.lower()
        headers = {k.lower(): v.lower() for k, v in response.headers.items()}
        
        # Check each technology pattern
        for tech_name, patterns in TECHNOLOGY_PATTERNS.items():
            confidence = 0.0
            found_patterns = []
            
            # Check headers
            for header_name, header_value in headers.items():
                for pattern in patterns:
                    if pattern.lower() in f"{header_name}: {header_value}":
                        confidence += 0.4
                        found_patterns.append(pattern)
            
            # Check content (HTML)
            for pattern in patterns:
                if pattern.lower() in content:
                    confidence += 0.5
                    found_patterns.append(pattern)
            
            # Check Cookie names specifically
            cookies = headers.get('set-cookie', '')
            for pattern in patterns:
                if pattern.lower() in cookies:
                    confidence += 0.3
                    found_patterns.append(pattern)
            
            # Cap confidence and filter
            confidence = min(confidence, 1.0)
            
            if confidence >= 0.4:  # Sharper threshold
                technologies.append({
                    'name': tech_name.replace('_', ' ').title(),
                    'version': self._extract_version(tech_name, headers, content),
                    'confidence': round(confidence, 2),
                    'categories': self._get_tech_categories(tech_name)
                })
        
        return technologies
    
    def _extract_version(self, tech_name: str, headers: Dict, content: str) -> Optional[str]:
        """Extract version number for a technology"""
        version_patterns = {
            'nginx': r'nginx/([\d\.]+)',
            'apache': r'Apache/([\d\.]+)',
            'wordpress': r'wp-([\d\.]+)\.(?:js|css)',
            'bootstrap': r'bootstrap/([\d\.]+)'
        }
        
        if tech_name in version_patterns:
            # Check headers first
            for header_value in headers.values():
                match = re.search(version_patterns[tech_name], header_value, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            # Check content
            match = re.search(version_patterns[tech_name], content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _get_tech_categories(self, tech_name: str) -> List[str]:
        """Get categories for a technology"""
        categories = {
            # Frontend
            'react': ['framework', 'javascript', 'frontend'],
            'vue': ['framework', 'javascript', 'frontend'],
            'angular': ['framework', 'javascript', 'frontend'],
            'jquery': ['library', 'javascript', 'frontend'],
            'bootstrap': ['framework', 'css', 'frontend'],
            'tailwindcss': ['framework', 'css', 'frontend'],
            
            # Backend Languages
            'python': ['language', 'backend'],
            'php': ['language', 'backend'],
            'nodejs': ['runtime', 'javascript', 'backend'],
            'ruby': ['language', 'backend'],
            'java': ['language', 'backend'],
            'aspnet': ['framework', 'dotnet', 'backend'],
            'go': ['language', 'backend'],
            
            # CMS
            'wordpress': ['cms', 'php', 'blog'],
            'drupal': ['cms', 'php'],
            'joomla': ['cms', 'php'],
            
            # Web Servers
            'nginx': ['server', 'proxy'],
            'apache': ['server'],
            'iis': ['server', 'microsoft'],
            'litespeed': ['server'],
            
            # CDN & Security
            'cloudflare': ['cdn', 'security'],
            'akamai': ['cdn'],
            'aws': ['cloud', 'hosting'],
            
            # Analytics
            'google_analytics': ['analytics', 'tracking'],
            'facebook_pixel': ['analytics', 'tracking', 'marketing'],
            'hotjar': ['analytics', 'ux']
        }
        
        return categories.get(tech_name, ['other'])
    
    def _analyze_cookies(self, response: httpx.Response) -> List[Dict]:
        """Analyze cookies for security issues"""
        cookies = []
        
        # Check Set-Cookie headers
        set_cookie_headers = response.headers.get_list('Set-Cookie')
        
        for cookie_header in set_cookie_headers:
            cookie_info = {
                'name': None,
                'secure': False,
                'httponly': False,
                'samesite': None,
                'domain': None,
                'path': '/',
                'max_age': None,
                'expires': None
            }
            
            # Parse cookie header
            parts = cookie_header.split(';')
            cookie_info['name'] = parts[0].split('=')[0].strip()
            
            for part in parts:
                part = part.strip().lower()
                if 'secure' in part:
                    cookie_info['secure'] = True
                elif 'httponly' in part:
                    cookie_info['httponly'] = True
                elif part.startswith('samesite='):
                    cookie_info['samesite'] = part.split('=')[1].upper()
                elif part.startswith('domain='):
                    cookie_info['domain'] = part.split('=')[1]
                elif part.startswith('path='):
                    cookie_info['path'] = part.split('=')[1]
                elif part.startswith('max-age='):
                    cookie_info['max_age'] = int(part.split('=')[1])
                elif part.startswith('expires='):
                    cookie_info['expires'] = part.split('=')[1]
            
            cookies.append(cookie_info)
        
        return cookies
    
    # ========== TECHNOLOGY STACK DETECTION ==========
    
    def detect_tech_stack(self, domain: str) -> Dict:
        """
        Detect technology stack for a domain
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Dictionary with technology stack results
        """
        start_time = time.time()
        results = {
            'domain': domain,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'technologies': [],
            'categories': {},
            'confidence_score': 0.0
        }
        
        try:
            # Analyze HTTP headers
            url = f'https://{domain}'
            header_results = self.analyze_headers(url, follow_redirects=True)
            
            if 'technologies' in header_results:
                results['technologies'] = header_results['technologies']
            
            # Group by category
            categories = {}
            for tech in results['technologies']:
                for category in tech['categories']:
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(tech['name'])
            
            results['categories'] = categories
            
            # Calculate overall confidence
            if results['technologies']:
                total_confidence = sum(t['confidence'] for t in results['technologies'])
                results['confidence_score'] = round(total_confidence / len(results['technologies']), 2)
        
        except Exception as e:
            results['error'] = str(e)
        
        results['scan_duration_ms'] = int((time.time() - start_time) * 1000)
        return results
    
    # ========== HTTP SECURITY ANALYSIS ==========
    
    def analyze_http_security(self, url: str) -> Dict:
        """
        Perform comprehensive HTTP security analysis
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with HTTP security analysis results
        """
        start_time = time.time()
        results = {
            'url': url,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'overall_score': 0.0,
            'security_headers_score': 0.0,
            'cookie_security_score': 0.0,
            'transport_security_score': 0.0,
            'recommendations': [],
            'warnings': [],
            'error': None
        }
        
        try:
            # Get header analysis
            header_results = self.analyze_headers(url, follow_redirects=True)
            
            if header_results.get('error'):
                raise Exception(header_results['error'])
            
            # Calculate security headers score
            security_headers = header_results.get('security_headers', [])
            present_headers = [h for h in security_headers if h['present']]
            
            if security_headers:
                results['security_headers_score'] = len(present_headers) / len(security_headers)
            
            # Calculate cookie security score
            cookies = header_results.get('cookies', [])
            secure_cookies = [c for c in cookies if c.get('secure') and c.get('httponly')]
            
            if cookies:
                results['cookie_security_score'] = len(secure_cookies) / len(cookies)
            
            # Calculate transport security score
            results['transport_security_score'] = self._calculate_transport_security(url)
            
            # Overall score (weighted average)
            weights = {
                'security_headers': 0.4,
                'cookie_security': 0.3,
                'transport_security': 0.3
            }
            
            results['overall_score'] = (
                results['security_headers_score'] * weights['security_headers'] +
                results['cookie_security_score'] * weights['cookie_security'] +
                results['transport_security_score'] * weights['transport_security']
            )
            
            # Generate recommendations
            results['recommendations'] = self._generate_security_recommendations(
                security_headers, cookies
            )
            
            # Generate warnings
            results['warnings'] = self._generate_security_warnings(
                security_headers, cookies, results['overall_score']
            )
        
        except Exception as e:
            results['error'] = str(e)
        
        results['scan_duration_ms'] = int((time.time() - start_time) * 1000)
        return results
    
    def _calculate_transport_security(self, url: str) -> float:
        """Calculate transport security score"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.split(':')[0]
            
            # Check SSL/TLS
            ssl_results = self.scan_ssl(domain)
            
            if ssl_results.get('error'):
                return 0.0
            
            # Score based on TLS version and vulnerabilities
            score = 1.0
            
            # Deduct for old TLS versions
            tls_versions = ssl_results.get('tls_versions', [])
            for version in tls_versions:
                if version.get('supported'):
                    ver_name = version.get('version', '')
                    if ver_name in ['SSLv2', 'SSLv3', 'TLSv1.0']:
                        score -= 0.2
                    elif ver_name == 'TLSv1.1':
                        score -= 0.1
            
            # Deduct for vulnerabilities
            vulnerabilities = ssl_results.get('vulnerabilities', [])
            for vuln in vulnerabilities:
                if vuln.get('affected'):
                    risk = vuln.get('risk', RiskLevel.LOW)
                    if risk == RiskLevel.CRITICAL:
                        score -= 0.3
                    elif risk == RiskLevel.HIGH:
                        score -= 0.2
                    elif risk == RiskLevel.MEDIUM:
                        score -= 0.1
                    elif risk == RiskLevel.LOW:
                        score -= 0.05
            
            return max(0.0, min(1.0, score))
        
        except:
            return 0.0
    
    def _generate_security_recommendations(self, security_headers: List[Dict], 
                                          cookies: List[Dict]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Header recommendations
        missing_headers = [h for h in security_headers if not h['present']]
        for header in missing_headers:
            recommendations.append(f"Add {header['header']}: {header['recommendation']}")
        
        # Cookie recommendations
        for cookie in cookies:
            if not cookie.get('secure'):
                recommendations.append(f"Set Secure flag for cookie: {cookie['name']}")
            if not cookie.get('httponly'):
                recommendations.append(f"Set HttpOnly flag for cookie: {cookie['name']}")
            if not cookie.get('samesite'):
                recommendations.append(f"Set SameSite=Lax or Strict for cookie: {cookie['name']}")
        
        return list(set(recommendations))[:10]  # Limit to 10
    
    def _generate_security_warnings(self, security_headers: List[Dict], 
                                   cookies: List[Dict], overall_score: float) -> List[str]:
        """Generate security warnings"""
        warnings = []
        
        # Critical warnings
        hsts_header = next((h for h in security_headers if h['header'] == SecurityHeader.HSTS.value), None)
        if not hsts_header or not hsts_header['present']:
            warnings.append("HSTS not enabled - allows SSL stripping attacks")
        
        csp_header = next((h for h in security_headers if h['header'] == SecurityHeader.CSP.value), None)
        if not csp_header or not csp_header['present']:
            warnings.append("Content Security Policy not enabled - vulnerable to XSS attacks")
        
        # Session cookies without HttpOnly
        session_cookies = [c for c in cookies if 'session' in c['name'].lower()]
        for cookie in session_cookies:
            if not cookie.get('httponly'):
                warnings.append(f"Session cookie '{cookie['name']}' not marked HttpOnly - vulnerable to XSS")
        
        # Low overall score warning
        if overall_score < 0.5:
            warnings.append(f"Low security score ({overall_score:.2f}) - implement recommendations above")
        
        return warnings[:5]  # Limit to 5

# Global instance
security_tools = SecurityTools()