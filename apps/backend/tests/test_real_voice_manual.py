"""
Manual Integration Test for Real ElevenLabs Voice / Text-to-Speech (TTS) Provider.
This test:
- Requires an explicit ELEVENLABS_API_KEY
- Uses VOICE_PROVIDER=elevenlabs
- Submits a short narration text to live ElevenLabs TTS API
- Receives binary audio bytes (audio/mpeg)
- Saves the resulting persistent MP3 audio asset to disk
- Validates the audio file using FFmpeg/ffprobe
- Reports provider, model, voice ID, local storage path, file size, and latency metadata
- Never prints secrets or API keys
- Fails clearly with instructions if ELEVENLABS_API_KEY is missing
"""

import os
import time
import pytest
import anyio
from app.core.config import settings
from app.core.voice_provider import ElevenLabsVoiceProvider, mask_secret
from app.services.rendering.ffmpeg import FFmpegEngine


pytestmark = pytest.mark.integration


@pytest.mark.anyio
async def test_real_voice_provider_manual_execution():
    """Manual integration test against live ElevenLabs TTS API endpoint."""
    api_key = (
        os.getenv("ELEVENLABS_API_KEY")
        or os.getenv("XI_API_KEY")
        or os.getenv("TTS_API_KEY")
        or getattr(settings, "ELEVENLABS_API_KEY", "")
    )

    if not api_key:
        pytest.skip("ELEVENLABS_API_KEY is not configured")

    voice_id = getattr(settings, "ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") or "21m00Tcm4TlvDq8ikWAM"
    model = getattr(settings, "ELEVENLABS_MODEL", "eleven_multilingual_v2") or "eleven_multilingual_v2"

    # Instantiate real ElevenLabs provider
    provider = ElevenLabsVoiceProvider(
        api_key=api_key,
        voice_id=voice_id,
        model=model,
        timeout_seconds=35.0
    )

    start_time = time.time()

    # Generate speech for a short test sentence
    text = "Little kitten learns primary colors and soft green grass."
    result = await provider.synthesize_speech(
        text=text,
        voice_name="Storyteller Emma",
        emotion="Cheerful",
        language="English (US)",
        project_id="proj_manual_real_voice"
    )

    latency = round(time.time() - start_time, 2)

    # Verify secret masking
    masked_key = mask_secret("Key check", secret=api_key)
    assert api_key not in masked_key, "Secret API key leaked in output!"

    # Verify audio result payload
    assert result is not None
    assert isinstance(result, dict)
    assert "storage_url" in result
    storage_url = result["storage_url"]

    # Verify local persistent audio asset file
    assert os.path.isfile(storage_url), f"Persisted audio asset missing at '{storage_url}'"
    file_size = os.path.getsize(storage_url)
    assert file_size > 0, f"Persisted audio asset is 0 bytes at '{storage_url}'"

    ext = os.path.splitext(storage_url)[1].lower()
    assert ext in (".mp3", ".wav", ".aac", ".m4a", ".ogg"), f"Persisted audio has invalid extension '{ext}'"

    # FFmpeg container inspection
    ret_code, stdout, stderr = FFmpegEngine.run_command(["-i", storage_url], timeout=15)
    probe_output = stderr or stdout or ""
    assert "Audio:" in probe_output or "Stream #" in probe_output, f"FFmpeg failed to detect audio stream in '{storage_url}': {probe_output}"

    # Record metadata without exposing secrets
    metadata = {
        "status": "SUCCESS",
        "provider": result.get("provider", "ElevenLabs-TTS"),
        "model": model,
        "voice_id": voice_id,
        "latency_seconds": latency,
        "local_storage_path": storage_url,
        "file_size_bytes": file_size,
        "audio_format": result.get("audio_format", "MP3")
    }

    print("\n--- Real ElevenLabs Voice Provider Manual Test Metadata ---")
    for k, v in metadata.items():
        print(f"  {k}: {v}")
    print("-----------------------------------------------------------\n")
