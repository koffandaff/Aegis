from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from model.Auth_Model import db
from model.User_Model import (
    UserProfileUpdate, PasswordChange, 
    ActivityResponse, StatsResponse, DeleteAccountRequest
)
from service.Auth_Service import AuthService
from service.User_Service import UserService

router = APIRouter()
security = HTTPBearer()

auth_service = AuthService(db)
user_service = UserService(db, auth_service)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Update user profile
@router.put("/profile")
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    try:
        # Log activity
        user_service.log_activity(
            user_id=current_user['id'],
            action="profile_update",
            details={"fields_updated": list(profile_data.dict(exclude_unset=True).keys())},
            request=request
        )
        
        # Update profile
        result = user_service.update_profile(current_user['id'], profile_data.dict(exclude_unset=True))
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Change password
@router.put("/password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    try:
        # Log activity
        user_service.log_activity(
            user_id=current_user['id'],
            action="password_change",
            request=request
        )
        
        # Change password
        user_service.change_password(
            current_user['id'],
            password_data.current_password,
            password_data.new_password
        )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete account
@router.delete("/account")
async def delete_account(
    delete_request: DeleteAccountRequest,
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    try:
        # Log activity (before deletion)
        user_service.log_activity(
            user_id=current_user['id'],
            action="account_deletion",
            request=request
        )
        
        # Delete account
        user_service.delete_account(current_user['id'], delete_request.password)
        return {"message": "Account deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get user activities
@router.get("/activities", response_model=ActivityResponse)
async def get_activities(
    limit: int = 20,
    page: int = 1,
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    try:
        # Log activity
        user_service.log_activity(
            user_id=current_user['id'],
            action="view_activities",
            request=request
        )
        
        # Get activities
        result = user_service.get_user_activities(current_user['id'], limit, page)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get user statistics
@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    try:
        # Log activity
        user_service.log_activity(
            user_id=current_user['id'],
            action="view_stats",
            request=request
        )
        
        # Get stats
        stats = user_service.get_user_stats(current_user['id'])
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))