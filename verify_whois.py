
import whois
import socket
import sys

domain = "drivegate.app"
print(f"Testing whois for {domain}...")

try:
    # Try raw socket first to checks DNS for whois server if we knew it
    # But let's check what whois module does
    w = whois.whois(domain)
    print("Success!")
    print(w)
except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
