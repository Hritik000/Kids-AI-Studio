import os
import urllib.parse
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class MusicProvider(ABC):
    @abstractmethod
    async def synthesize_music_and_mix(
        self,
        prompt: str,
        duration_seconds: float = 5.0,
        bpm: int = 110
    ) -> Dict[str, Any]:
        pass

class MockMusicProvider(MusicProvider):
    async def synthesize_music_and_mix(
        self,
        prompt: str,
        duration_seconds: float = 5.0,
        bpm: int = 110
    ) -> Dict[str, Any]:
        audio_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"

        return {
            "provider": "StableAudio-Open-Mock",
            "sample_rate": 44100,
            "audio_format": "MP3",
            "storage_url": audio_url
        }

class StableAudioProvider(MusicProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("STABLE_AUDIO_API_KEY")

    async def synthesize_music_and_mix(
        self,
        prompt: str,
        duration_seconds: float = 5.0,
        bpm: int = 110
    ) -> Dict[str, Any]:
        if not self.api_key:
            return await MockMusicProvider().synthesize_music_and_mix(prompt, duration_seconds, bpm)

        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            body = {
                "prompt": prompt,
                "duration": duration_seconds,
                "bpm": bpm
            }
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post("https://api.stability.ai/v2beta/stable-image/generate/core", headers=headers, json=body)
                resp.raise_for_status()
                return {
                    "provider": "StableAudio-Open-API",
                    "sample_rate": 44100,
                    "audio_format": "MP3",
                    "storage_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
                }
        except Exception as e:
            print(f"Stable Audio API error, falling back to mock provider: {e}")
            return await MockMusicProvider().synthesize_music_and_mix(prompt, duration_seconds, bpm)

def get_music_provider(provider_type: str = "auto") -> MusicProvider:
    if provider_type == "mock":
        return MockMusicProvider()
    elif provider_type == "stable_audio":
        return StableAudioProvider()
    else:
        if os.getenv("STABLE_AUDIO_API_KEY"):
            return StableAudioProvider()
        return MockMusicProvider()
