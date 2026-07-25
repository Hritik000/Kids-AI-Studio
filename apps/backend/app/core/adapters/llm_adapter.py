from abc import ABC, abstractmethod
import json
import os
import httpx
from typing import Dict, Any

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_json(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """Generate structured JSON output from LLM."""
        pass

class MockLLMProvider(BaseLLMProvider):
    async def generate_json(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """Fallback mock provider generating high quality kids story structure."""
        return {
            "title": f"The Magical Adventure: {prompt.capitalize()}",
            "description": f"An educational and fun story exploring {prompt} for kids.",
            "tags": ["Kids", "Education", "Animation", "Learning"],
            "scenes": [
                {
                    "scene_number": 1,
                    "narration_text": f"Once upon a time in a colorful forest, red dinosaur Sammy was super excited to explore the sunny meadow!",
                    "visual_prompt": f"Friendly cute red baby dinosaur standing in a bright green sunny forest meadow, Pixar 3D style, vibrant colors"
                },
                {
                    "scene_number": 2,
                    "narration_text": f"Sammy met a friendly blue bird who loved singing about bright blue skies and shiny water drops.",
                    "visual_prompt": f"Cute red dinosaur looking up at a cheerful blue songbird sitting on a tree branch, vibrant 3D animation"
                },
                {
                    "scene_number": 3,
                    "narration_text": f"Together, they found a giant yellow sunflower that giggled whenever the wind blew softly.",
                    "visual_prompt": f"Red dinosaur and blue bird playing next to a giant happy yellow sunflower in a blooming garden, 3D style"
                },
                {
                    "scene_number": 4,
                    "narration_text": f"What a wonderful day learning about red, blue, and yellow! See you on our next adventure!",
                    "visual_prompt": f"Cute red dinosaur waving goodbye with rainbow background, happy expression, 3D animated style"
                }
            ]
        }

class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

    async def generate_json(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        if not self.api_key:
            return await MockLLMProvider().generate_json(prompt, system_prompt)
            
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            return json.loads(content.strip())

class LLMAdapter:
    def __init__(self, provider: BaseLLMProvider | None = None):
        if provider:
            self.provider = provider
        elif os.getenv("OPENAI_API_KEY"):
            self.provider = OpenAILLMProvider()
        else:
            self.provider = MockLLMProvider()

    async def generate_json(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        return await self.provider.generate_json(prompt, system_prompt)

llm_adapter = LLMAdapter()
