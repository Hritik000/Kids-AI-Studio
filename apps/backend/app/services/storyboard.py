import json
from typing import Dict, Any, Optional
from app.core.llm import get_llm_provider, PromptLoader, LLMProvider
from app.services.storyboard_validator import StoryboardValidationService, StoryboardValidationError

class StoryboardAgentService:
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    async def generate_storyboard(
        self,
        project_id: str,
        story_script: Dict[str, Any],
        production_plan: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        system_prompt = PromptLoader.load_prompt("system.md")
        storyboard_prompt = PromptLoader.load_prompt("storyboard.md", {
            "project_id": project_id,
            "story_script_json": json.dumps(story_script, indent=2),
            "production_plan_json": json.dumps(production_plan or {}, indent=2)
        })

        max_retries = 3
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                raw_sb = await self.llm.generate_json(storyboard_prompt, system_prompt)
                raw_sb["project_id"] = project_id
                
                # Validate Storyboard & Continuity
                warnings = StoryboardValidationService.validate_storyboard(
                    raw_sb,
                    expected_scene_count=len(story_script.get("scenes", []))
                )
                raw_sb["_warnings"] = warnings
                raw_sb["approved"] = False
                return raw_sb
            except StoryboardValidationError as sve:
                last_error = str(sve)
                print(f"Storyboard Agent Validation Attempt {attempt} failed: {sve}")
            except Exception as e:
                last_error = str(e)
                print(f"Storyboard Agent LLM Attempt {attempt} error: {e}")

        raise RuntimeError(f"Storyboard Agent failed to produce valid storyboard after {max_retries} attempts: {last_error}")

    async def regenerate_single_scene(
        self,
        storyboard: Dict[str, Any],
        scene_number: int
    ) -> Dict[str, Any]:
        # Regenerates a single scene in the storyboard while maintaining global continuity
        scenes = storyboard.get("scenes", [])
        target_scene_idx = next((i for i, s in enumerate(scenes) if s.get("scene_number") == scene_number), None)
        
        if target_scene_idx is None:
            raise ValueError(f"Scene #{scene_number} not found in storyboard.")

        # In Mock/Default mode, regenerate scene with refined parameters
        updated_scene = dict(scenes[target_scene_idx])
        updated_scene["camera_plan"]["movement"] = "Refined Pan & Zoom"
        updated_scene["visual_plan"]["mood"] = "Extra Vibrant & Playful"
        
        storyboard["scenes"][target_scene_idx] = updated_scene
        return storyboard
