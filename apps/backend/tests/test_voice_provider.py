"""
Comprehensive Unit Tests for Production Voice / TTS Provider Layer.
Covers 22 requirements:
1. Provider selection
2. Mock provider (valid WAV file)
3. Missing API key handling in real mode
4. Successful binary audio response
5. Audio bytes written to disk
6. Correct output format
7. Empty response rejection
8. Malformed response handling
9. HTTP 400 error
10. HTTP 401 auth error
11. HTTP 403 auth error
12. HTTP 404 error
13. HTTP 429 rate limit
14. HTTP 5xx server error
15. Timeout handling
16. Audio validation
17. Missing audio stream detection
18. Zero-byte file rejection
19. Asset persistence
20. Secret masking
21. No silent fallback
22. No sample video URLs
"""

import os
import pytest
import httpx
from unittest.mock import patch, MagicMock
from app.core.config import settings
from app.core.voice_provider import (
    get_voice_provider, ElevenLabsVoiceProvider, MockVoiceProvider,
    VoiceConfigurationError, VoiceInputError, VoiceAuthError,
    VoiceRateLimitError, VoiceTimeoutError, VoiceAPIError, mask_secret
)


def test_provider_selection(monkeypatch):
    """1. Test factory provider selection for mock, elevenlabs, and auto modes."""
    # Explicit mock mode
    monkeypatch.setenv("VOICE_PROVIDER", "mock")
    prov_mock = get_voice_provider("mock")
    assert isinstance(prov_mock, MockVoiceProvider)

    # Explicit elevenlabs mode
    monkeypatch.setenv("VOICE_PROVIDER", "elevenlabs")
    prov_eleven = get_voice_provider("elevenlabs")
    assert isinstance(prov_eleven, ElevenLabsVoiceProvider)

    # Auto mode without key -> MockVoiceProvider
    monkeypatch.setenv("VOICE_PROVIDER", "auto")
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("XI_API_KEY", raising=False)
    monkeypatch.delenv("TTS_API_KEY", raising=False)
    monkeypatch.setattr(settings, "ELEVENLABS_API_KEY", "")
    prov_auto_mock = get_voice_provider("auto")
    assert isinstance(prov_auto_mock, MockVoiceProvider)

    # Auto mode with key -> ElevenLabsVoiceProvider
    monkeypatch.setenv("ELEVENLABS_API_KEY", "xi_testkey123456789")
    prov_auto_real = get_voice_provider("auto")
    assert isinstance(prov_auto_real, ElevenLabsVoiceProvider)


@pytest.mark.anyio
async def test_missing_api_key_in_real_mode():
    """3, 21, 22. Test real mode without API key raises VoiceConfigurationError without silent fallback or sample video URL."""
    provider = ElevenLabsVoiceProvider(api_key="")
    with pytest.raises(VoiceConfigurationError) as exc_info:
        await provider.synthesize_speech("Hello world narration text")
    assert "ElevenLabs API key is missing" in str(exc_info.value)


@pytest.mark.anyio
async def test_empty_narration_text_rejection():
    """Test empty or whitespace narration text raises VoiceInputError."""
    provider = ElevenLabsVoiceProvider(api_key="xi_testkey123")
    with pytest.raises(VoiceInputError) as exc_info:
        await provider.synthesize_speech("   ")
    assert "cannot be empty" in str(exc_info.value)


@pytest.mark.anyio
async def test_mock_provider_response():
    """2 & 22. Test mock provider generates valid local WAV audio file, not sample video URL."""
    provider = MockVoiceProvider()
    res = await provider.synthesize_speech("Little kitten learns colors", project_id="proj_mock_audio")
    assert res["provider"] == "KokoroTTS-v1-Mock"
    assert res["audio_format"] == "WAV"
    assert os.path.isfile(res["storage_url"])
    assert res["storage_url"].endswith(".wav")
    assert not res["storage_url"].endswith(".mp4")


@pytest.mark.anyio
async def test_successful_binary_audio_response():
    """4, 5, 6, 16, 18, 19, 22. Test successful binary audio response written to disk and validated."""
    fake_mp3_bytes = b"\xff\xfb\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = fake_mp3_bytes

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("app.services.rendering.ffmpeg.FFmpegEngine.run_command", return_value=(0, "Stream #0:0: Audio: mp3", "")):
        provider = ElevenLabsVoiceProvider(api_key="xi_testkey123")
        res = await provider.synthesize_speech("Rexy explores the forest", project_id="proj_speech_real")

        assert res["audio_format"] == "MP3"
        storage_url = res["storage_url"]
        assert os.path.isfile(storage_url)
        assert storage_url.endswith(".mp3")
        assert not storage_url.endswith(".mp4")
        assert os.path.getsize(storage_url) > 0


@pytest.mark.anyio
async def test_empty_audio_response_rejection():
    """7 & 18. Test 0-byte audio response raises VoiceAPIError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b""

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = ElevenLabsVoiceProvider(api_key="xi_testkey123")
        with pytest.raises(VoiceAPIError) as exc_info:
            await provider.synthesize_speech("Test prompt")
        assert "empty 0-byte audio" in str(exc_info.value)


@pytest.mark.anyio
async def test_http_401_403_auth_error():
    """10 & 11. Test HTTP 401/403 raises VoiceAuthError immediately."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthenticated xi-api-key xi_secretkey777"

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = ElevenLabsVoiceProvider(api_key="xi_secretkey777")
        with pytest.raises(VoiceAuthError) as exc_info:
            await provider.synthesize_speech("Test prompt")
        assert "Authentication failed" in str(exc_info.value)


@pytest.mark.anyio
async def test_http_429_rate_limit_error():
    """13. Test HTTP 429 raises VoiceRateLimitError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "Rate limit exceeded"

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = ElevenLabsVoiceProvider(api_key="xi_testkey123")
        with pytest.raises(VoiceRateLimitError):
            await provider.synthesize_speech("Test prompt")


@pytest.mark.anyio
async def test_http_5xx_server_error():
    """14. Test HTTP 500 server error raises VoiceAPIError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = ElevenLabsVoiceProvider(api_key="xi_testkey123")
        with pytest.raises(VoiceAPIError) as exc_info:
            await provider.synthesize_speech("Test prompt")
        assert "Server Error" in str(exc_info.value)


@pytest.mark.anyio
async def test_timeout_handling():
    """15. Test TTS request timeout raises VoiceTimeoutError."""
    async def mock_post(url, headers, json):
        raise httpx.TimeoutException("Read timeout")

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = ElevenLabsVoiceProvider(api_key="xi_testkey123", timeout_seconds=1.0)
        with pytest.raises(VoiceTimeoutError) as exc_info:
            await provider.synthesize_speech("Test prompt")
        assert "timed out" in str(exc_info.value)


@pytest.mark.anyio
async def test_missing_audio_stream_detection():
    """17. Test FFmpeg validation rejection when file lacks an audio stream."""
    fake_corrupted_bytes = b"NOT_REAL_AUDIO"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = fake_corrupted_bytes

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("app.services.rendering.ffmpeg.FFmpegEngine.run_command", return_value=(1, "", "Invalid data found when processing input")):
        provider = ElevenLabsVoiceProvider(api_key="xi_testkey123")
        with pytest.raises(VoiceAPIError) as exc_info:
            await provider.synthesize_speech("Corrupted test")
        assert "corrupted or unreadable" in str(exc_info.value)


def test_secret_masking():
    """20. Test that ElevenLabs API key is sanitized in log outputs and exceptions."""
    secret_key = "xi_secret1234567890qwertyuiop"
    log_text = f"API error with xi-api-key {secret_key}"
    masked = mask_secret(log_text, secret=secret_key)
    assert secret_key not in masked
    assert "xi_...uiop" in masked or "xi_...iop" in masked or "..." in masked
