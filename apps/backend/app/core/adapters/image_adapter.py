from abc import ABC, abstractmethod
import os
import urllib.parse
from typing import Dict, Any

class BaseImageProvider(ABC):
    @abstractmethod
    async def generate_image(self, prompt: str, scene_number: int) -> str:
        """Returns image URL for scene."""
        pass

class MockImageProvider(BaseImageProvider):
    async def generate_image(self, prompt: str, scene_number: int) -> str:
        """Generates dynamic high quality SVG/Placeholder image with prompt text embedded."""
        encoded_prompt = urllib.parse.quote(prompt[:40])
        # Generate SVG placeholder with pastel kids color theme
        colors = ["FF6B6B", "4ECDC4", "FFE66D", "1A535C", "70A1D7"]
        bg_color = colors[(scene_number - 1) % len(colors)]
        return f"https://placehold.co/1280x720/{bg_color}/FFFFFF/png?text=Scene+{scene_number}:+{encoded_prompt}"

class ImageAdapter:
    def __init__(self, provider: BaseImageProvider | None = None):
        self.provider = provider or MockImageProvider()

    async def generate_image(self, prompt: str, scene_number: int) -> str:
        return await self.provider.generate_image(prompt, scene_number)

image_adapter = ImageAdapter()
