"""
Network scanning and OSINT tools
"""
import socket
import dns.resolver
import requests
import re
import time
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class NetworkTools:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Fsociety-Scanner/1.0 (Security Research Tool)'
        })
        self.timeout = 10
    
    # ========== DNS METHODS ==========
    
    def get_dns_records(self, domain: str) -> Dict:
        """Get all DNS records for a domain"""
        results = {}
        
        try:
            # A Records
            try:
                answers = dns.resolver.resolve(domain, 'A')
                results['a_records'] = [str(r) for r in answers]
            except:
                results['a_records'] = []
            
            # AAAA Records (IPv6)
            try:
                answers = dns.resolver.resolve(domain, 'AAAA')
                results['aaaa_records'] = [str(r) for r in answers]
            except:
                results['aaaa_records'] = []
            
            # MX Records
            try:
                answers = dns.resolver.resolve(domain, 'MX')
                results['mx_records'] = [str(r.exchange) for r in answers]
            except:
                results['mx_records'] = []
            
            # NS Records
            try:
                answers = dns.resolver.resolve(domain, 'NS')
                results['ns_records'] = [str(r) for r in answers]
            except:
                results['ns_records'] = []
            
            # TXT Records
            try:
                answers = dns.resolver.resolve(domain, 'TXT')
                results['txt_records'] = [str(r).strip('"') for r in answers]
            except:
                results['txt_records'] = []
            
            # CNAME Records
            try:
                answers = dns.resolver.resolve(domain, 'CNAME')
                results['cname_records'] = [str(r) for r in answers]
            except:
                results['cname_records'] = []
            
            # SOA Record
            try:
                answers = dns.resolver.resolve(domain, 'SOA')
                results['soa_record'] = str(answers[0])
            except:
                results['soa_record'] = None
            
            return results
            
        except Exception as e:
            return {'error': str(e)}
    
    # ========== WHOIS METHODS ==========
    
    def get_whois(self, domain: str) -> Dict:
        """Get WHOIS information for a domain using python-whois"""
        try:
            # Try to import python-whois (which is installed as whois)
            import whois as python_whois
            
            w = python_whois.whois(domain)
            
            # Convert whois object to dict
            whois_dict = {}
            
            # Common fields
            fields = [
                'domain_name', 'registrar', 'whois_server', 'updated_date',
                'creation_date', 'expiration_date', 'name_servers', 'status',
                'emails', 'dnssec', 'name', 'org', 'address', 'city',
                'state', 'zipcode', 'country'
            ]
            
            for field in fields:
                if hasattr(w, field):
                    value = getattr(w, field)
                    if value:
                        whois_dict[field] = str(value) if not isinstance(value, list) else [str(v) for v in value]
            
            # Clean up dates
            date_fields = ['updated_date', 'creation_date', 'expiration_date']
            for field in date_fields:
                if field in whois_dict:
                    if isinstance(whois_dict[field], list):
                        whois_dict[field] = whois_dict[field][0]
            
            return whois_dict
            
        except ImportError:
            # Alternative: Use whois command line if available
            return self._get_whois_via_cli(domain)
        except Exception as e:
            return {'error': f'WHOIS lookup failed: {str(e)}'}
    
    def _get_whois_via_cli(self, domain: str) -> Dict:
        """Fallback: Use system whois command"""
        try:
            # Try to use system whois command
            result = subprocess.run(
                ['whois', domain],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    'raw_whois': result.stdout,
                    'note': 'Raw WHOIS data (parsed version not available)'
                }
            else:
                return {'error': 'WHOIS command failed or not available'}
        except:
            return {'error': 'WHOIS not available. Install with: pip install python-whois'}
    
    # ========== SUBDOMAIN METHODS ==========
    
    def find_subdomains(self, domain: str, wordlist: List[str] = None) -> Dict:
        """Find subdomains using common wordlist"""
        if not wordlist:
            wordlist = [
                'www', 'mail', 'ftp', 'admin', 'blog', 'api', 'test',
                'dev', 'staging', 'mobile', 'secure', 'portal', 'cpanel',
                'webmail', 'server', 'ns1', 'ns2', 'dns', 'vpn', 'mx'
            ]
        
        subdomains = []
        
        for sub in wordlist:
            full_domain = f"{sub}.{domain}"
            try:
                socket.gethostbyname(full_domain)
                subdomains.append(full_domain)
                time.sleep(0.1)  # Rate limiting
            except socket.gaierror:
                continue
        
        return {
            'domain': domain,
            'subdomains_found': subdomains,
            'total_found': len(subdomains)
        }
    
    # ========== IP INFORMATION ==========
    
    def get_ip_info(self, ip: str) -> Dict:
        """Get information about an IP address"""
        try:
            # Get hostname (reverse DNS)
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except:
                hostname = None
            
            # Geolocation (using free API - optional)
            geo_info = self._get_ip_geolocation(ip)
            
            # Check if it's a known service
            service = self._identify_service(ip)
            
            return {
                'ip': ip,
                'hostname': hostname,
                'geolocation': geo_info,
                'service': service,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_ip_geolocation(self, ip: str) -> Dict:
        """Get IP geolocation using ip-api.com (free) - optional"""
        try:
            # This is optional - if it fails, we'll still return basic info
            response = self.session.get(
                f'http://ip-api.com/json/{ip}',
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'country': data.get('country'),
                        'region': data.get('regionName'),
                        'city': data.get('city'),
                        'isp': data.get('isp'),
                        'org': data.get('org'),
                        'lat': data.get('lat'),
                        'lon': data.get('lon'),
                        'as': data.get('as')
                    }
            
            return {'note': 'Geolocation service unavailable'}
            
        except:
            return {'note': 'Geolocation service unavailable'}
    
    def _identify_service(self, ip: str) -> Optional[str]:
        """Try to identify what service runs on common ports"""
        common_ports = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            465: 'SMTPS',
            587: 'SMTP Submission',
            993: 'IMAPS',
            995: 'POP3S',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            8080: 'HTTP-ALT',
            8443: 'HTTPS-ALT'
        }
        
        try:
            # Quick check on common ports
            for port, service in list(common_ports.items())[:5]:  # Check first 5
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    return service
        
        except:
            pass
        
        return None
    
    # ========== PORT SCANNING ==========
    
    def scan_ports(self, ip: str, ports: List[int] = None) -> Dict:
        """Scan common ports on an IP"""
        if not ports:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 
                    587, 993, 995, 3306, 3389, 5432, 8080, 8443]
        
        open_ports = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    open_ports.append({
                        'port': port,
                        'service': self._get_service_name(port),
                        'status': 'open'
                    })
                
                time.sleep(0.1)  # Rate limiting
                
            except:
                continue
        
        return {
            'ip': ip,
            'open_ports': open_ports,
            'total_scanned': len(ports),
            'total_open': len(open_ports)
        }
    
    def _get_service_name(self, port: int) -> str:
        """Get common service name for port"""
        service_map = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            465: 'SMTPS',
            587: 'SMTP Submission',
            993: 'IMAPS',
            995: 'POP3S',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            8080: 'HTTP-ALT',
            8443: 'HTTPS-ALT'
        }
        return service_map.get(port, f'Port {port}')
    
    # ========== FULL DOMAIN SCAN ==========
    
    def full_domain_scan(self, domain: str) -> Dict:
        """Perform comprehensive domain scan"""
        results = {
            'domain': domain,
            'timestamp': datetime.utcnow().isoformat(),
            'scan_type': 'full'
        }
        
        # Run all scans
        results['dns_records'] = self.get_dns_records(domain)
        results['whois'] = self.get_whois(domain)
        results['subdomains'] = self.find_subdomains(domain)
        
        # Get IPs and scan them
        if 'a_records' in results['dns_records'] and results['dns_records']['a_records']:
            ips = results['dns_records']['a_records']
            ip_scans = []
            
            for ip in ips[:2]:  # Limit to first 2 IPs
                ip_scans.append({
                    'ip': ip,
                    'info': self.get_ip_info(ip),
                    'ports': self.scan_ports(ip, [80, 443, 22, 21, 25])  # Common ports only
                })
            
            results['ip_scans'] = ip_scans
        
        return results

# Global instance
network_tools = NetworkTools()