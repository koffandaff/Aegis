
import sys
import os
import json
import logging

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
logging.basicConfig(level=logging.CRITICAL) 

from utils.network_tools import network_tools

domain = "drivegate.app"
print(f"simulating full scan for {domain}...")

try:
    results = network_tools.full_domain_scan(domain)
    # Generate summary as Scan_Service does
    results['analysis_summary'] = network_tools.generate_scan_summary('full', domain, results)
    
    with open('debug_output.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("DONE: debug_output.json written")

except Exception as e:
    print(f"FAILED: {e}")
