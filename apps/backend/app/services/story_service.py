import os
from typing import Dict, Any
from app.core.adapters.llm_adapter import llm_adapter
from app.models.project import StoryboardResponse, Scene

class StoryService:
    def _load_prompt_template(self) -> str:
        # Resolve path to monorepo packages/prompts/story.md
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../packages/prompts"))
        prompt_file = os.path.join(base_dir, "story.md")
        if os.path.exists(prompt_file):
            with open(prompt_file, "r") as f:
                return f.read()
        return "You are the Story Director for KidsAI Studio. Generate story JSON for kids."

    async def generate_storyboard(self, prompt: str, target_age_group: str) -> StoryboardResponse:
        system_prompt = self._load_prompt_template()
        user_prompt = f"Create a video script based on prompt: '{prompt}' for age group '{target_age_group}'."
        
        result_json = await llm_adapter.generate_json(user_prompt, system_prompt)
        
        scenes = [
            Scene(
                scene_number=s.get("scene_number", idx + 1),
                narration_text=s.get("narration_text", ""),
                visual_prompt=s.get("visual_prompt", "")
            )
            for idx, s in enumerate(result_json.get("scenes", []))
        ]
        
        return StoryboardResponse(
            title=result_json.get("title", f"Story: {prompt}"),
            description=result_json.get("description", ""),
            tags=result_json.get("tags", ["Kids", "Learning"]),
            scenes=scenes
        )

story_service = StoryService()
