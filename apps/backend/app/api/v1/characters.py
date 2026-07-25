from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Body
from app.models.project import APIResponse, APIError
from app.models.character import CharacterProfile
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.api.v1.projects import projects_db
from app.api.v1.ai import stories_db, plans_db
from app.services.character import CharacterEngineService

router = APIRouter()

@router.post("/projects/{project_id}/characters/generate", response_model=APIResponse[List[CharacterProfile]])
async def generate_characters(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    story_script = stories_db.get(project_id)
    if not story_script:
        return APIResponse(
            success=False,
            error=APIError(code="STORY_NOT_FOUND", message="Please generate a story script first.")
        )

    production_plan = plans_db.get(project_id)

    profiles = CharacterEngineService.generate_character_profiles(
        project_id=project_id,
        story_script=story_script,
        production_plan=production_plan
    )

    return APIResponse(success=True, data=profiles)

@router.get("/projects/{project_id}/characters", response_model=APIResponse[List[CharacterProfile]])
async def get_characters(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    profiles = CharacterEngineService.get_project_characters(project_id)
    return APIResponse(success=True, data=profiles)

@router.put("/projects/{project_id}/characters/{char_id}", response_model=APIResponse[CharacterProfile])
async def update_character(
    project_id: str,
    char_id: str,
    payload: Dict[str, Any] = Body(...),
    current_user: UserProfile = Depends(get_current_user)
):
    updated = CharacterEngineService.update_character_profile(project_id, char_id, payload)
    if not updated:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Character profile not found")
        )

    return APIResponse(success=True, data=updated)
