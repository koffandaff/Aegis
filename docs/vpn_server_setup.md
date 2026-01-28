# OpenVPN Server Setup Guide

This guide explains how to set up an OpenVPN server that works with the Fsociety VPN client configurations.

## Prerequisites

- A VPS or server with a **public IP address** (or WSL on Windows)
- Linux OS (Ubuntu 20.04+ or Debian 11+ recommended)
- Root/sudo access
- Port 1194/UDP open in firewall

---

## Quick Start: Automated Server Setup (Python)

The easiest way to set up your OpenVPN server is using our automated Python script. This script fetches everything it needs from the Fsociety backend automatically.

### Step 1: Save this script as `setup_vpn_server.py` on your Linux/WSL machine:

```python
#!/usr/bin/env python3
"""
Fsociety VPN Server - Fully Automated Setup Script
This script fetches PKI files from the Fsociety API and starts the OpenVPN server.

Usage:
    sudo python3 setup_vpn_server.py
"""

import os
import sys
import json
import socket
import subprocess
from pathlib import Path

# Configuration - BAkED IN SECRETS FOR AUTOMATION
SERVER_SECRET = "Fsociety-Server-Setup-Secure-Secret-2026"
DEFAULT_PORT = 8000

# Try to import requests, install if not available
try:
    import requests
except ImportError:
    print("[*] Installing requests library...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
        import requests
    except:
        print("[!] Failed to install requests. Please run: pip install requests")
        sys.exit(1)


def get_backend_ip():
    """Attempt to discover the Windows host IP from WSL."""
    print("[*] Attempting to discover Fsociety backend...")
    
    # Try common WSL host entry
    try:
        host_ip = subprocess.check_output(["sh", "-c", "ip route | grep default | awk '{print $3}'"], text=True).strip()
        if host_ip:
            print(f"    ✓ Found host IP via route: {host_ip}")
            return host_ip
    except:
        pass

    # Fallback to local
    return "localhost"


def fetch_server_files(api_url: str) -> dict:
    """Fetch PKI files using the server secret."""
    print(f"[*] Fetching PKI files from {api_url}...")
    
    headers = {"X-Server-Secret": SERVER_SECRET}
    try:
        response = requests.get(f"{api_url}/vpn/server-setup", headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[!] API Error: {response.status_code}")
            print(f"[!] Detail: {response.text}")
            return None
    except Exception as e:
        print(f"[!] Connection failed: {e}")
        return None


def write_pki_files(files: dict, pki_dir: Path):
    """Write certificates to the filesystem."""
    print(f"[*] Provisioning PKI files to {pki_dir}...")
    pki_dir.mkdir(parents=True, exist_ok=True)
    
    file_mapping = {
        "ca_cert": "ca.crt",
        "server_cert": "server.crt",
        "server_key": "server.key",
        "ta_key": "ta.key",
        "dh_params": "dh.pem"
    }
    
    for key, filename in file_mapping.items():
        filepath = pki_dir / filename
        with open(filepath, "w") as f:
            f.write(files[key])
        if "key" in filename:
            os.chmod(filepath, 0o600)
        print(f"    ✓ {filename}")


def create_server_config(pki_dir: Path, config_path: Path):
    """Build the OpenVPN server configuration."""
    print(f"[*] Generating OpenVPN configuration...")
    
    config = f"""# Fsociety OpenVPN Server Config
port 1194
proto udp
dev tun
topology subnet

ca {pki_dir}/ca.crt
cert {pki_dir}/server.crt
key {pki_dir}/server.key
dh {pki_dir}/dh.pem
tls-auth {pki_dir}/ta.key 0

server 10.8.0.0 255.255.255.0
ifconfig-pool-persist /var/log/openvpn/ipp.txt

push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 1.1.1.1"

cipher AES-256-GCM
auth SHA256
tls-version-min 1.2
remote-cert-tls client

keepalive 10 120
max-clients 100
persist-key
persist-tun

status /var/log/openvpn/openvpn-status.log
log-append /var/log/openvpn/openvpn.log
verb 3
"""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        f.write(config)
    print(f"    ✓ server.conf created")


def setup_networking():
    """Basic networking setup for packet forwarding."""
    print("[*] Optimizing network for VPN traffic...")
    os.system("sysctl -w net.ipv4.ip_forward=1 > /dev/null")
    
    # Simple NAT rule
    result = subprocess.run("ip route | grep default | awk '{print $5}'", shell=True, capture_output=True, text=True)
    interface = result.stdout.strip() or "eth0"
    os.system(f"iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o {interface} -j MASQUERADE")


def main():
    if os.geteuid() != 0:
        print("[!] ERROR: This script must be run with sudo")
        sys.exit(1)

    print("=" * 60)
    print("      FSOCIETY VPN SERVER - AUTOMATED DEPLOYMENT")
    print("=" * 60)

    # 1. Discover host
    host_ip = get_backend_ip()
    api_url = f"http://{host_ip}:{DEFAULT_PORT}"

    # 2. Fetch PKI
    files = fetch_server_files(api_url)
    if not files:
        print("[!] AUTO-DISCOVERY FAILED.")
        manual_ip = input("[?] Enter Windows Host IP (e.g. 172.x.x.x): ").strip()
        api_url = f"http://{manual_ip}:{DEFAULT_PORT}"
        files = fetch_server_files(api_url)
        if not files:
            print("[!!] FATAL: Could not connect to Fsociety Backend.")
            sys.exit(1)

    # 3. Provision
    pki_dir = Path("/etc/openvpn/server")
    config_path = pki_dir / "server.conf"
    
    write_pki_files(files, pki_dir)
    create_server_config(pki_dir, config_path)
    
    Path("/var/log/openvpn").mkdir(parents=True, exist_ok=True)
    setup_networking()

    print("\n" + "=" * 60)
    print("  SUCCESS: VPN Server is configured and ready.")
    print("  Starting OpenVPN daemon...")
    print("  (Press Ctrl+C to shutdown)")
    print("=" * 60 + "\n")

    # 4. Start Server
    try:
        subprocess.run(["openvpn", "--config", str(config_path)], check=True)
    except KeyboardInterrupt:
        print("\n[*] Shutting down VPN server...")
    except Exception as e:
        print(f"\n[!] OpenVPN Error: {e}")


if __name__ == "__main__":
    main()
```

### Step 2: Run the automated setup

Simply copy the code above into a file named `setup_vpn_server.py` and run it:

```bash
# Install OpenVPN if you haven't
sudo apt update && sudo apt install openvpn -y

# Run the automation
sudo python3 setup_vpn_server.py
```

**That's it!** The script will:
1. Detect your Windows host IP automatically.
2. Authenticate using the built-in server secret.
3. Download all Certificates and Keys.
4. Configure OpenVPN and start the server.

---

## Troubleshooting

1. **Connection Refused**: Make sure the Fsociety backend is running on Windows.
2. **WSL Networking**: Ensure your Windows firewall is not blocking incoming connections on port 8000 (Backend) and port 1194 (VPN).

### Windows Firewall (Run as Admin)
```powershell
# Allow Backend API (8000)
New-NetFirewallRule -DisplayName "Fsociety-API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# Allow VPN Server (1194)
New-NetFirewallRule -DisplayName "Fsociety-VPN" -Direction Inbound -Protocol UDP -LocalPort 1194 -Action Allow
```
