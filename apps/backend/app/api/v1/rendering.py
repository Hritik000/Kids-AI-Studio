from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.models.project import ProjectStatus, APIResponse, APIError
from app.models.rendering import VideoTimeline, RenderTask
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.api.v1.projects import projects_db
from app.api.v1.storyboard import storyboards_db
from app.api.v1.animations import animations_db
from app.api.v1.audio import audios_db
from app.api.v1.music import music_mixes_db
from app.services.timeline_builder import TimelineBuilderService
from app.services.ffmpeg_renderer import FFmpegRenderService, timelines_db, renders_db
from app.services.export_service import ExportService

router = APIRouter()

@router.post("/projects/{project_id}/timeline/build", response_model=APIResponse[VideoTimeline])
async def build_project_timeline(
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
            error=APIError(code="STORYBOARD_NOT_FOUND", message="Please generate a storyboard first before building video timeline.")
        )

    animations = [a.model_dump() for a in animations_db.get(project_id, [])]
    voices = [v.model_dump() for v in audios_db.get(project_id, [])]
    music_mixes = [m.model_dump() for m in music_mixes_db.get(project_id, [])]
    project = projects_db[project_id]

    timeline = TimelineBuilderService.build_timeline(
        project_id=project_id,
        storyboard=storyboard,
        animations=animations,
        voices=voices,
        music_mixes=music_mixes,
        aspect_ratio=project.aspect_ratio
    )

    timelines_db[project_id] = timeline
    return APIResponse(success=True, data=timeline)

@router.get("/projects/{project_id}/timeline", response_model=APIResponse[VideoTimeline])
async def get_project_timeline(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    timeline = timelines_db.get(project_id)
    if not timeline:
        return APIResponse(
            success=False,
            error=APIError(code="TIMELINE_NOT_FOUND", message="Timeline has not been built for this project yet.")
        )

    return APIResponse(success=True, data=timeline)

@router.post("/projects/{project_id}/render/generate", response_model=APIResponse[RenderTask])
async def render_project_video(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    timeline = timelines_db.get(project_id)
    if not timeline:
        # Build timeline automatically if not present
        storyboard = storyboards_db.get(project_id)
        if not storyboard:
            return APIResponse(
                success=False,
                error=APIError(code="STORYBOARD_NOT_FOUND", message="Storyboard required before rendering video.")
            )
        animations = [a.model_dump() for a in animations_db.get(project_id, [])]
        voices = [v.model_dump() for v in audios_db.get(project_id, [])]
        music_mixes = [m.model_dump() for m in music_mixes_db.get(project_id, [])]
        timeline = TimelineBuilderService.build_timeline(
            project_id=project_id,
            storyboard=storyboard,
            animations=animations,
            voices=voices,
            music_mixes=music_mixes
        )
        timelines_db[project_id] = timeline

    try:
        project = projects_db[project_id]
        project.status = ProjectStatus.RENDERING
        projects_db[project_id] = project

        render_task = await FFmpegRenderService.render_video(
            project_id=project_id,
            timeline=timeline,
            resolution="1080p",
            codec="H.264"
        )

        project.status = ProjectStatus.COMPLETED
        project.final_video_url = render_task.final_video_url
        projects_db[project_id] = project

        return APIResponse(success=True, data=render_task)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="RENDER_FAILED", message=str(e))
        )

@router.get("/projects/{project_id}/render", response_model=APIResponse[List[RenderTask]])
async def list_project_renders(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project_renders = renders_db.get(project_id, [])
    return APIResponse(success=True, data=project_renders)

@router.post("/projects/{project_id}/render/approve/{render_id}", response_model=APIResponse[Dict[str, Any]])
async def approve_render(
    project_id: str,
    render_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    renders = renders_db.get(project_id, [])
    target = next((r for r in renders if r.render_id == render_id), None)
    if not target:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Render task not found")
        )

    target.status = "APPROVED"
    return APIResponse(success=True, data={"message": f"Render task {render_id} approved", "status": "APPROVED"})

@router.post("/projects/{project_id}/render/reject/{render_id}", response_model=APIResponse[Dict[str, Any]])
async def reject_render(
    project_id: str,
    render_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    renders = renders_db.get(project_id, [])
    target = next((r for r in renders if r.render_id == render_id), None)
    if not target:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Render task not found")
        )

    target.status = "REJECTED"
    return APIResponse(success=True, data={"message": f"Render task {render_id} rejected", "status": "REJECTED"})

@router.get("/projects/{project_id}/render/export", response_model=APIResponse[Dict[str, Any]])
async def export_project_package(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    renders = renders_db.get(project_id, [])
    if not renders:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_RENDERED", message="Please render the project video first before exporting.")
        )

    latest_render = renders[-1]
    timeline = timelines_db.get(project_id) or VideoTimeline(timeline_id="tl_tmp", project_id=project_id, scenes=[])
    project_dict = projects_db[project_id].model_dump()

    export_pkg = ExportService.generate_project_export_package(
        project=project_dict,
        render_task=latest_render,
        timeline=timeline
    )

    return APIResponse(success=True, data=export_pkg)

@router.get("/projects/{project_id}/render/status", response_model=APIResponse[Dict[str, Any]])
async def get_render_status(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    renders = renders_db.get(project_id, [])
    has_render = len(renders) > 0
    latest = renders[-1] if has_render else None

    return APIResponse(
        success=True,
        data={
            "project_id": project_id,
            "has_render": has_render,
            "latest_status": latest.status if latest else "NOT_STARTED",
            "final_video_url": latest.final_video_url if latest else None
        }
    )
