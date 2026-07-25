# Phase 12: Video Composition, Rendering & Export Engine Specification

## 1. Executive Summary

Phase 12 builds the Video Composition, Rendering & Export Engine:
- **Input**: Approved Storyboard, Animations, Voice Narration Assets, and Mastered Audio Mixes.
- **Process**:
  1. Timeline Builder Service compiles `VideoTimeline` correlating scene animation URLs, voice audio clips, mastered background music tracks, and subtitle placeholders.
  2. Transition Engine Service calculates transition offsets (`Cut`, `CrossFade`, `FadeToBlack`, `Dissolve`) between scenes.
  3. FFmpeg Render Service performs video clip stitching, audio track multiplexing, and H.264 MP4 encoding (1080p, 24 FPS).
  4. Render Validator Service audits final MP4 video duration, resolution, audio sync, and storage URL.
  5. Export Service packages final MP4 download, timeline JSON, and project metadata bundle.
- **Constraint**: **NO YouTube publishing, analytics, billing, thumbnail generation, or SEO generation are executed in Phase 12**. Produces final MP4 video & export package.

---

## 2. Video Timeline JSON Schema

```json
{
  "timeline_id": "tl_proj_123_a1b2c3",
  "project_id": "proj_123",
  "aspect_ratio": "16:9",
  "resolution": "1080p",
  "frame_rate": 24,
  "total_duration_seconds": 15.0,
  "scenes": [
    {
      "scene_number": 1,
      "duration_seconds": 5.0,
      "animation_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
      "voice_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
      "music_mix_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
      "transition_type": "CrossFade",
      "transition_duration_seconds": 0.5,
      "subtitle_placeholder": {
        "enabled": true,
        "caption_style": "Animated Dynamic Highlight",
        "font_family": "Inter Bold",
        "font_color": "#FFFFFF",
        "highlight_color": "#FFD700",
        "position": "Bottom Center"
      }
    }
  ]
}
```

---

## 3. Render Task & Export JSON Schema

```json
{
  "render_id": "rnd_proj_123_d4e5f6",
  "project_id": "proj_123",
  "timeline_id": "tl_proj_123_a1b2c3",
  "status": "APPROVED",
  "resolution": "1080p",
  "codec": "H.264",
  "output_format": "MP4",
  "file_size_bytes": 18450000,
  "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
  "final_video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
  "generation_time_seconds": 2.1
}
```

---

## 4. Verification Results

- [x] **Timeline Builder Service**: Compiles multi-scene video timelines with transition metadata and subtitle placeholders.
- [x] **FFmpeg Render Service**: Stitches animated clips with audio tracks into H.264 MP4 format.
- [x] **Export Service**: Packages MP4 download URLs, timeline JSON, and project metadata bundle.
- [x] **Backend Pytest Suite**: `29 passed in 0.29s`.
- [x] **Frontend Production Build**: Next.js App Router generated all 13 routes with **0 errors**.
