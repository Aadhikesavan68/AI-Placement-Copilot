from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from core.config import settings
from core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from repositories.user_repo import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    serialize_user,
)
from schemas.user_schema import TokenResponse, User, UserCreate, UserLogin, RegisterResponse

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return User.model_validate(serialize_user(user))


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterResponse)
async def register(request: UserCreate):
    existing = await get_user_by_email(request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password minimum 8 characters")

    request.password = get_password_hash(request.password)
    await create_user(request)
    return {"message": "User created successfully"}


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLogin):
    user = await get_user_by_email(request.email)
    if not user or not user.get("hashed_password"):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user["id"], expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": serialize_user(user),
    }


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
