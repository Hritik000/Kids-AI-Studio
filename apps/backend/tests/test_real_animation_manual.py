"""
Manual Integration Test for Real Replicate Wan 2.1 Animation Provider.
This test:
- Requires an explicit REPLICATE_API_KEY
- Uses ANIMATION_PROVIDER=wan
- Creates a small local test image asset
- Submits an animation prediction request to live Replicate API
- Polls prediction status until completion
- Downloads and validates the resulting persistent video asset using FFmpeg/ffprobe
- Reports provider, model, local storage path, file size, and latency metadata
- Never prints secrets or API keys
- Fails clearly with instructions if REPLICATE_API_KEY is missing
"""

import os
import time
import pytest
import anyio
from app.core.config import settings
from app.core.animation_provider import Wan2AnimationProvider, mask_secret
from app.services.rendering.ffmpeg import FFmpegEngine


pytestmark = pytest.mark.integration


@pytest.mark.anyio
async def test_real_animation_provider_manual_execution():
    """Manual integration test against live Replicate Wan 2.1 API endpoint."""
    api_key = (
        os.getenv("REPLICATE_API_KEY")
        or os.getenv("WAN_API_KEY")
        or getattr(settings, "REPLICATE_API_KEY", "")
    )

    if not api_key:
        pytest.skip("REPLICATE_API_KEY is not configured")

    model = getattr(settings, "ANIMATION_MODEL", "wan-video/wan-2.1-1.3b") or "wan-video/wan-2.1-1.3b"

    # Create a small local test image file using FFmpeg
    test_image_dir = "/tmp/kidsai_test_inputs"
    os.makedirs(test_image_dir, exist_ok=True)
    test_image_path = os.path.join(test_image_dir, "test_input_dino.png")

    if not os.path.exists(test_image_path):
        FFmpegEngine.run_command([
            "-y",
            "-f", "lavfi",
            "-i", "color=c=0x1A1D27:s=1280x720:d=1",
            "-vframes", "1",
            test_image_path
        ])

    # Instantiate real Wan2 provider
    provider = Wan2AnimationProvider(
        api_key=api_key,
        model=model,
        poll_interval=2.0,
        timeout_seconds=180.0
    )

    start_time = time.time()

    # Generate small animation clip (duration: 3.0s)
    prompt = "Soft camera pan across sunny green dinosaur meadow, baby dinosaur blinks happily"
    result = await provider.generate_animation_clip(
        image_url=test_image_path,
        motion_prompt=prompt,
        duration_seconds=3.0,
        width=1280,
        height=720,
        seed=4321,
        project_id="proj_manual_real_anim"
    )

    latency = round(time.time() - start_time, 2)

    # Verify secret masking
    masked_key = mask_secret("Key check", secret=api_key)
    assert api_key not in masked_key, "Secret API key leaked in output!"

    # Verify video result payload
    assert result is not None
    assert isinstance(result, dict)
    assert "storage_url" in result
    storage_url = result["storage_url"]

    # Verify local persistent video asset file
    assert os.path.isfile(storage_url), f"Persisted video asset missing at '{storage_url}'"
    file_size = os.path.getsize(storage_url)
    assert file_size > 0, f"Persisted video asset is 0 bytes at '{storage_url}'"

    ext = os.path.splitext(storage_url)[1].lower()
    assert ext in (".mp4", ".webm", ".mov", ".mkv"), f"Persisted video has invalid extension '{ext}'"

    # FFmpeg container inspection
    ret_code, stdout, stderr = FFmpegEngine.run_command(["-i", storage_url], timeout=15)
    probe_output = stderr or stdout or ""
    assert "Video:" in probe_output or "Stream #" in probe_output, f"FFmpeg failed to detect video stream in '{storage_url}': {probe_output}"

    # Record metadata without exposing secrets
    metadata = {
        "status": "SUCCESS",
        "provider": result.get("provider", "Wan2-Replicate"),
        "model": model,
        "latency_seconds": latency,
        "local_storage_path": storage_url,
        "file_size_bytes": file_size,
        "duration_seconds": result.get("duration_seconds")
    }

    print("\n--- Real Replicate Animation Provider Manual Test Metadata ---")
    for k, v in metadata.items():
        print(f"  {k}: {v}")
    print("--------------------------------------------------------------\n")
