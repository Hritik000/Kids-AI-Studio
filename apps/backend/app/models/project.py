from enum import Enum
from typing import List, Optional, Generic, TypeVar, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

T = TypeVar('T')

class ProjectStatus(str, Enum):
    DRAFT = "DRAFT"
    PLANNING = "PLANNING"
    STORY_READY = "STORY_READY"
    STORYBOARD_READY = "STORYBOARD_READY"
    IMAGES_READY = "IMAGES_READY"
    ANIMATION_READY = "ANIMATION_READY"
    VOICE_READY = "VOICE_READY"
    MUSIC_READY = "MUSIC_READY"
    RENDERING = "RENDERING"
    QUALITY_CHECK = "QUALITY_CHECK"
    COMPLETED = "COMPLETED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"

class Scene(BaseModel):
    scene_number: int
    narration_text: str
    visual_prompt: str
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    duration_seconds: float = 3.0

class CreateProjectRequest(BaseModel):
    title: str = Field(..., min_length=2, description="Project Name")
    prompt: str = Field(..., min_length=3, description="Video topic or prompt")
    target_age_group: str = Field(default="3-5")
    language: str = Field(default="English (US)")
    video_length: str = Field(default="Standard (2-3 min)")
    aspect_ratio: str = Field(default="16:9")
    video_style: str = Field(default="3D Pixar Render")
    voice: str = Field(default="Storyteller Emma")
    save_as_draft: bool = Field(default=True)

class UpdateProjectRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    target_age_group: Optional[str] = None
    language: Optional[str] = None
    video_length: Optional[str] = None
    aspect_ratio: Optional[str] = None
    video_style: Optional[str] = None
    voice: Optional[str] = None
    status: Optional[ProjectStatus] = None
    tags: Optional[List[str]] = None
    favorite: Optional[bool] = None
    archived: Optional[bool] = None

class ProjectMetrics(BaseModel):
    generation_time_seconds: float = 0.0
    model_used: str = "KidsAI-Director-v2.0"
    tokens_used: int = 0
    image_count: int = 0
    video_duration_seconds: float = 0.0
    render_time_seconds: float = 0.0
    estimated_cost_usd: float = 0.0

class Project(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    prompt: str
    target_age_group: str = "3-5"
    language: str = "English (US)"
    video_length: str = "Standard (2-3 min)"
    aspect_ratio: str = "16:9"
    video_style: str = "3D Pixar Render"
    voice: str = "Storyteller Emma"
    status: ProjectStatus = ProjectStatus.DRAFT
    thumbnail_url: Optional[str] = "https://placehold.co/1280x720/1A1D27/FFFFFF/png?text=KidsAI+Studio"
    tags: List[str] = []
    scenes: List[Scene] = []
    final_video_url: Optional[str] = None
    metrics: ProjectMetrics = Field(default_factory=ProjectMetrics)
    favorite: bool = False
    archived: bool = False
    owner_id: str = "user_demo_123"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_opened_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class APIError(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[APIError] = None

class PaginatedProjects(BaseModel):
    items: List[Project]
    total: int
    page: int
    limit: int
    pages: int
