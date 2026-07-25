from typing import Dict, Any, List, Optional

class StoryboardValidationError(Exception):
    pass

class StoryboardValidationService:
    VALID_SHOT_TYPES = ["Wide Shot", "Medium Shot", "Close Up", "Extreme Close Up", "Overhead", "Low Angle", "High Angle"]
    VALID_TRANSITIONS = ["Cut", "Fade", "Cross Fade", "Slide", "Zoom", "Whip", "Match Cut", "Hold Frame"]

    @staticmethod
    def validate_storyboard(storyboard: Dict[str, Any], expected_scene_count: Optional[int] = None) -> List[str]:
        warnings = []

        required_root = ["project_id", "story_title", "total_scenes", "scenes"]
        for key in required_root:
            if key not in storyboard or storyboard[key] is None:
                raise StoryboardValidationError(f"Storyboard JSON missing root field: '{key}'")

        scenes = storyboard.get("scenes", [])
        if len(scenes) == 0:
            raise StoryboardValidationError("Storyboard contains zero scenes.")

        if expected_scene_count and len(scenes) != expected_scene_count:
            warnings.append(f"Storyboard scene count ({len(scenes)}) differs from story scene count ({expected_scene_count}).")

        # Track character appearances across scenes for Continuity Audit
        character_appearances = {}

        for i, scene in enumerate(scenes, 1):
            # Check Scene Metadata
            if "visual_plan" not in scene:
                raise StoryboardValidationError(f"Scene #{i} is missing 'visual_plan'.")
            if "camera_plan" not in scene:
                raise StoryboardValidationError(f"Scene #{i} is missing 'camera_plan'.")
            if "transition" not in scene:
                raise StoryboardValidationError(f"Scene #{i} is missing 'transition'.")

            # Check Camera Shot Type
            camera = scene["camera_plan"]
            shot_type = camera.get("shot_type", "Medium Shot")
            if shot_type not in StoryboardValidationService.VALID_SHOT_TYPES:
                warnings.append(f"Scene #{i} camera shot_type '{shot_type}' is unconventional.")

            # Check Transition Type
            trans = scene["transition"]
            trans_type = trans.get("type", "Cross Fade")
            if trans_type not in StoryboardValidationService.VALID_TRANSITIONS:
                warnings.append(f"Scene #{i} transition type '{trans_type}' is unconventional.")

            # Continuity Audit: Track character references
            refs = scene.get("character_references", [])
            for ref in refs:
                name = ref.get("character_name")
                if name:
                    if name not in character_appearances:
                        character_appearances[name] = []
                    character_appearances[name].append(i)

        if len(character_appearances) == 0:
            warnings.append("No character references were placed across the storyboard scenes.")

        return warnings
