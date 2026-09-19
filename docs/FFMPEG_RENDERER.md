# Industry-Grade FFmpeg Rendering Engine

Production-grade, high-performance FFmpeg video rendering engine for **KidsAI Studio**.
This module transforms storyboards, generated Pixar-style scene images, voice narrations, background music, and subtitles into a broadcast-ready **1080p MP4** video file with synchronized audio and CTR-optimized thumbnails.

---

## 🏛️ Architecture & Module Structure

The rendering engine lives inside `apps/backend/app/services/rendering/`:

```
app/services/rendering/
├── __init__.py          # Exposed rendering package interfaces
├── models.py            # Pydantic data schemas for scene, audio, subtitle & task objects
├── config.py            # Centralized rendering options (resolutions, codecs, ducking, LUFS, subtitles)
├── validator.py         # Pre-render asset validation & FFmpeg environment checks
├── ffmpeg.py            # Safe subprocess runner, binary auto-discovery & log capturing
├── camera.py            # FFmpeg zoompan camera motion engine (8 directions)
├── transitions.py       # Multi-scene xfade transition filter builder
├── subtitles.py         # SRT/VTT parser, ASS style generator & subtitle burn-in overlay
├── audio.py             # Multi-track audio mixing, sidechain speech ducking & loudnorm
├── thumbnail.py         # Middle/highest-scoring frame extraction engine
├── timeline.py          # Automated scene timeline builder from storyboard/project assets
└── renderer.py          # Core pipeline orchestrator
```

---

## 🔄 Rendering Pipeline Workflow

```
Project Assets (storyboard.json, images/, narration.wav, music.mp3, subtitles.srt)
                            │
                            ▼
               1. Pre-Render Validation (validator.py)
                            │
                            ▼
        2. Camera Motion Engine (camera.py / zoompan)
            [Scene 1] [Scene 2] ... [Scene N] Clips
                            │
                            ▼
       3. Scene Transition Engine (transitions.py / xfade)
            [Master Concatenated Video Track]
                            │
                            ▼
      4. Subtitle Overlay Engine (subtitles.py / ASS burn-in)
            [Subtitled Master Video Track]
                            │
                            ▼
   5. Multi-Track Audio Engine (audio.py / amix + ducking + loudnorm)
            - Narration + Music Sidechain Ducking (-12dB)
            - EBU R128 Loudness Normalization (-14.0 LUFS)
                            │
                            ▼
     6. Final Muxing & Encoding (1080p, H.264, AAC, YUV420P)
            final.mp4
                            │
                            ▼
             7. Frame Extraction (thumbnail.py)
            thumbnail.jpg
                            │
                            ▼
               8. Temporary Workspace Cleanup
```

---

## 🎨 Camera Engine Filters (`camera.py`)

The camera motion engine translates camera directions into dynamic FFmpeg `zoompan` filter expressions:

| Motion Type | Description | FFmpeg Zoom / Center Expressions |
| :--- | :--- | :--- |
| **Zoom In** | Smooth center zoom from 1.0 to 1.25x | `z='min(1.0+on*step,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'` |
| **Zoom Out** | Smooth zoom out from 1.25x to 1.0 | `z='max(1.25-on*step,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'` |
| **Pan Left** | Fixed 1.25x zoom, pan right to left | `z='1.25':x='(1-on/D)*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)'` |
| **Pan Right** | Fixed 1.25x zoom, pan left to right | `z='1.25':x='(on/D)*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)'` |
| **Pan Up** | Fixed 1.25x zoom, pan bottom to top | `z='1.25':x='iw/2-(iw/zoom/2)':y='(1-on/D)*(ih-ih/zoom)'` |
| **Pan Down** | Fixed 1.25x zoom, pan top to bottom | `z='1.25':x='iw/2-(iw/zoom/2)':y='(on/D)*(ih-ih/zoom)'` |
| **Slow Dolly** | Subtle gradual push-in (1.0 -> 1.15x) | `z='min(1.0+on*step,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'` |
| **Static** | Standard static frame centered | `z='1.0':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'` |

---

## 🔀 Transition Engine (`transitions.py`)

Scene-to-scene transitions are implemented using the FFmpeg `xfade` complex filter:

```bash
[v0][v1]xfade=transition=fade:duration=0.50:offset=4.50[v_out]
```

Supported transitions:
- **Fade** (`fade`)
- **Crossfade** (`fade`)
- **Slide Left** (`slideleft`)
- **Slide Right** (`slideright`)
- **Zoom** (`circlecrop`)
- **Dissolve** (`dissolve`)
- **Cut** (direct zero-duration hard cut)

---

## 🎙️ Audio Ducking & Loudness Normalization (`audio.py`)

Audio mixing enforces child-friendly broadcast standards:
1. **Speech Ducking**: Uses `sidechaincompress` to automatically attenuate background music volume by **-12dB** whenever narration speech is present.
2. **Loudness Normalization**: Uses `loudnorm=I=-14:LRA=11:TP=-1` to target **-14.0 LUFS** integrated loudness for YouTube/TikTok/Reels compliance.
3. **Fade Transitions**: Applies 1.0s fade-in and 1.5s fade-out to background music tracks.

Filter graph sample:
```bash
[nar]asplit=2[nar_mix][nar_sc];
[music]afade=t=in:ss=0:d=1.0,afade=t=out:st=28.5:d=1.5[m_faded];
[m_faded][nar_sc]sidechaincompress=threshold=0.03:ratio=4:attack=100:release=300[m_ducked];
[nar_mix][m_ducked]amix=inputs=2:duration=first[a_unnorm];
[a_unnorm]loudnorm=I=-14:TP=-1[a_out]
```

---

## ⚡ Performance & Memory Strategy

1. **Streaming Processing**: Scenes are processed into temporary clip files (`scene_001.mp4`, `scene_002.mp4`) on disk rather than buffering decoded raw RGB video frames in RAM.
2. **Temporary Directory Isolation**: Uses `tempfile.TemporaryDirectory` which guarantees automatic removal of intermediate render files upon job completion or failure.
3. **Fallback Resiliency**:
   - Missing images automatically fall back to styled solid color canvas scenes without stopping the pipeline.
   - Missing audio tracks fall back to generated silent audio streams.
   - FFmpeg binary discovery checks system `PATH` and falls back to `imageio-ffmpeg` wheel binaries.

---

## ⚙️ Configuration Reference (`config.py`)

All rendering constants are centralized in `RenderingSettings`:

```python
from app.services.rendering import rendering_settings

# Video Settings
rendering_settings.video.width = 1920
rendering_settings.video.height = 1080
rendering_settings.video.fps = 30
rendering_settings.video.video_codec = "libx264"
rendering_settings.video.crf = 23

# Audio Settings
rendering_settings.audio.music_ducking_db = -12.0
rendering_settings.audio.target_lufs = -14.0
rendering_settings.audio.sample_rate = 44100

# Subtitle Styling
rendering_settings.subtitles.font_name = "Inter"
rendering_settings.subtitles.font_size = 24
rendering_settings.subtitles.margin_v = 40
```

---

## 🧪 Automated Testing

Run the rendering test suite:

```bash
cd apps/backend
PYTHONPATH=. ./.venv/bin/pytest tests/test_ffmpeg_rendering_engine.py tests/test_rendering.py
```
