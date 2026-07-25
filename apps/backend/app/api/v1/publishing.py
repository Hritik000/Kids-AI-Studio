from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.models.project import ProjectStatus, APIResponse, APIError
from app.models.publishing import PublishingAssetBundle, ThumbnailVariant, SEOPackage
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.api.v1.projects import projects_db
from app.api.v1.storyboard import storyboards_db
from app.api.v1.ai import stories_db
from app.services.publishing_service import PublishingPipelineService, publishing_bundles_db

router = APIRouter()

@router.post("/projects/{project_id}/publishing/generate", response_model=APIResponse[PublishingAssetBundle])
async def generate_publishing_assets(
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
            error=APIError(code="STORYBOARD_NOT_FOUND", message="Please generate a storyboard first before generating publishing assets.")
        )

    project = projects_db[project_id]
    story_script = stories_db.get(project_id)

    try:
        bundle = PublishingPipelineService.generate_publishing_assets(
            project_id=project_id,
            project_title=project.title,
            prompt=project.prompt,
            storyboard=storyboard,
            story_script=story_script
        )

        project.status = ProjectStatus.PUBLISHED
        if bundle.thumbnails:
            project.thumbnail_url = bundle.thumbnails[0].storage_url
        projects_db[project_id] = project

        return APIResponse(success=True, data=bundle)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="PUBLISHING_GENERATION_FAILED", message=str(e))
        )

@router.get("/projects/{project_id}/publishing", response_model=APIResponse[PublishingAssetBundle])
async def get_publishing_assets(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    bundle = publishing_bundles_db.get(project_id)
    if not bundle:
        return APIResponse(
            success=False,
            error=APIError(code="BUNDLE_NOT_FOUND", message="Publishing assets have not been generated for this project yet.")
        )

    return APIResponse(success=True, data=bundle)

@router.post("/projects/{project_id}/publishing/select-thumbnail/{variant_id}", response_model=APIResponse[ThumbnailVariant])
async def select_thumbnail_variant(
    project_id: str,
    variant_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    try:
        variant = PublishingPipelineService.select_thumbnail_variant(project_id, variant_id)
        project = projects_db[project_id]
        project.thumbnail_url = variant.storage_url
        projects_db[project_id] = project
        return APIResponse(success=True, data=variant)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="SELECT_THUMBNAIL_FAILED", message=str(e))
        )

@router.post("/projects/{project_id}/publishing/approve", response_model=APIResponse[Dict[str, Any]])
async def approve_publishing_assets(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    bundle = publishing_bundles_db.get(project_id)
    if not bundle:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Publishing asset bundle not found")
        )

    bundle.status = "APPROVED"
    publishing_bundles_db[project_id] = bundle
    return APIResponse(success=True, data={"message": "Publishing assets approved", "status": "APPROVED"})

@router.post("/projects/{project_id}/publishing/reject", response_model=APIResponse[Dict[str, Any]])
async def reject_publishing_assets(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    bundle = publishing_bundles_db.get(project_id)
    if not bundle:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Publishing asset bundle not found")
        )

    bundle.status = "REJECTED"
    publishing_bundles_db[project_id] = bundle
    return APIResponse(success=True, data={"message": "Publishing assets rejected", "status": "REJECTED"})

@router.get("/projects/{project_id}/publishing/status", response_model=APIResponse[Dict[str, Any]])
async def get_publishing_status(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    bundle = publishing_bundles_db.get(project_id)
    has_bundle = bundle is not None

    return APIResponse(
        success=True,
        data={
            "project_id": project_id,
            "has_publishing_assets": has_bundle,
            "thumbnail_variants_count": len(bundle.thumbnails) if bundle else 0,
            "status": bundle.status if bundle else "NOT_STARTED"
        }
    )
