from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from app.models.project import ProjectStatus, APIResponse, APIError
from app.models.character import GeneratedImage
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.api.v1.projects import projects_db
from app.api.v1.storyboard import storyboards_db
from app.services.character import CharacterEngineService
from app.services.image_generator import ImagePipelineService, images_db

router = APIRouter()
image_service = ImagePipelineService()

@router.post("/projects/{project_id}/images/generate", response_model=APIResponse[List[GeneratedImage]])
async def generate_scene_images(
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
            error=APIError(code="STORYBOARD_NOT_FOUND", message="Please generate and approve a storyboard first before generating images.")
        )

    # Fetch Character Profiles from Memory Engine
    characters = CharacterEngineService.get_project_characters(project_id)

    try:
        images = await image_service.generate_all_scene_images(
            project_id=project_id,
            storyboard=storyboard,
            characters=characters
        )

        project = projects_db[project_id]
        project.status = ProjectStatus.IMAGES_READY
        projects_db[project_id] = project

        return APIResponse(success=True, data=images)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="IMAGE_GENERATION_FAILED", message=str(e))
        )

@router.post("/projects/{project_id}/images/regenerate-scene/{scene_number}", response_model=APIResponse[GeneratedImage])
async def regenerate_scene_image(
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
    characters = CharacterEngineService.get_project_characters(project_id)

    try:
        new_img = await image_service.regenerate_single_scene_image(
            project_id=project_id,
            scene_number=scene_number,
            storyboard=storyboard,
            characters=characters
        )
        return APIResponse(success=True, data=new_img)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="REGENERATE_IMAGE_FAILED", message=str(e))
        )

@router.get("/projects/{project_id}/images", response_model=APIResponse[List[GeneratedImage]])
async def list_scene_images(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    images = images_db.get(project_id, [])
    return APIResponse(success=True, data=images)

@router.post("/projects/{project_id}/images/approve/{image_id}", response_model=APIResponse[Dict[str, Any]])
async def approve_image(
    project_id: str,
    image_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    images = images_db.get(project_id, [])
    target = next((img for img in images if img.image_id == image_id), None)
    if not target:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Image not found")
        )

    target.status = "APPROVED"
    return APIResponse(success=True, data={"message": f"Image {image_id} approved", "status": "APPROVED"})

@router.post("/projects/{project_id}/images/reject/{image_id}", response_model=APIResponse[Dict[str, Any]])
async def reject_image(
    project_id: str,
    image_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    images = images_db.get(project_id, [])
    target = next((img for img in images if img.image_id == image_id), None)
    if not target:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Image not found")
        )

    target.status = "REJECTED"
    return APIResponse(success=True, data={"message": f"Image {image_id} rejected", "status": "REJECTED"})

@router.get("/projects/{project_id}/images/status", response_model=APIResponse[Dict[str, Any]])
async def get_image_status(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    images = images_db.get(project_id, [])
    has_images = len(images) > 0
    approved_count = len([img for img in images if img.status == "APPROVED"])

    return APIResponse(
        success=True,
        data={
            "project_id": project_id,
            "has_images": has_images,
            "total_images": len(images),
            "approved_images": approved_count,
            "all_approved": has_images and approved_count == len(images)
        }
    )
