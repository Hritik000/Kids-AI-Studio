import os
from typing import Dict, Any, List

class MusicValidationError(Exception):
    pass

class MusicValidationService:
    @staticmethod
    def validate_mixed_track(mix_data: Dict[str, Any]) -> List[str]:
        warnings = []
        required_keys = ["mix_id", "project_id", "scene_number", "storage_url", "music_plan"]

        for key in required_keys:
            if key not in mix_data or not mix_data[key]:
                raise MusicValidationError(f"Generated mixed audio track missing field: '{key}'")

        url_or_path = str(mix_data["storage_url"])
        if not (url_or_path.startswith("http://") or url_or_path.startswith("https://") or url_or_path.startswith("file://") or url_or_path.startswith("/tmp") or os.path.isabs(url_or_path)):
            raise MusicValidationError(f"Invalid mixed audio storage URL format: '{mix_data['storage_url']}'")

        duration = mix_data.get("duration_seconds", 0)
        if duration <= 0:
            raise MusicValidationError("Mixed audio track duration must be greater than 0 seconds.")

        loudness = mix_data.get("master_loudness_lufs", -14.0)
        if loudness > -6.0:
            warnings.append(f"High master loudness level detected: {loudness} LUFS (may cause clipping)")

        return warnings
