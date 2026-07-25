from typing import Dict, Any, List
from app.models.character import CharacterProfile
from app.core.llm import PromptLoader

class PromptComposerService:
    @staticmethod
    def compose_scene_prompt(
        scene_storyboard: Dict[str, Any],
        characters: List[CharacterProfile],
        visual_style: str = "3D Pixar Render"
    ) -> Dict[str, str]:
        visual_plan = scene_storyboard.get("visual_plan", {})
        camera_plan = scene_storyboard.get("camera_plan", {})
        char_refs = scene_storyboard.get("character_references", [])
        narration = scene_storyboard.get("narration_text", "")

        # 1. Environment & Lighting Context
        env = visual_plan.get("environment", "Lush Meadow")
        time_of_day = visual_plan.get("time_of_day", "Sunny Golden Hour")
        lighting = visual_plan.get("lighting_style", "Soft Warm Sunlight")
        bg = visual_plan.get("background", "Rolling green hills")
        fg = visual_plan.get("foreground", "Soft grass")
        palette = ", ".join(visual_plan.get("color_palette", ["Vibrant Colors"]))

        # 2. Camera Context
        shot_type = camera_plan.get("shot_type", "Medium Shot")
        angle = camera_plan.get("angle", "Eye Level")
        focal_point = camera_plan.get("focal_point", "Characters")

        # 3. Assemble Character Anchors
        char_anchor_strings = []
        for ref in char_refs:
            name = ref.get("character_name", "")
            expression = ref.get("expression", "Happy")
            pose = ref.get("pose", "Standing")
            
            # Match with Character Memory Profile if available
            matched_prof = next((p for p in characters if p.name.lower() in name.lower()), None)
            if matched_prof:
                anchor = f"{matched_prof.name} ({matched_prof.species}, {matched_prof.skin_color}, wearing {matched_prof.clothing}) with {expression} expression, {pose}"
            else:
                anchor = f"{name} with {expression} expression, {pose}"
            char_anchor_strings.append(anchor)

        characters_prompt_section = " and ".join(char_anchor_strings) if char_anchor_strings else "Friendly baby dinosaur"

        # 4. Compose Final Visual Prompt
        composed_positive = (
            f"A master high quality {visual_style} scene. {shot_type}, {angle} camera focusing on {focal_point}. "
            f"Characters present: {characters_prompt_section}. "
            f"Environment: {env} during {time_of_day} with {lighting}. "
            f"Background: {bg}. Foreground: {fg}. Master color palette: {palette}. "
            f"Atmosphere: Cheerful, child-safe, vibrant 8k digital art, Octane render quality."
        )

        negative_prompt = PromptLoader.load_prompt("negative.md").strip()

        return {
            "positive_prompt": composed_positive,
            "negative_prompt": negative_prompt
        }
