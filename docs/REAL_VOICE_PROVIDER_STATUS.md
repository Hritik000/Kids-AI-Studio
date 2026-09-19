# Real Voice Provider Status

## Current Provider
The primary real speech generation provider is **`ElevenLabsVoiceProvider`** (`app/core/voice_provider.py`), which communicates directly with ElevenLabs REST API (`https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`).

For automated unit tests and keyless local development, **`MockVoiceProvider`** generates clean, valid local WAV audio files containing soft warm audio tones via Python standard library `wave` and `struct`.

---

## Model Configuration
- **Default Model**: `eleven_multilingual_v2`
- **Supported Models**: `eleven_multilingual_v2`, `eleven_monolingual_v1`, `eleven_turbo_v2`
- **Configurable Settings**: Configured via `settings.ELEVENLABS_MODEL` or `ELEVENLABS_MODEL` environment variable.

---

## Voice Configuration
- **Default Voice ID**: `21m00Tcm4TlvDq8ikWAM` ("Rachel" / default narrator)
- **Configurable Voice ID**: Configured via `settings.ELEVENLABS_VOICE_ID` or `ELEVENLABS_VOICE_ID` environment variable.
- **Voice Settings**: `stability: 0.5`, `similarity_boost: 0.75`.

---

## Environment Variables
The following environment variables configure the voice provider layer (`app/core/config.py` & `.env.example`):

- **`VOICE_PROVIDER`**: Provider selection mode (`auto` | `elevenlabs` | `kokoro` | `mock`). Default: `auto`.
- **`ELEVENLABS_API_KEY`**: API Key for ElevenLabs service (obtained at [elevenlabs.io](https://elevenlabs.io)).
- **`ELEVENLABS_VOICE_ID`**: Target voice ID (default: `21m00Tcm4TlvDq8ikWAM`).
- **`ELEVENLABS_MODEL`**: Target model ID (default: `eleven_multilingual_v2`).
- **`VOICE_TIMEOUT`**: Maximum request timeout in seconds (default: `35.0`).

---

## Request Format
`POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
Headers:
```json
{
  "xi-api-key": "<ELEVENLABS_API_KEY>",
  "Content-Type": "application/json",
  "Accept": "audio/mpeg"
}
```
Payload Body:
```json
{
  "text": "Narration text string...",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.75
  }
}
```

---

## Response/Audio Format
- **Content Type**: `audio/mpeg` (binary stream).
- **Container / Encoding**: MP3 format (`.mp3`), 44.1 kHz sample rate.
- **Direct Processing**: Binary audio bytes (`resp.content`) are written directly to disk without discarding response data or returning sample video URLs.

---

## Error Handling
- **`VoiceConfigurationError`**: Raised if `VOICE_PROVIDER=elevenlabs` is selected but `ELEVENLABS_API_KEY` is missing. **No silent fallback to mock mode or sample MP4 URLs.**
- **`VoiceInputError`**: Raised if narration text is empty or invalid.
- **`VoiceAuthError`**: Raised immediately on HTTP 401/403 (invalid API key). **Not retried.**
- **`VoiceRateLimitError`**: Raised on HTTP 429 rate limits.
- **`VoiceAPIError`**: Raised on HTTP 5xx server errors, 0-byte audio responses, malformed responses, or corrupted audio streams.
- **`VoiceTimeoutError`**: Raised if request exceeds timeout limit.

---

## Retry Behavior
- Bounded retries apply only to transient network or server errors.
- Authentication/configuration errors fail immediately without retrying indefinitely.

---

## Audio Validation
After writing binary audio bytes to disk, `ElevenLabsVoiceProvider` validates:
1. File existence on disk (`os.path.isfile`).
2. Non-zero file size (`os.path.getsize > 0`).
3. Non-executable permissions (`0o644`).
4. Extension check (`.mp3`, `.wav`, `.aac`, `.m4a`, `.ogg`).
5. Container and stream inspection using `FFmpegEngine` (`ffmpeg -i`) to ensure the file contains a valid, uncorrupted audio stream.

---

## Asset Persistence
- **Storage Location**: Local assets folder `/tmp/kidsai_renders/{project_id}/assets/asset_elevenlabs_narration_{hash}.mp3`.
- **Downstream Compatibility**: Returns local filesystem path for audio mixer, lip-sync engine, and FFmpeg renderer compatibility.

---

## Security
- **Secret Masking**: All API keys (`ELEVENLABS_API_KEY`, `XI_API_KEY`, `TTS_API_KEY`) are sanitized in log statements and error messages via `mask_secret()`. Example: `xi_1234...5678`.
- **Path Traversal Protection**: Enforced by path boundary check `local_audio_path.startswith(base_dir + os.sep)`.
- **Non-Executable Permissions**: All audio files set to `0o644`.

---

## Automated Tests
- **Test File**: `apps/backend/tests/test_voice_provider.py`
- **Result**: **12/12 PASSED** (100%)
  1. `test_provider_selection`: Factory selection for mock, elevenlabs, auto (PASSED)
  2. `test_missing_api_key_in_real_mode`: Configuration error enforcement (PASSED)
  3. `test_empty_narration_text_rejection`: Input text validation (PASSED)
  4. `test_mock_provider_response`: Local WAV generation (PASSED)
  5. `test_successful_binary_audio_response`: Binary MP3 writing and validation (PASSED)
  6. `test_empty_audio_response_rejection`: 0-byte rejection (PASSED)
  7. `test_http_401_403_auth_error`: Auth error fail-fast (PASSED)
  8. `test_http_429_rate_limit_error`: Rate limit error (PASSED)
  9. `test_http_5xx_server_error`: 5xx server error (PASSED)
  10. `test_timeout_handling`: Timeout handling (PASSED)
  11. `test_missing_audio_stream_detection`: FFmpeg stream validation rejection (PASSED)
  12. `test_secret_masking`: API key sanitization (PASSED)

---

## Manual Integration Test
- **Test File**: `apps/backend/tests/test_real_voice_manual.py`
- **Command**: `ELEVENLABS_API_KEY=xi_... VOICE_PROVIDER=elevenlabs PYTHONPATH=. ./.venv/bin/pytest tests/test_real_voice_manual.py`
- **Behavior**:
  - Missing key behavior: Fails clearly with actionable instructions on obtaining an API token at [elevenlabs.io](https://elevenlabs.io).
  - Live execution behavior: Sends short test narration sentence to ElevenLabs TTS API, writes binary MP3 audio to disk, validates container with FFmpeg, and logs latency and asset path without leaking secrets.

---

## Cost Considerations
- **Manual Test Only**: Live integration test is excluded from automated test suites to prevent consuming API character limits.
- **Short Sentence**: Configured to synthesize a single short sentence (~8 words) for minimal character usage during manual testing.

---

## Free/Local Provider Migration Strategy
The clean `VoiceProvider(ABC)` abstraction decouples speech synthesis completely from higher-level services (`VoicePipelineService`, `DialoguePlannerService`, `LipSyncEngineService`, `FFmpegRenderer`).
To switch to a local or free TTS engine (e.g. Kokoro-TTS local ONNX, Coqui TTS, or edge-tts):
1. Implement a new subclass `LocalTTSProvider(VoiceProvider)`.
2. Implement `async def synthesize_speech(...) -> Dict[str, Any]` returning local audio asset metadata.
3. Update `get_voice_provider()` factory routing.
Zero changes will be required in story services, storyboard services, lip-sync, or rendering pipelines!

---

## Known Limitations
- Live ElevenLabs speech synthesis requires a valid `ELEVENLABS_API_KEY` and available character quota.
- Offline unit tests use mocked HTTP responses (`httpx`) to prevent API character consumption during automated testing.
