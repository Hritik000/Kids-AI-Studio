"""
Manual Integration Test for Real Stability AI Stable Audio Provider.
This test:
- Requires an explicit STABLE_AUDIO_API_KEY or STABILITY_API_KEY
- Uses MUSIC_PROVIDER=stable_audio
- Submits a short music generation prompt to live Stability AI Stable Audio REST API
- Receives binary audio bytes (audio/mpeg)
- Saves the resulting persistent MP3 music asset to disk
- Validates the audio file using FFmpeg/ffprobe
- Reports provider, model, local storage path, file size, and latency metadata
- Never prints secrets or API keys
- Fails clearly with instructions if API key is missing
"""

import os
import time
import pytest
import anyio
from app.core.config import settings
from app.core.music_provider import StableAudioProvider, mask_secret
from app.services.rendering.ffmpeg import FFmpegEngine


@pytest.mark.anyio
async def test_real_music_provider_manual_execution():
    """Manual integration test against live Stability AI Stable Audio REST API endpoint."""
    api_key = (
        os.getenv("STABLE_AUDIO_API_KEY")
        or os.getenv("STABILITY_API_KEY")
        or getattr(settings, "STABLE_AUDIO_API_KEY", "")
        or getattr(settings, "STABILITY_API_KEY", "")
    )

    if not api_key:
        pytest.fail(
            "MANUAL STABLE AUDIO TEST SKIPPED / FAILED: STABLE_AUDIO_API_KEY is missing.\n"
            "To run this manual integration test against live Stability AI API:\n"
            "  1. Obtain an API key at https://platform.stability.ai\n"
            "  2. Run: STABLE_AUDIO_API_KEY=sk-... MUSIC_PROVIDER=stable_audio PYTHONPATH=. ./.venv/bin/pytest tests/test_real_music_manual.py\n"
            "NOTE: This test calls live Stability AI audio generation which may consume API credits."
        )

    model = getattr(settings, "MUSIC_MODEL", "stable-audio") or "stable-audio"

    # Instantiate real Stable Audio provider
    provider = StableAudioProvider(
        api_key=api_key,
        model=model,
        timeout_seconds=60.0
    )

    start_time = time.time()

    # Generate a short music clip (duration: 3.0s)
    prompt = "Upbeat cheerful acoustic ukulele melody, bright playful children adventure theme"
    result = await provider.synthesize_music_and_mix(
        prompt=prompt,
        duration_seconds=3.0,
        bpm=110,
        project_id="proj_manual_real_music"
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
    assert os.path.isfile(storage_url), f"Persisted music asset missing at '{storage_url}'"
    file_size = os.path.getsize(storage_url)
    assert file_size > 0, f"Persisted music asset is 0 bytes at '{storage_url}'"

    ext = os.path.splitext(storage_url)[1].lower()
    assert ext in (".mp3", ".wav", ".aac", ".m4a", ".ogg"), f"Persisted music has invalid extension '{ext}'"

    # FFmpeg container inspection
    ret_code, stdout, stderr = FFmpegEngine.run_command(["-i", storage_url], timeout=15)
    probe_output = stderr or stdout or ""
    assert "Audio:" in probe_output or "Stream #" in probe_output, f"FFmpeg failed to detect audio stream in '{storage_url}': {probe_output}"

    # Record metadata without exposing secrets
    metadata = {
        "status": "SUCCESS",
        "provider": result.get("provider", "StableAudio-API"),
        "model": model,
        "latency_seconds": latency,
        "local_storage_path": storage_url,
        "file_size_bytes": file_size,
        "audio_format": result.get("audio_format", "MP3")
    }

    print("\n--- Real Stability AI Music Provider Manual Test Metadata ---")
    for k, v in metadata.items():
        print(f"  {k}: {v}")
    print("-------------------------------------------------------------\n")
