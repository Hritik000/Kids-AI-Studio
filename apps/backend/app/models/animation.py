from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class MotionPlan(BaseModel):
    motion_type: str = "3D Camera Pan & Character Walk"
    camera_path: str = "Slow Zoom In"
    camera_speed: str = "Gentle"
    character_motion: str = "Walking with cheerful wave"
    environment_motion: str = "Moving clouds & swaying grass"
    duration_seconds: float = 5.0
    frame_rate: int = 24
    speed: str = "Normal"
    transition_style: str = "Cross Fade"
    complexity: str = "Medium"

class AnimatedSceneClip(BaseModel):
    animation_id: str
    project_id: str
    scene_number: int
    motion_plan: MotionPlan
    composed_motion_prompt: str
    provider: str = "Wan2.2-i2v"
    seed: int = 42
    width: int = 1280
    height: int = 720
    aspect_ratio: str = "16:9"
    duration_seconds: float = 5.0
    frame_rate: int = 24
    generation_time_seconds: float = 4.2
    status: str = "GENERATED"  # GENERATED | APPROVED | REJECTED
    storage_url: str
    thumbnail_url: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
