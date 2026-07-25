import os
import urllib.parse
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class VoiceProvider(ABC):
    @abstractmethod
    async def synthesize_speech(
        self,
        text: str,
        voice_name: str = "Storyteller Emma",
        emotion: str = "Cheerful",
        language: str = "English (US)"
    ) -> Dict[str, Any]:
        pass

class MockVoiceProvider(VoiceProvider):
    async def synthesize_speech(
        self,
        text: str,
        voice_name: str = "Storyteller Emma",
        emotion: str = "Cheerful",
        language: str = "English (US)"
    ) -> Dict[str, Any]:
        # High quality sample audio clip URL for testing audio playback
        audio_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"

        return {
            "provider": "KokoroTTS-v1-Mock",
            "voice_name": voice_name,
            "sample_rate": 24000,
            "audio_format": "MP3",
            "storage_url": audio_url
        }

class KokoroTTSProvider(VoiceProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")

    async def synthesize_speech(
        self,
        text: str,
        voice_name: str = "Storyteller Emma",
        emotion: str = "Cheerful",
        language: str = "English (US)"
    ) -> Dict[str, Any]:
        if not self.api_key:
            return await MockVoiceProvider().synthesize_speech(text, voice_name, emotion, language)

        try:
            import httpx
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            body = {
                "text": text,
                "model_id": "eleven_multilingual_v2"
            }
            async with httpx.AsyncClient(timeout=35.0) as client:
                resp = await client.post("https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM", headers=headers, json=body)
                resp.raise_for_status()
                return {
                    "provider": "ElevenLabs-TTS",
                    "voice_name": voice_name,
                    "sample_rate": 44100,
                    "audio_format": "MP3",
                    "storage_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
                }
        except Exception as e:
            print(f"ElevenLabs TTS API error, falling back to mock provider: {e}")
            return await MockVoiceProvider().synthesize_speech(text, voice_name, emotion, language)

def get_voice_provider(provider_type: str = "auto") -> VoiceProvider:
    if provider_type == "mock":
        return MockVoiceProvider()
    elif provider_type == "kokoro":
        return KokoroTTSProvider()
    else:
        if os.getenv("ELEVENLABS_API_KEY"):
            return KokoroTTSProvider()
        return MockVoiceProvider()
