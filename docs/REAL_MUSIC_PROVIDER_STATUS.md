# Real Music Provider Status

## Current Provider
The primary real background music generation provider is **`StableAudioProvider`** (`app/core/music_provider.py`), which communicates directly with Stability AI's Stable Audio REST API (`https://api.stability.ai/v2beta/audio/stable-audio`).

For automated unit tests and keyless local development, **`MockMusicProvider`** generates clean, valid local WAV audio files containing soft warm background musical chords via Python standard library `wave` and `struct`.

---

## Current API Status
- **Corrected Endpoint**: Previously, `music_provider.py` attempted to POST music requests to an image endpoint (`https://api.stability.ai/v2beta/stable-image/generate/core`) and returned sample MP4 video URLs.
- **Fixed & Verified**: Fixed to send requests directly to Stability AI's official audio endpoint `https://api.stability.ai/v2beta/audio/stable-audio`, capturing binary MP3 audio bytes (`audio/mpeg`), validating container integrity via FFmpeg, and storing persistent `.mp3` files locally.

---

## Endpoint
- **URL**: `https://api.stability.ai/v2beta/audio/stable-audio`
- **Method**: `POST`
- **Headers**:
  - `Authorization`: `Bearer <STABLE_AUDIO_API_KEY>` or `Bearer <STABILITY_API_KEY>`
  - `Accept`: `audio/mpeg`

---

## Model
- **Default Model**: `stable-audio`
- **Supported Models**: `stable-audio` or `meta/musicgen` (via Replicate).
- **Configurable Settings**: Configured via `settings.MUSIC_MODEL` or `MUSIC_MODEL` environment variable.

---

## Environment Variables
The following environment variables configure the music provider layer (`app/core/config.py` & `.env.example`):

- **`MUSIC_PROVIDER`**: Provider selection mode (`auto` | `stable_audio` | `replicate_music` | `mock`). Default: `auto`.
- **`STABLE_AUDIO_API_KEY`**: API Key for Stability AI Stable Audio service (obtained at [platform.stability.ai](https://platform.stability.ai)).
- **`STABILITY_API_KEY`**: Alternative API Key alias for Stability AI.
- **`MUSIC_MODEL`**: Target model ID (default: `stable-audio`).
- **`MUSIC_POLL_INTERVAL`**: Polling interval for async endpoints (default: `2.0`).
- **`MUSIC_TIMEOUT`**: Maximum request timeout in seconds (default: `60.0`).

---

## Request Format
`POST https://api.stability.ai/v2beta/audio/stable-audio`
Headers:
```json
{
  "Authorization": "Bearer <STABLE_AUDIO_API_KEY>",
  "Accept": "audio/mpeg"
}
```
Form Data / Body:
```json
{
  "prompt": "Upbeat cheerful acoustic ukulele melody for children story",
  "seconds_start": "0",
  "seconds_total": "5",
  "output_format": "mp3"
}
```

---

## Response Format
- **Content Type**: `audio/mpeg` (binary stream).
- **Container / Encoding**: MP3 format (`.mp3`), 44.1 kHz sample rate.
- **Direct Processing**: Binary audio bytes (`resp.content`) are written directly to disk without discarding response data or returning sample video URLs.

---

## Async/Sync Lifecycle
- **Stability AI REST API**: Synchronous binary stream delivery (`Accept: audio/mpeg`).
- **Replicate MusicGen Endpoint**: Asynchronous prediction creation (`POST /v1/models/meta/musicgen/predictions`) with status polling (`starting` / `processing` -> `succeeded`), downloading generated `.wav`/`.mp3` output file via `MediaDownloader`.

---

## Polling
- Applicable for asynchronous providers (e.g. Replicate MusicGen).
- Bounded polling loop at `MUSIC_POLL_INTERVAL` (2.0s) intervals up to `MUSIC_TIMEOUT` (60.0s).

---

## Timeout
- **Default Timeout**: 60.0 seconds (configurable via `MUSIC_TIMEOUT`).
- **Timeout Exception**: Throws `MusicTimeoutError` if request exceeds timeout bound.

---

## Error Handling
- **`MusicConfigurationError`**: Raised if `MUSIC_PROVIDER=stable_audio` is selected but `STABLE_AUDIO_API_KEY` is missing. **No silent fallback to mock mode or sample MP4 URLs.**
- **`MusicInputError`**: Raised if music prompt is empty or invalid.
- **`MusicAuthError`**: Raised immediately on HTTP 401/403 (invalid API key). **Not retried.**
- **`MusicRateLimitError`**: Raised on HTTP 429 rate limits.
- **`MusicAPIError`**: Raised on HTTP 5xx server errors, 0-byte audio responses, malformed responses, or corrupted audio streams.
- **`MusicTimeoutError`**: Raised if request exceeds timeout limit.

---

## Audio Validation
After writing binary audio bytes to disk, `StableAudioProvider` validates:
1. File existence on disk (`os.path.isfile`).
2. Non-zero file size (`os.path.getsize > 0`).
3. Non-executable permissions (`0o644`).
4. Extension check (`.mp3`, `.wav`, `.aac`, `.m4a`, `.ogg`).
5. Container and stream inspection using `FFmpegEngine` (`ffmpeg -i`) to ensure the file contains a valid, uncorrupted audio stream.

---

## Persistence
- **Storage Location**: Local assets folder `/tmp/kidsai_renders/{project_id}/assets/asset_stable_audio_{hash}.mp3`.
- **Downstream Compatibility**: Returns local filesystem path for `MusicPipelineService`, audio mixer (narration ducking & loudness normalization), and FFmpeg renderer compatibility.

---

## Security
- **Secret Masking**: All API keys (`STABLE_AUDIO_API_KEY`, `STABILITY_API_KEY`, `MUSIC_API_KEY`) are sanitized in log statements and error messages via `mask_secret()`. Example: `sk_1234...5678`.
- **Path Traversal Protection**: Enforced by path boundary check `local_audio_path.startswith(base_dir + os.sep)`.
- **Non-Executable Permissions**: All audio files set to `0o644`.

---

## Mixer Compatibility
- `MusicPipelineService` receives the generated local audio asset path.
- Compatible with narration ducking (`music_ducked_volume: 0.25`), ambient audio mixing (`ambient_volume: 0.15`), and master loudness normalization (`-14.0 LUFS`).

---

## Automated Tests
- **Test File**: `apps/backend/tests/test_music_provider.py`
- **Result**: **13/13 PASSED** (100%)
  1. `test_provider_selection`: Factory selection for mock, stable_audio, auto (PASSED)
  2. `test_missing_api_key_in_real_mode`: Configuration error enforcement (PASSED)
  3. `test_empty_music_prompt_rejection`: Prompt input validation (PASSED)
  4. `test_mock_provider_response`: Local WAV music generation (PASSED)
  5. `test_successful_binary_audio_response`: Binary MP3 writing and validation (PASSED)
  6. `test_empty_audio_response_rejection`: 0-byte rejection (PASSED)
  7. `test_http_401_403_auth_error`: Auth error fail-fast (PASSED)
  8. `test_http_429_rate_limit_error`: Rate limit error (PASSED)
  9. `test_http_5xx_server_error`: 5xx server error (PASSED)
  10. `test_timeout_handling`: Timeout handling (PASSED)
  11. `test_corrupted_audio_stream_detection`: FFmpeg stream validation rejection (PASSED)
  12. `test_secret_masking`: API key sanitization (PASSED)
  13. `test_music_pipeline_mixer_compatibility`: Audio mixer compatibility (PASSED)

---

## Manual Integration Test
- **Test File**: `apps/backend/tests/test_real_music_manual.py`
- **Command**: `STABLE_AUDIO_API_KEY=sk-... MUSIC_PROVIDER=stable_audio PYTHONPATH=. ./.venv/bin/pytest tests/test_real_music_manual.py`
- **Behavior**:
  - Missing key behavior: Fails clearly with actionable instructions on obtaining an API token at [platform.stability.ai](https://platform.stability.ai).
  - Live execution behavior: Sends short test music prompt to Stability AI REST API, writes binary MP3 audio to disk, validates container with FFmpeg, and logs latency and asset path without leaking secrets.

---

## Cost Considerations
- **Manual Test Only**: Live integration test is excluded from automated test suites to prevent consuming API credits.
- **Short Duration**: Configured to 3.0s duration for cost control during manual verification.

---

## Free/Local Migration Strategy
The clean `MusicProvider(ABC)` abstraction (`synthesize_music_and_mix(prompt, duration_seconds, bpm, project_id) -> Dict[str, Any]`) decouples background music generation completely from higher-level services (`MusicPipelineService`, `AudioMixer`, `FFmpegRenderer`).
To switch to a local or free music engine (e.g. Audiocraft/MusicGen local PyTorch, procedural music generator, or a royalty-free local music library):
1. Implement a new subclass `LocalMusicProvider(MusicProvider)`.
2. Implement `async def synthesize_music_and_mix(...) -> Dict[str, Any]` returning local audio asset metadata.
3. Update `get_music_provider()` factory routing.
Zero changes will be required in story services, storyboard services, audio mixer, or rendering pipelines!

---

## Known Limitations
- Live Stability AI music generation requires a valid `STABLE_AUDIO_API_KEY` or `STABILITY_API_KEY` with account credits.
- Offline unit tests use mocked HTTP responses (`httpx`) to prevent API credit consumption during automated testing.
