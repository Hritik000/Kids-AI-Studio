import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from app.models.project import APIResponse, APIError
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserProfile,
    UserRole
)
from app.core.security import get_current_user, mock_users_db

router = APIRouter()

@router.post("/register", response_model=APIResponse[TokenResponse])
async def register(payload: RegisterRequest):
    if payload.password != payload.confirm_password:
        return APIResponse(
            success=False,
            error=APIError(code="VALIDATION_ERROR", message="Passwords do not match")
        )
        
    if not payload.terms_accepted:
        return APIResponse(
            success=False,
            error=APIError(code="VALIDATION_ERROR", message="You must accept the terms and conditions")
        )

    # Check if email exists
    for u in mock_users_db.values():
        if u.email.lower() == payload.email.lower():
            return APIResponse(
                success=False,
                error=APIError(code="EMAIL_EXISTS", message="Account with this email already exists")
            )

    user_id = f"usr_{uuid.uuid4().hex[:8]}"
    new_user = UserProfile(
        id=user_id,
        email=payload.email,
        full_name=payload.full_name,
        avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_id}",
        role=UserRole.USER
    )
    mock_users_db[user_id] = new_user

    return APIResponse(
        success=True,
        data=TokenResponse(
            access_token=f"demo_token_{user_id}",
            user=new_user
        )
    )

@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(payload: LoginRequest):
    # Lookup email in mock store
    target_user = None
    for u in mock_users_db.values():
        if u.email.lower() == payload.email.lower():
            target_user = u
            break

    if not target_user:
        # For seamless demo, auto-create account or return invalid credentials
        if payload.email == "creator@kidsai.studio":
            target_user = mock_users_db["user_demo_123"]
        else:
            return APIResponse(
                success=False,
                error=APIError(code="INVALID_CREDENTIALS", message="Invalid email or password")
            )

    return APIResponse(
        success=True,
        data=TokenResponse(
            access_token=f"demo_token_{target_user.id}",
            user=target_user
        )
    )

@router.post("/forgot-password", response_model=APIResponse[dict])
async def forgot_password(payload: ForgotPasswordRequest):
    return APIResponse(
        success=True,
        data={"message": f"Password reset instructions sent to {payload.email}"}
    )

@router.post("/reset-password", response_model=APIResponse[dict])
async def reset_password(payload: ResetPasswordRequest):
    return APIResponse(
        success=True,
        data={"message": "Password successfully reset. You may now sign in with your new password."}
    )

@router.get("/me", response_model=APIResponse[UserProfile])
async def get_me(current_user: UserProfile = Depends(get_current_user)):
    return APIResponse(success=True, data=current_user)

@router.post("/logout", response_model=APIResponse[dict])
async def logout(current_user: UserProfile = Depends(get_current_user)):
    return APIResponse(success=True, data={"message": "Successfully logged out"})
