"""
Admin Router - SQLite Version

Admin-only endpoints for user management, platform stats, and SQL console.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from model.Admin_Model import (
    UserUpdateRequest, PlatformStats, UserListResponse
)
from service.Admin_Service import AdminService
from database.engine import get_db
from routers.dependencies import require_admin

router = APIRouter()


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    """Get AdminService with database session"""
    return AdminService(db)


# ==================== USER MANAGEMENT ====================

@router.get("/users", response_model=UserListResponse)
async def get_users(
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    role: str = Query(None),
    active_only: bool = Query(False),
    search: str = Query(None),
    admin: dict = Depends(require_admin),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Get all users with filtering and pagination"""
    try:
        skip = (page - 1) * limit
        result = admin_service.get_all_users(limit, skip, role, active_only, search)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    update_data: UserUpdateRequest,
    admin: dict = Depends(require_admin),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Update any user (admin only)"""
    try:
        result = admin_service.update_user(user_id, update_data.dict(exclude_unset=True))
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: dict = Depends(require_admin),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Delete any user (admin only)"""
    try:
        admin_service.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PLATFORM STATS ====================

@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats(
    admin: dict = Depends(require_admin),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Get platform statistics"""
    try:
        stats = admin_service.get_platform_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ACTIVITY SEARCH ====================

@router.get("/activities")
async def search_activities(
    user_id: str = Query(None),
    action: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    admin: dict = Depends(require_admin),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Search activities across all users"""
    try:
        skip = (page - 1) * limit
        activities = admin_service.search_activities(
            user_id=user_id,
            action=action,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            skip=skip
        )
        return {"activities": activities, "count": len(activities)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SQL QUERY CONSOLE ====================

class SQLQueryRequest(BaseModel):
    query: str
    
class SQLQueryResponse(BaseModel):
    success: bool
    columns: list = []
    rows: list = []
    row_count: int = 0
    message: str = ""


@router.post("/sql", response_model=SQLQueryResponse)
async def execute_sql_query(
    request: SQLQueryRequest,
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Execute a SQL query directly on the database.
    
    **Security**: Admin-only endpoint.
    **Warning**: Use with caution in production!
    
    Returns structured data with column names and rows.
    """
    from sqlalchemy import text
    
    query = request.query.strip()
    
    try:
        result = db.execute(text(query))
        
        # Check if it's a SELECT query (returns rows)
        if result.returns_rows:
            columns = list(result.keys())
            rows = [list(row) for row in result.fetchall()]
            db.commit()
            return SQLQueryResponse(
                success=True,
                columns=columns,
                rows=rows,
                row_count=len(rows),
                message=f"Query executed successfully. {len(rows)} rows returned."
            )
        else:
            # For INSERT, UPDATE, DELETE
            affected = result.rowcount
            db.commit()
            return SQLQueryResponse(
                success=True,
                columns=[],
                rows=[],
                row_count=affected,
                message=f"Query executed successfully. {affected} rows affected."
            )
    except Exception as e:
        db.rollback()
        return SQLQueryResponse(
            success=False,
            message=f"SQL Error: {str(e)}"
        )
