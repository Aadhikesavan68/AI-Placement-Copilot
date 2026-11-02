from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: EmailStr
    name: str
    picture: Optional[str] = None


class UserCreate(UserBase):
    password: str
    google_id: Optional[str] = None


class UserInDB(UserBase):
    id: str
    google_id: Optional[str] = None
    hashed_password: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class User(UserBase):
    """Public user returned by the API. Never includes hashed_password."""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class RegisterResponse(BaseModel):
    message: str
