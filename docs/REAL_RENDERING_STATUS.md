# KidsAI Studio Real Rendering Status

## Overview
This document details the implementation of the **Rendering Foundation** for KidsAI Studio v2.0. The rendering engine is now equipped with robust FFmpeg binary discovery, safe streaming HTTP/HTTPS asset downloading, strict file validation without silent fallback artifacts, and security protections against path traversal.

---

## 1. FFmpeg Binary Discovery Method

The `FFmpegEngine` (`app/services/rendering/ffmpeg.py`) uses a prioritized 5-tier discovery strategy to locate the system FFmpeg binary:

1. **Environment Variable Override (`FFMPEG_PATH`)**: Checks `os.getenv("FFMPEG_PATH")`. If configured and executable, this path is used unconditionally.
2. **In-Memory Executable Cache**: Caches the resolved binary path across invocations.
3. **System `PATH` Lookup**: Executes `shutil.which("ffmpeg")` to discover standard system binaries.
4. **`imageio_ffmpeg` Python Package**: Checks if `imageio_ffmpeg.get_ffmpeg_exe()` is installed in the active Python environment.
5. **Standard OS Binary Locations**:
   - macOS (Homebrew ARM): `/opt/homebrew/bin/ffmpeg`
   - macOS (Homebrew Intel): `/usr/local/bin/ffmpeg`
   - Linux: `/usr/bin/ffmpeg`
   - Linux (Snap): `/snap/bin/ffmpeg`
   - Windows: `C:\ffmpeg\bin\ffmpeg.exe`

If no valid binary is located, `FFmpegEngine` raises a clear, actionable `FFmpegNotFoundError` detailing instructions for installation.

---

## 2. Supported Operating Systems

- **macOS**: Fully supported (Apple Silicon `/opt/homebrew` & Intel `/usr/local`).
- **Linux**: Fully supported (Ubuntu/Debian `/usr/bin/ffmpeg`, Snap `/snap/bin/ffmpeg`).
- **Windows**: Supported (`C:\ffmpeg\bin\ffmpeg.exe` & `FFMPEG_PATH` environment variable).

---

## 3. Asset Download Behavior (`MediaDownloader`)

The `MediaDownloader` service (`app/services/rendering/downloader.py`) handles remote HTTP/HTTPS asset preparation:

- **Local File Pass-Through**: If an asset path is already a local filesystem path (`os.path.isfile(path)`), it passes directly through without downloading.
- **Streaming Chunks**: Downloads remote HTTP assets in 64 KB chunks via `httpx.Client.stream("GET", url)` to prevent loading large media files into RAM.
- **Size Limit Enforcement**: Enforces a strict default maximum size of 250 MB (`DEFAULT_MAX_BYTES`). Stream aborts immediately if exceeded.
- **Timeouts**: Connection timeout set to 10 seconds; read timeout set to 60 seconds.
- **HTTP Status Validation**: Requires HTTP 200 OK response; non-2xx status codes raise `DownloaderError`.
- **Extension Resolution**: Resolves safe file extensions from URL path or `Content-Type` headers (`.png`, `.jpg`, `.mp4`, `.mp3`, `.wav`, `.aac`, etc.).
- **Permissions Safety**: All downloaded files are written with non-executable file permissions (`0o644`).

---

## 4. Temporary Directory Structure

All media assets and rendering workspaces are organized deterministically under `/tmp/kidsai_renders`:

```
/tmp/kidsai_renders/
└── {project_id}/
    ├── assets/                             # Downloaded remote HTTP media files
    │   ├── asset_99164840ea556703.png
    │   ├── asset_df259223395b05fa.mp4
    │   └── asset_audio_5514f7b6.wav
    ├── final.mp4                           # Final rendered 1080p video file
    └── thumbnail.jpg                       # Extracted video cover image
```

---

## 5. Security Protections

1. **Path Traversal Shield**: Resolves absolute target paths and verifies `target_path.startswith(assets_dir + os.sep)`. Prevents malicious URLs containing `../` from escaping `/tmp/kidsai_renders/{project_id}/assets/`.
2. **Collision-Safe Filenames**: Generates SHA256 hashes of input URLs (`asset_{sha256[:16]}.{ext}`).
3. **Execution Prevention**: Explicitly enforces `os.chmod(target_path, 0o644)` on all downloaded files.
4. **No Silent Fallback (Task 4)**: Removed solid color canvas / `drawtext` silent fallbacks. Missing or corrupted scene assets immediately trigger a clean render job failure with status `"FAILED"`.

---

## 6. Test Results

### Foundation Unit Tests (`tests/test_rendering_foundation.py`):
11/11 tests passing:
- `test_ffmpeg_path_discovery` (PASSED)
- `test_local_image_input` (PASSED)
- `test_local_audio_input` (PASSED)
- `test_http_image_download` (PASSED)
- `test_http_audio_download` (PASSED)
- `test_http_video_download` (PASSED)
- `test_failed_download_handling` (PASSED)
- `test_unsupported_url_scheme` (PASSED)
- `test_missing_ffmpeg_handling` (PASSED)
- `test_path_traversal_protection` (PASSED)
- `test_render_failure_propagation` (PASSED)

### Real Local Render Test (`tests/test_real_local_render.py`):
1/1 test passing.

---

## 7. Real Render Test Execution Details

- **Test Script**: `apps/backend/tests/test_real_local_render.py`
- **Detected FFmpeg Version**: `ffmpeg version 7.1` (via `imageio_ffmpeg` binary)
- **Synthetic Assets Generated**:
  - Image: 1280x720 RGB blue PNG generated via FFmpeg `color` filter
  - Audio: 2-second 440 Hz PCM WAV audio generated via Python `wave` module
- **Command Executed**: `PYTHONPATH=. ./.venv/bin/pytest tests/test_real_local_render.py`
- **Output Location**: `/tmp/real_local_render_test_.../output/final.mp4`
- **Verification Results**:
  - Output file created: YES
  - Size > 0 bytes: YES
  - FFmpeg container inspection: `Input #0, mov,mp4,m4a, duration: 00:00:03.00, Video: h264, Audio: aac`

---

## 8. Remaining Renderer Limitations & Next Steps

1. **AI Provider Media Mocks**: AI provider wrapper classes (`voice_provider.py`, `music_provider.py`) currently return mock video sample URLs (`TearsOfSteel.mp4`) instead of real audio files (`.mp3`/`.wav`). These mock URLs need to be updated to output proper audio formats in the next phase.
2. **Replicate Async Polling**: AI provider wrappers (`FluxImageProvider`, `Wan2AnimationProvider`) require async prediction polling to return real image/video URLs.
3. **Frontend Integration**: The frontend detail view needs to connect to `POST /api/v1/projects/{project_id}/generate-full-pipeline` and render the final MP4 in an HTML5 video player.
