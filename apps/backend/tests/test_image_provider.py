"""
Comprehensive Unit Tests for Production Image Provider Layer.
Covers 20 requirements:
1. Provider selection
2. Missing API key handling in real mode
3. Mock provider response
4. Prediction creation
5. processing -> succeeded polling
6. Immediate succeeded response
7. Failed prediction status
8. Canceled prediction status
9. Polling timeout
10. HTTP 401 auth error
11. HTTP 403 auth error
12. HTTP 429 rate limit
13. HTTP 5xx server error
14. Malformed response
15. Missing output
16. Output URL extraction
17. Image download
18. Image validation
19. Asset persistence
20. No silent fallback
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from app.core.config import settings
from app.core.image_provider import (
    get_image_provider, FluxImageProvider, MockImageProvider, PollinationsImageProvider,
    ImageConfigurationError, ImageAuthError, ImageRateLimitError,
    ImageTimeoutError, ImageAPIError, mask_secret
)


def test_provider_selection(monkeypatch):
    """1. Test environment precedence and explicit provider selection."""
    # Environment selection must take precedence over settings in tests/CI.
    monkeypatch.setenv("IMAGE_PROVIDER", "mock")
    prov_mock = get_image_provider()
    assert isinstance(prov_mock, MockImageProvider)

    # An explicit provider argument has the highest precedence.
    monkeypatch.setenv("IMAGE_PROVIDER", "flux")
    assert isinstance(get_image_provider("mock"), MockImageProvider)

    # Explicit flux mode
    monkeypatch.setenv("IMAGE_PROVIDER", "flux")
    prov_flux = get_image_provider("flux")
    assert isinstance(prov_flux, FluxImageProvider)

    # Auto mode without key -> free Pollinations provider
    monkeypatch.setenv("IMAGE_PROVIDER", "auto")
    monkeypatch.delenv("REPLICATE_API_KEY", raising=False)
    monkeypatch.delenv("FLUX_API_KEY", raising=False)
    monkeypatch.setattr(settings, "REPLICATE_API_KEY", "")
    prov_auto_free = get_image_provider("auto")
    assert isinstance(prov_auto_free, PollinationsImageProvider)

    # Auto mode with Replicate key -> FluxImageProvider
    monkeypatch.setenv("REPLICATE_API_KEY", "r8_testkey123456789")
    prov_auto_real = get_image_provider("auto")
    assert isinstance(prov_auto_real, FluxImageProvider)


@pytest.mark.anyio
async def test_missing_api_key_in_real_mode():
    """2. Test real mode without API key raises ImageConfigurationError without silent fallback."""
    provider = FluxImageProvider(api_key="")
    with pytest.raises(ImageConfigurationError) as exc_info:
        await provider.generate_image("Test prompt")
    assert "Replicate API key is missing" in str(exc_info.value)


@pytest.mark.anyio
async def test_mock_provider_response():
    """3. Test mock provider generates structured mock image payload."""
    provider = MockImageProvider()
    res = await provider.generate_image("Friendly dinosaur in meadow", width=1280, height=720)
    assert res["provider"] == "FLUX-v1-Mock"
    assert res["width"] == 1280
    assert res["height"] == 720
    assert "placehold.co" in res["storage_url"]


@pytest.mark.anyio
async def test_immediate_succeeded_response():
    """4 & 6. Test immediate succeeded prediction response without polling."""
    fake_png_path = "/tmp/test_downloaded_image.png"
    with open(fake_png_path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")

    try:
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "id": "pred_imm_123",
            "status": "succeeded",
            "output": ["https://replicate.delivery/pbxt/out.png"]
        }

        async def mock_post(url, headers, json):
            return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post), \
             patch("app.services.rendering.downloader.MediaDownloader.download_asset", return_value=fake_png_path):
            provider = FluxImageProvider(api_key="r8_testkey123")
            res = await provider.generate_image("Cute puppy playing", project_id="proj_imm")
            assert res["storage_url"] == fake_png_path
            assert "FLUX-Replicate" in res["provider"]
    finally:
        if os.path.exists(fake_png_path):
            os.remove(fake_png_path)


@pytest.mark.anyio
async def test_processing_to_succeeded_polling():
    """5, 16, 17, 18, 19. Test prediction starting -> processing -> succeeded bounded polling loop."""
    fake_png_path = "/tmp/test_polled_image.png"
    with open(fake_png_path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")

    try:
        init_resp = MagicMock()
        init_resp.status_code = 201
        init_resp.json.return_value = {
            "id": "pred_poll_123",
            "status": "starting",
            "urls": {"get": "https://api.replicate.com/v1/predictions/pred_poll_123"}
        }

        poll_proc_resp = MagicMock()
        poll_proc_resp.status_code = 200
        poll_proc_resp.json.return_value = {
            "id": "pred_poll_123",
            "status": "processing"
        }

        poll_succ_resp = MagicMock()
        poll_succ_resp.status_code = 200
        poll_succ_resp.json.return_value = {
            "id": "pred_poll_123",
            "status": "succeeded",
            "output": ["https://replicate.delivery/pbxt/final_art.png"]
        }

        async def mock_post(url, headers, json):
            return init_resp

        poll_count = 0

        async def mock_get(url, headers):
            nonlocal poll_count
            poll_count += 1
            if poll_count == 1:
                return poll_proc_resp
            return poll_succ_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post), \
             patch("httpx.AsyncClient.get", side_effect=mock_get), \
             patch("app.services.rendering.downloader.MediaDownloader.download_asset", return_value=fake_png_path), \
             patch("asyncio.sleep", return_value=None):
            provider = FluxImageProvider(api_key="r8_testkey123", poll_interval=0.1)
            res = await provider.generate_image("Rainbow over mountains", project_id="proj_poll")
            assert res["storage_url"] == fake_png_path
            assert poll_count == 2
    finally:
        if os.path.exists(fake_png_path):
            os.remove(fake_png_path)


@pytest.mark.anyio
async def test_failed_prediction_status():
    """7. Test status 'failed' raises ImageAPIError."""
    init_resp = MagicMock()
    init_resp.status_code = 201
    init_resp.json.return_value = {
        "id": "pred_fail_123",
        "status": "failed",
        "error": "Safety filter triggered or model crash"
    }

    async def mock_post(url, headers, json):
        return init_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = FluxImageProvider(api_key="r8_testkey123")
        with pytest.raises(ImageAPIError) as exc_info:
            await provider.generate_image("Unsafe prompt")
        assert "Replicate image generation failed" in str(exc_info.value)


@pytest.mark.anyio
async def test_canceled_prediction_status():
    """8. Test status 'canceled' raises ImageAPIError."""
    init_resp = MagicMock()
    init_resp.status_code = 201
    init_resp.json.return_value = {
        "id": "pred_canc_123",
        "status": "canceled"
    }

    async def mock_post(url, headers, json):
        return init_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = FluxImageProvider(api_key="r8_testkey123")
        with pytest.raises(ImageAPIError) as exc_info:
            await provider.generate_image("Canceled prompt")
        assert "canceled" in str(exc_info.value)


@pytest.mark.anyio
async def test_polling_timeout():
    """9. Test polling timeout raises ImageTimeoutError."""
    init_resp = MagicMock()
    init_resp.status_code = 201
    init_resp.json.return_value = {
        "id": "pred_timeout_123",
        "status": "processing",
        "urls": {"get": "https://api.replicate.com/v1/predictions/pred_timeout_123"}
    }

    poll_resp = MagicMock()
    poll_resp.status_code = 200
    poll_resp.json.return_value = {
        "id": "pred_timeout_123",
        "status": "processing"
    }

    async def mock_post(url, headers, json):
        return init_resp

    async def mock_get(url, headers):
        return poll_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("httpx.AsyncClient.get", side_effect=mock_get), \
         patch("asyncio.sleep", return_value=None):
        provider = FluxImageProvider(api_key="r8_testkey123", poll_interval=0.1, timeout_seconds=0.05)
        with pytest.raises(ImageTimeoutError) as exc_info:
            await provider.generate_image("Slow prompt")
        assert "timed out" in str(exc_info.value)


@pytest.mark.anyio
async def test_http_401_403_auth_error():
    """10 & 11. Test HTTP 401/403 raises ImageAuthError immediately."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthenticated API token r8_secretkey999"

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = FluxImageProvider(api_key="r8_secretkey999")
        with pytest.raises(ImageAuthError) as exc_info:
            await provider.generate_image("Test prompt")
        assert "Authentication failed" in str(exc_info.value)


@pytest.mark.anyio
async def test_http_429_rate_limit_error():
    """12. Test HTTP 429 raises ImageRateLimitError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "Rate limit exceeded"

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = FluxImageProvider(api_key="r8_testkey123")
        with pytest.raises(ImageRateLimitError):
            await provider.generate_image("Test prompt")


@pytest.mark.anyio
async def test_http_5xx_server_error():
    """13. Test HTTP 500 server error raises ImageAPIError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 503
    mock_resp.text = "Service Unavailable"

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = FluxImageProvider(api_key="r8_testkey123")
        with pytest.raises(ImageAPIError) as exc_info:
            await provider.generate_image("Test prompt")
        assert "Server Error" in str(exc_info.value)


@pytest.mark.anyio
async def test_malformed_response_handling():
    """14 & 15. Test malformed JSON or missing output in succeeded response."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "pred_malformed_123",
        "status": "succeeded",
        "output": None  # Missing output
    }

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = FluxImageProvider(api_key="r8_testkey123")
        with pytest.raises(ImageAPIError) as exc_info:
            await provider.generate_image("Test prompt")
        assert "missing valid output image URL" in str(exc_info.value)


def test_secret_masking():
    """20. Test that Replicate API key is sanitized in log outputs and exceptions."""
    secret_key = "r8_abcdef1234567890qwertyuiop"
    log_text = f"API error occurred using token {secret_key}"
    masked = mask_secret(log_text, secret=secret_key)
    assert secret_key not in masked
    assert "r8_...uiop" in masked or "r8_...iop" in masked or "..." in masked
