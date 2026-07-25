from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"

class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, description="User full name")
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password min 8 characters")
    confirm_password: str = Field(..., min_length=8)
    terms_accepted: bool = Field(..., description="Must accept Terms and Conditions")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class UserProfile(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    avatar_url: Optional[str] = None
    role: UserRole = UserRole.USER
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: UserProfile
