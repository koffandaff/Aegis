from fastapi import APIRouter, HTTPException, Depends, Query
from model.Admin_Model import (
    UserUpdateRequest, PlatformStats, UserListResponse
)
from service.Admin_Service import AdminService
from model.Auth_Model import db
from routers.dependencies import require_admin

router = APIRouter()
admin_service = AdminService(db)

# Get all users (admin only)
@router.get("/users", response_model=UserListResponse)
async def get_users(
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    role: str = Query(None),
    active_only: bool = Query(False),
    admin: dict = Depends(require_admin)  # Requires admin role
):
    try:
        skip = (page - 1) * limit
        result = admin_service.get_all_users(limit, skip, role, active_only)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update any user (admin only)
@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    update_data: UserUpdateRequest,
    admin: dict = Depends(require_admin)
):
    try:
        result = admin_service.update_user(user_id, update_data.dict(exclude_unset=True))
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete any user (admin only)
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: dict = Depends(require_admin)
):
    try:
        admin_service.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get platform statistics (admin only)
@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats(admin: dict = Depends(require_admin)):
    try:
        stats = admin_service.get_platform_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search activities (admin only)
@router.get("/activities")
async def search_activities(
    user_id: str = Query(None),
    action: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    admin: dict = Depends(require_admin)
):
    try:
        activities = admin_service.search_activities(
            user_id=user_id,
            action=action,
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )
        return {"activities": activities, "count": len(activities)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))