import uuid
from typing import Dict, Any
from app.models.music import AmbientAudioPlan

class AmbientAudioService:
    @staticmethod
    def generate_ambient_plan_for_scene(scene: Dict[str, Any]) -> AmbientAudioPlan:
        visual_plan = scene.get("visual_plan", {})
        env = visual_plan.get("environment", "Sunny Meadow")

        return AmbientAudioPlan(
            ambient_id=f"amb_{uuid.uuid4().hex[:6]}",
            environment_type=env,
            volume_level=0.15
        )
