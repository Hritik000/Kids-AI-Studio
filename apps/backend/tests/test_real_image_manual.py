"""
Manual Integration Test for Real Replicate FLUX Image Provider.
This test:
- Requires an explicit REPLICATE_API_KEY
- Uses IMAGE_PROVIDER=flux
- Submits one small test image generation request to live Replicate API
- Polls prediction status until completion
- Downloads and validates the resulting persistent image asset
- Reports provider, model, local storage path, and latency metadata
- Never prints secrets or API keys
- Fails clearly with instructions if REPLICATE_API_KEY is missing
"""

import os
import time
import pytest
import anyio
from app.core.config import settings
from app.core.image_provider import FluxImageProvider, mask_secret


@pytest.mark.anyio
async def test_real_image_provider_manual_execution():
    """Manual integration test against live Replicate FLUX API endpoint."""
    api_key = (
        os.getenv("REPLICATE_API_KEY")
        or os.getenv("FLUX_API_KEY")
        or os.getenv("IMAGE_API_KEY")
        or getattr(settings, "REPLICATE_API_KEY", "")
    )

    if not api_key:
        pytest.fail(
            "MANUAL REPLICATE IMAGE TEST SKIPPED / FAILED: REPLICATE_API_KEY is missing.\n"
            "To run this manual integration test against live Replicate API:\n"
            "  1. Obtain an API key at https://replicate.com/account/api-tokens\n"
            "  2. Run: REPLICATE_API_KEY=r8_... IMAGE_PROVIDER=flux PYTHONPATH=. ./.venv/bin/pytest tests/test_real_image_manual.py\n"
        )

    model = getattr(settings, "IMAGE_MODEL", "black-forest-labs/flux-schnell") or "black-forest-labs/flux-schnell"

    # Instantiate real Flux provider
    provider = FluxImageProvider(
        api_key=api_key,
        model=model,
        poll_interval=1.5,
        timeout_seconds=90.0
    )

    start_time = time.time()

    # Generate one test image
    prompt = "Cute friendly green baby dinosaur standing in a sunny flower meadow, 3D Pixar render style"
    result = await provider.generate_image(
        prompt=prompt,
        negative_prompt="blurry, scary, dark",
        width=1280,
        height=720,
        seed=12345,
        project_id="proj_manual_real_image"
    )

    latency = round(time.time() - start_time, 2)

    # Verify secret masking
    masked_key = mask_secret("Key check", secret=api_key)
    assert api_key not in masked_key, "Secret API key leaked in output!"

    # Verify image result payload
    assert result is not None
    assert isinstance(result, dict)
    assert "storage_url" in result
    storage_url = result["storage_url"]

    # Verify local persistent asset file
    assert os.path.isfile(storage_url), f"Persisted image asset missing at '{storage_url}'"
    file_size = os.path.getsize(storage_url)
    assert file_size > 0, f"Persisted image asset is 0 bytes at '{storage_url}'"

    ext = os.path.splitext(storage_url)[1].lower()
    assert ext in (".png", ".jpg", ".jpeg", ".webp"), f"Persisted image has invalid extension '{ext}'"

    # Record metadata without exposing secrets
    metadata = {
        "status": "SUCCESS",
        "provider": result.get("provider", "FLUX-Replicate"),
        "model": model,
        "latency_seconds": latency,
        "local_storage_path": storage_url,
        "file_size_bytes": file_size,
        "image_dimensions": f"{result.get('width')}x{result.get('height')}"
    }

    print("\n--- Real Replicate Image Provider Manual Test Metadata ---")
    for k, v in metadata.items():
        print(f"  {k}: {v}")
    print("----------------------------------------------------------\n")
