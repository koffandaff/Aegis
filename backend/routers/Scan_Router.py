"""
Scan Router with Rate Limiting and Security
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List

from model.Scan_Model import (
    DomainScanRequest, IPScanRequest, WhoisRequest,
    DNSRequest, SubdomainRequest, PortScanRequest,
    ScanResult, ScanHistoryResponse
)
from service.Scan_Service import scan_service
from routers.dependencies import get_current_user, require_admin
from utils.rate_limiter import rate_limiter
from model.Auth_Model import db  # ADD THIS IMPORT

router = APIRouter()
security = HTTPBearer()

# ========== DOMAIN SCANNING ==========

@router.post("/domain", response_model=ScanResult)
async def scan_domain(
    request: DomainScanRequest,
    current_user: dict = Depends(get_current_user),
    http_request: Request = None
):
    """Perform comprehensive domain scan"""
    try:
        # Rate limiting
        allowed, remaining, reset_in = scan_service.check_rate_limit(
            current_user['id'], "scan_domain"
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": "5 scans per minute",
                    "remaining": 0,
                    "reset_in": reset_in
                }
            )
        
        # Create and perform scan
        scan_id = scan_service.validate_and_create_scan(
            current_user['id'], "domain", request.domain
        )
        
        results = scan_service.perform_scan(scan_id)
        scan = scan_service.get_scan(scan_id, current_user['id'])
        
        return ScanResult(**scan)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/whois", response_model=ScanResult)
async def scan_whois(
    request: WhoisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Perform WHOIS lookup"""
    try:
        # Rate limiting
        allowed, remaining, reset_in = scan_service.check_rate_limit(
            current_user['id'], "scan_whois"
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Maximum 10 WHOIS lookups per minute."
            )
        
        scan_id = scan_service.validate_and_create_scan(
            current_user['id'], "whois", request.domain
        )
        
        results = scan_service.perform_scan(scan_id)
        scan = scan_service.get_scan(scan_id, current_user['id'])
        
        return ScanResult(**scan)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dns", response_model=ScanResult)
async def scan_dns(
    request: DNSRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get DNS records"""
    try:
        # Rate limiting
        allowed, remaining, reset_in = scan_service.check_rate_limit(
            current_user['id'], "scan_dns"
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Maximum 15 DNS lookups per minute."
            )
        
        scan_id = scan_service.validate_and_create_scan(
            current_user['id'], "dns", request.domain
        )
        
        results = scan_service.perform_scan(scan_id)
        scan = scan_service.get_scan(scan_id, current_user['id'])
        
        return ScanResult(**scan)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subdomains", response_model=ScanResult)
async def scan_subdomains(
    request: SubdomainRequest,
    current_user: dict = Depends(get_current_user)
):
    """Discover subdomains"""
    try:
        # Rate limiting
        allowed, remaining, reset_in = scan_service.check_rate_limit(
            current_user['id'], "scan_subdomains"
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Maximum 2 subdomain scans per minute."
            )
        
        scan_id = scan_service.validate_and_create_scan(
            current_user['id'], "subdomains", request.domain
        )
        
        results = scan_service.perform_scan(scan_id)
        scan = scan_service.get_scan(scan_id, current_user['id'])
        
        return ScanResult(**scan)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== IP SCANNING ==========

@router.post("/ip", response_model=ScanResult)
async def scan_ip(
    request: IPScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get IP information"""
    try:
        # Rate limiting
        allowed, remaining, reset_in = scan_service.check_rate_limit(
            current_user['id'], "scan_ip"
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Maximum 10 IP scans per minute."
            )
        
        scan_id = scan_service.validate_and_create_scan(
            current_user['id'], "ip", request.ip
        )
        
        results = scan_service.perform_scan(scan_id)
        scan = scan_service.get_scan(scan_id, current_user['id'])
        
        return ScanResult(**scan)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ports", response_model=ScanResult)
async def scan_ports(
    request: PortScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Scan ports on target"""
    try:
        # Rate limiting
        allowed, remaining, reset_in = scan_service.check_rate_limit(
            current_user['id'], "scan_ports"
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Maximum 3 port scans per minute."
            )
        
        scan_id = scan_service.validate_and_create_scan(
            current_user['id'], "ports", request.target
        )
        
        results = scan_service.perform_scan(scan_id)
        scan = scan_service.get_scan(scan_id, current_user['id'])
        
        return ScanResult(**scan)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== SCAN MANAGEMENT ==========

@router.get("/{scan_id}", response_model=ScanResult)
async def get_scan_result(
    scan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get scan result by ID"""
    try:
        scan = scan_service.get_scan(scan_id, current_user['id'])
        
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found or access denied")
        
        return ScanResult(**scan)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/history", response_model=ScanHistoryResponse)
async def get_scan_history(
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    current_user: dict = Depends(get_current_user)
):
    """Get user's scan history"""
    try:
        result = scan_service.get_user_scans(current_user['id'], limit, page)
        return ScanHistoryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{scan_id}")
async def delete_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a scan"""
    try:
        success = scan_service.delete_scan(scan_id, current_user['id'])
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Scan not found or you don't have permission to delete it"
            )
        
        return {"message": "Scan deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== ADMIN ENDPOINTS ==========

@router.get("/admin/all")
async def get_all_scans(
    limit: int = Query(50, ge=1, le=200),
    page: int = Query(1, ge=1),
    admin: dict = Depends(require_admin)
):
    """Get all scans (admin only)"""
    try:
        skip = (page - 1) * limit
        scans = db.get_all_scans(limit, skip)
        total = len(db.scans)
        
        return {
            "scans": scans,
            "total": total,
            "page": page,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/{scan_id}")
async def admin_delete_scan(
    scan_id: str,
    admin: dict = Depends(require_admin)
):
    """Delete any scan (admin only)"""
    try:
        if scan_id in db.scans:
            del db.scans[scan_id]
            return {"message": "Scan deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Scan not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))