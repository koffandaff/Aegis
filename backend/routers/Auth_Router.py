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

@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    try:
        user_dict = user_data.dict()
        result = auth_service.register_user(user_dict)
        return UserResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/login')
async def login(login_data: UserLogin):
    try:
        result = auth_service.login_user(login_data.email, login_data.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/logout')
async def logout(request: RefreshTokenRequest, current_user: dict = Depends(get_current_user)):
    try:
        auth_service.logout(current_user['id'], request.refresh_token)
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