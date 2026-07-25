from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from app.models.project import Project, ProjectStatus, APIResponse, APIError, Scene
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.api.v1.projects import projects_db
from app.services.director import DirectorAgentService
from app.services.story import StoryAgentService

router = APIRouter()

# In-memory caches/storage for Phase 6 Production Plans & Story Scripts
plans_db: Dict[str, Dict[str, Any]] = {}
stories_db: Dict[str, Dict[str, Any]] = {}

director_service = DirectorAgentService()
story_service = StoryAgentService()

@router.post("/projects/{project_id}/generate-plan", response_model=APIResponse[Dict[str, Any]])
async def generate_production_plan(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    
    try:
        plan = await director_service.generate_production_plan(
            project_id=project.id,
            topic=project.prompt,
            target_age_group=project.target_age_group,
            language=project.language,
            video_length=project.video_length,
            aspect_ratio=project.aspect_ratio,
            video_style=project.video_style
        )
        
        # Save to storage and update project status
        plans_db[project_id] = plan
        project.status = ProjectStatus.PLANNING
        projects_db[project_id] = project

        return APIResponse(success=True, data=plan)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="PLAN_GENERATION_FAILED", message=str(e))
        )

@router.post("/projects/{project_id}/generate-story", response_model=APIResponse[Dict[str, Any]])
async def generate_story(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    
    # Check if Production Plan exists; if not, generate it first via Director Agent
    plan = plans_db.get(project_id)
    if not plan:
        plan = await director_service.generate_production_plan(
            project_id=project.id,
            topic=project.prompt,
            target_age_group=project.target_age_group,
            language=project.language,
            video_length=project.video_length,
            aspect_ratio=project.aspect_ratio,
            video_style=project.video_style
        )
        plans_db[project_id] = plan

    try:
        story = await story_service.generate_story_script(production_plan=plan)
        
        # Save to storage
        stories_db[project_id] = story
        
        # Map scenes to Project model
        mapped_scenes = []
        for s in story.get("scenes", []):
            mapped_scenes.append(
                Scene(
                    scene_number=s.get("scene_number", 1),
                    narration_text=s.get("narration_text", ""),
                    visual_prompt=s.get("visual_description", ""),
                    duration_seconds=s.get("estimated_duration", 3.0)
                )
            )
        
        project.title = story.get("story_title", project.title)
        project.description = story.get("story_summary", project.description)
        project.scenes = mapped_scenes
        project.status = ProjectStatus.STORY_READY
        projects_db[project_id] = project

        return APIResponse(success=True, data=story)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="STORY_GENERATION_FAILED", message=str(e))
        )

@router.get("/projects/{project_id}/plan", response_model=APIResponse[Dict[str, Any]])
async def get_production_plan(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    plan = plans_db.get(project_id)
    if not plan:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Production plan has not been generated yet")
        )

    return APIResponse(success=True, data=plan)

@router.get("/projects/{project_id}/story", response_model=APIResponse[Dict[str, Any]])
async def get_story_script(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    story = stories_db.get(project_id)
    if not story:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Story script has not been generated yet")
        )

    return APIResponse(success=True, data=story)

@router.post("/projects/{project_id}/regenerate-story", response_model=APIResponse[Dict[str, Any]])
async def regenerate_story(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    return await generate_story(project_id=project_id, current_user=current_user)

@router.get("/projects/{project_id}/pipeline-status", response_model=APIResponse[Dict[str, Any]])
async def get_pipeline_status(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    has_plan = project_id in plans_db
    has_story = project_id in stories_db

    return APIResponse(
        success=True,
        data={
            "project_id": project.id,
            "status": project.status,
            "has_production_plan": has_plan,
            "has_story_script": has_story,
            "current_step": 3 if has_story else 2 if has_plan else 1,
            "total_steps": 10
        }
    )
