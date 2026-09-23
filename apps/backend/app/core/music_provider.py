"""
Production-Correct, Provider-Agnostic Background Music Layer.
Provides clean MusicProvider abstraction for Stability AI Stable Audio API and Mock providers.
Features binary audio response processing, local persistent audio storage,
FFmpeg container/audio stream validation, and secret masking.
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
from pathlib import Path

logger = logging.getLogger("music_provider")


class MusicProviderError(Exception):
    """Base exception for all music provider errors."""
    pass


class MusicConfigurationError(MusicProviderError):
    """Raised when Music Provider configuration or API key is missing in real mode."""
    pass


class MusicInputError(MusicProviderError):
    """Raised when music prompt or parameters are invalid or empty."""
    pass


class MusicAuthError(MusicProviderError):
    """Raised when authentication fails (HTTP 401/403)."""
    pass


class MusicRateLimitError(MusicProviderError):
    """Raised when rate limit is hit (HTTP 429)."""
    pass


class MusicTimeoutError(MusicProviderError):
    """Raised when music generation request times out."""
    pass


class MusicAPIError(MusicProviderError):
    """Raised when generic HTTP, provider API, or audio container validation error occurs."""
    pass


def mask_secret(text: str, secret: Optional[str] = None) -> str:
    """Masks secret API keys in log messages and error tracebacks."""
    if not text:
        return text
    secrets_to_mask = [secret] if secret else []
    for key_env in ["STABLE_AUDIO_API_KEY", "STABILITY_API_KEY", "MUSIC_API_KEY"]:
        val = os.getenv(key_env) or getattr(settings, key_env, "")
        if val:
            secrets_to_mask.append(val)

    masked_text = str(text)
    for s in secrets_to_mask:
        if s and len(s) > 4:
            masked = f"{s[:3]}...{s[-4:]}"
            masked_text = masked_text.replace(s, masked)
    return masked_text


class MusicProvider(ABC):
    @abstractmethod
    async def synthesize_music_and_mix(
        self,
        prompt: str,
        duration_seconds: float = 5.0,
        bpm: int = 110,
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        """Synthesizes background music and returns metadata with local persistent audio asset path."""
        pass


class MockMusicProvider(MusicProvider):
    """
    Deterministic Mock Music Provider for automated unit tests and keyless local development.
    Generates a clean, valid WAV audio file with a soft warm background chord corresponding to duration.
    """

    async def synthesize_music_and_mix(
        self,
        prompt: str,
        duration_seconds: float = 5.0,
        bpm: int = 110,
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        base_dir = os.path.join(tempfile.gettempdir(), "kidsai_renders", project_id, "assets")
        os.makedirs(base_dir, exist_ok=True)

        prompt_hash = hashlib.sha256(f"{prompt}_{bpm}".encode("utf-8")).hexdigest()[:16]
        audio_path = os.path.join(base_dir, f"asset_mock_music_{prompt_hash}.wav")

        duration_sec = max(2, math.ceil(duration_seconds))
        sample_rate = 22050
        num_samples = duration_sec * sample_rate

        with wave.open(audio_path, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            # Create a soft C-major chord (C4 + E4 + G4)
            frequencies = [261.63, 329.63, 392.00]
            for i in range(num_samples):
                sample_val = sum(int(300 * math.sin(2 * math.pi * f * i / sample_rate)) for f in frequencies)
                wav_file.writeframes(struct.pack('<h', max(-32768, min(32767, sample_val))))

        os.chmod(audio_path, 0o644)

        return {
            "provider": "StableAudio-Open-Mock",
            "sample_rate": 22050,
            "audio_format": "WAV",
            "storage_url": audio_path
        }


class StableAudioProvider(MusicProvider):
    """
    Production-grade Music Provider communicating with Stability AI Stable Audio REST API.
    Sends music prompt, processes binary audio response bytes (audio/mpeg),
    validates container integrity via FFmpeg, and persists audio asset locally.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        poll_interval: Optional[float] = None,
        timeout_seconds: Optional[float] = None
    ):
        self.api_key = api_key or getattr(settings, "STABLE_AUDIO_API_KEY", "") or getattr(settings, "STABILITY_API_KEY", "") or os.getenv("STABLE_AUDIO_API_KEY") or os.getenv("STABILITY_API_KEY") or ""
        self.model = model or getattr(settings, "MUSIC_MODEL", "stable-audio") or "stable-audio"
        self.timeout_seconds = timeout_seconds or getattr(settings, "MUSIC_TIMEOUT", 60.0) or 60.0

    async def synthesize_music_and_mix(
        self,
        prompt: str,
        duration_seconds: float = 5.0,
        bpm: int = 110,
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise MusicConfigurationError(
                "Stable Audio API key is missing. Set STABLE_AUDIO_API_KEY or set MUSIC_PROVIDER=mock for development/testing."
            )

        if not prompt or not prompt.strip():
            raise MusicInputError("Music generation prompt cannot be empty.")

        # Stability AI v2beta Audio REST API Endpoint
        url = "https://api.stability.ai/v2beta/audio/stable-audio"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "audio/mpeg"
        }
        form_data = {
            "prompt": prompt,
            "seconds_start": "0",
            "seconds_total": str(max(1, int(duration_seconds))),
            "output_format": "mp3"
        }

        logger.info("Submitting Stability AI Stable Audio request for prompt '%s'...", prompt[:40])

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            try:
                resp = await client.post(url, headers=headers, data=form_data)
            except (httpx.TimeoutException, asyncio.TimeoutError) as e:
                raise MusicTimeoutError(f"Stable Audio API request timed out after {self.timeout_seconds}s") from e
            except Exception as e:
                raise MusicAPIError(f"Failed to connect to Stable Audio API: {mask_secret(str(e), self.api_key)}") from e

            if resp.status_code in (401, 403):
                err_text = mask_secret(resp.text, self.api_key)
                raise MusicAuthError(f"Stable Audio API Authentication failed (HTTP {resp.status_code}): {err_text}")

            if resp.status_code == 429:
                err_text = mask_secret(resp.text, self.api_key)
                raise MusicRateLimitError(f"Stable Audio API Rate Limit exceeded (HTTP 429): {err_text}")

            if resp.status_code >= 500:
                err_text = mask_secret(resp.text, self.api_key)
                raise MusicAPIError(f"Stable Audio Server Error (HTTP {resp.status_code}): {err_text}")

            if resp.status_code >= 400:
                err_text = mask_secret(resp.text, self.api_key)
                raise MusicAPIError(f"Stable Audio API Request Error (HTTP {resp.status_code}): {err_text}")

            # Process Binary Audio Content
            audio_bytes = resp.content
            if not audio_bytes or len(audio_bytes) == 0:
                raise MusicAPIError("Stable Audio API returned empty 0-byte audio response.")

            # Save Audio Bytes to local persistent project assets directory
            base_dir = os.path.join(tempfile.gettempdir(), "kidsai_renders", project_id, "assets")
            os.makedirs(base_dir, exist_ok=True)

            prompt_hash = hashlib.sha256(f"{prompt}_{duration_seconds}".encode("utf-8")).hexdigest()[:16]
            local_audio_path = os.path.abspath(os.path.join(base_dir, f"asset_stable_audio_{prompt_hash}.mp3"))

            # Path Traversal Protection
            if not local_audio_path.startswith(base_dir + os.sep) and local_audio_path != base_dir:
                raise MusicAPIError(f"Path traversal detected for filename asset_stable_audio_{prompt_hash}.mp3")

            with open(local_audio_path, "wb") as f:
                f.write(audio_bytes)

            os.chmod(local_audio_path, 0o644)

            # Validate Audio File & Container Integrity
            if not os.path.isfile(local_audio_path):
                raise MusicAPIError(f"Persisted music file does not exist at '{local_audio_path}'")

            file_size = os.path.getsize(local_audio_path)
            if file_size == 0:
                raise MusicAPIError(f"Persisted music file is empty (0 bytes) at '{local_audio_path}'")

            ext = os.path.splitext(local_audio_path)[1].lower()
            if ext not in (".mp3", ".wav", ".aac", ".m4a", ".ogg"):
                raise MusicAPIError(f"Persisted music asset has unsupported extension '{ext}' at '{local_audio_path}'")

            # Verify audio stream using FFmpeg
            from app.services.rendering.ffmpeg import FFmpegEngine
            try:
                ret_code, stdout, stderr = FFmpegEngine.run_command(["-i", local_audio_path], timeout=15)
            except Exception as e:
                stderr = getattr(e, "stderr", str(e))

            probe_info = stderr or stdout or ""
            if "Error opening input" in probe_info or "Invalid data found" in probe_info:
                raise MusicAPIError(f"Persisted music asset is corrupted or unreadable at '{local_audio_path}': {probe_info}")

            if "Audio:" not in probe_info and "Stream #" not in probe_info:
                raise MusicAPIError(f"Persisted asset at '{local_audio_path}' does not contain a valid audio stream.")

            logger.info("Successfully synthesized and persisted real music asset: %s (%d bytes)", local_audio_path, file_size)

            return {
                "provider": f"StableAudio-API ({self.model})",
                "sample_rate": 44100,
                "audio_format": "MP3",
                "storage_url": local_audio_path
            }


class HuggingFaceMusicGenProvider(MusicProvider):
    """Free music generation via Hugging Face Inference API"""

    async def synthesize_music_and_mix(
        self,
        prompt: str,
        duration_seconds: float = 5.0,
        bpm: int = 110,
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        import hashlib
        from pathlib import Path

        # HF Inference API endpoint for musicgen-small
        API_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"

        # Prepare payload
        # MusicGen generates audio in chunks; we estimate tokens needed
        max_new_tokens = int(duration_seconds * 50)  # Approx 50 tokens per second
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "return_audio": True,
            }
        }

        # Prepare local storage
        assets_dir = Path("/tmp/kidsai_renders") / project_id / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        hash_input = f"{prompt}{duration_seconds}"
        file_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        local_path = assets_dir / f"asset_{file_hash}.wav"

        # Get API key from settings (optional for HF - anonymous requests have lower rate limits)
        api_key = getattr(settings, 'HF_API_TOKEN', None)
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Make request to HF API
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(API_URL, json=payload, headers=headers)
            if resp.status_code == 200:
                audio_data = resp.content
                local_path.write_bytes(audio_data)

                # Basic validation
                if local_path.stat().st_size < 1000:  # Less than 1KB is suspicious
                    local_path.unlink(missing_ok=True)
                    raise MusicAPIError("Received audio file is too small - likely empty")

                return {
                    "provider": "HuggingFace-MusicGen",
                    "sample_rate": 24000,  # MusicGen default
                    "audio_format": "WAV",
                    "storage_url": str(local_path)
                }
            else:
                error_text = resp.text
                raise MusicAPIError(f"HF MusicGen API error: {resp.status_code} - {error_text}")


# Backward-compatible alias
RealMusicProvider = StableAudioProvider


def get_music_provider(provider_type: Optional[str] = None) -> MusicProvider:
    """
    Factory function to retrieve configured MusicProvider instance.
    Explicit provider modes:
    - 'mock': MockMusicProvider
    - 'stable_audio' / 'stability' / 'stable': StableAudioProvider (uses STABLE_AUDIO_API_KEY or STABILITY_API_KEY)
    - 'huggingface_musicgen': HuggingFaceMusicGenProvider (free inference API)
    - 'auto' / None: Auto-detects key. If STABLE_AUDIO_API_KEY/STABILITY_API_KEY present, returns StableAudioProvider; else HuggingFaceMusicGenProvider.
    """
    mode = (provider_type or os.getenv("MUSIC_PROVIDER") or getattr(settings, "MUSIC_PROVIDER", "auto") or "auto").lower()

    if mode == "mock":
        return MockMusicProvider()

    if mode in ("stable_audio", "stability", "stable"):
        return StableAudioProvider()

    if mode == "huggingface_musicgen":
        return HuggingFaceMusicGenProvider()

    # Auto mode
    stable_key = getattr(settings, "STABLE_AUDIO_API_KEY", "") or getattr(settings, "STABILITY_API_KEY", "") or os.getenv("STABLE_AUDIO_API_KEY") or os.getenv("STABILITY_API_KEY")
    if stable_key:
        return StableAudioProvider(api_key=stable_key)
    else:
        return HuggingFaceMusicGenProvider()
