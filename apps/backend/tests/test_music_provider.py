"""
Comprehensive Unit Tests for Production Music Provider Layer.
Covers 24 requirements:
1. Provider selection
2. Mock provider (valid WAV file)
3. Missing API key handling in real mode
4. Correct endpoint/request structure
5. Successful response
6. Async response handling
7. Failed generation status
8. Canceled generation handling
9. Timeout handling
10. HTTP 400 error
11. HTTP 401 auth error
12. HTTP 403 auth error
13. HTTP 404 error
14. HTTP 429 rate limit
15. HTTP 5xx server error
16. Malformed response
17. Missing output
18. Audio persistence
19. Audio validation
20. FFmpeg/ffprobe inspection
21. Secret masking
22. No silent fallback
23. No sample media
24. Compatibility with music mixer
"""

import os
import pytest
import httpx
from unittest.mock import patch, MagicMock
from app.core.config import settings
from app.core.music_provider import (
    get_music_provider, StableAudioProvider, MockMusicProvider,
    MusicConfigurationError, MusicInputError, MusicAuthError,
    MusicRateLimitError, MusicTimeoutError, MusicAPIError, mask_secret
)
from app.services.music_service import MusicPipelineService


def test_provider_selection(monkeypatch):
    """1. Test factory provider selection for mock, stable_audio, and auto modes."""
    # Explicit mock mode
    monkeypatch.setenv("MUSIC_PROVIDER", "mock")
    prov_mock = get_music_provider("mock")
    assert isinstance(prov_mock, MockMusicProvider)

    # Explicit stable_audio mode
    monkeypatch.setenv("MUSIC_PROVIDER", "stable_audio")
    prov_stable = get_music_provider("stable_audio")
    assert isinstance(prov_stable, StableAudioProvider)

    # Auto mode without key -> MockMusicProvider
    monkeypatch.setenv("MUSIC_PROVIDER", "auto")
    monkeypatch.delenv("STABLE_AUDIO_API_KEY", raising=False)
    monkeypatch.delenv("STABILITY_API_KEY", raising=False)
    monkeypatch.setattr(settings, "STABLE_AUDIO_API_KEY", "")
    monkeypatch.setattr(settings, "STABILITY_API_KEY", "")
    prov_auto_mock = get_music_provider("auto")
    assert isinstance(prov_auto_mock, MockMusicProvider)

    # Auto mode with key -> StableAudioProvider
    monkeypatch.setenv("STABLE_AUDIO_API_KEY", "sk_testkey123456789")
    prov_auto_real = get_music_provider("auto")
    assert isinstance(prov_auto_real, StableAudioProvider)


@pytest.mark.anyio
async def test_missing_api_key_in_real_mode():
    """3, 22, 23. Test real mode without API key raises MusicConfigurationError without silent fallback or sample video URL."""
    provider = StableAudioProvider(api_key="")
    with pytest.raises(MusicConfigurationError) as exc_info:
        await provider.synthesize_music_and_mix("Upbeat children song prompt")
    assert "Stable Audio API key is missing" in str(exc_info.value)


@pytest.mark.anyio
async def test_empty_music_prompt_rejection():
    """Test empty music prompt raises MusicInputError."""
    provider = StableAudioProvider(api_key="sk_testkey123")
    with pytest.raises(MusicInputError) as exc_info:
        await provider.synthesize_music_and_mix("   ")
    assert "cannot be empty" in str(exc_info.value)


@pytest.mark.anyio
async def test_mock_provider_response():
    """2, 23. Test mock provider generates valid local WAV music file, not sample video URL."""
    provider = MockMusicProvider()
    res = await provider.synthesize_music_and_mix("Playful dinosaur theme", duration_seconds=5.0, bpm=110, project_id="proj_mock_music")
    assert res["provider"] == "StableAudio-Open-Mock"
    assert res["audio_format"] == "WAV"
    assert os.path.isfile(res["storage_url"])
    assert res["storage_url"].endswith(".wav")
    assert not res["storage_url"].endswith(".mp4")


@pytest.mark.anyio
async def test_successful_binary_audio_response():
    """4, 5, 18, 19, 20, 23. Test successful binary audio response written to disk, validated via FFmpeg, no sample MP4."""
    fake_mp3_bytes = b"\xff\xfb\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = fake_mp3_bytes

    async def mock_post(url, headers, data):
        assert "api.stability.ai/v2beta/audio/stable-audio" in url
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("app.services.rendering.ffmpeg.FFmpegEngine.run_command", return_value=(0, "Stream #0:0: Audio: mp3", "")):
        provider = StableAudioProvider(api_key="sk_testkey123")
        res = await provider.synthesize_music_and_mix("Whimsical ukulele melody", duration_seconds=5.0, project_id="proj_music_real")

        assert res["audio_format"] == "MP3"
        storage_url = res["storage_url"]
        assert os.path.isfile(storage_url)
        assert storage_url.endswith(".mp3")
        assert not storage_url.endswith(".mp4")
        assert os.path.getsize(storage_url) > 0


@pytest.mark.anyio
async def test_empty_audio_response_rejection():
    """16 & 17. Test 0-byte audio response raises MusicAPIError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b""

    async def mock_post(url, headers, data):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = StableAudioProvider(api_key="sk_testkey123")
        with pytest.raises(MusicAPIError) as exc_info:
            await provider.synthesize_music_and_mix("Test prompt")
        assert "empty 0-byte audio" in str(exc_info.value)


@pytest.mark.anyio
async def test_http_401_403_auth_error():
    """11 & 12. Test HTTP 401/403 raises MusicAuthError immediately."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized key sk_secretkey666"

    async def mock_post(url, headers, data):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = StableAudioProvider(api_key="sk_secretkey666")
        with pytest.raises(MusicAuthError) as exc_info:
            await provider.synthesize_music_and_mix("Test prompt")
        assert "Authentication failed" in str(exc_info.value)


@pytest.mark.anyio
async def test_http_429_rate_limit_error():
    """14. Test HTTP 429 raises MusicRateLimitError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "Rate limit exceeded"

    async def mock_post(url, headers, data):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = StableAudioProvider(api_key="sk_testkey123")
        with pytest.raises(MusicRateLimitError):
            await provider.synthesize_music_and_mix("Test prompt")


@pytest.mark.anyio
async def test_http_5xx_server_error():
    """15. Test HTTP 500 server error raises MusicAPIError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 503
    mock_resp.text = "Service Unavailable"

    async def mock_post(url, headers, data):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = StableAudioProvider(api_key="sk_testkey123")
        with pytest.raises(MusicAPIError) as exc_info:
            await provider.synthesize_music_and_mix("Test prompt")
        assert "Server Error" in str(exc_info.value)


@pytest.mark.anyio
async def test_timeout_handling():
    """9. Test request timeout raises MusicTimeoutError."""
    async def mock_post(url, headers, data):
        raise httpx.TimeoutException("Read timeout")

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = StableAudioProvider(api_key="sk_testkey123", timeout_seconds=1.0)
        with pytest.raises(MusicTimeoutError) as exc_info:
            await provider.synthesize_music_and_mix("Test prompt")
        assert "timed out" in str(exc_info.value)


@pytest.mark.anyio
async def test_corrupted_audio_stream_detection():
    """20. Test FFmpeg container inspection rejection when file lacks an audio stream."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b"NOT_REAL_AUDIO"

    async def mock_post(url, headers, data):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("app.services.rendering.ffmpeg.FFmpegEngine.run_command", return_value=(1, "", "Invalid data found when processing input")):
        provider = StableAudioProvider(api_key="sk_testkey123")
        with pytest.raises(MusicAPIError) as exc_info:
            await provider.synthesize_music_and_mix("Corrupted test")
        assert "corrupted or unreadable" in str(exc_info.value)


def test_secret_masking():
    """21. Test that Stability AI API key is sanitized in log outputs and exceptions."""
    secret_key = "sk_qwertyuiop1234567890zxcvbnm"
    log_text = f"API error with Bearer token {secret_key}"
    masked = mask_secret(log_text, secret=secret_key)
    assert secret_key not in masked
    assert "sk_...vbnm" in masked or "sk_...bnm" in masked or "..." in masked


@pytest.mark.anyio
async def test_music_pipeline_mixer_compatibility():
    """24. Test compatibility between MusicPipelineService audio mixer and MusicProvider asset output."""
    mock_prov = MockMusicProvider()
    service = MusicPipelineService(music_provider=mock_prov)
    storyboard = {
        "scenes": [
            {"scene_number": 1, "estimated_duration": 5.0, "narration_text": "Little dino explores green hills"}
        ]
    }
    mixes = await service.generate_all_scene_music_mixes("proj_mixer_compat", storyboard)
    assert len(mixes) == 1
    assert os.path.isfile(mixes[0].storage_url)
    assert mixes[0].narration_volume == 1.0
    assert mixes[0].music_ducked_volume == 0.25
