from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import List, Optional
from model.VPN_Model import VPNConfigRequest, WireGuardRequest, VPNConfigResponse
from service.VPN_Service import vpn_service
from routers.dependencies import get_current_user, get_current_user_optional

router = APIRouter()

@router.get("/servers")
async def get_available_servers(
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of available Fsociety VPN nodes.
    """
    return vpn_service.get_available_servers()

@router.post("/openvpn", response_model=VPNConfigResponse)
async def generate_openvpn_config(
    request: VPNConfigRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate an OpenVPN configuration file.
    """
    try:
        config = vpn_service.generate_openvpn_config(request, current_user['id'])
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate OpenVPN configuration: {str(e)}"
        )

@router.post("/wireguard", response_model=VPNConfigResponse)
async def generate_wireguard_config(
    request: WireGuardRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a WireGuard configuration file.
    """
    try:
        config = vpn_service.generate_wireguard_config(request, current_user['id'])
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate WireGuard configuration: {str(e)}"
        )

@router.get("/configs", response_model=List[VPNConfigResponse])
async def list_user_configs(
    current_user: dict = Depends(get_current_user)
):
    """
    List all VPN configurations created by the current user.
    """
    try:
        configs = vpn_service.get_user_configs(current_user['id'])
        return configs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve configurations: {str(e)}"
        )


@router.get("/server-setup")
async def get_server_setup_files(
    x_server_secret: Optional[str] = Header(None, alias="X-Server-Secret"),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get all PKI files needed to set up the OpenVPN server.
    
    Can be authenticated via:
    1. X-Server-Secret header (for automated scripts)
    2. JWT token (for authorized admins)
    """
    import os
    server_secret = os.getenv("VPN_SERVER_SECRET")
    
    if x_server_secret and x_server_secret == server_secret:
        # Authenticated via shared secret
        pass
    elif current_user:
        # In production, add admin check here
        # if current_user.get('role') != 'admin':
        #     raise HTTPException(status_code=403, detail="Admin access required")
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to fetch server setup files"
        )
    
    try:
        files = vpn_service.get_server_setup_files()
        return files
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve server setup files: {str(e)}"
        )
