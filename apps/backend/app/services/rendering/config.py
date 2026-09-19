"""
Rendering Engine Configuration settings.
Centralizes all FFmpeg rendering, audio ducking, subtitle styling, camera motion,
and transition options. No hardcoded magic values in processing logic.
"""

from pydantic import BaseModel, Field


class VideoOutputConfig(BaseModel):
    width: int = 1920
    height: int = 1080
    fps: int = 30
    video_codec: str = "libx264"
    preset: str = "medium"
    crf: int = 23
    pixel_format: str = "yuv420p"
    aspect_ratio: str = "16:9"


class AudioOutputConfig(BaseModel):
    audio_codec: str = "aac"
    sample_rate: int = 44100
    channels: int = 2
    bitrate: str = "192k"
    music_ducking_db: float = -12.0  # Reduce music during narration by -12dB
    ducking_attack_ms: int = 100
    ducking_release_ms: int = 300
    target_lufs: float = -14.0  # Loudness normalization target (-14 LUFS)
    max_peak_db: float = -1.0
    music_fade_in_sec: float = 1.0
    music_fade_out_sec: float = 1.5


class SubtitleStyleConfig(BaseModel):
    font_name: str = "Inter"
    font_size: int = 24
    primary_color: str = "&H00FFFFFF"  # White (ASS format: &HAAABBBGGRR)
    outline_color: str = "&H00000000"  # Black outline
    back_color: str = "&H80000000"     # Semi-transparent shadow
    bold: bool = True
    italic: bool = False
    outline_width: float = 2.0
    shadow_depth: float = 1.0
    alignment: int = 2  # 2 = Bottom Center in ASS subtitle spec
    margin_v: int = 40  # Safe bottom margin in pixels
    margin_l: int = 40  # Safe left margin
    margin_r: int = 40  # Safe right margin


class CameraMotionConfig(BaseModel):
    default_zoom_ratio: float = 1.25
    pan_speed_multiplier: float = 1.0
    slow_dolly_scale: float = 1.15


class TransitionConfig(BaseModel):
    default_duration_sec: float = 0.5
    min_duration_sec: float = 0.1
    max_duration_sec: float = 2.0


class RenderingSettings(BaseModel):
    video: VideoOutputConfig = Field(default_factory=VideoOutputConfig)
    audio: AudioOutputConfig = Field(default_factory=AudioOutputConfig)
    subtitles: SubtitleStyleConfig = Field(default_factory=SubtitleStyleConfig)
    camera: CameraMotionConfig = Field(default_factory=CameraMotionConfig)
    transitions: TransitionConfig = Field(default_factory=TransitionConfig)
    timeout_seconds: int = 600
    max_threads: int = 4


# Default global settings instance
rendering_settings = RenderingSettings()
