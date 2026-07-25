from typing import Dict, Any, List
from app.models.animation import MotionPlan

class MotionPlannerService:
    @staticmethod
    def plan_motion_for_scene(
        scene_storyboard: Dict[str, Any],
        characters: List[Any]
    ) -> MotionPlan:
        camera_plan = scene_storyboard.get("camera_plan", {})
        visual_plan = scene_storyboard.get("visual_plan", {})
        char_refs = scene_storyboard.get("character_references", [])
        transition = scene_storyboard.get("transition", {})
        duration = float(scene_storyboard.get("estimated_duration", 5.0))

        # 1. Camera Motion Mapping
        camera_path = camera_plan.get("movement", "Slow Zoom In")
        if not camera_path or camera_path == "None":
            shot_type = camera_plan.get("shot_type", "Medium Shot")
            camera_path = "Pan Right" if "Wide" in shot_type else "Slow Zoom In"

        camera_speed = camera_plan.get("camera_speed", "Gentle")

        # 2. Character Motion Mapping
        char_motions = []
        for ref in char_refs:
            name = ref.get("character_name", "Hero")
            pose = ref.get("pose", "Standing")
            expr = ref.get("expression", "Happy")
            char_motions.append(f"{name} {pose.lower()} with {expr.lower()} expression and natural blinking")

        char_motion_str = ", ".join(char_motions) if char_motions else "Character breathing softly with joyful smile"

        # 3. Environment Motion Mapping
        weather = visual_plan.get("weather", "Clear")
        time_of_day = visual_plan.get("time_of_day", "Morning")
        env_motion = f"Soft breeze swaying background foliage during {time_of_day}, subtle moving clouds"

        return MotionPlan(
            motion_type=f"{camera_path} & {char_refs[0].get('pose', 'Idle') if char_refs else 'Idle'}",
            camera_path=camera_path,
            camera_speed=camera_speed,
            character_motion=char_motion_str,
            environment_motion=env_motion,
            duration_seconds=duration,
            frame_rate=24,
            transition_style=transition.get("type", "Cross Fade"),
            complexity="Medium"
        )
