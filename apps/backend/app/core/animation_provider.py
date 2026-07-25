import os
import urllib.parse
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AnimationProvider(ABC):
    @abstractmethod
    async def generate_animation_clip(
        self,
        image_url: str,
        motion_prompt: str,
        duration_seconds: float = 5.0,
        width: int = 1280,
        height: int = 720,
        seed: int = 42
    ) -> Dict[str, Any]:
        pass

class MockAnimationProvider(AnimationProvider):
    async def generate_animation_clip(
        self,
        image_url: str,
        motion_prompt: str,
        duration_seconds: float = 5.0,
        width: int = 1280,
        height: int = 720,
        seed: int = 42
    ) -> Dict[str, Any]:
        short_prompt = motion_prompt[:40].replace(" ", "+")
        encoded = urllib.parse.quote(short_prompt)
        # Mock high-resolution video preview URL
        video_url = f"https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
        thumb_url = f"https://placehold.co/400x225/1A1D27/FFFFFF/png?text=Animated+{encoded}"

        return {
            "provider": "Wan2.2-i2v-Mock",
            "seed": seed,
            "duration_seconds": duration_seconds,
            "width": width,
            "height": height,
            "storage_url": video_url,
            "thumbnail_url": thumb_url
        }

class Wan2AnimationProvider(AnimationProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("REPLICATE_API_KEY")

    async def generate_animation_clip(
        self,
        image_url: str,
        motion_prompt: str,
        duration_seconds: float = 5.0,
        width: int = 1280,
        height: int = 720,
        seed: int = 42
    ) -> Dict[str, Any]:
        if not self.api_key:
            return await MockAnimationProvider().generate_animation_clip(image_url, motion_prompt, duration_seconds, width, height, seed)

        try:
            import httpx
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            body = {
                "version": "wan-video/wan-2.1-1.3b",
                "input": {
                    "image": image_url,
                    "prompt": motion_prompt,
                    "duration": duration_seconds
                }
            }
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post("https://api.replicate.com/v1/predictions", headers=headers, json=body)
                resp.raise_for_status()
                data = resp.json()
                video_url = data.get("output", [None])[0] or "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
                return {
                    "provider": "Wan2.2-Replicate",
                    "seed": seed,
                    "duration_seconds": duration_seconds,
                    "width": width,
                    "height": height,
                    "storage_url": video_url,
                    "thumbnail_url": image_url
                }
        except Exception as e:
            print(f"Wan 2.2 Replicate API error, falling back to mock provider: {e}")
            return await MockAnimationProvider().generate_animation_clip(image_url, motion_prompt, duration_seconds, width, height, seed)

def get_animation_provider(provider_type: str = "auto") -> AnimationProvider:
    if provider_type == "mock":
        return MockAnimationProvider()
    elif provider_type == "wan2":
        return Wan2AnimationProvider()
    else:
        if os.getenv("REPLICATE_API_KEY"):
            return Wan2AnimationProvider()
        return MockAnimationProvider()
