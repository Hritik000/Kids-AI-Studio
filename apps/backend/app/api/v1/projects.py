import uuid
import time
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from app.models.project import (
    CreateProjectRequest,
    UpdateProjectRequest,
    Project,
    ProjectStatus,
    APIResponse,
    APIError,
    PaginatedProjects
)
from app.schemas.auth import UserProfile
from app.core.security import get_current_user

router = APIRouter()

# In-memory database repository for MVP & Phase 5 CRUD operations
projects_db: Dict[str, Project] = {}

# Seed initial demo projects for testing
demo_proj_1 = Project(
    id="proj_demo_colors",
    title="Dinosaurs Learn Colors",
    prompt="Dinosaurs learn colors at a birthday party in the sunny meadow",
    target_age_group="3-5",
    language="English (US)",
    video_length="Standard (2-3 min)",
    aspect_ratio="16:9",
    video_style="3D Pixar Render",
    voice="Storyteller Emma",
    status=ProjectStatus.COMPLETED,
    favorite=True,
    archived=False,
    owner_id="user_demo_123"
)

demo_proj_2 = Project(
    id="proj_demo_shapes",
    title="Little Astronauts Explore Shapes",
    prompt="Little astronauts find geometric shapes on Mars",
    target_age_group="3-5",
    language="English (US)",
    video_length="Short (30-60s)",
    aspect_ratio="9:16",
    video_style="2D Storybook",
    voice="Uncle Bob",
    status=ProjectStatus.DRAFT,
    favorite=False,
    archived=False,
    owner_id="user_demo_123"
)

projects_db[demo_proj_1.id] = demo_proj_1
projects_db[demo_proj_2.id] = demo_proj_2

@router.post("", response_model=APIResponse[Project])
async def create_project(
    payload: CreateProjectRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    try:
        project_id = f"proj_{uuid.uuid4().hex[:10]}"
        project = Project(
            id=project_id,
            title=payload.title,
            prompt=payload.prompt,
            target_age_group=payload.target_age_group,
            language=payload.language,
            video_length=payload.video_length,
            aspect_ratio=payload.aspect_ratio,
            video_style=payload.video_style,
            voice=payload.voice,
            status=ProjectStatus.DRAFT,
            owner_id=current_user.id
        )
        projects_db[project_id] = project
        return APIResponse(success=True, data=project)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="CREATE_FAILED", message=str(e))
        )

@router.get("", response_model=APIResponse[PaginatedProjects])
async def list_projects(
    q: Optional[str] = Query(None, description="Search query by title or prompt"),
    project_status: Optional[ProjectStatus] = Query(None, alias="status", description="Filter by project status"),
    is_favorite: Optional[bool] = Query(None, description="Filter by favorite status"),
    is_archived: Optional[bool] = Query(False, description="Filter archived projects"),
    sort: str = Query("newest", description="Sort by: newest, oldest, title, recently_opened"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: UserProfile = Depends(get_current_user)
):
    # Filter by user ownership
    user_projects = [p for p in projects_db.values() if p.owner_id == current_user.id or p.owner_id == "user_demo_123"]
    
    # Filter by archive status
    if is_archived is not None:
        user_projects = [p for p in user_projects if p.archived == is_archived]
        
    # Filter by favorite status
    if is_favorite is not None:
        user_projects = [p for p in user_projects if p.favorite == is_favorite]
        
    # Filter by status enum
    if project_status is not None:
        user_projects = [p for p in user_projects if p.status == project_status]

    # Search query matching title or prompt
    if q and q.strip():
        query_str = q.strip().lower()
        user_projects = [
            p for p in user_projects
            if query_str in p.title.lower() or query_str in p.prompt.lower()
        ]

    # Sorting logic
    if sort == "oldest":
        user_projects.sort(key=lambda p: p.created_at)
    elif sort == "title":
        user_projects.sort(key=lambda p: p.title.lower())
    elif sort == "recently_opened":
        user_projects.sort(key=lambda p: p.last_opened_at or p.updated_at, reverse=True)
    else:  # newest default
        user_projects.sort(key=lambda p: p.created_at, reverse=True)

    total = len(user_projects)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_items = user_projects[start_idx:end_idx]
    pages = (total + limit - 1) // limit if total > 0 else 1

    return APIResponse(
        success=True,
        data=PaginatedProjects(
            items=paginated_items,
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    )

@router.get("/{project_id}", response_model=APIResponse[Project])
async def get_project(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )
    
    project = projects_db[project_id]
    project.last_opened_at = datetime.now(timezone.utc).isoformat()
    projects_db[project_id] = project
    return APIResponse(success=True, data=project)

@router.put("/{project_id}", response_model=APIResponse[Project])
async def update_project(
    project_id: str,
    payload: UpdateProjectRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    update_data = payload.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(project, key, value)

    project.updated_at = datetime.now(timezone.utc).isoformat()
    projects_db[project_id] = project
    return APIResponse(success=True, data=project)

@router.delete("/{project_id}", response_model=APIResponse[dict])
async def delete_project(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    del projects_db[project_id]
    return APIResponse(success=True, data={"message": f"Project {project_id} deleted successfully"})

@router.post("/{project_id}/duplicate", response_model=APIResponse[Project])
async def duplicate_project(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    source = projects_db[project_id]
    new_id = f"proj_{uuid.uuid4().hex[:10]}"
    
    duplicated = Project(
        id=new_id,
        title=f"{source.title} (Copy)",
        description=source.description,
        prompt=source.prompt,
        target_age_group=source.target_age_group,
        language=source.language,
        video_length=source.video_length,
        aspect_ratio=source.aspect_ratio,
        video_style=source.video_style,
        voice=source.voice,
        status=ProjectStatus.DRAFT,
        tags=list(source.tags),
        favorite=False,
        archived=False,
        owner_id=current_user.id
    )
    
    projects_db[new_id] = duplicated
    return APIResponse(success=True, data=duplicated)

@router.post("/{project_id}/archive", response_model=APIResponse[Project])
async def archive_project(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    project.archived = True
    project.status = ProjectStatus.ARCHIVED
    project.updated_at = datetime.now(timezone.utc).isoformat()
    projects_db[project_id] = project
    return APIResponse(success=True, data=project)

@router.post("/{project_id}/restore", response_model=APIResponse[Project])
async def restore_project(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    project.archived = False
    project.status = ProjectStatus.DRAFT
    project.updated_at = datetime.now(timezone.utc).isoformat()
    projects_db[project_id] = project
    return APIResponse(success=True, data=project)

@router.post("/{project_id}/favorite", response_model=APIResponse[Project])
async def toggle_favorite(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    project.favorite = not project.favorite
    project.updated_at = datetime.now(timezone.utc).isoformat()
    projects_db[project_id] = project
    return APIResponse(success=True, data=project)
