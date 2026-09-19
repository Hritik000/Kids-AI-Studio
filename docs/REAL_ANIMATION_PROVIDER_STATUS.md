# Real Animation Provider Status

## Current Provider
The primary real animation generation provider is **`Wan2AnimationProvider`** (`app/core/animation_provider.py`), which communicates with Replicate's REST API (`https://api.replicate.com/v1/predictions` and `https://api.replicate.com/v1/models/{model}/predictions`).

For automated unit tests and keyless local development, **`MockAnimationProvider`** provides mock video payloads without making external network requests.

---

## Model Configuration
- **Default Model**: `wan-video/wan-2.1-1.3b`
- **Supported Models**: `wan-video/wan-2.1-1.3b`, `wan-video/wan-2.1-14b`, or custom model version hashes.
- **Configurable Settings**: Configured via `settings.ANIMATION_MODEL` or `ANIMATION_MODEL` environment variable.

---

## Environment Variables
The following environment variables configure the animation provider layer (`app/core/config.py` & `.env.example`):

- **`ANIMATION_PROVIDER`**: Provider selection mode (`auto` | `wan` | `mock`). Default: `auto`.
- **`REPLICATE_API_KEY`**: API Key for Replicate service (shared with image provider).
- **`ANIMATION_MODEL`**: Target model identifier (default: `wan-video/wan-2.1-1.3b`).
- **`ANIMATION_POLL_INTERVAL`**: Status polling interval in seconds (default: `2.0`).
- **`ANIMATION_TIMEOUT`**: Maximum generation timeout in seconds (default: `120.0`).

---

## Input Format
- **Source Image**: `image_url` (must be a valid HTTP/HTTPS URL or an existing local image file path). Validated before submitting prediction request.
- **Motion Prompt**: Text prompt loaded from `packages/prompts/animation.md` defining camera motion path, camera speed, character motion, and environment motion.
- **Duration**: Target clip duration in seconds (default: `5.0`s).

---

## Prediction Lifecycle
1. **Input Verification**: Validates that `image_url` exists locally or is a valid HTTP URL.
2. **Submit Request**: `Wan2AnimationProvider` POSTs model inputs (`image`, `prompt`, `duration`) to Replicate with header `Prefer: wait`.
3. **Initial Status Check**: Replicate returns prediction payload containing `id`, `status` (`starting`, `processing`, or `succeeded`), and polling URL (`urls.get`).
4. **Async Polling Loop**: If status is `starting` or `processing`, `Wan2AnimationProvider` polls `urls.get` at `ANIMATION_POLL_INTERVAL` intervals until status is `succeeded`, `failed`, or `canceled`.
5. **Output Extraction**: Safely extracts output video HTTP URL from `data["output"][0]`.
6. **Download & Persistence**: Streams video file locally via `MediaDownloader` to persistent storage (`/tmp/kidsai_renders/{project_id}/assets/`).
7. **Container Validation**: Validates file existence, non-zero size, valid video extension (`.mp4`, `.webm`, `.mov`, `.mkv`), non-executable permissions (`0o644`), and container integrity using `FFmpegEngine` (`ffmpeg -i`).

---

## Polling Strategy
- **Interval**: 2.0 seconds between status `GET` requests (configurable via `ANIMATION_POLL_INTERVAL`).
- **Rate Limit Handling**: If `GET` polling encounters HTTP 429, the loop backs off by 3.0 seconds and resumes polling without failing immediately.
- **Loop Boundedness**: Bounded by `ANIMATION_TIMEOUT` seconds (`time.time() - start_poll < timeout`).

---

## Timeout Strategy
- **Initial Connection Timeout**: 10.0 seconds for HTTP connect.
- **Max Overall Prediction Timeout**: 120.0 seconds default (configurable via `ANIMATION_TIMEOUT`).
- **Timeout Exception**: Throws `AnimationTimeoutError` if prediction exceeds timeout bound.

---

## Output Handling
- Extracts raw output video URL.
- Downloads via `MediaDownloader` to persistent storage `/tmp/kidsai_renders/{project_id}/assets/asset_{sha256[:16]}.mp4`.
- Validates container via `FFmpegEngine`.
- Returns local file path for FFmpeg renderer.

---

## Video Validation
- File existence (`os.path.isfile`).
- Non-zero file size (`os.path.getsize > 0`).
- Valid video extension (`.mp4`, `.webm`, `.mov`, `.mkv`).
- Container probe via FFmpeg (`FFmpegEngine.run_command(["-i", path])`).

---

## Storage
- **Local Assets**: Separated into temporary project directory `/tmp/kidsai_renders/{project_id}/assets/`.
- **Non-Executable**: Enforced with `0o644` permissions.

---

## Security
- **Secret Masking**: All API keys (`REPLICATE_API_KEY`, `WAN_API_KEY`, `ANIMATION_API_KEY`) are sanitized in log statements and error messages via `mask_secret()`. Example: `r8_1234...5678`.
- **Path Traversal Protection**: Enforced by `MediaDownloader` path boundary checks.
- **Non-Executable Permissions**: Video files strictly set to `0o644`.

---

## Automated Tests
- **Test File**: `apps/backend/tests/test_animation_provider.py`
- **Result**: **14/14 PASSED** (100%)
  1. `test_provider_selection`: Factory selection logic (PASSED)
  2. `test_missing_api_key_in_real_mode`: Configuration error enforcement (PASSED)
  3. `test_nonexistent_local_input_image`: Local input image validation (PASSED)
  4. `test_mock_provider_response`: Mock response output (PASSED)
  5. `test_immediate_success_response`: Direct sync response (PASSED)
  6. `test_processing_to_succeeded_polling`: Polling loop (PASSED)
  7. `test_failed_prediction_status`: Failed status handling (PASSED)
  8. `test_canceled_prediction_status`: Canceled status handling (PASSED)
  9. `test_polling_timeout`: Timeout handling (PASSED)
  10. `test_http_401_403_auth_error`: Auth error fail-fast (PASSED)
  11. `test_http_429_rate_limit_error`: Rate limit error (PASSED)
  12. `test_http_5xx_server_error`: 5xx server error (PASSED)
  13. `test_malformed_response_handling`: Missing output URL detection (PASSED)
  14. `test_secret_masking`: API key sanitization (PASSED)

---

## Manual Integration Test Procedure
- **Test File**: `apps/backend/tests/test_real_animation_manual.py`
- **Command**: `REPLICATE_API_KEY=r8_... ANIMATION_PROVIDER=wan PYTHONPATH=. ./.venv/bin/pytest tests/test_real_animation_manual.py`
- **Behavior**:
  - Missing key behavior: Fails clearly with actionable instructions on obtaining an API token at [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens).
  - Live execution behavior: Generates local test image asset via FFmpeg, submits live animation prediction to Replicate (Wan 2.1), polls until completion, downloads persistent video asset, validates container using FFmpeg, and outputs metadata.

---

## Cost Considerations
- **Manual Test Only**: The live manual test (`test_real_animation_manual.py`) is excluded from automated unit test runs to prevent unexpected API credit consumption.
- **Short Duration**: Configured to 3.0s duration for cost control during manual verification.

---

## Known Limitations
- Real Replicate API video generation requires an active `REPLICATE_API_KEY` with account credits.
- Offline automated unit tests use mocked HTTP responses (`httpx`) to prevent incurring API charges.
