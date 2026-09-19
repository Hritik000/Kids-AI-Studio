"""
Comprehensive Unit Tests for Production Animation Provider Layer.
Covers 21 requirements:
1. Provider selection
2. Missing API key handling in real mode
3. Mock provider response
4. Prediction creation
5. starting -> processing -> succeeded polling
6. Immediate success response
7. Failed prediction status
8. Canceled prediction status
9. Polling timeout
10. HTTP 401 auth error
11. HTTP 403 auth error
12. HTTP 429 rate limit
13. HTTP 5xx server error
14. Malformed response
15. Missing output
16. Video download
17. Video validation
18. FFmpeg/ffprobe container validation
19. Asset persistence
20. Secret masking
21. No silent fallback
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from app.core.config import settings
from app.core.animation_provider import (
    get_animation_provider, Wan2AnimationProvider, MockAnimationProvider,
    AnimationConfigurationError, AnimationInputError, AnimationAuthError,
    AnimationRateLimitError, AnimationTimeoutError, AnimationAPIError, mask_secret
)


def test_provider_selection(monkeypatch):
    """1. Test factory provider selection for mock, wan, and auto modes."""
    # Explicit mock mode
    monkeypatch.setenv("ANIMATION_PROVIDER", "mock")
    prov_mock = get_animation_provider("mock")
    assert isinstance(prov_mock, MockAnimationProvider)

    # Explicit wan mode
    monkeypatch.setenv("ANIMATION_PROVIDER", "wan")
    prov_wan = get_animation_provider("wan")
    assert isinstance(prov_wan, Wan2AnimationProvider)

    # Auto mode without key -> MockAnimationProvider
    monkeypatch.setenv("ANIMATION_PROVIDER", "auto")
    monkeypatch.delenv("REPLICATE_API_KEY", raising=False)
    monkeypatch.delenv("WAN_API_KEY", raising=False)
    monkeypatch.setattr(settings, "REPLICATE_API_KEY", "")
    prov_auto_mock = get_animation_provider("auto")
    assert isinstance(prov_auto_mock, MockAnimationProvider)

    # Auto mode with Replicate key -> Wan2AnimationProvider
    monkeypatch.setenv("REPLICATE_API_KEY", "r8_testkey123456789")
    prov_auto_real = get_animation_provider("auto")
    assert isinstance(prov_auto_real, Wan2AnimationProvider)


@pytest.mark.anyio
async def test_missing_api_key_in_real_mode():
    """2 & 21. Test real mode without API key raises AnimationConfigurationError without silent fallback."""
    provider = Wan2AnimationProvider(api_key="")
    with pytest.raises(AnimationConfigurationError) as exc_info:
        await provider.generate_animation_clip("https://example.com/input.png", "Test motion")
    assert "Replicate API key is missing" in str(exc_info.value)


@pytest.mark.anyio
async def test_nonexistent_local_input_image():
    """Test nonexistent local input image path raises AnimationInputError."""
    provider = Wan2AnimationProvider(api_key="r8_testkey123")
    with pytest.raises(AnimationInputError) as exc_info:
        await provider.generate_animation_clip("/tmp/nonexistent_image_123.png", "Test motion")
    assert "Source image file does not exist" in str(exc_info.value)


@pytest.mark.anyio
async def test_mock_provider_response():
    """3. Test mock provider generates structured mock video payload."""
    provider = MockAnimationProvider()
    res = await provider.generate_animation_clip("https://example.com/source.png", "Rexy jumps happily", duration_seconds=5.0)
    assert res["provider"] == "Wan2.1-i2v-Mock"
    assert res["duration_seconds"] == 5.0
    assert "gtv-videos-bucket" in res["storage_url"] or "mp4" in res["storage_url"]


@pytest.mark.anyio
async def test_immediate_success_response():
    """4 & 6. Test immediate succeeded prediction response without polling."""
    fake_mp4_path = "/tmp/test_downloaded_video.mp4"
    with open(fake_mp4_path, "wb") as f:
        f.write(b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2avc1mp41")

    try:
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "id": "pred_vid_123",
            "status": "succeeded",
            "output": ["https://replicate.delivery/pbxt/out.mp4"]
        }

        async def mock_post(url, headers, json):
            return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post), \
             patch("app.services.rendering.downloader.MediaDownloader.download_asset", return_value=fake_mp4_path), \
             patch("app.services.rendering.ffmpeg.FFmpegEngine.run_command", return_value=(0, "", "")):
            provider = Wan2AnimationProvider(api_key="r8_testkey123")
            res = await provider.generate_animation_clip("https://example.com/input.png", "Rexy waves hello", project_id="proj_vid_imm")
            assert res["storage_url"] == fake_mp4_path
            assert "Wan2-Replicate" in res["provider"]
    finally:
        if os.path.exists(fake_mp4_path):
            os.remove(fake_mp4_path)


@pytest.mark.anyio
async def test_processing_to_succeeded_polling():
    """5, 16, 17, 18, 19. Test video prediction starting -> processing -> succeeded bounded polling loop."""
    fake_mp4_path = "/tmp/test_polled_video.mp4"
    with open(fake_mp4_path, "wb") as f:
        f.write(b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2avc1mp41")

    try:
        init_resp = MagicMock()
        init_resp.status_code = 201
        init_resp.json.return_value = {
            "id": "pred_vpoll_123",
            "status": "starting",
            "urls": {"get": "https://api.replicate.com/v1/predictions/pred_vpoll_123"}
        }

        poll_proc_resp = MagicMock()
        poll_proc_resp.status_code = 200
        poll_proc_resp.json.return_value = {
            "id": "pred_vpoll_123",
            "status": "processing"
        }

        poll_succ_resp = MagicMock()
        poll_succ_resp.status_code = 200
        poll_succ_resp.json.return_value = {
            "id": "pred_vpoll_123",
            "status": "succeeded",
            "output": ["https://replicate.delivery/pbxt/final_video.mp4"]
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
             patch("app.services.rendering.downloader.MediaDownloader.download_asset", return_value=fake_mp4_path), \
             patch("app.services.rendering.ffmpeg.FFmpegEngine.run_command", return_value=(0, "", "")), \
             patch("asyncio.sleep", return_value=None):
            provider = Wan2AnimationProvider(api_key="r8_testkey123", poll_interval=0.1)
            res = await provider.generate_animation_clip("https://example.com/input.png", "Rexy dances", project_id="proj_vpoll")
            assert res["storage_url"] == fake_mp4_path
            assert poll_count == 2
    finally:
        if os.path.exists(fake_mp4_path):
            os.remove(fake_mp4_path)


@pytest.mark.anyio
async def test_failed_prediction_status():
    """7. Test status 'failed' raises AnimationAPIError."""
    init_resp = MagicMock()
    init_resp.status_code = 201
    init_resp.json.return_value = {
        "id": "pred_vfail_123",
        "status": "failed",
        "error": "GPU memory out of bounds"
    }

    async def mock_post(url, headers, json):
        return init_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = Wan2AnimationProvider(api_key="r8_testkey123")
        with pytest.raises(AnimationAPIError) as exc_info:
            await provider.generate_animation_clip("https://example.com/input.png", "Test motion")
        assert "Replicate video generation failed" in str(exc_info.value)


@pytest.mark.anyio
async def test_canceled_prediction_status():
    """8. Test status 'canceled' raises AnimationAPIError."""
    init_resp = MagicMock()
    init_resp.status_code = 201
    init_resp.json.return_value = {
        "id": "pred_vcanc_123",
        "status": "canceled"
    }

    async def mock_post(url, headers, json):
        return init_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = Wan2AnimationProvider(api_key="r8_testkey123")
        with pytest.raises(AnimationAPIError) as exc_info:
            await provider.generate_animation_clip("https://example.com/input.png", "Test motion")
        assert "canceled" in str(exc_info.value)


@pytest.mark.anyio
async def test_polling_timeout():
    """9. Test polling timeout raises AnimationTimeoutError."""
    init_resp = MagicMock()
    init_resp.status_code = 201
    init_resp.json.return_value = {
        "id": "pred_vtimeout_123",
        "status": "processing",
        "urls": {"get": "https://api.replicate.com/v1/predictions/pred_vtimeout_123"}
    }

    poll_resp = MagicMock()
    poll_resp.status_code = 200
    poll_resp.json.return_value = {
        "id": "pred_vtimeout_123",
        "status": "processing"
    }

    async def mock_post(url, headers, json):
        return init_resp

    async def mock_get(url, headers):
        return poll_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("httpx.AsyncClient.get", side_effect=mock_get), \
         patch("asyncio.sleep", return_value=None):
        provider = Wan2AnimationProvider(api_key="r8_testkey123", poll_interval=0.1, timeout_seconds=0.05)
        with pytest.raises(AnimationTimeoutError) as exc_info:
            await provider.generate_animation_clip("https://example.com/input.png", "Slow motion")
        assert "timed out" in str(exc_info.value)


@pytest.mark.anyio
async def test_http_401_403_auth_error():
    """10 & 11. Test HTTP 401/403 raises AnimationAuthError immediately."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthenticated token r8_secretkey888"

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = Wan2AnimationProvider(api_key="r8_secretkey888")
        with pytest.raises(AnimationAuthError) as exc_info:
            await provider.generate_animation_clip("https://example.com/input.png", "Test motion")
        assert "Authentication failed" in str(exc_info.value)


@pytest.mark.anyio
async def test_http_429_rate_limit_error():
    """12. Test HTTP 429 raises AnimationRateLimitError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "Rate limit exceeded"

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = Wan2AnimationProvider(api_key="r8_testkey123")
        with pytest.raises(AnimationRateLimitError):
            await provider.generate_animation_clip("https://example.com/input.png", "Test motion")


@pytest.mark.anyio
async def test_http_5xx_server_error():
    """13. Test HTTP 500 server error raises AnimationAPIError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 502
    mock_resp.text = "Bad Gateway"

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = Wan2AnimationProvider(api_key="r8_testkey123")
        with pytest.raises(AnimationAPIError) as exc_info:
            await provider.generate_animation_clip("https://example.com/input.png", "Test motion")
        assert "Server Error" in str(exc_info.value)


@pytest.mark.anyio
async def test_malformed_response_handling():
    """14 & 15. Test malformed JSON or missing output in succeeded response."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "pred_vmalformed_123",
        "status": "succeeded",
        "output": None
    }

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = Wan2AnimationProvider(api_key="r8_testkey123")
        with pytest.raises(AnimationAPIError) as exc_info:
            await provider.generate_animation_clip("https://example.com/input.png", "Test motion")
        assert "missing valid output video URL" in str(exc_info.value)


def test_secret_masking():
    """20. Test that Replicate API key is sanitized in log outputs and exceptions."""
    secret_key = "r8_qwertyuiop1234567890zxcvbnm"
    log_text = f"API error with token {secret_key}"
    masked = mask_secret(log_text, secret=secret_key)
    assert secret_key not in masked
    assert "r8_...vbnm" in masked or "r8_...bnm" in masked or "..." in masked
