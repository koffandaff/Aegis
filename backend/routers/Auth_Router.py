"""
Auth Router - SQLite Version

Authentication endpoints: signup, login, logout, refresh, and user info.
"""
import os
from fastapi import APIRouter, HTTPException, Depends, status, Response, Request, Cookie
from sqlalchemy.orm import Session

from model.Auth_Model import (
    UserCreate, UserLogin, Token, RefreshTokenRequest, UserResponse,
    PasswordResetRequest, PasswordResetConfirm, OTPVerifyRequest
)
from service.Auth_Service import AuthService
from database.engine import get_db
from routers.dependencies import get_current_user
from routers.limiter import limiter

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Get AuthService with database session"""
    return AuthService(db)


# ==================== ENDPOINTS ====================

@router.post("/signup", response_model=UserResponse)
async def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    print(f"[AUTH] Signup attempt for email: {user_data.email}, username: {user_data.username}")
    try:
        user_dict = user_data.dict()
        user = auth_service.register_user(user_dict)
        print(f"[AUTH] Signup SUCCESS for {user_data.username}")
        return UserResponse(**user)
    except ValueError as e:
        print(f"[AUTH] Signup FAILED: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(
    login_data: UserLogin,
    response: Response,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    _ = Depends(limiter.limit(limit=10, window=60))
):
    """Login and get token"""
    print(f"[AUTH] Login attempt for: {login_data.email}")
    try:
        result = auth_service.login_user(login_data.email, login_data.password)
        
        # Record login IP
        client_ip = request.client.host if request.client else None
        if client_ip:
            auth_service.record_login_ip(result['user']['id'], client_ip)
        
        # Set refresh token in HttpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        # Remove refresh_token from body response
        if "refresh_token" in result:
            del result["refresh_token"]
            
        print(f"[AUTH] Login SUCCESS for: {login_data.email}")
        return result
    except PermissionError as e:
        if str(e) == "ACCOUNT_DISABLED":
            print(f"[AUTH] Login BLOCKED - Account disabled: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_DISABLED", "message": "Your account has been disabled by an administrator. Please contact support."}
            )
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        print(f"[AUTH] Login FAILED for: {login_data.email}")
        raise HTTPException(status_code=401, detail=str(e))


@router.post('/logout')
async def logout(
    response: Response,
    request: Request,
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Logout user and invalidate refresh token"""
    try:
        # Get refresh token from cookie or body
        refresh_token = request.cookies.get("refresh_token")
        
        if refresh_token:
            auth_service.logout(current_user['id'], refresh_token)
            
        # Clear cookie
        response.delete_cookie(key="refresh_token")
        
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/refresh', response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token using refresh token from cookie"""
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    new_access_token = auth_service.refresh_access_token(refresh_token)
    if not new_access_token:
        raise HTTPException(status_code=401, detail="Invalid Refresh Token")
    return Token(access_token=new_access_token)


@router.get('/me', response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(**current_user)


@router.post('/forgot-password')
async def forgot_password(
    request: PasswordResetRequest, # Updated import
    auth_service: AuthService = Depends(get_auth_service),
    _ = Depends(limiter.limit(limit=3, window=60))
):
    """Request password reset (generates token)"""
    try:
        auth_service.request_password_reset(request.email)
        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a reset link has been sent."}
    except Exception as e:
        print(f"[AUTH] Forgot Password Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post('/verify-otp')
async def verify_otp(
    request: OTPVerifyRequest, 
    auth_service: AuthService = Depends(get_auth_service),
    _ = Depends(limiter.limit(limit=5, window=300))
):
    """Verify OTP without resetting password"""
    try:
        # We'll add a check_otp method to service
        auth_service.verify_otp_only(request.email, request.otp)
        return {"message": "OTP verified successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[AUTH] Verify OTP Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post('/reset-password')
async def reset_password(
    request: PasswordResetConfirm, # Updated import
    auth_service: AuthService = Depends(get_auth_service),
    _ = Depends(limiter.limit(limit=5, window=300))
):
    """Reset password using token"""
    try:
        auth_service.reset_password(request.email, request.otp, request.new_password)
        return {"message": "Password reset successfully. Please login."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[AUTH] Reset Password Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
