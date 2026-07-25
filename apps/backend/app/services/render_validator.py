from typing import Dict, Any

class RenderValidationError(Exception):
    pass

class RenderValidationService:
    @staticmethod
    def validate_render_task(task_data: Dict[str, Any]) -> None:
        required = ["render_id", "project_id", "timeline_id", "final_video_url", "preview_url"]
        for key in required:
            if key not in task_data or not task_data[key]:
                raise RenderValidationError(f"Render task missing required field: '{key}'")

        if not task_data["final_video_url"].startswith("http"):
            raise RenderValidationError(f"Invalid final video storage URL format: '{task_data['final_video_url']}'")

        if task_data.get("file_size_bytes", 0) <= 0:
            raise RenderValidationError("Rendered video file size must be greater than 0 bytes.")
