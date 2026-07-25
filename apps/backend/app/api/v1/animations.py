from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from app.models.project import ProjectStatus, APIResponse, APIError
from app.models.animation import AnimatedSceneClip
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.api.v1.projects import projects_db
from app.api.v1.storyboard import storyboards_db
from app.services.character import CharacterEngineService
from app.services.image_generator import images_db
from app.services.animation_generator import AnimationPipelineService, animations_db

router = APIRouter()
animation_service = AnimationPipelineService()

@router.post("/projects/{project_id}/animations/generate", response_model=APIResponse[List[AnimatedSceneClip]])
async def generate_scene_animations(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    storyboard = storyboards_db.get(project_id)
    if not storyboard:
        return APIResponse(
            success=False,
            error=APIError(code="STORYBOARD_NOT_FOUND", message="Please generate a storyboard first before generating animations.")
        )

    scene_images = images_db.get(project_id, [])
    characters = CharacterEngineService.get_project_characters(project_id)

    try:
        clips = await animation_service.generate_all_scene_animations(
            project_id=project_id,
            storyboard=storyboard,
            scene_images=scene_images,
            characters=characters
        )

        project = projects_db[project_id]
        project.status = ProjectStatus.ANIMATION_READY
        projects_db[project_id] = project

        return APIResponse(success=True, data=clips)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="ANIMATION_GENERATION_FAILED", message=str(e))
        )

@router.post("/projects/{project_id}/animations/regenerate-scene/{scene_number}", response_model=APIResponse[AnimatedSceneClip])
async def regenerate_scene_animation(
    project_id: str,
    scene_number: int,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db or project_id not in storyboards_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project or Storyboard not found")
        )

    storyboard = storyboards_db[project_id]
    scene_images = images_db.get(project_id, [])
    characters = CharacterEngineService.get_project_characters(project_id)

    try:
        new_clip = await animation_service.regenerate_single_scene_animation(
            project_id=project_id,
            scene_number=scene_number,
            storyboard=storyboard,
            scene_images=scene_images,
            characters=characters
        )
        return APIResponse(success=True, data=new_clip)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="REGENERATE_ANIMATION_FAILED", message=str(e))
        )

@router.get("/projects/{project_id}/animations", response_model=APIResponse[List[AnimatedSceneClip]])
async def list_scene_animations(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    clips = animations_db.get(project_id, [])
    return APIResponse(success=True, data=clips)

@router.post("/projects/{project_id}/animations/approve/{animation_id}", response_model=APIResponse[Dict[str, Any]])
async def approve_animation(
    project_id: str,
    animation_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    clips = animations_db.get(project_id, [])
    target = next((c for c in clips if c.animation_id == animation_id), None)
    if not target:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Animation clip not found")
        )

    target.status = "APPROVED"
    return APIResponse(success=True, data={"message": f"Animation clip {animation_id} approved", "status": "APPROVED"})

@router.post("/projects/{project_id}/animations/reject/{animation_id}", response_model=APIResponse[Dict[str, Any]])
async def reject_animation(
    project_id: str,
    animation_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    clips = animations_db.get(project_id, [])
    target = next((c for c in clips if c.animation_id == animation_id), None)
    if not target:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Animation clip not found")
        )

    target.status = "REJECTED"
    return APIResponse(success=True, data={"message": f"Animation clip {animation_id} rejected", "status": "REJECTED"})

@router.get("/projects/{project_id}/animations/status", response_model=APIResponse[Dict[str, Any]])
async def get_animation_status(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    clips = animations_db.get(project_id, [])
    has_clips = len(clips) > 0
    approved_count = len([c for c in clips if c.status == "APPROVED"])

    return APIResponse(
        success=True,
        data={
            "project_id": project_id,
            "has_animations": has_clips,
            "total_clips": len(clips),
            "approved_clips": approved_count,
            "all_approved": has_clips and approved_count == len(clips)
        }
    )
