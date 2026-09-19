from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Body
from app.models.project import Project, ProjectStatus, APIResponse, APIError
from app.models.storyboard import Storyboard
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.api.v1.projects import projects_db
from app.core.db import plans_db, stories_db, storyboards_db
from app.services.storyboard import StoryboardAgentService

router = APIRouter()

storyboard_service = StoryboardAgentService()

@router.post("/projects/{project_id}/generate-storyboard", response_model=APIResponse[Dict[str, Any]])
async def generate_storyboard(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    story_script = stories_db.get(project_id)

    if not story_script:
        return APIResponse(
            success=False,
            error=APIError(code="STORY_NOT_FOUND", message="Please generate a story script first before creating a storyboard.")
        )

    production_plan = plans_db.get(project_id)

    try:
        sb = await storyboard_service.generate_storyboard(
            project_id=project_id,
            story_script=story_script,
            production_plan=production_plan
        )

        storyboards_db[project_id] = sb
        project.status = ProjectStatus.STORYBOARD_READY
        projects_db[project_id] = project

        return APIResponse(success=True, data=sb)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="STORYBOARD_GENERATION_FAILED", message=str(e))
        )

@router.get("/projects/{project_id}/storyboard", response_model=APIResponse[Dict[str, Any]])
async def get_storyboard(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    sb = storyboards_db.get(project_id)
    if not sb:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Storyboard has not been generated yet for this project.")
        )

    return APIResponse(success=True, data=sb)

@router.post("/projects/{project_id}/storyboard/regenerate-scene/{scene_number}", response_model=APIResponse[Dict[str, Any]])
async def regenerate_scene(
    project_id: str,
    scene_number: int,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    sb = storyboards_db.get(project_id)
    if not sb:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Storyboard not found")
        )

    try:
        updated_sb = await storyboard_service.regenerate_single_scene(sb, scene_number)
        storyboards_db[project_id] = updated_sb
        return APIResponse(success=True, data=updated_sb)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="REGENERATE_SCENE_FAILED", message=str(e))
        )

@router.put("/projects/{project_id}/storyboard/scenes/{scene_number}", response_model=APIResponse[Dict[str, Any]])
async def update_scene_metadata(
    project_id: str,
    scene_number: int,
    payload: Dict[str, Any] = Body(...),
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db or project_id not in storyboards_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project or Storyboard not found")
        )

    sb = storyboards_db[project_id]
    scenes = sb.get("scenes", [])
    target = next((s for s in scenes if s.get("scene_number") == scene_number), None)

    if not target:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message=f"Scene #{scene_number} not found")
        )

    for key, value in payload.items():
        target[key] = value

    storyboards_db[project_id] = sb
    return APIResponse(success=True, data=sb)

@router.post("/projects/{project_id}/storyboard/approve", response_model=APIResponse[Dict[str, Any]])
async def approve_storyboard(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db or project_id not in storyboards_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Storyboard not found")
        )

    sb = storyboards_db[project_id]
    sb["approved"] = True
    storyboards_db[project_id] = sb

    project = projects_db[project_id]
    project.status = ProjectStatus.STORYBOARD_READY
    projects_db[project_id] = project

    return APIResponse(success=True, data={"message": "Storyboard approved successfully", "approved": True})

@router.get("/projects/{project_id}/storyboard/status", response_model=APIResponse[Dict[str, Any]])
async def get_storyboard_status(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    sb = storyboards_db.get(project_id)
    has_sb = sb is not None
    is_approved = sb.get("approved", False) if sb else False

    return APIResponse(
        success=True,
        data={
            "project_id": project_id,
            "has_storyboard": has_sb,
            "approved": is_approved,
            "scene_count": len(sb.get("scenes", [])) if sb else 0
        }
    )
