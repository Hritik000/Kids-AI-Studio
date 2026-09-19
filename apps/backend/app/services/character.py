import uuid
from typing import List, Dict, Any, Optional
from app.models.character import CharacterProfile
from app.core.llm import PromptLoader

# In-memory repository for Character Profiles
characters_db: Dict[str, List[CharacterProfile]] = {}

class CharacterEngineService:
    @staticmethod
    def generate_character_profiles(
        project_id: str,
        story_script: Dict[str, Any],
        production_plan: Optional[Dict[str, Any]] = None
    ) -> List[CharacterProfile]:
        raw_chars = story_script.get("characters", [])
        if not raw_chars and production_plan:
            raw_chars = production_plan.get("character_requirements", [])

        profiles: List[CharacterProfile] = []
        visual_style = production_plan.get("visual_style", "3D Pixar Render") if production_plan else "3D Pixar Render"

        for idx, char_data in enumerate(raw_chars, 1):
            name = char_data.get("name", f"Character_{idx}")
            species = char_data.get("species_or_type", char_data.get("role", "Dinosaur"))
            visual_features = char_data.get("visual_features", char_data.get("description", "Friendly soft scales with bright cheerful eyes"))
            personality = char_data.get("personality", "Curious and playful")

            char_id = f"char_{project_id}_{idx}"
            
            # Construct permanent reference prompt anchor
            ref_prompt = PromptLoader.load_prompt("character.md", {
                "name": name,
                "species": species,
                "visual_features": visual_features,
                "clothing": "custom child-friendly explorer gear",
                "primary_colors": "Vibrant Pixar color palette",
                "visual_style": visual_style
            })

            ref_image_url = f"https://placehold.co/512x512/1A1D27/FFFFFF/png?text=Character+{name}"

            profile = CharacterProfile(
                character_id=char_id,
                project_id=project_id,
                name=name,
                species=species,
                personality=personality,
                role="Hero" if idx == 1 else "Sidekick",
                skin_color=visual_features,
                reference_prompt=ref_prompt,
                reference_image_url=ref_image_url,
                visual_style=visual_style
            )
            profiles.append(profile)

        characters_db[project_id] = profiles
        return profiles

    @staticmethod
    def extract_and_generate_profiles(
        project_id: str,
        story_script: Dict[str, Any],
        video_style: str = "3D Pixar Render"
    ) -> List[CharacterProfile]:
        return CharacterEngineService.generate_character_profiles(
            project_id=project_id,
            story_script=story_script,
            production_plan={"visual_style": video_style}
        )

    @staticmethod
    def get_project_characters(project_id: str) -> List[CharacterProfile]:
        return characters_db.get(project_id, [])

    @staticmethod
    def update_character_profile(project_id: str, char_id: str, payload: Dict[str, Any]) -> Optional[CharacterProfile]:
        profiles = characters_db.get(project_id, [])
        for p in profiles:
            if p.character_id == char_id:
                for k, v in payload.items():
                    if hasattr(p, k):
                        setattr(p, k, v)
                return p
        return None
