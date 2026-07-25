from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class SubtitlePlaceholder(BaseModel):
    enabled: bool = True
    caption_style: str = "Animated Dynamic Highlight"
    font_family: str = "Inter Bold"
    font_color: str = "#FFFFFF"
    highlight_color: str = "#FFD700"
    position: str = "Bottom Center"

class TimelineSceneItem(BaseModel):
    scene_number: int
    duration_seconds: float = 5.0
    animation_url: str
    voice_url: Optional[str] = None
    music_mix_url: Optional[str] = None
    transition_type: str = "CrossFade"  # Cut | CrossFade | FadeToBlack | Dissolve | Zoom
    transition_duration_seconds: float = 0.5
    subtitle_placeholder: SubtitlePlaceholder = Field(default_factory=SubtitlePlaceholder)

class VideoTimeline(BaseModel):
    timeline_id: str
    project_id: str
    aspect_ratio: str = "16:9"
    resolution: str = "1080p"  # 1080p | 720p
    frame_rate: int = 24  # 24 | 30 | 60
    total_duration_seconds: float = 60.0
    scenes: List[TimelineSceneItem]
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class RenderTask(BaseModel):
    render_id: str
    project_id: str
    timeline_id: str
    status: str = "COMPLETED"  # PENDING | RENDERING | COMPLETED | APPROVED | REJECTED | FAILED
    resolution: str = "1080p"
    codec: str = "H.264"
    output_format: str = "MP4"
    file_size_bytes: int = 15420000
    preview_url: str
    final_video_url: str
    generation_time_seconds: float = 3.5
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
