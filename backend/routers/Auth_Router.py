from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from model.Auth_Model import UserCreate, UserLogin, Token, RefreshTokenRequest, UserResponse, db
from service.Auth_Service import AuthService

router = APIRouter()
security = HTTPBearer()

auth_service = AuthService(db)

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

# Endpoints

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate):
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
async def login(login_data: UserLogin):
    """Login and get token"""
    print(f"[AUTH] Login attempt for: {login_data.email}")
    try:
        result = auth_service.login_user(login_data.email, login_data.password)
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
async def logout(request: RefreshTokenRequest, current_user: dict = Depends(get_current_user)):
    from model.Auth_Model import db
    try:
        auth_service.logout(current_user['id'], request.refresh_token)
        # Log logout activity
        db.log_activity(
            user_id=current_user['id'],
            action='logout',
            details={'email': current_user.get('email')}
        )
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/refresh', response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    new_access_token = auth_service.refresh_access_token(request.refresh_token)
    if not new_access_token:
        raise HTTPException(status_code=401, detail="Invalid Refresh Token")
    return Token(access_token=new_access_token)

@router.get('/me', response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

@router.get('/all')
async def get_all_users():
    return {"users": db.get_all_users()}