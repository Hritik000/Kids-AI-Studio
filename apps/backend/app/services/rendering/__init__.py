"""
Industry-Grade FFmpeg Rendering Engine Package.
"""

from app.services.rendering.config import rendering_settings, RenderingSettings
from app.services.rendering.models import (
    SceneInput, CameraDirection, TransitionType, AudioInput, SubtitleItem,
    RenderJobInput, RenderTaskResult, ValidationResult
)
from app.services.rendering.ffmpeg import FFmpegEngine, FFmpegExecutionError, FFmpegNotFoundError
from app.services.rendering.validator import RenderValidatorService
from app.services.rendering.camera import CameraEngine
from app.services.rendering.transitions import TransitionEngine
from app.services.rendering.subtitles import SubtitleEngine
from app.services.rendering.audio import AudioEngine
from app.services.rendering.thumbnail import ThumbnailEngine
from app.services.rendering.timeline import TimelineEngine
from app.services.rendering.downloader import (
    MediaDownloader, DownloaderError, DownloadSizeExceededError, PathTraversalError
)
from app.services.rendering.renderer import FFmpegRenderer

__all__ = [
    "rendering_settings",
    "RenderingSettings",
    "SceneInput",
    "CameraDirection",
    "TransitionType",
    "AudioInput",
    "SubtitleItem",
    "RenderJobInput",
    "RenderTaskResult",
    "ValidationResult",
    "FFmpegEngine",
    "FFmpegExecutionError",
    "FFmpegNotFoundError",
    "RenderValidatorService",
    "CameraEngine",
    "TransitionEngine",
    "SubtitleEngine",
    "AudioEngine",
    "ThumbnailEngine",
    "TimelineEngine",
    "FFmpegRenderer",
    "MediaDownloader",
    "DownloaderError",
    "DownloadSizeExceededError",
    "PathTraversalError",
]
