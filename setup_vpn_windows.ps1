# Fsociety VPN - Windows Port Forwarding Setup
# Run this script in Administrator PowerShell

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Fsociety VPN - Port Forward Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Get WSL IP
Write-Host "[*] Detecting WSL IP address..." -ForegroundColor Yellow
$wslIP = (wsl hostname -I).Trim().Split(" ")[0]

if (-not $wslIP) {
    Write-Host "[!] ERROR: Could not detect WSL IP. Is WSL running?" -ForegroundColor Red
    exit 1
}

Write-Host "    Found WSL IP: $wslIP" -ForegroundColor Green
Write-Host ""

# Remove existing rule if any
Write-Host "[*] Removing any existing port proxy rules for 1194..." -ForegroundColor Yellow
netsh interface portproxy delete v4tov4 listenport=1194 listenaddress=0.0.0.0 2>$null

# Add new port proxy rule
Write-Host "[*] Creating port forward: 0.0.0.0:1194 -> ${wslIP}:1194" -ForegroundColor Yellow
netsh interface portproxy add v4tov4 listenport=1194 listenaddress=0.0.0.0 connectport=1194 connectaddress=$wslIP

# Verify
Write-Host ""
Write-Host "[*] Current port proxy rules:" -ForegroundColor Yellow
netsh interface portproxy show all

# Add firewall rule if not exists
Write-Host ""
Write-Host "[*] Ensuring firewall rule exists for UDP 1194..." -ForegroundColor Yellow
$rule = Get-NetFirewallRule -DisplayName "OpenVPN-UDP" -ErrorAction SilentlyContinue
if (-not $rule) {
    New-NetFirewallRule -DisplayName "OpenVPN-UDP" -Direction Inbound -Protocol UDP -LocalPort 1194 -Action Allow | Out-Null
    Write-Host "    Created firewall rule: OpenVPN-UDP" -ForegroundColor Green
} else {
    Write-Host "    Firewall rule already exists" -ForegroundColor Green
}

# Also allow TCP just in case
$ruleTcp = Get-NetFirewallRule -DisplayName "OpenVPN-TCP" -ErrorAction SilentlyContinue
if (-not $ruleTcp) {
    New-NetFirewallRule -DisplayName "OpenVPN-TCP" -Direction Inbound -Protocol TCP -LocalPort 1194 -Action Allow | Out-Null
    Write-Host "    Created firewall rule: OpenVPN-TCP" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Setup Complete!" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Start your OpenVPN server in WSL: sudo python3 setup_vpn_server.py" -ForegroundColor Gray
Write-Host "2. Configure your router to forward UDP 1194 to this PC" -ForegroundColor Gray
Write-Host "3. Download a VPN profile from the Fsociety web interface" -ForegroundColor Gray
Write-Host "4. Import the .ovpn file into OpenVPN Connect and connect!" -ForegroundColor Gray
Write-Host ""
Write-Host "For local testing (same machine), edit your .ovpn file and change:" -ForegroundColor Yellow
Write-Host "  remote 106.215.155.126 1194" -ForegroundColor Red
Write-Host "to:" -ForegroundColor Yellow
Write-Host "  remote 127.0.0.1 1194" -ForegroundColor Green
Write-Host ""
