from fastapi import APIRouter, Depends
from app.models.project import APIResponse, APIError
from app.schemas.auth import UserProfile, UserUpdate, ChangePasswordRequest
from app.core.security import get_current_user, mock_users_db

router = APIRouter()

@router.get("/profile", response_model=APIResponse[UserProfile])
async def get_profile(current_user: UserProfile = Depends(get_current_user)):
    return APIResponse(success=True, data=current_user)

@router.put("/profile", response_model=APIResponse[UserProfile])
async def update_profile(
    payload: UserUpdate,
    current_user: UserProfile = Depends(get_current_user)
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
        
    mock_users_db[current_user.id] = current_user
    return APIResponse(success=True, data=current_user)

@router.post("/change-password", response_model=APIResponse[dict])
async def change_password(
    payload: ChangePasswordRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    if len(payload.new_password) < 8:
        return APIResponse(
            success=False,
            error=APIError(code="VALIDATION_ERROR", message="Password must be at least 8 characters long")
        )
    return APIResponse(success=True, data={"message": "Password updated successfully"})
