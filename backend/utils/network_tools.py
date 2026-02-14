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
import io
import contextlib
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

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
            # Clean domain name
            domain = domain.lower().replace('http://', '').replace('https://', '').split('/')[0]
            
            # Try to import whois (installed via pip install python-whois)
            import whois
            
            # Use the whois look function - handle both main packages (python-whois/whois)
            lookup_func = None
            if hasattr(whois, 'whois'):
                lookup_func = whois.whois
            elif hasattr(whois, 'query'):
                lookup_func = whois.query
            
            if not lookup_func:
                return {'error': 'WHOIS module found but incompatible API. Try: pip install python-whois'}

            # Perform the lookup with stderr suppression (as it prints socket errors)
            w = None
            try:
                # Capture stderr to suppress "Error trying to connect to socket" messages
                f = io.StringIO()
                with contextlib.redirect_stderr(f):
                    w = lookup_func(domain)
            except Exception as e:
                # Specific handling for .app domains which often fail in python-whois
                if domain.endswith('.app'):
                    print(f"[DEBUG] .app domain lookup failed, attempting direct query to whois.nic.google...")
                    return self._get_whois_raw_socket(domain, "whois.nic.google")

                # Fallback to CLI if Python module fails
                print(f"[DEBUG] python-whois failed ({str(e)}), trying CLI fallback...")
                return self._get_whois_via_cli(domain)
            
            # Convert whois object to dict
            whois_dict = {}
            
            # Common fields
            fields = [
                'domain_name', 'registrar', 'whois_server', 'updated_date',
                'creation_date', 'expiration_date', 'name_servers', 'status',
                'emails', 'dnssec', 'name', 'org', 'address', 'city',
                'state', 'zipcode', 'country'
            ]
            
            if w:
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
            else:
                return {'error': 'No WHOIS data found'}
            
        except ImportError:
            # Alternative: Use whois command line if available
            return self._get_whois_via_cli(domain)
        except Exception as e:
            # import traceback
            # error_trace = traceback.format_exc()
            print(f"[ERROR] WHOIS failed for {domain}: {str(e)}")
            return {'error': f'WHOIS lookup failed (internal error).'}
    
    def _get_whois_raw_socket(self, domain: str, server: str) -> Dict:
        """Query WHOIS server directly via socket"""
        try:
            with socket.create_connection((server, 43), timeout=10) as s:
                s.sendall(f"{domain}\r\n".encode())
                response = b""
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    response += data
            
            # Return raw data structure
            return {
                'raw_whois': response.decode('utf-8', errors='ignore'),
                'note': f'Raw WHOIS data from {server} (parsing unavailable)',
                'domain_name': domain
            }
        except Exception as e:
             return {'error': f'Direct WHOIS query failed: {str(e)}'}

    def _get_whois_via_cli(self, domain: str) -> Dict:
        """Fallback: Use system whois command"""
        try:
            # Try to use system whois command
            result = subprocess.run(
                ['whois', domain],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True # Needed for some Windows environments
            )
            
            if result.returncode == 0 and result.stdout:
                return {
                    'raw_whois': result.stdout,
                    'note': 'Raw WHOIS data (parsed version not available)'
                }
            else:
                return {'error': f'WHOIS module/command not found. Try: pip install python-whois'}
        except:
            return {'error': 'WHOIS lookup unavailable on this system.'}
    
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
                'timestamp': datetime.now(timezone.utc).isoformat()
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
        """Smart scan: Tries Nmap (if installed), falls back to pure Python Sockets (Vercel compatible)"""
        try:
            return self._scan_ports_nmap(ip, ports)
        except Exception as e:
            # Fallback to sockets if nmap is missing or fails (common on Vercel)
            err_str = str(e)
            if "No module named" in err_str or "not found in path" in err_str:
                 print(f"[SCAN] Nmap unavailable (Platform limitation), using socket fallback.")
            else:
                 print(f"[SCAN] Nmap unavailable ({str(e)}), using socket fallback.")
            return self._scan_ports_socket(ip, ports)

    def _scan_ports_nmap(self, ip: str, ports: List[int] = None) -> Dict:
        """Scan using python-nmap wrapper"""
        # Import here to avoid top-level ImportErrors on Vercel
        import nmap
        
        nm = nmap.PortScanner()
        port_str = ','.join(map(str, ports)) if ports else '21-445,1433,3306,3389,5432,6379,8000,8080,27017'
        
        args = '-sS -sV -O -T4' if os.name != 'nt' else '-sT -sV -T4' # sS requires root, sT is connect scan
        nm.scan(ip, ports=port_str, arguments=args)
        
        open_ports = []
        if ip in nm.all_hosts():
            for proto in nm[ip].all_protocols():
                lport = nm[ip][proto].keys()
                for port in lport:
                    service = nm[ip][proto][port]
                    state = service['state']
                    if state == 'open':
                         risk_info = self.get_port_risk(port)
                         open_ports.append({
                            'port': port,
                            'service': service.get('name', self._get_service_name(port)),
                            'version': service.get('product', '') + ' ' + service.get('version', ''),
                            'status': 'open',
                            'risk': risk_info['level'],
                            'risk_score': risk_info['score'],
                            'risk_color': risk_info['color']
                        })
                        
        return {
            'ip': ip,
            'open_ports': open_ports,
            'total_scanned': len(ports) if ports else 100, # Approximate
            'total_open': len(open_ports),
            'method': 'nmap'
        }

    def _scan_ports_socket(self, ip: str, ports: List[int] = None) -> Dict:
        """Scan using pure Python sockets (Vercel compatible)"""
        if not ports:
            # Common top ports (Expanded)
            ports = [
                21, 22, 23, 25, 53, 80, 81, 110, 111, 135, 139, 143, 443, 445, 
                465, 587, 993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 6379, 
                8000, 8080, 8443, 8888, 9200, 27017, 27018
            ]
        
        open_ports = []
        
        # Simple synchronous scan for now
        for port in ports:
            try:
                # Create a new socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)  # Fast timeout
                
                # Attempt connection
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    risk_info = self.get_port_risk(port)
                    open_ports.append({
                        'port': port,
                        'service': self._get_service_name(port),
                        'status': 'open',
                        'risk': risk_info['level'],
                        'risk_score': risk_info['score'],
                        'risk_color': risk_info['color']
                    })
            except:
                continue
                
        return {
            'ip': ip,
            'open_ports': open_ports,
            'total_scanned': len(ports),
            'total_open': len(open_ports),
            'method': 'socket'
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
            81: 'HTTP-ALT',
            110: 'POP3',
            111: 'RPC',
            135: 'MS-RPC',
            139: 'NetBIOS',
            143: 'IMAP',
            443: 'HTTPS',
            445: 'SMB',
            465: 'SMTPS',
            587: 'SMTP Submission',
            993: 'IMAPS',
            995: 'POP3S',
            1433: 'MSSQL',
            1521: 'Oracle',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            5900: 'VNC',
            6379: 'Redis',
            8000: 'HTTP-DEV',
            8080: 'HTTP-ALT',
            8443: 'HTTPS-ALT',
            8888: 'HTTP-ALT',
            9200: 'Elasticsearch',
            27017: 'MongoDB',
            27018: 'MongoDB'
        }
        return service_map.get(port, f'Port {port}')
    
    # ========== FULL DOMAIN SCAN ==========
    
    def full_domain_scan(self, domain: str) -> Dict:
        """Perform comprehensive domain scan"""
        results = {
            'domain': domain,
            'timestamp': datetime.now(timezone.utc).isoformat(),
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
                    # Comprehensive port set for full scan consistency
                    'ports': self.scan_ports(ip, [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389])
                })
            
            results['ip_scans'] = ip_scans
        
        return results

    def get_port_risk(self, port: int) -> Dict:
        """Classify port risk level: low, medium, high"""
        high_risk = [22, 23, 3306, 3389, 5432]  # Management or Database
        medium_risk = [21, 25, 53, 110, 143, 465, 587, 8080] # Legacy or E-mail
        
        if port in high_risk:
            return {'level': 'HIGH', 'score': 85, 'color': '#ff4757'}
        elif port in medium_risk:
            return {'level': 'MEDIUM', 'score': 45, 'color': '#ffa502'}
        else:
            return {'level': 'LOW', 'score': 15, 'color': '#00ff9d'}

    def generate_scan_summary(self, scan_type: str, target: str, results: Dict) -> str:
        """Generate a human-readable summary of the scan results"""
        summary = f"### Security Assessment: {target}\n\n"
        
        if scan_type == 'dns':
            a_records = results.get('a_records', [])
            mx_records = results.get('mx_records', [])
            summary += f"Target infrastructure consists of **{len(a_records)}** publicly accessible IPs.\n"
            summary += f"Mail topology indicates **{len(mx_records)}** gateway points found. "
            if mx_records:
                summary += f"Primary mail delivery handled by `{mx_records[0]}`.\n"
            summary += "\n**Vulnerability Note**: If DNSSEC is missing, target remains susceptible to cache poisoning."
        
        elif scan_type == 'whois':
            if results.get('error'):
                summary += "CRITICAL: WHOIS subsystem unreachable. Registration privacy could not be verified.\n"
            else:
                registrar = results.get('registrar', 'Unknown')
                expiry = results.get('expiration_date', 'Unknown')
                summary += f"Asset identified as registered through **{registrar}**.\n"
                summary += f"Operational window expires: `{expiry}`.\n"
                summary += "\n**Analysis**: Verify administrative contacts to detect potential subdomain takeover avenues."
        
        elif scan_type == 'subdomains':
            subs = results.get('subdomains_found', [])
            summary += f"Surface area expansion detected: **{len(subs)}** active sub-assets identified.\n"
            if subs:
                summary += "High-traffic endpoints found: " + ", ".join(subs[:5]) + (", etc.\n" if len(subs) > 5 else "\n")
                summary += "\n**Warning**: Each subdomain increases the potential attack surface. Proper WAF coverage is recommended."
        
        elif scan_type == 'ports':
            open_ports = results.get('open_ports', [])
            summary += f"Active service map reveals **{len(open_ports)}** exposed ports.\n"
            if open_ports:
                summary += "Detected Protocol Stack:\n"
                for p in open_ports[:5]:
                    summary += f"- Port {p['port']}: Running **{p['service']}** daemon.\n"
                summary += "\n**Expert Analysis**: " + ("Open management ports (22, 3389) detected. Ensure IP whitelisting." if any(p['port'] in [22, 3389] for p in open_ports) else "Standard HTTP/HTTPS stack identified.")
        
        elif scan_type == 'ip':
            summary += f"Target mapped to node type: **{results.get('service', 'General Infrastructure')}**.\n"
            if results.get('geolocation'):
                geo = results['geolocation']
                summary += f"Physical Location: {geo.get('city')}, {geo.get('country')} via {geo.get('isp')}.\n"
                summary += f"ASN: `{geo.get('as', 'Private/Internal')}`\n"
        
        if scan_type == 'domain' or results.get('scan_type') == 'full':
            summary = "### Executive Summary (Threat Report)\n"
            dns = results.get('dns_records', {})
            ports_data = results.get('ip_scans', [{}])[0].get('ports', {})
            open_ports = ports_data.get('open_ports', [])
            
            summary += f"- **Infrastructure Reliability**: Resolved to `{dns.get('a_records', ['N/A'])[0]}`. High availability cluster detected.\n"
            summary += f"- **Mail Security**: {len(dns.get('mx_records', []))} MX nodes found. Check SPF/DKIM for spoofing protection.\n"
            summary += f"- **Service Exposure**: OSINT indicates {len(open_ports)} open listener(s). "
            if open_ports:
                summary += f"Primary entry: **{open_ports[0]['service']}**.\n"
            summary += f"- **Asset Tracking**: {len(results.get('subdomains', {}).get('subdomains_found', []))} endpoints mapped in the current session.\n"
            summary += "\n**Overall Risk Level**: " + ("MODERATE" if len(open_ports) > 2 else "LOW") + " (OSINT visibility)"

        return summary

# Global instance
network_tools = NetworkTools()