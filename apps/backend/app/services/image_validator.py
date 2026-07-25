from typing import Dict, Any, List

class ImageValidationError(Exception):
    pass

class ImageValidationService:
    @staticmethod
    def validate_image(image_data: Dict[str, Any]) -> List[str]:
        warnings = []
        required_keys = ["image_id", "project_id", "scene_number", "composed_prompt", "storage_url"]

        for key in required_keys:
            if key not in image_data or not image_data[key]:
                raise ImageValidationError(f"Generated image record missing field: '{key}'")

        if not image_data["storage_url"].startswith("http"):
            raise ImageValidationError(f"Invalid image storage URL format: '{image_data['storage_url']}'")

        width = image_data.get("width", 1280)
        height = image_data.get("height", 720)
        if width <= 0 or height <= 0:
            raise ImageValidationError("Image dimensions must be positive integers.")

        return warnings
