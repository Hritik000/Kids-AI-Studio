import json
from typing import Dict, Any, Optional
from app.core.llm import get_llm_provider, PromptLoader, LLMProvider
from app.services.validator import ValidationService, QualityValidationError

class DirectorAgentService:
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    async def generate_production_plan(
        self,
        project_id: str,
        topic: str,
        target_age_group: str = "3-5",
        language: str = "English (US)",
        video_length: str = "Standard (2-3 min)",
        aspect_ratio: str = "16:9",
        video_style: str = "3D Pixar Render"
    ) -> Dict[str, Any]:
        system_prompt = PromptLoader.load_prompt("system.md")
        director_prompt = PromptLoader.load_prompt("director.md", {
            "project_id": project_id,
            "topic": topic,
            "target_age_group": target_age_group,
            "language": language,
            "video_length": video_length,
            "aspect_ratio": aspect_ratio,
            "video_style": video_style
        })

        max_retries = 3
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                raw_plan = await self.llm.generate_json(director_prompt, system_prompt)

                # Override project_id if needed
                raw_plan["project_id"] = project_id

                # Validate Plan
                warnings = ValidationService.validate_production_plan(raw_plan)
                raw_plan["_warnings"] = warnings
                return raw_plan
            except QualityValidationError as qe:
                last_error = str(qe)
                print(f"Director Agent Validation Attempt {attempt} failed: {qe}")
            except Exception as e:
                last_error = str(e)
                print(f"Director Agent LLM Attempt {attempt} error: {e}")

        raise RuntimeError(f"Director Agent failed to produce valid production plan after {max_retries} attempts: {last_error}")
