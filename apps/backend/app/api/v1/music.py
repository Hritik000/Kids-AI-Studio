from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from app.models.project import ProjectStatus, APIResponse, APIError
from app.models.music import MixedAudioTrack
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.api.v1.projects import projects_db
from app.api.v1.storyboard import storyboards_db
from app.api.v1.ai import plans_db
from app.services.music_service import MusicPipelineService, music_mixes_db

router = APIRouter()
music_service = MusicPipelineService()

@router.post("/projects/{project_id}/music/generate", response_model=APIResponse[List[MixedAudioTrack]])
async def generate_scene_music_mixes(
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
            error=APIError(code="STORYBOARD_NOT_FOUND", message="Please generate a storyboard first before generating music.")
        )

    production_plan = plans_db.get(project_id)

    try:
        mixes = await music_service.generate_all_scene_music_mixes(
            project_id=project_id,
            storyboard=storyboard,
            production_plan=production_plan
        )

        project = projects_db[project_id]
        project.status = ProjectStatus.MUSIC_READY
        projects_db[project_id] = project

        return APIResponse(success=True, data=mixes)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="MUSIC_GENERATION_FAILED", message=str(e))
        )

@router.post("/projects/{project_id}/music/regenerate-scene/{scene_number}", response_model=APIResponse[MixedAudioTrack])
async def regenerate_scene_music(
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

    try:
        new_mix = await music_service.regenerate_single_scene_music(
            project_id=project_id,
            scene_number=scene_number,
            storyboard=storyboard
        )
        return APIResponse(success=True, data=new_mix)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="REGENERATE_MUSIC_FAILED", message=str(e))
        )

@router.get("/projects/{project_id}/music", response_model=APIResponse[List[MixedAudioTrack]])
async def list_scene_music_mixes(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    mixes = music_mixes_db.get(project_id, [])
    return APIResponse(success=True, data=mixes)

@router.post("/projects/{project_id}/music/approve/{mix_id}", response_model=APIResponse[Dict[str, Any]])
async def approve_music_mix(
    project_id: str,
    mix_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    mixes = music_mixes_db.get(project_id, [])
    target = next((m for m in mixes if m.mix_id == mix_id), None)
    if not target:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Mixed audio track not found")
        )

    target.status = "APPROVED"
    return APIResponse(success=True, data={"message": f"Audio mix {mix_id} approved", "status": "APPROVED"})

@router.post("/projects/{project_id}/music/reject/{mix_id}", response_model=APIResponse[Dict[str, Any]])
async def reject_music_mix(
    project_id: str,
    mix_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    mixes = music_mixes_db.get(project_id, [])
    target = next((m for m in mixes if m.mix_id == mix_id), None)
    if not target:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Mixed audio track not found")
        )

    target.status = "REJECTED"
    return APIResponse(success=True, data={"message": f"Audio mix {mix_id} rejected", "status": "REJECTED"})

@router.get("/projects/{project_id}/music/status", response_model=APIResponse[Dict[str, Any]])
async def get_music_status(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    mixes = music_mixes_db.get(project_id, [])
    has_music = len(mixes) > 0
    approved_count = len([m for m in mixes if m.status == "APPROVED"])

    return APIResponse(
        success=True,
        data={
            "project_id": project_id,
            "has_music": has_music,
            "total_tracks": len(mixes),
            "approved_tracks": approved_count,
            "all_approved": has_music and approved_count == len(mixes)
        }
    )
