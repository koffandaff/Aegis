
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from utils.network_tools import network_tools

domain = "drivegate.app"
print(f"Scanning {domain}...")

try:
    # Test 1: Full scan (which calls get_whois)
    results = network_tools.full_domain_scan(domain)
    whois_data = results.get('whois', {})
    
    print("\n[WHOIS Result]")
    if 'raw_whois' in whois_data:
        print("Type: Raw Socket Fallback (Success)")
        print(f"Data length: {len(whois_data['raw_whois'])}")
    elif 'registrar' in whois_data:
        print("Type: Standard Library (Success)")
        print(f"Registrar: {whois_data['registrar']}")
    elif 'error' in whois_data:
        print(f"Type: Error ({whois_data['error']})")
    
    # Test 2: Direct call to fallback to ensure connectivity
    print("\n[Direct Fallback Connectivity Test]")
    fallback = network_tools._get_whois_raw_socket(domain, "whois.nic.google")
    if 'error' not in fallback:
         print("Direct connection to whois.nic.google successful!")
         print(f"Response sample: {fallback['raw_whois'][:100]}...")
    else:
         print(f"Direct connection failed: {fallback['error']}")

except Exception as e:
    print(f"Scan failed: {e}")
