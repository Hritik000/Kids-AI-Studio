"""
Production-Correct, Provider-Agnostic Voice / Text-to-Speech (TTS) Generation Layer.
Provides clean VoiceProvider abstraction for ElevenLabs TTS API and Mock providers.
Features binary audio response processing, local persistent audio storage,
FFmpeg container/stream validation, and secret masking.
"""

import os
import time
import math
import wave
import struct
import hashlib
import tempfile
import urllib.parse
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger("voice_provider")


class VoiceProviderError(Exception):
    """Base exception for all voice/TTS provider errors."""
    pass


class VoiceConfigurationError(VoiceProviderError):
    """Raised when Voice Provider configuration or API key is missing in real mode."""
    pass


class VoiceInputError(VoiceProviderError):
    """Raised when narration text or voice parameters are invalid or empty."""
    pass


class VoiceAuthError(VoiceProviderError):
    """Raised when authentication fails (HTTP 401/403)."""
    pass


class VoiceRateLimitError(VoiceProviderError):
    """Raised when rate limit is hit (HTTP 429)."""
    pass


class VoiceTimeoutError(VoiceProviderError):
    """Raised when TTS generation request times out."""
    pass


class VoiceAPIError(VoiceProviderError):
    """Raised when generic HTTP, provider API, or audio container validation error occurs."""
    pass


def mask_secret(text: str, secret: Optional[str] = None) -> str:
    """Masks secret API keys in log messages and error tracebacks."""
    if not text:
        return text
    secrets_to_mask = [secret] if secret else []
    for key_env in ["ELEVENLABS_API_KEY", "XI_API_KEY", "TTS_API_KEY"]:
        val = os.getenv(key_env) or getattr(settings, key_env, "")
        if val:
            secrets_to_mask.append(val)

    masked_text = str(text)
    for s in secrets_to_mask:
        if s and len(s) > 4:
            masked = f"{s[:3]}...{s[-4:]}"
            masked_text = masked_text.replace(s, masked)
    return masked_text


class VoiceProvider(ABC):
    @abstractmethod
    async def synthesize_speech(
        self,
        text: str,
        voice_name: str = "Storyteller Emma",
        emotion: str = "Cheerful",
        language: str = "English (US)",
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        """Synthesizes speech audio and returns metadata with local persistent audio asset path."""
        pass


class MockVoiceProvider(VoiceProvider):
    """
    Deterministic Mock Voice Provider for automated unit tests and keyless local development.
    Generates a clean, valid WAV audio file with a soft warm tone corresponding to narration length.
    """

    async def synthesize_speech(
        self,
        text: str,
        voice_name: str = "Storyteller Emma",
        emotion: str = "Cheerful",
        language: str = "English (US)",
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        base_dir = os.path.join(tempfile.gettempdir(), "kidsai_renders", project_id, "assets")
        os.makedirs(base_dir, exist_ok=True)

        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        audio_path = os.path.join(base_dir, f"asset_mock_narration_{text_hash}.wav")

        word_count = len(text.split()) if text else 1
        duration_sec = max(3, math.ceil(word_count / 3))
        sample_rate = 22050
        num_samples = duration_sec * sample_rate

        with wave.open(audio_path, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            frequency = 440.0  # A4 note
            for i in range(num_samples):
                sample = int(1000 * math.sin(2 * math.pi * frequency * i / sample_rate))
                wav_file.writeframes(struct.pack('<h', sample))

        os.chmod(audio_path, 0o644)

        return {
            "provider": "KokoroTTS-v1-Mock",
            "voice_name": voice_name,
            "sample_rate": 22050,
            "audio_format": "WAV",
            "storage_url": audio_path
        }


class ElevenLabsVoiceProvider(VoiceProvider):
    """
    Production-grade Voice Provider communicating with ElevenLabs TTS API.
    Sends narration text, processes binary audio response bytes (audio/mpeg),
    validates container integrity via FFmpeg, and persists audio asset locally.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None
    ):
        self.api_key = api_key or getattr(settings, "ELEVENLABS_API_KEY", "") or os.getenv("ELEVENLABS_API_KEY") or os.getenv("XI_API_KEY") or os.getenv("TTS_API_KEY") or ""
        self.voice_id = voice_id or getattr(settings, "ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") or "21m00Tcm4TlvDq8ikWAM"
        self.model = model or getattr(settings, "ELEVENLABS_MODEL", "eleven_multilingual_v2") or "eleven_multilingual_v2"
        self.timeout_seconds = timeout_seconds or getattr(settings, "VOICE_TIMEOUT", 35.0) or 35.0

    async def synthesize_speech(
        self,
        text: str,
        voice_name: str = "Storyteller Emma",
        emotion: str = "Cheerful",
        language: str = "English (US)",
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise VoiceConfigurationError(
                "ElevenLabs API key is missing. Set ELEVENLABS_API_KEY or set VOICE_PROVIDER=mock for development/testing."
            )

        if not text or not text.strip():
            raise VoiceInputError("Narration text for speech synthesis cannot be empty.")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        body = {
            "text": text,
            "model_id": self.model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        logger.info("Submitting ElevenLabs TTS speech synthesis request for voice %s...", self.voice_id)

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            try:
                resp = await client.post(url, headers=headers, json=body)
            except (httpx.TimeoutException, asyncio.TimeoutError) as e:
                raise VoiceTimeoutError(f"ElevenLabs TTS API request timed out after {self.timeout_seconds}s") from e
            except Exception as e:
                raise VoiceAPIError(f"Failed to connect to ElevenLabs API: {mask_secret(str(e), self.api_key)}") from e

            if resp.status_code in (401, 403):
                err_text = mask_secret(resp.text, self.api_key)
                raise VoiceAuthError(f"ElevenLabs API Authentication failed (HTTP {resp.status_code}): {err_text}")

            if resp.status_code == 429:
                err_text = mask_secret(resp.text, self.api_key)
                raise VoiceRateLimitError(f"ElevenLabs API Rate Limit exceeded (HTTP 429): {err_text}")

            if resp.status_code >= 500:
                err_text = mask_secret(resp.text, self.api_key)
                raise VoiceAPIError(f"ElevenLabs Server Error (HTTP {resp.status_code}): {err_text}")

            if resp.status_code >= 400:
                err_text = mask_secret(resp.text, self.api_key)
                raise VoiceAPIError(f"ElevenLabs API Request Error (HTTP {resp.status_code}): {err_text}")

            # Process Binary Audio Content
            audio_bytes = resp.content
            if not audio_bytes or len(audio_bytes) == 0:
                raise VoiceAPIError("ElevenLabs API returned empty 0-byte audio response.")

            # Save Audio Bytes to local persistent project assets directory
            base_dir = os.path.join(tempfile.gettempdir(), "kidsai_renders", project_id, "assets")
            os.makedirs(base_dir, exist_ok=True)

            text_hash = hashlib.sha256(f"{text}_{self.voice_id}".encode("utf-8")).hexdigest()[:16]
            local_audio_path = os.path.abspath(os.path.join(base_dir, f"asset_elevenlabs_narration_{text_hash}.mp3"))

            # Path Traversal Protection
            if not local_audio_path.startswith(base_dir + os.sep) and local_audio_path != base_dir:
                raise VoiceAPIError(f"Path traversal detected for filename asset_elevenlabs_narration_{text_hash}.mp3")

            with open(local_audio_path, "wb") as f:
                f.write(audio_bytes)

            os.chmod(local_audio_path, 0o644)

            # Validate Audio File & Container Integrity
            if not os.path.isfile(local_audio_path):
                raise VoiceAPIError(f"Persisted audio file does not exist at '{local_audio_path}'")

            file_size = os.path.getsize(local_audio_path)
            if file_size == 0:
                raise VoiceAPIError(f"Persisted audio file is empty (0 bytes) at '{local_audio_path}'")

            ext = os.path.splitext(local_audio_path)[1].lower()
            if ext not in (".mp3", ".wav", ".aac", ".m4a", ".ogg"):
                raise VoiceAPIError(f"Persisted audio asset has unsupported extension '{ext}' at '{local_audio_path}'")

            # Verify audio stream using FFmpeg
            from app.services.rendering.ffmpeg import FFmpegEngine
            try:
                ret_code, stdout, stderr = FFmpegEngine.run_command(["-i", local_audio_path], timeout=15)
            except Exception as e:
                stderr = getattr(e, "stderr", str(e))

            probe_info = stderr or stdout or ""
            if "Error opening input" in probe_info or "Invalid data found" in probe_info:
                raise VoiceAPIError(f"Persisted audio asset is corrupted or unreadable at '{local_audio_path}': {probe_info}")

            if "Audio:" not in probe_info and "Stream #" not in probe_info:
                raise VoiceAPIError(f"Persisted asset at '{local_audio_path}' does not contain a valid audio stream.")

            logger.info("Successfully synthesized and persisted real audio asset: %s (%d bytes)", local_audio_path, file_size)

            return {
                "provider": f"ElevenLabs-TTS ({self.model})",
                "voice_name": voice_name,
                "voice_id": self.voice_id,
                "sample_rate": 44100,
                "audio_format": "MP3",
                "storage_url": local_audio_path
            }


class KokoroTTSProvider(VoiceProvider):
    """Local Kokoro TTS provider for zero-cost, lightweight speech synthesis"""

    async def synthesize_speech(
        self,
        text: str,
        voice_name: str = "Storyteller Emma",
        emotion: str = "Cheerful",
        language: str = "English (US)",
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        import numpy as np
        from kokoro import KPipeline
        import soundfile as sf

        if not text or not text.strip():
            raise VoiceInputError("Narration text for speech synthesis cannot be empty.")

        # Initialize pipeline for American English
        # Using 'a' for American English, can be adjusted based on language parameter
        pipeline = KPipeline(lang_code='a')  # 'a' = American English

        # Select voice based on voice_name parameter
        voice_map = {
            "Storyteller Emma": "af_heart",  # Warm female voice
            "Cheerful Child": "af_bella",    # Friendly female voice
            "Warm Grandpa": "am_adam",       # Friendly male voice
            "Calm Mother": "af_sarah",       # Calm female voice
            # Default to af_heart if voice not found
        }
        voice_id = voice_map.get(voice_name, "af_heart")

        # Generate audio
        generator = pipeline(text, voice=voice_id)

        # Collect and save audio
        audio_segments = []
        for i, (gs, ps, audio) in enumerate(generator):
            audio_segments.append(audio)
            logger.debug(f"Kokoro segment {i}: {gs} {ps}")

        # Concatenate and save
        if not audio_segments:
            raise VoiceAPIError("Kokoro TTS generated no audio")

        full_audio = np.concatenate(audio_segments)

        # Prepare local storage
        base_dir = os.path.join(tempfile.gettempdir(), "kidsai_renders", project_id, "assets")
        os.makedirs(base_dir, exist_ok=True)

        text_hash = hashlib.sha256(f"{text}_{voice_name}".encode("utf-8")).hexdigest()[:16]
        local_audio_path = os.path.abspath(os.path.join(base_dir, f"asset_kokoro_narration_{text_hash}.wav"))

        # Path Traversal Protection
        if not local_audio_path.startswith(base_dir + os.sep) and local_audio_path != base_dir:
            raise VoiceAPIError(f"Path traversal detected for filename asset_kokoro_narration_{text_hash}.wav")

        # Save as WAV file
        sf.write(local_audio_path, full_audio, 24000)  # Kokoro outputs at 24kHz

        os.chmod(local_audio_path, 0o644)

        # Validate Audio File
        if not os.path.isfile(local_audio_path):
            raise VoiceAPIError(f"Persisted audio file does not exist at '{local_audio_path}'")

        file_size = os.path.getsize(local_audio_path)
        if file_size == 0:
            raise VoiceAPIError(f"Persisted audio file is empty (0 bytes) at '{local_audio_path}'")

        ext = os.path.splitext(local_audio_path)[1].lower()
        if ext not in (".wav",):
            raise VoiceAPIError(f"Persisted audio asset has unsupported extension '{ext}' at '{local_audio_path}'")

        logger.info("Successfully synthesized and persisted real audio asset: %s (%d bytes)", local_audio_path, file_size)

        return {
            "provider": "KokoroTTS-Local",
            "voice_name": voice_name,
            "sample_rate": 24000,
            "audio_format": "WAV",
            "storage_url": local_audio_path
        }


# Backward-compatible alias for existing imports (DEPRECATED - use KokoroTTSProvider directly)
KokoroTTSProvider_Legacy = ElevenLabsVoiceProvider


def get_voice_provider(provider_type: Optional[str] = None) -> VoiceProvider:
    """
    Factory function to retrieve configured VoiceProvider instance.
    Explicit provider modes:
    - 'mock': MockVoiceProvider
    - 'elevenlabs' / 'eleven': ElevenLabsVoiceProvider (uses ELEVENLABS_API_KEY)
    - 'kokoro': KokoroTTSProvider (zero-cost local TTS)
    - 'auto' / None: Auto-detects key. If ELEVENLABS_API_KEY present, returns ElevenLabsVoiceProvider; else KokoroTTSProvider.
    """
    mode = (provider_type or os.getenv("VOICE_PROVIDER") or getattr(settings, "VOICE_PROVIDER", "auto") or "auto").lower()

    if mode == "mock":
        return MockVoiceProvider()

    if mode == "kokoro":
        return KokoroTTSProvider()

    if mode in ("elevenlabs", "eleven"):
        return ElevenLabsVoiceProvider()

    # Auto mode
    eleven_key = getattr(settings, "ELEVENLABS_API_KEY", "") or os.getenv("ELEVENLABS_API_KEY") or os.getenv("XI_API_KEY") or os.getenv("TTS_API_KEY")
    if eleven_key:
        return ElevenLabsVoiceProvider(api_key=eleven_key)
    else:
        return KokoroTTSProvider()
