"""
Rendering Asset Validator.
Validates input media files, FFmpeg installation, scene timings, and resources before starting the render pipeline.
"""

import os
from typing import List, Optional
from app.services.rendering.models import ValidationResult, SceneInput, AudioInput
from app.services.rendering.ffmpeg import FFmpegEngine, FFmpegNotFoundError


class RenderValidatorService:
    @staticmethod
    def validate_render_environment() -> ValidationResult:
        """Validates that FFmpeg binary is accessible."""
        result = ValidationResult()
        try:
            version_str = FFmpegEngine.get_version()
            result.ffmpeg_version = version_str
            result.is_valid = True
        except FFmpegNotFoundError as e:
            result.is_valid = False
            result.errors.append(str(e))
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"FFmpeg validation failed: {str(e)}")

        return result

    @staticmethod
    def validate_scene_assets(scenes: List[SceneInput]) -> ValidationResult:
        """Validates images, narration, and timings for every scene."""
        result = RenderValidatorService.validate_render_environment()
        if not scenes:
            result.is_valid = False
            result.errors.append("No scenes provided for rendering.")
            return result

        for scene in scenes:
            # Check duration
            if scene.duration_seconds <= 0:
                result.errors.append(f"Scene {scene.scene_number} has invalid duration: {scene.duration_seconds}s")
                result.is_valid = False

            # Check image path (local file or HTTP URL to download)
            if scene.image_path:
                if not (scene.image_path.startswith("http://") or scene.image_path.startswith("https://")) and not os.path.exists(scene.image_path):
                    result.is_valid = False
                    result.errors.append(f"Scene {scene.scene_number} image asset missing at '{scene.image_path}'.")
            else:
                result.is_valid = False
                result.errors.append(f"Scene {scene.scene_number} has no image asset specified.")

            # Check narration path
            if scene.narration_path and not (scene.narration_path.startswith("http://") or scene.narration_path.startswith("https://")) and not os.path.exists(scene.narration_path):
                result.warnings.append(
                    f"Scene {scene.scene_number} narration file missing at '{scene.narration_path}'."
                )

        return result

    @staticmethod
    def validate_audio_assets(audio: AudioInput) -> ValidationResult:
        """Validates background music and voice audio tracks."""
        result = ValidationResult()
        if audio.music_path and not os.path.exists(audio.music_path):
            result.warnings.append(f"Background music file missing at '{audio.music_path}'. Render will proceed without music.")

        for path in audio.narration_paths:
            if not os.path.exists(path):
                result.warnings.append(f"Narration path '{path}' does not exist.")

        return result
