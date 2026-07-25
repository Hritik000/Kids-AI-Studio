from typing import Dict, Any, Optional
from app.models.rendering import RenderTask, VideoTimeline

class ExportService:
    @staticmethod
    def generate_project_export_package(
        project: Dict[str, Any],
        render_task: RenderTask,
        timeline: VideoTimeline
    ) -> Dict[str, Any]:
        return {
            "project_id": project.get("id"),
            "project_title": project.get("title"),
            "export_version": "2.0.0",
            "video_url": render_task.final_video_url,
            "preview_url": render_task.preview_url,
            "resolution": render_task.resolution,
            "codec": render_task.codec,
            "output_format": render_task.output_format,
            "file_size_bytes": render_task.file_size_bytes,
            "timeline": timeline.model_dump(),
            "export_files": [
                {"name": f"{project.get('title')}.mp4", "url": render_task.final_video_url, "type": "VIDEO_MP4"},
                {"name": "timeline.json", "url": f"https://api.kidsaistudio.com/export/{project.get('id')}/timeline.json", "type": "JSON"}
            ]
        }
