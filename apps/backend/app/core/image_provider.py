import os
import urllib.parse
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ImageProvider(ABC):
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str,
        width: int = 1280,
        height: int = 720,
        seed: int = 42
    ) -> Dict[str, Any]:
        pass

class MockImageProvider(ImageProvider):
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str,
        width: int = 1280,
        height: int = 720,
        seed: int = 42
    ) -> Dict[str, Any]:
        # Encode prompt keywords into placeholder image title for clear visual feedback
        short_prompt = prompt[:45].replace(" ", "+")
        encoded = urllib.parse.quote(short_prompt)
        image_url = f"https://placehold.co/{width}x{height}/1A1D27/FFFFFF/png?text={encoded}"
        thumb_url = f"https://placehold.co/400x225/1A1D27/FFFFFF/png?text={encoded}"

        return {
            "provider": "FLUX-v1-Mock",
            "seed": seed,
            "width": width,
            "height": height,
            "storage_url": image_url,
            "thumbnail_url": thumb_url
        }

class FluxImageProvider(ImageProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("REPLICATE_API_KEY")

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str,
        width: int = 1280,
        height: int = 720,
        seed: int = 42
    ) -> Dict[str, Any]:
        if not self.api_key:
            return await MockImageProvider().generate_image(prompt, negative_prompt, width, height, seed)

        try:
            import httpx
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            body = {
                "version": "black-forest-labs/flux-schnell",
                "input": {
                    "prompt": prompt,
                    "aspect_ratio": "16:9",
                    "seed": seed
                }
            }
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post("https://api.replicate.com/v1/predictions", headers=headers, json=body)
                resp.raise_for_status()
                data = resp.json()
                output_url = data.get("output", [None])[0] or f"https://placehold.co/{width}x{height}/1A1D27/FFFFFF/png?text=FLUX+Generated"
                return {
                    "provider": "FLUX-Schnell-Replicate",
                    "seed": seed,
                    "width": width,
                    "height": height,
                    "storage_url": output_url,
                    "thumbnail_url": output_url
                }
        except Exception as e:
            print(f"FLUX Replicate API error, falling back to mock provider: {e}")
            return await MockImageProvider().generate_image(prompt, negative_prompt, width, height, seed)

def get_image_provider(provider_type: str = "auto") -> ImageProvider:
    if provider_type == "mock":
        return MockImageProvider()
    elif provider_type == "flux":
        return FluxImageProvider()
    else:
        if os.getenv("REPLICATE_API_KEY"):
            return FluxImageProvider()
        return MockImageProvider()
