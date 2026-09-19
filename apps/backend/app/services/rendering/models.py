"""
Data models for the FFmpeg Rendering Engine.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class CameraDirection(str, Enum):
    ZOOM_IN = "Zoom In"
    ZOOM_OUT = "Zoom Out"
    PAN_LEFT = "Pan Left"
    PAN_RIGHT = "Pan Right"
    PAN_UP = "Pan Up"
    PAN_DOWN = "Pan Down"
    SLOW_DOLLY = "Slow Dolly"
    STATIC = "Static"


class TransitionType(str, Enum):
    FADE = "Fade"
    CROSSFADE = "Crossfade"
    SLIDE_LEFT = "Slide Left"
    SLIDE_RIGHT = "Slide Right"
    ZOOM = "Zoom"
    DISSOLVE = "Dissolve"
    CUT = "Cut"


class SubtitleItem(BaseModel):
    index: int
    start_time_sec: float
    end_time_sec: float
    text: str


class SceneInput(BaseModel):
    scene_number: int
    image_path: Optional[str] = None
    duration_seconds: float = 5.0
    camera_direction: CameraDirection = CameraDirection.STATIC
    camera_zoom: float = 1.2
    transition: TransitionType = TransitionType.CROSSFADE
    transition_duration_seconds: float = 0.5
    narration_path: Optional[str] = None
    subtitles: List[SubtitleItem] = Field(default_factory=list)


class AudioInput(BaseModel):
    narration_paths: List[str] = Field(default_factory=list)
    music_path: Optional[str] = None
    music_volume: float = 1.0
    narration_volume: float = 1.0


class RenderJobInput(BaseModel):
    project_id: str
    timeline_id: str
    scenes: List[SceneInput]
    music_path: Optional[str] = None
    subtitles_path: Optional[str] = None
    output_dir: str
    resolution: str = "1080p"
    codec: str = "H.264"


class RenderTaskResult(BaseModel):
    render_id: str
    project_id: str
    timeline_id: str
    status: str = "COMPLETED"  # PENDING | RENDERING | COMPLETED | FAILED
    resolution: str = "1080p"
    codec: str = "H.264"
    output_format: str = "MP4"
    file_size_bytes: int = 0
    final_video_path: str = ""
    final_video_url: str = ""
    thumbnail_path: str = ""
    thumbnail_url: str = ""
    generation_time_seconds: float = 0.0
    logs: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ValidationResult(BaseModel):
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    ffmpeg_version: Optional[str] = None
