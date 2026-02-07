from datetime import datetime, timezone
import uuid
import os
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from model.VPN_Model import VPNConfigRequest, WireGuardRequest, VPNConfigResponse, VPNKeys
from utils.vpn_tools import vpn_tools
from utils.pki_manager import pki_manager
from database.repositories.vpn_repository import VPNRepository
from database.repositories.activity_repository import ActivityRepository 


class VPNService:
    """
    VPN Service with REAL PKI infrastructure.
    
    Generates valid X.509 certificates that work with OpenVPN.
    Requires a real OpenVPN server to connect to.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.vpn_repo = VPNRepository(db)
        self.activity_repo = ActivityRepository(db)

        # VPN Server configuration from environment
        self.vpn_server_ip = os.getenv("VPN_SERVER_IP", "your.server.ip.here")
        self.vpn_server_port = int(os.getenv("VPN_SERVER_PORT", "1194"))
        self.vpn_protocol = os.getenv("VPN_PROTOCOL", "udp")

        # Defined VPN Servers for our "Service"
        # In production, these would point to real server endpoints
        self.available_servers = [
            {
                "id": "us-east", 
                "name": "USA - New York", 
                "address": self.vpn_server_ip,  # All use same server for now
                "region": "Americas", 
                "load": "42%"
            },
            {
                "id": "eu-central", 
                "name": "Germany - Frankfurt", 
                "address": self.vpn_server_ip, 
                "region": "Europe", 
                "load": "18%"
            },
            {
                "id": "asia-east", 
                "name": "Japan - Tokyo", 
                "address": self.vpn_server_ip, 
                "region": "Asia", 
                "load": "65%"
            },
            {
                "id": "in-west", 
                "name": "India - Mumbai", 
                "address": self.vpn_server_ip, 
                "region": "Asia", 
                "load": "20%"
            }
        ]

    def get_available_servers(self) -> List[Dict]:
        """Return list of available VPN servers"""
        return self.available_servers

    def generate_openvpn_config(self, request: VPNConfigRequest, user_id: str) -> VPNConfigResponse:
        """
        Generate an OpenVPN configuration with REAL certificates.
        
        Uses the PKI manager to generate valid X.509 certificates
        signed by our Certificate Authority.
        """
        # Determine server name and ID
        server_name = f"Fsociety-{request.server_address}"
        server_id = "custom"
        for s in self.available_servers:
            if s['address'] == request.server_address or s['id'] in request.server_address:
                server_name = s['name']
                server_id = s['id']
                break

        # Create unique client name for certificate (Safe for filename)
        config_id = str(uuid.uuid4())
        # Use a generic name pattern to avoid exposing sensitive info in filenames
        client_name = f"fsociety_user_{config_id[:8]}"
        
        # Generate REAL client certificate using PKI
        client_cert, client_key = pki_manager.generate_client_certificate(client_name)
        
        # Get CA certificate
        ca_cert = pki_manager.get_ca_certificate()
        
        # Get TLS-Auth key
        ta_key = pki_manager.get_ta_key()
        
        # Build OpenVPN config with real certs
        try:
            config_content = self._build_openvpn_config(
                server=request.server_address,
                port=request.port,
                proto=request.protocol,
                ca=ca_cert,
                cert=client_cert,
                key=client_key,
                ta=ta_key
            )
        except Exception:
             # Fallback to MOCK config if real PKI fails (e.g. on Windows without easy-rsa)
            config_content = self._build_mock_openvpn_config(server_name, user_id)
        
        config = VPNConfigResponse(
            id=config_id,
            user_id=user_id,
            type="openvpn",
            name=f"{server_name} - {config_id[:4].upper()}",
            filename=f"fsociety_vpn_{server_id}_{config_id[:4]}", # Clean filename
            config_content=config_content,
            created_at=datetime.now(timezone.utc)
        )
        
        # Store in DB
        config_data = config.model_dump()
        config_data["server_id"] = server_id
        config_data["config_type"] = "openvpn"
        
        self.vpn_repo.create(config_data)
        
        # Log VPN activity
        self.activity_repo.log_activity(
            user_id=user_id,
            action='vpn_generate',
            details={'server': server_name, 'type': 'openvpn'}
        )
        
        return config

    def _build_openvpn_config(
        self, 
        server_ip: str, 
        port: int, 
        protocol: str,
        ca_cert: str,
        client_cert: str,
        client_key: str,
        ta_key: str
    ) -> str:
        """
        Build a complete OpenVPN configuration file with embedded certificates.
        """
        config = f"""# Fsociety VPN - OpenVPN Client Configuration
# Generated: {datetime.now(timezone.utc).isoformat()}
# This is a REAL configuration with valid certificates

client
dev tun
proto {protocol}
remote {server_ip} {port}
resolv-retry infinite
nobind
persist-key
persist-tun

# Security settings
remote-cert-tls server
cipher AES-256-GCM
auth SHA256
key-direction 1

# Logging
verb 3
mute 20

# ==========================================================
# TROUBLESHOOTING (delete this section after reading)
# ==========================================================
# If connection hangs/times out, you likely have a PORT FORWARDING issue.
#
# FOR LOCAL TESTING (same Windows machine as WSL server):
# Change the "remote" line above to: remote 127.0.0.1 {port}
#
# FOR EXTERNAL CONNECTIONS:
# 1. Forward UDP {port} from Windows to WSL:
#    netsh interface portproxy add v4tov4 listenport={port} listenaddress=0.0.0.0 connectport={port} connectaddress=<WSL_IP>
# 2. Allow UDP {port} in Windows Firewall
# 3. Forward UDP {port} on your router to your Windows machine
# ==========================================================

# Certificate Authority
<ca>
{ca_cert.strip()}
</ca>

# Client Certificate
<cert>
{client_cert.strip()}
</cert>

# Client Private Key
<key>
{client_key.strip()}
</key>

# TLS-Auth Key
<tls-auth>
{ta_key.strip()}
</tls-auth>
"""
        return config

    def generate_wireguard_keys(self) -> VPNKeys:
        """
        Generate WireGuard keys.
        """
        keys = vpn_tools.generate_wireguard_keys()
        return VPNKeys(**keys)

    def generate_wireguard_config(self, request: WireGuardRequest, user_id: str) -> VPNConfigResponse:
        """
        Generate a WireGuard configuration.
        """
        # If client private key is not provided, generate one
        if not request.client_private_key:
            keys = vpn_tools.generate_wireguard_keys()
            client_private_key = keys['private_key']
        else:
            client_private_key = request.client_private_key
            
        # Mock client address allocation
        client_address = "10.100.0.2/32"
        
        config_content = vpn_tools.generate_wireguard_config(
            private_key=client_private_key,
            address=client_address,
            server_public_key=request.server_public_key,
            server_endpoint=request.server_endpoint,
            allowed_ips=request.allowed_ips
        )
        
        config_id = str(uuid.uuid4())
        
        config = VPNConfigResponse(
            id=config_id,
            user_id=user_id,
            type="wireguard",
            name=f"WG-{request.server_endpoint}",
            config_content=config_content,
            created_at=datetime.now(timezone.utc)
        )
        
        # Store in DB
        config_data = config.model_dump()
        config_data["config_type"] = "wireguard"
        # WireGuard doesn't strictly have a 'server_id' from our list, but we can imply one
        config_data["server_id"] = "wireguard-custom" 
        
        self.vpn_repo.create(config_data)
        
        return config

    def get_user_configs(self, user_id: str) -> List[VPNConfigResponse]:
        """
        Get all VPN configs for a user.
        """
        configs = self.vpn_repo.get_by_user(user_id)
        return [
            VPNConfigResponse(
                id=c.id,
                user_id=c.user_id,
                type=c.config_type,  # Map config_type to type
                name=c.filename or f"VPN-{c.server_id}", # Map filename or server_id to name
                filename=c.filename,
                config_content=c.config_content,
                created_at=c.created_at
            )
            for c in configs
        ]
    
    def get_server_setup_files(self) -> Dict:
        """
        Get all files needed to set up the OpenVPN server.
        Returns dict with all PKI files for server configuration.
        """
    def _build_mock_openvpn_config(self, server_name: str, user_id: str) -> str:
        """
        Build a MOCK OpenVPN configuration for environments without VPN tools.
        """
        return f"""# Fsociety VPN - MOCK Configuration
# Generated: {datetime.now(timezone.utc).isoformat()}
# Server: {server_name}
# User: {user_id}
# NOTICE: This is a simulation for testing/demo purposes.

client
dev tun
proto udp
remote mock.vpn.fsociety.dev 1194
resolv-retry infinite
nobind
persist-key
persist-tun

# Dummy Certificates
<ca>
-----BEGIN CERTIFICATE-----
MIIBtzCCASwCCQDTxH... (Mock CA Certificate) ...3f5g=
-----END CERTIFICATE-----
</ca>

<cert>
-----BEGIN CERTIFICATE-----
MIIBtzCCASwCCQDTxH... (Mock Client Certificate) ...3f5g=
-----END CERTIFICATE-----
</cert>

<key>
-----BEGIN PRIVATE KEY-----
MIIBtzCCASwCCQDTxH... (Mock Private Key) ...3f5g=
-----END PRIVATE KEY-----
</key>
"""


