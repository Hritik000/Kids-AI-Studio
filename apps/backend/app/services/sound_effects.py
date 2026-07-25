import uuid
from typing import Dict, Any, List
from app.models.music import SoundEffectItem

class SoundEffectService:
    @staticmethod
    def generate_sound_effects_for_scene(scene: Dict[str, Any], scene_number: int) -> List[SoundEffectItem]:
        sfx_list: List[SoundEffectItem] = []
        char_refs = scene.get("character_references", [])

        for idx, ref in enumerate(char_refs, 1):
            pose = ref.get("pose", "").lower()
            if "walk" in pose or "run" in pose:
                sfx_list.append(SoundEffectItem(
                    sfx_id=f"sfx_{scene_number}_{idx}_footsteps",
                    name="Soft Dino Footsteps",
                    category="Footsteps",
                    timestamp_seconds=0.8,
                    volume_level=0.4
                ))
            elif "jump" in pose:
                sfx_list.append(SoundEffectItem(
                    sfx_id=f"sfx_{scene_number}_{idx}_jump",
                    name="Boing Spring Jump",
                    category="Jump",
                    timestamp_seconds=1.2,
                    volume_level=0.5
                ))

        if not sfx_list:
            sfx_list.append(SoundEffectItem(
                sfx_id=f"sfx_{scene_number}_sparkle",
                name="Magical Sparkle Chime",
                category="Sparkle",
                timestamp_seconds=0.5,
                volume_level=0.3
            ))

        return sfx_list
