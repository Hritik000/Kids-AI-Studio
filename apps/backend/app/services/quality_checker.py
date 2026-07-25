from typing import Tuple, List
from app.models.project import Project, ProjectStatus

class QualityCheckerService:
    """
    Automated Quality Control Agent:
    Validates project outputs before status can transition to COMPLETED.
    """

    def verify_project_readiness(self, project: Project) -> Tuple[bool, List[str]]:
        errors = []

        if not project.title or not project.scenes:
            errors.append("Story script or title missing")

        if len(project.scenes) == 0:
            errors.append("No scenes found in project")

        for scene in project.scenes:
            if not scene.image_url:
                errors.append(f"Scene {scene.scene_number} missing visual image asset")
            if not scene.audio_url:
                errors.append(f"Scene {scene.scene_number} missing narration audio asset")

        if not project.final_video_url:
            errors.append("Final composite video export missing")

        is_passed = len(errors) == 0
        return is_passed, errors

quality_checker = QualityCheckerService()
