from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from service.Auth_Service import AuthService
from model.Auth_Model import db

security = HTTPBearer()
auth_service = AuthService(db)

# Dependency to get current user
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

# Dependency to check if user is admin
async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Dependency to check specific role
def require_role(required_role: str):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get('role') != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role.capitalize()} access required"
            )
        return current_user
    return role_checker