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

        # Create unique client name for certificate
        config_id = str(uuid.uuid4())
        client_name = f"{user_id}_{server_id}_{config_id[:8]}"
        
        # Generate REAL client certificate using PKI
        client_cert, client_key = pki_manager.generate_client_certificate(client_name)
        
        # Get CA certificate
        ca_cert = pki_manager.get_ca_certificate()
        
        # Get TLS-Auth key
        ta_key = pki_manager.get_ta_key()
        
        # Build OpenVPN config with real certs
        config_content = self._build_openvpn_config(
            server_ip=self.vpn_server_ip,
            port=self.vpn_server_port,
            protocol=self.vpn_protocol,
            ca_cert=ca_cert,
            client_cert=client_cert,
            client_key=client_key,
            ta_key=ta_key
        )
        
        # Create filename: username_fsociety_servername
        safe_server_name = server_id.replace("-", "_").replace(" ", "_")
        config_filename = f"{user_id}_fsociety_{safe_server_name}"
        
        config = VPNConfigResponse(
            id=config_id,
            user_id=user_id,
            type="openvpn",
            name=server_name,
            filename=config_filename,
            config_content=config_content,
            created_at=datetime.now(timezone.utc)
        )
        
        # Store in DB
        self.vpn_repo.create(config.model_dump())
        
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
        self.vpn_repo.create(config.model_dump())
        
        return config

    def get_user_configs(self, user_id: str) -> List[VPNConfigResponse]:
        """
        Get all VPN configs for a user.
        """
        configs = self.vpn_repo.get_by_user(user_id)
        return [VPNConfigResponse(**c.to_dict()) if hasattr(c, 'to_dict') else VPNConfigResponse(**c.__dict__) for c in configs]
    
    def get_server_setup_files(self) -> Dict:
        """
        Get all files needed to set up the OpenVPN server.
        Returns dict with all PKI files for server configuration.
        """
        return pki_manager.get_server_files()


