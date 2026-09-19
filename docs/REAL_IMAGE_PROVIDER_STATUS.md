# Real Image Provider Status

## Current Provider
The primary real image generation provider is **`FluxImageProvider`** (`app/core/image_provider.py`), which communicates with Replicate's REST API (`https://api.replicate.com/v1/predictions` and `https://api.replicate.com/v1/models/{model}/predictions`).

For automated unit tests and keyless local development, **`MockImageProvider`** provides deterministic placeholder image URLs without making external API calls.

---

## Model Configuration
- **Default Model**: `black-forest-labs/flux-schnell`
- **Supported Models**: `black-forest-labs/flux-schnell`, `black-forest-labs/flux-1.1-pro`, or custom model version hashes.
- **Configurable Settings**: Configured via `settings.IMAGE_MODEL` or `IMAGE_MODEL` environment variable.

---

## Environment Variables
The following environment variables configure the image provider layer (`app/core/config.py` & `.env.example`):

- **`IMAGE_PROVIDER`**: Provider selection mode (`auto` | `flux` | `mock`). Default: `auto`.
- **`REPLICATE_API_KEY`**: API Key for Replicate service (obtained at [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens)).
- **`IMAGE_MODEL`**: Target model identifier (default: `black-forest-labs/flux-schnell`).
- **`IMAGE_POLL_INTERVAL`**: Status polling interval in seconds (default: `1.0`).
- **`IMAGE_TIMEOUT`**: Maximum generation timeout in seconds (default: `60.0`).

---

## Prediction Lifecycle
1. **Submit Request**: `FluxImageProvider` POSTs model inputs (`prompt`, `aspect_ratio: "16:9"`, `seed`) to Replicate with header `Prefer: wait`.
2. **Initial Status Check**: Replicate returns prediction payload containing `id`, `status` (`starting`, `processing`, or `succeeded`), and polling URL (`urls.get`).
3. **Async Polling Loop**: If status is `starting` or `processing`, `FluxImageProvider` polls `urls.get` at `IMAGE_POLL_INTERVAL` intervals until status is `succeeded`, `failed`, or `canceled`.
4. **Output Extraction**: Safely extracts the HTTP image URL from `data["output"][0]`.
5. **Download & Persistence**: Downloads the generated image file locally via `MediaDownloader` to persistent storage (`/tmp/kidsai_renders/{project_id}/assets/`).
6. **Validation**: Confirms file exists on disk, size > 0 bytes, non-executable permissions (`0o644`), and valid image extension (`.png`, `.jpg`, `.jpeg`, `.webp`).

---

## Polling Strategy
- **Interval**: 1.0 second between status `GET` requests (configurable via `IMAGE_POLL_INTERVAL`).
- **Rate Limit Handling**: If `GET` polling encounters HTTP 429, the loop backs off by 2.0 seconds and resumes polling without failing immediately.
- **Loop Boundedness**: Bounded by `IMAGE_TIMEOUT` seconds (`time.time() - start_poll < timeout`).

---

## Timeout Strategy
- **Initial Connection Timeout**: 10.0 seconds for HTTP connect.
- **Max Overall Prediction Timeout**: 60.0 seconds default (configurable via `IMAGE_TIMEOUT`).
- **Timeout Exception**: Throws `ImageTimeoutError` if prediction exceeds timeout bound.

---

## Error Handling
- **`ImageConfigurationError`**: Raised if `IMAGE_PROVIDER=flux` is active but `REPLICATE_API_KEY` is missing. **No silent fallback to mock mode.**
- **`ImageAuthError`**: Raised immediately on HTTP 401/403 (invalid API key). **Not retried.**
- **`ImageRateLimitError`**: Raised on HTTP 429 rate limits.
- **`ImageAPIError`**: Raised on HTTP 5xx server errors, `status == "failed"`, `status == "canceled"`, malformed responses, or missing output URLs.
- **`ImageTimeoutError`**: Raised if initial request or polling exceeds timeout.

---

## Download & Persistence
- **Storage Location**: Local assets folder `/tmp/kidsai_renders/{project_id}/assets/asset_{sha256[:16]}.png`.
- **MediaDownloader Integration**: Streams HTTP content in 64 KB chunks, checks path traversal, enforces 250 MB size limit, sets non-executable `0o644` file permissions.
- **Downstream Usability**: Returns local filesystem path (`/tmp/.../asset_xyz.png`) for FFmpeg video rendering engine compatibility.

---

## Security
- **Secret Masking**: All API keys (`REPLICATE_API_KEY`, `FLUX_API_KEY`, `IMAGE_API_KEY`) are sanitized in log statements and error messages via `mask_secret()`. Example: `r8_1234...5678`.
- **Path Traversal Protection**: Enforced by `MediaDownloader` verification `target_path.startswith(assets_dir + os.sep)`.
- **Non-Executable Permissions**: All downloaded image files strictly enforced with `0o644`.

---

## Automated Tests
- **Test File**: `apps/backend/tests/test_image_provider.py`
- **Result**: **13/13 PASSED** (100%)
  1. `test_provider_selection`: Factory selection for mock, flux, auto (PASSED)
  2. `test_missing_api_key_in_real_mode`: Configuration error enforcement (PASSED)
  3. `test_mock_provider_response`: Mock response output (PASSED)
  4. `test_immediate_succeeded_response`: Direct sync response (PASSED)
  5. `test_processing_to_succeeded_polling`: Starting -> processing -> succeeded polling loop (PASSED)
  6. `test_failed_prediction_status`: Failed prediction status handling (PASSED)
  7. `test_canceled_prediction_status`: Canceled status handling (PASSED)
  8. `test_polling_timeout`: Timeout handling (PASSED)
  9. `test_http_401_403_auth_error`: Auth error fail-fast (PASSED)
  10. `test_http_429_rate_limit_error`: Rate limit error (PASSED)
  11. `test_http_5xx_server_error`: 5xx server error (PASSED)
  12. `test_malformed_response_handling`: Missing output URL detection (PASSED)
  13. `test_secret_masking`: API key sanitization (PASSED)

---

## Manual Integration Test
- **Test File**: `apps/backend/tests/test_real_image_manual.py`
- **Command**: `REPLICATE_API_KEY=r8_... IMAGE_PROVIDER=flux PYTHONPATH=. ./.venv/bin/pytest tests/test_real_image_manual.py`
- **Behavior**:
  - Missing key behavior: Fails clearly with actionable instructions on obtaining an API token at [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens).
  - Live execution behavior: Submits live image prediction to Replicate, polls until completion, downloads persistent image asset to disk, validates file integrity, and outputs latency and asset path metadata without leaking secrets.

---

## Known Limitations
- Real Replicate API execution requires an active `REPLICATE_API_KEY` with account credits.
- Offline automated unit tests use mocked HTTP responses (`httpx`) to prevent incurring API charges during local unit testing.
