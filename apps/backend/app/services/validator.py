from typing import Dict, Any, List, Optional

class QualityValidationError(Exception):
    pass

class ValidationService:
    FORBIDDEN_KEYWORDS = [
        "scary", "monster", "kill", "die", "death", "blood", "fight", "weapon", "gun", "knife", "ghost", "nightmare", "evil"
    ]

    @staticmethod
    def validate_production_plan(plan: Dict[str, Any]) -> List[str]:
        warnings = []
        required_keys = [
            "topic", "educational_objective", "target_age_group",
            "estimated_duration_seconds", "scene_count", "narration_style",
            "visual_style", "character_requirements", "music_mood_plan"
        ]

        for key in required_keys:
            if key not in plan or plan[key] is None:
                raise QualityValidationError(f"Production plan missing required field: {key}")

        if not (2 <= plan["scene_count"] <= 10):
            raise QualityValidationError(f"Scene count {plan['scene_count']} out of recommended bounds (2-10 scenes)")

        if not isinstance(plan.get("character_requirements"), list) or len(plan["character_requirements"]) == 0:
            warnings.append("Production plan has no character requirements defined.")

        return warnings

    @staticmethod
    def validate_story_script(story: Dict[str, Any], expected_scene_count: Optional[int] = None) -> List[str]:
        warnings = []
        required_keys = ["story_title", "story_summary", "educational_goal", "characters", "scenes"]

        for key in required_keys:
            if key not in story or story[key] is None:
                raise QualityValidationError(f"Story script missing required field: {key}")

        scenes = story.get("scenes", [])
        if len(scenes) == 0:
            raise QualityValidationError("Story contains zero scenes.")

        if expected_scene_count and len(scenes) != expected_scene_count:
            warnings.append(f"Story generated {len(scenes)} scenes, expected {expected_scene_count} from production plan.")

        # Safety & Child-Friendly Content Audit
        full_text = f"{story.get('story_title', '')} {story.get('story_summary', '')} " + " ".join(
            [s.get("narration_text", "") + " " + s.get("visual_description", "") for s in scenes]
        )

        full_text_lower = full_text.lower()
        for forbidden in ValidationService.FORBIDDEN_KEYWORDS:
            if forbidden in full_text_lower:
                raise QualityValidationError(f"Child safety audit failed: forbidden word '{forbidden}' detected in story output.")

        # Validate Scene Structure
        for i, scene in enumerate(scenes, 1):
            if "narration_text" not in scene or not scene["narration_text"].strip():
                raise QualityValidationError(f"Scene #{i} is missing narration text.")
            if "visual_description" not in scene or not scene["visual_description"].strip():
                raise QualityValidationError(f"Scene #{i} is missing visual description.")

        return warnings
