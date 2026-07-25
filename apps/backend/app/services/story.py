import json
from typing import Dict, Any, Optional
from app.core.llm import get_llm_provider, PromptLoader, LLMProvider
from app.services.validator import ValidationService, QualityValidationError

class StoryAgentService:
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    async def generate_story_script(
        self,
        production_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        system_prompt = PromptLoader.load_prompt("system.md")
        story_prompt = PromptLoader.load_prompt("story.md", {
            "production_plan_json": json.dumps(production_plan, indent=2),
            "target_age_group": production_plan.get("target_age_group", "3-5"),
            "scene_count": production_plan.get("scene_count", 4)
        })

        max_retries = 3
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                raw_story = await self.llm.generate_json(story_prompt, system_prompt)
                
                # Validate Story Script
                warnings = ValidationService.validate_story_script(
                    raw_story,
                    expected_scene_count=production_plan.get("scene_count")
                )
                raw_story["_warnings"] = warnings
                return raw_story
            except QualityValidationError as qe:
                last_error = str(qe)
                print(f"Story Agent Validation Attempt {attempt} failed: {qe}")
            except Exception as e:
                last_error = str(e)
                print(f"Story Agent LLM Attempt {attempt} error: {e}")

        raise RuntimeError(f"Story Agent failed to produce valid story script after {max_retries} attempts: {last_error}")
