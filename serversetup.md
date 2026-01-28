# Fsociety VPN Server - Automated Setup (Python)

> **CRITICAL**: OpenVPN server runs in WSL, which has its own internal IP. For external connections, you MUST forward port 1194/UDP from Windows to WSL.

## Prerequisites (Windows)

Before running the setup, execute these commands **in a PowerShell Admin window** on Windows:

### 1. Get WSL IP Address
```powershell
wsl hostname -I
# Example output: 172.25.80.25
```

### 2. Create Port Forwarding Rule (Replace with your WSL IP)
```powershell
# Replace 172.25.80.25 with your actual WSL IP
netsh interface portproxy add v4tov4 listenport=1194 listenaddress=0.0.0.0 connectport=1194 connectaddress=172.25.80.25

# Verify the rule was added
netsh interface portproxy show all
```

### 3. Allow UDP 1194 in Firewall
```powershell
New-NetFirewallRule -DisplayName "OpenVPN-UDP" -Direction Inbound -Protocol UDP -LocalPort 1194 -Action Allow
```

### 4. Router Port Forwarding
Configure your router to forward:
- **External Port**: 1194/UDP
- **Internal IP**: Your Windows machine's LAN IP (e.g., 192.168.1.x)
- **Internal Port**: 1194

---

## Setup Script

Save the following code as `setup_vpn_server.py` on your Linux/WSL machine:

```python
#!/usr/bin/env python3
"""
Fsociety VPN Server - Fully Automated Setup Script
This script fetches PKI files from the Fsociety API and starts the OpenVPN server.

PREREQUISITES (Run these on Windows first!):
1. Get WSL IP: wsl hostname -I
2. Create port forward (replace IP):
   netsh interface portproxy add v4tov4 listenport=1194 listenaddress=0.0.0.0 connectport=1194 connectaddress=<WSL_IP>
3. Allow UDP 1194 in Windows Firewall:
   New-NetFirewallRule -DisplayName "OpenVPN-UDP" -Direction Inbound -Protocol UDP -LocalPort 1194 -Action Allow
4. Configure router to forward 1194/UDP to your Windows machine

Usage:
    sudo python3 setup_vpn_server.py
"""

import os
import sys
import json
import socket
import subprocess
from pathlib import Path

# Configuration - BAKED IN SECRETS FOR AUTOMATION
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


def get_wsl_ip():
    """Get WSL's own IP address for port forwarding instructions."""
    try:
        result = subprocess.check_output(["hostname", "-I"], text=True).strip()
        return result.split()[0] if result else "unknown"
    except:
        return "unknown"


def fetch_server_files(api_url: str) -> dict:
    """Fetch PKI files using the server secret."""
    print(f"[*] Fetching PKI files from {api_url}...")
    
    headers = {"X-Server-Secret": SERVER_SECRET}
    try:
        response = requests.get(f"{api_url}/api/vpn/server-setup", headers=headers, timeout=10)
        
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
    os.system("sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1")
    
    # Simple NAT rule
    result = subprocess.run("ip route | grep default | awk '{print $5}'", shell=True, capture_output=True, text=True)
    interface = result.stdout.strip() or "eth0"
    os.system(f"iptables -t nat -C POSTROUTING -s 10.8.0.0/24 -o {interface} -j MASQUERADE 2>/dev/null || iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o {interface} -j MASQUERADE")
    print(f"    ✓ NAT configured on interface: {interface}")


def main():
    if os.geteuid() != 0:
        print("[!] ERROR: This script must be run with sudo")
        sys.exit(1)

    print("=" * 60)
    print("      FSOCIETY VPN SERVER - AUTOMATED DEPLOYMENT")
    print("=" * 60)

    # Get WSL IP for port forwarding instructions
    wsl_ip = get_wsl_ip()
    print(f"[*] WSL IP Address: {wsl_ip}")
    print(f"")
    print(f"    ⚠️  IMPORTANT: Run this on Windows (Admin PowerShell):")
    print(f"    netsh interface portproxy add v4tov4 listenport=1194 listenaddress=0.0.0.0 connectport=1194 connectaddress={wsl_ip}")
    print(f"")

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

    print("")
    print("=" * 60)
    print("  SUCCESS: VPN Server is configured and ready.")
    print("=" * 60)
    print("")
    print("  [CHECKLIST FOR EXTERNAL CONNECTIONS]")
    print(f"  1. Windows Port Forward: netsh interface portproxy add v4tov4 listenport=1194 listenaddress=0.0.0.0 connectport=1194 connectaddress={wsl_ip}")
    print("  2. Windows Firewall: Allow UDP 1194 inbound")
    print("  3. Router: Forward UDP 1194 to your Windows machine")
    print("")
    print("  Starting OpenVPN daemon... (Press Ctrl+C to shutdown)")
    print("=" * 60)
    print("")

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

---

## Troubleshooting

### Connection Hangs / Times Out

This is almost always a **port forwarding issue**. Verify:

1. **WSL IP hasn't changed**: WSL2 IP changes on restart. Re-run:
   ```powershell
   wsl hostname -I
   netsh interface portproxy delete v4tov4 listenport=1194 listenaddress=0.0.0.0
   netsh interface portproxy add v4tov4 listenport=1194 listenaddress=0.0.0.0 connectport=1194 connectaddress=<NEW_WSL_IP>
   ```

2. **Test from Local Network First**: Before testing with public IP, try connecting from another device on your LAN using your Windows machine's local IP (e.g., `192.168.1.x`).

3. **NAT Hairpinning**: If you're testing from the *same* Windows machine, most routers don't support this. Edit your `.ovpn` file and change:
   ```
   remote 106.215.155.126 1194 udp
   ```
   to:
   ```
   remote 127.0.0.1 1194 udp
   ```
   (This only works for local testing on the same machine)

4. **Check if packets reach WSL**:
   ```bash
   # In WSL
   sudo tcpdump -i any udp port 1194
   ```
   If you don't see any packets when connecting, the issue is Windows/Router forwarding.

### TLS Handshake Failed

- Verify system clocks are synced on both client and server.
- Ensure the CA certificate in the `.ovpn` file matches the one on the server.

---

## Quick Test (Same Machine)

For testing on the same Windows machine where WSL is running:

1. Edit your downloaded `.ovpn` file
2. Change `remote 106.215.155.126 1194` to `remote 127.0.0.1 1194`
3. Import into OpenVPN Connect and try connecting

This bypasses all external networking and tests the core VPN functionality.
