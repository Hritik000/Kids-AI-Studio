import os
import time
import secrets
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
import jwt
from jwt.exceptions import InvalidTokenError
from app.schemas.auth import UserProfile, UserRole
from app.core.config import settings

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per hour"])

# Auth-specific rate limits
auth_limiter = Limiter(key_func=get_remote_address, default_limits=["10 per minute"])

# Security scheme
security_scheme = HTTPBearer(auto_error=False)

# Mock in-memory user store for dev/testing when Supabase is not connected
mock_users_db = {
    "user_demo_123": UserProfile(
        id="user_demo_123",
        email="creator@kidsai.studio",
        full_name="Alex Creator",
        avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Alex",
        role=UserRole.USER
    ),
    "user_admin_999": UserProfile(
        id="user_admin_999",
        email="admin@kidsai.studio",
        full_name="Studio Admin",
        avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Admin",
        role=UserRole.ADMIN
    )
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except InvalidTokenError:
        return None

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)) -> UserProfile:
    """
    FastAPI Security Dependency:
    Validates Bearer JWT Token and returns the authenticated user profile.
    Falls back to mock users for development when no valid token is provided.
    """
    # For development, allow mock tokens if no real token provided
    if settings.ENVIRONMENT == "development":
        if not credentials or not credentials.credentials:
            # Return demo user for development when no token provided
            return mock_users_db["user_demo_123"]

        token = credentials.credentials

        # Handle demo tokens for development
        if token.startswith("demo_token_admin"):
            return mock_users_db["user_admin_999"]
        elif token.startswith("demo_token_"):
            user_id = token[11:]
            return mock_users_db.get(user_id, mock_users_db["user_demo_123"])
        elif token.startswith("bearer_"):
            return mock_users_db["user_demo_123"]
        elif token.startswith("eyJ") or token.startswith("mock_jwt_"):
            return mock_users_db["user_demo_123"]

    # Production: validate real JWT token
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Extract user info from token payload
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # In a real implementation, you would fetch the user from Supabase here
    # For now, we'll return a basic user profile based on the token
    # TODO: Replace with actual Supabase user lookup
    return UserProfile(
        id=user_id,
        email=payload.get("email", "user@example.com"),
        full_name=payload.get("full_name", "User"),
        avatar_url=payload.get("avatar_url", ""),
        role=UserRole(payload.get("role", "user"))
    )

def require_role(allowed_roles: List[UserRole]):
    """Role-based access control dependency factory."""
    async def role_checker(current_user: UserProfile = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for current user role"
            )
        return current_user
    return role_checker

# Input validation helpers
def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Basic input sanitization to prevent XSS and injection attacks."""
    if not text:
        return ""
    
    # Truncate to max length
    text = text[:max_length]
    
    # Remove or escape potentially dangerous characters
    # This is a basic implementation - consider using a library like bleach for production
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '\\', '$', '`']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

def validate_uuid(uuid_string: str) -> bool:
    """Validate that a string is a valid UUID."""
    try:
        import uuid
        uuid_obj = uuid.UUID(uuid_string)
        return str(uuid_obj) == uuid_string
    except ValueError:
        return False

# Security headers middleware would be added in main.py
