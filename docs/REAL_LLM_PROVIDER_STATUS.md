# Real LLM Provider Status

## Current Provider
The primary real LLM providers supported by **`OpenAILLMProvider`** (`app/core/llm.py`) include:
- **Google Gemini API (AI Studio Free Tier)**: `gemini-2.5-flash` via `https://generativelanguage.googleapis.com/v1beta/openai`
- **OpenAI API**: `gpt-4o-mini`, `gpt-4o` via `https://api.openai.com/v1`
- **Moonshot Kimi API**: `moonshot-v1-8k` via `https://api.moonshot.cn/v1`

For automated unit tests and keyless local development, **`MockLLMProvider`** provides high-quality, deterministic structured JSON output without making external network calls.

---

## Provider Selection & Routing
Provider selection is explicitly controlled via `get_llm_provider(provider_type: Optional[str] = None)` or the `LLM_PROVIDER` environment setting:

1. **`LLM_PROVIDER="gemini"`**: Uses `OpenAILLMProvider` configured for Google Gemini API (`https://generativelanguage.googleapis.com/v1beta/openai`, `GEMINI_API_KEY`, model `gemini-2.5-flash`).
2. **`LLM_PROVIDER="openai"`**: Uses `OpenAILLMProvider` configured for OpenAI (`https://api.openai.com/v1`, `OPENAI_API_KEY`, model `gpt-4o-mini`).
3. **`LLM_PROVIDER="kimi"`**: Uses `OpenAILLMProvider` configured for Moonshot Kimi API (`https://api.moonshot.cn/v1`, `KIMI_API_KEY`, model `moonshot-v1-8k`).
4. **`LLM_PROVIDER="mock"`**: Uses `MockLLMProvider` unconditionally.
5. **`LLM_PROVIDER="auto"` (Default)**:
   - Priority 1: If `GEMINI_API_KEY` is present -> uses `gemini` provider (`gemini-2.5-flash`).
   - Priority 2: If `OPENAI_API_KEY` is present -> uses `openai` provider (`gpt-4o-mini`).
   - Priority 3: If `KIMI_API_KEY` is present -> uses `kimi` provider.
   - Priority 4: If no key is present -> defaults to `MockLLMProvider`.

> **STRICT RULE ENFORCED**: When operating in real mode (`gemini`, `openai`, `kimi`, or `auto` with real key configured), missing API keys or invalid credentials raise a clear `LLMConfigurationError` or `LLMAuthError`. The system **never** silently falls back from real mode to mock mode.

---

## Environment Variables
The following environment variables configure the LLM layer (`app/core/config.py` & `.env.example`):

- **`LLM_PROVIDER`**: Provider selection mode (`auto` | `gemini` | `openai` | `kimi` | `mock`).
- **`GEMINI_API_KEY`**: API Key for Google Gemini (obtained free at [aistudio.google.com](https://aistudio.google.com)).
- **`GEMINI_MODEL`**: Gemini model name (default: `gemini-2.5-flash`).
- **`GEMINI_BASE_URL`**: Base API endpoint URL (default: `https://generativelanguage.googleapis.com/v1beta/openai`).
- **`OPENAI_API_KEY`**: API Key for OpenAI service.
- **`OPENAI_MODEL`**: Target OpenAI model (default: `gpt-4o-mini`).
- **`OPENAI_BASE_URL`**: Base API endpoint URL (default: `https://api.openai.com/v1`).
- **`KIMI_API_KEY`**: API Key for Moonshot Kimi service.

---

## Request/Response Flow
1. **Service Prompt Composition**: `DirectorAgentService`, `StoryAgentService`, or `StoryboardAgentService` loads monorepo prompt templates (`packages/prompts/*.md`) using `PromptLoader`.
2. **LLM Provider Dispatch**: Services invoke `await self.llm.generate_json(prompt, system_prompt)`.
3. **HTTP Streaming / Response**: `OpenAILLMProvider` posts JSON payload with `response_format: {"type": "json_object"}` to the configured endpoint (e.g. Gemini OpenAI-compatible REST API).
4. **Payload Extraction**: `extract_json_payload` cleans whitespace, strips markdown fences (```` ```json ... ``` ````), extracts `{...}` blocks, and parses JSON.
5. **Schema Validation**: Results pass through `ValidationService` or `StoryboardValidationService` for child safety and structural compliance.

---

## JSON Validation
`extract_json_payload()` handles 4 recovery cases:
1. Pure valid JSON string.
2. Markdown fenced JSON (```` ```json { ... } ``` ```` or ```` ``` { ... } ``` ````).
3. Non-JSON text surrounding valid `{ ... }` dictionary blocks.
4. Unrecoverable non-JSON text -> raises `LLMJSONParseError`.

Validated results are checked by `ValidationService` for required fields (`scene_count`, `narration_text`, `visual_description`, child safety keywords).

---

## Retry/Error Handling
Bounded exponential backoff is implemented for transient errors (max 3 retries, delays of 1.0s, 2.0s, 4.0s):

- **`LLMRateLimitError` (HTTP 429)**: Retried with exponential backoff.
- **`LLMAPIError` (HTTP 5xx)**: Retried with exponential backoff.
- **`LLMTimeoutError`**: Retried with exponential backoff.
- **`LLMAuthError` (HTTP 401/403)**: **NOT** retried; raises immediately.
- **`LLMConfigurationError`**: **NOT** retried; raises immediately.

---

## Security Notes
- **Secret Masking**: All API keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `KIMI_API_KEY`, `STORY_API_KEY`) are sanitized in log outputs and error tracebacks via `mask_secret()`. Example: `AIzaSy123456...` is masked as `AIz...56`.
- **No Secret Leaks**: API keys are never printed in console output, error responses, or test artifacts.
- **Git Exclusions**: Verified `.gitignore` excludes `.env`, `.env.local`, `.env*.local`, `*.pem`, `*.key`.

---

## Automated Tests
- **Test Suite**: `apps/backend/tests/test_llm_provider.py`
- **Result**: **13/13 PASSED** (100%)
  1. `test_provider_selection`: Factory selection logic for mock, gemini, openai, kimi, auto (PASSED)
  2. `test_missing_api_key_in_real_mode`: Strict configuration error handling (PASSED)
  3. `test_mock_mode_response`: Structured mock generation (PASSED)
  4. `test_successful_real_provider_mocked_http`: Gemini / OpenAI API payload mapping (PASSED)
  5. `test_http_401_403_auth_error`: Auth error fail-fast (PASSED)
  6. `test_http_429_rate_limit_retry`: Rate limit retry bounds (PASSED)
  7. `test_http_5xx_server_error_retry`: 5xx server error retries (PASSED)
  8. `test_timeout_handling`: Request timeout handling (PASSED)
  9. `test_invalid_json_parsing`: Non-JSON parse rejection (PASSED)
  10. `test_markdown_json_extraction`: Markdown fence recovery (PASSED)
  11. `test_schema_validation_failure`: Schema violation detection (PASSED)
  12. `test_retry_recovery`: Transient 502 recovery on retry (PASSED)
  13. `test_secret_masking`: API key sanitization (PASSED)

---

## Manual Integration Tests

### 1. Manual Gemini Integration Test (`tests/test_real_gemini_manual.py`)
- **Execution Command**: `GEMINI_API_KEY=AIzaSy... LLM_PROVIDER=gemini PYTHONPATH=. ./.venv/bin/pytest tests/test_real_gemini_manual.py`
- **Behavior**:
  - Missing key behavior: Fails clearly with actionable instructions on obtaining a free key at [aistudio.google.com](https://aistudio.google.com).
  - Live execution behavior: Sends a live production plan + story script request to Google Gemini API (`gemini-2.5-flash`), validates returned JSON schema, masks secrets, and outputs request latency and metadata.

### 2. Manual OpenAI Integration Test (`tests/test_real_llm_manual.py`)
- **Execution Command**: `OPENAI_API_KEY=sk-... LLM_PROVIDER=openai PYTHONPATH=. ./.venv/bin/pytest tests/test_real_llm_manual.py`
