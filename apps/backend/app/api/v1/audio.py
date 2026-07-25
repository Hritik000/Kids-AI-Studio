from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from app.models.project import ProjectStatus, APIResponse, APIError
from app.models.audio import VoiceNarrationAsset
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.api.v1.projects import projects_db
from app.api.v1.storyboard import storyboards_db
from app.services.voice_service import VoicePipelineService, audios_db

router = APIRouter()
voice_service = VoicePipelineService()

@router.post("/projects/{project_id}/audio/generate-voices", response_model=APIResponse[List[VoiceNarrationAsset]])
async def generate_scene_voices(
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
            error=APIError(code="STORYBOARD_NOT_FOUND", message="Please generate a storyboard first before generating voice narration.")
        )

    project = projects_db[project_id]
    voice_name = project.voice or "Storyteller Emma"
    language = project.language or "English (US)"

    try:
        audio_clips = await voice_service.generate_all_scene_voices(
            project_id=project_id,
            storyboard=storyboard,
            voice_name=voice_name,
            language=language
        )

        project.status = ProjectStatus.VOICE_READY
        projects_db[project_id] = project

        return APIResponse(success=True, data=audio_clips)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="VOICE_GENERATION_FAILED", message=str(e))
        )

@router.post("/projects/{project_id}/audio/regenerate-scene/{scene_number}", response_model=APIResponse[VoiceNarrationAsset])
async def regenerate_scene_voice(
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
    project = projects_db[project_id]

    try:
        new_audio = await voice_service.regenerate_single_scene_voice(
            project_id=project_id,
            scene_number=scene_number,
            storyboard=storyboard,
            voice_name=project.voice or "Storyteller Emma",
            language=project.language or "English (US)"
        )
        return APIResponse(success=True, data=new_audio)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="REGENERATE_VOICE_FAILED", message=str(e))
        )

@router.get("/projects/{project_id}/audio", response_model=APIResponse[List[VoiceNarrationAsset]])
async def list_scene_voices(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    audios = audios_db.get(project_id, [])
    return APIResponse(success=True, data=audios)

@router.post("/projects/{project_id}/audio/approve/{audio_id}", response_model=APIResponse[Dict[str, Any]])
async def approve_audio(
    project_id: str,
    audio_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    audios = audios_db.get(project_id, [])
    target = next((a for a in audios if a.audio_id == audio_id), None)
    if not target:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Audio narration clip not found")
        )

    target.status = "APPROVED"
    return APIResponse(success=True, data={"message": f"Audio clip {audio_id} approved", "status": "APPROVED"})

@router.post("/projects/{project_id}/audio/reject/{audio_id}", response_model=APIResponse[Dict[str, Any]])
async def reject_audio(
    project_id: str,
    audio_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    audios = audios_db.get(project_id, [])
    target = next((a for a in audios if a.audio_id == audio_id), None)
    if not target:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Audio narration clip not found")
        )

    target.status = "REJECTED"
    return APIResponse(success=True, data={"message": f"Audio clip {audio_id} rejected", "status": "REJECTED"})

@router.get("/projects/{project_id}/audio/status", response_model=APIResponse[Dict[str, Any]])
async def get_audio_status(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    audios = audios_db.get(project_id, [])
    has_audio = len(audios) > 0
    approved_count = len([a for a in audios if a.status == "APPROVED"])

    return APIResponse(
        success=True,
        data={
            "project_id": project_id,
            "has_audio": has_audio,
            "total_clips": len(audios),
            "approved_clips": approved_count,
            "all_approved": has_audio and approved_count == len(audios)
        }
    )
