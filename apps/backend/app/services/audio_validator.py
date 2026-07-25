from typing import Dict, Any, List

class AudioValidationError(Exception):
    pass

class AudioValidationService:
    @staticmethod
    def validate_audio(audio_data: Dict[str, Any]) -> List[str]:
        warnings = []
        required_keys = ["audio_id", "project_id", "scene_number", "storage_url", "dialogue_segments"]

        for key in required_keys:
            if key not in audio_data or not audio_data[key]:
                raise AudioValidationError(f"Generated audio record missing field: '{key}'")

        if not audio_data["storage_url"].startswith("http"):
            raise AudioValidationError(f"Invalid audio storage URL format: '{audio_data['storage_url']}'")

        duration = audio_data.get("duration_seconds", 0)
        if duration <= 0:
            raise AudioValidationError("Audio narration duration must be greater than 0 seconds.")

        return warnings
