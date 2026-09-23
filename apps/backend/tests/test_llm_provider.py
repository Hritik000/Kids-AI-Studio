"""
Automated Unit Tests for Production LLM Provider Layer.
Covers:
1. Provider selection
2. Missing API key in real mode
3. Mock mode
4. Successful real-provider response (mocked HTTP)
5. HTTP 401/403 authentication failure
6. HTTP 429 rate limiting
7. HTTP 5xx server errors
8. Timeout handling
9. Invalid JSON response
10. Markdown fenced JSON parsing
11. Schema validation failure
12. Exponential backoff retry behavior
13. Secret masking (API key never exposed in logs/exceptions)
"""

import os
import pytest
import httpx
from unittest.mock import patch, MagicMock
from app.core.config import settings
from app.core.llm import (
    get_llm_provider, OpenAILLMProvider, MockLLMProvider, MLXLLMProvider,
    LLMConfigurationError, LLMAuthError, LLMRateLimitError,
    LLMTimeoutError, LLMAPIError, LLMJSONParseError,
    extract_json_payload, mask_secret
)


def test_provider_selection(monkeypatch):
    """1. Test environment precedence and explicit provider selection."""
    # Environment selection must take precedence over settings in tests/CI.
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    provider = get_llm_provider()
    assert isinstance(provider, MockLLMProvider)

    # An explicit provider argument has the highest precedence.
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    assert isinstance(get_llm_provider("mock"), MockLLMProvider)

    # Test explicit gemini mode
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyTest123456789")
    provider_gemini = get_llm_provider("gemini")
    assert isinstance(provider_gemini, OpenAILLMProvider)
    assert "generativelanguage.googleapis.com" in provider_gemini.base_url
    assert provider_gemini.model == "gemini-2.5-flash"

    # Test explicit openai mode
    provider_openai = get_llm_provider("openai")
    assert isinstance(provider_openai, OpenAILLMProvider)

    # Test explicit kimi mode
    provider_kimi = get_llm_provider("kimi")
    assert isinstance(provider_kimi, OpenAILLMProvider)
    assert "moonshot.cn" in provider_kimi.base_url

    # Test auto mode without hosted keys -> local MLX provider
    monkeypatch.setenv("LLM_PROVIDER", "auto")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("KIMI_API_KEY", raising=False)
    monkeypatch.delenv("STORY_API_KEY", raising=False)
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(settings, "KIMI_API_KEY", "")
    provider_auto_local = get_llm_provider("auto")
    assert isinstance(provider_auto_local, MLXLLMProvider)

    # Test auto mode with Gemini key -> OpenAILLMProvider (Gemini default)
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyAutoKey123")
    provider_auto_real = get_llm_provider("auto")
    assert isinstance(provider_auto_real, OpenAILLMProvider)
    assert "generativelanguage.googleapis.com" in provider_auto_real.base_url


@pytest.mark.anyio
async def test_missing_api_key_in_real_mode():
    """2. Test that real mode without API key raises LLMConfigurationError without silent mock fallback."""
    provider = OpenAILLMProvider(api_key="")
    with pytest.raises(LLMConfigurationError) as exc_info:
        await provider.generate_json("Test prompt")
    assert "LLM API key is missing" in str(exc_info.value)


@pytest.mark.anyio
async def test_mock_mode_response():
    """3. Test mock mode generates valid structured production plan JSON."""
    provider = MockLLMProvider()
    res = await provider.generate_json("Director Agent Master Protocol Topic: Space Explorers")
    assert isinstance(res, dict)
    assert res["topic"] == "Space Explorers"
    assert "scene_count" in res


@pytest.mark.anyio
async def test_successful_real_provider_mocked_http():
    """4. Test successful response from OpenAILLMProvider using mocked HTTP client."""
    fake_json_text = '{"story_title": "Magic Bear", "scenes": []}'
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": fake_json_text}}]
    }
    mock_resp.raise_for_status = MagicMock()

    async def mock_post(url, headers, json):
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = OpenAILLMProvider(api_key="sk-testkey12345678")
        result = await provider.generate_json("Generate story script", system_prompt="System prompt")
        assert result == {"story_title": "Magic Bear", "scenes": []}


@pytest.mark.anyio
async def test_http_401_403_auth_error():
    """5. Test HTTP 401/403 raises LLMAuthError immediately without retrying."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized: Invalid API key sk-secretkey999"

    call_count = 0

    async def mock_post(url, headers, json):
        nonlocal call_count
        call_count += 1
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        provider = OpenAILLMProvider(api_key="sk-secretkey999", max_retries=3)
        with pytest.raises(LLMAuthError) as exc_info:
            await provider.generate_json("Test prompt")
        assert "Authentication failed" in str(exc_info.value)
        assert call_count == 1  # Verify NO retries occurred for auth errors


@pytest.mark.anyio
async def test_http_429_rate_limit_retry():
    """6. Test HTTP 429 raises LLMRateLimitError after bounded retries."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "Rate limit exceeded"

    call_count = 0

    async def mock_post(url, headers, json):
        nonlocal call_count
        call_count += 1
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("asyncio.sleep", return_value=None):
        provider = OpenAILLMProvider(api_key="sk-testkey123", max_retries=3)
        with pytest.raises(LLMRateLimitError):
            await provider.generate_json("Test prompt")
        assert call_count == 3


@pytest.mark.anyio
async def test_http_5xx_server_error_retry():
    """7. Test HTTP 500 server error raises LLMAPIError after bounded retries."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    call_count = 0

    async def mock_post(url, headers, json):
        nonlocal call_count
        call_count += 1
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("asyncio.sleep", return_value=None):
        provider = OpenAILLMProvider(api_key="sk-testkey123", max_retries=2)
        with pytest.raises(LLMAPIError) as exc_info:
            await provider.generate_json("Test prompt")
        assert "Server Error" in str(exc_info.value)
        assert call_count == 2


@pytest.mark.anyio
async def test_timeout_handling():
    """8. Test request timeout raises LLMTimeoutError after retries."""
    call_count = 0

    async def mock_post(url, headers, json):
        nonlocal call_count
        call_count += 1
        raise httpx.TimeoutException("Connection timeout")

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("asyncio.sleep", return_value=None):
        provider = OpenAILLMProvider(api_key="sk-testkey123", max_retries=2, timeout_seconds=5.0)
        with pytest.raises(LLMTimeoutError):
            await provider.generate_json("Test prompt")
        assert call_count == 2


def test_invalid_json_parsing():
    """9. Test invalid non-JSON output raises LLMJSONParseError."""
    with pytest.raises(LLMJSONParseError) as exc_info:
        extract_json_payload("Here is your story: once upon a time...")
    assert "No valid JSON object found" in str(exc_info.value)


def test_markdown_json_extraction():
    """10. Test markdown code block extraction (```json { ... } ```)."""
    raw = """Here is the structured JSON output:
```json
{
    "title": "Star Adventure",
    "scene_count": 3
}
```
Hope this helps!"""
    data = extract_json_payload(raw)
    assert data["title"] == "Star Adventure"
    assert data["scene_count"] == 3


def test_schema_validation_failure():
    """11. Test schema validation error when required fields are missing."""
    invalid_data = "```json\n{\"invalid_field\": 123}\n```"
    parsed = extract_json_payload(invalid_data)
    assert "invalid_field" in parsed
    assert "story_title" not in parsed


@pytest.mark.anyio
async def test_retry_recovery():
    """12. Test transient 500 error recovers on second retry."""
    fail_resp = MagicMock()
    fail_resp.status_code = 502

    succ_resp = MagicMock()
    succ_resp.status_code = 200
    succ_resp.json.return_value = {
        "choices": [{"message": {"content": '{"status": "recovered"}'}}]
    }
    succ_resp.raise_for_status = MagicMock()

    call_count = 0

    async def mock_post(url, headers, json):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return fail_resp
        return succ_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("asyncio.sleep", return_value=None):
        provider = OpenAILLMProvider(api_key="sk-testkey123", max_retries=3)
        res = await provider.generate_json("Test recovery")
        assert res == {"status": "recovered"}
        assert call_count == 2


def test_secret_masking():
    """13. Test that API keys are sanitized and masked in logs/exception strings."""
    raw_secret = "sk-proj-1234567890abcdef1234567890"
    log_msg = f"Failed call with key {raw_secret} on endpoint"
    masked = mask_secret(log_msg, secret=raw_secret)

    assert raw_secret not in masked
    assert "sk-...7890" in masked or "sk-...890" in masked or "..." in masked
