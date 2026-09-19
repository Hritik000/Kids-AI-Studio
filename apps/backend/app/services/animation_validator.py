from typing import Dict, Any, List

import os

class AnimationValidationError(Exception):
    pass

class AnimationValidationService:
    @staticmethod
    def validate_animation(clip_data: Dict[str, Any]) -> List[str]:
        warnings = []
        required_keys = ["animation_id", "project_id", "scene_number", "composed_motion_prompt", "storage_url"]

        for key in required_keys:
            if key not in clip_data or not clip_data[key]:
                raise AnimationValidationError(f"Generated animation record missing field: '{key}'")

        url_or_path = str(clip_data["storage_url"])
        if not (url_or_path.startswith("http://") or url_or_path.startswith("https://") or url_or_path.startswith("file://") or url_or_path.startswith("/tmp") or os.path.isabs(url_or_path)):
            raise AnimationValidationError(f"Invalid video storage URL format: '{clip_data['storage_url']}'")

        duration = clip_data.get("duration_seconds", 0)
        if duration <= 0:
            raise AnimationValidationError("Animation clip duration must be greater than 0 seconds.")

        frame_rate = clip_data.get("frame_rate", 24)
        if frame_rate not in [24, 30, 60]:
            warnings.append(f"Non-standard frame rate detected: {frame_rate}fps (standard is 24fps)")

        return warnings
