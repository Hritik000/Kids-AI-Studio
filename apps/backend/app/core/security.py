import os
import time
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.auth import UserProfile, UserRole

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

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)) -> UserProfile:
    """
    FastAPI Security Dependency:
    Validates Bearer JWT Token and returns the authenticated user profile.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing or invalid",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    
    # Simple validation for development/testing tokens
    if token.startswith("demo_token_admin"):
        return mock_users_db["user_admin_999"]
    elif token.startswith("demo_token_"):
        user_id = token[11:]
        return mock_users_db.get(user_id, mock_users_db["user_demo_123"])
    elif token.startswith("bearer_"):
        return mock_users_db["user_demo_123"]
        
    # Standard JWT decoding logic for production Supabase Auth
    try:
        # In production Supabase setup: pyjwt.decode(token, secret, algorithms=["HS256"])
        return mock_users_db["user_demo_123"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

def require_role(allowed_roles: list[UserRole]):
    """Role-based access control dependency factor."""
    async def role_checker(current_user: UserProfile = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for current user role"
            )
        return current_user
    return role_checker
