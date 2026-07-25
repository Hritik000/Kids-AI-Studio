# Phase 11: Music Generation, Sound Effects & Audio Mixing Pipeline Specification

## 1. Executive Summary

Phase 11 builds the Music Generation, Sound Effects, Ambient Audio & Intelligent Audio Mixing Pipeline:
- **Input**: Approved Voice Narration Assets & Storyboard Scenes.
- **Process**:
  1. Music Planner determines genre, mood (`Cheerful & Playful`), BPM (112), key (`C Major`), and instrumentation.
  2. Sound Effect Service generates scene-matched timed SFX items (`Footsteps`, `Jump`, `Sparkle`).
  3. Ambient Audio Service generates environment soundscapes (`Jungle`, `Meadow`, `Ocean`).
  4. Music Provider Adapter (Stable Audio Open / Mock) synthesizes soundtrack.
  5. Audio Mixer & Mastering Engine applies automatic speech ducking (-12dB) and loudness mastering (-14 LUFS).
- **Constraint**: **NO subtitle generation, final video rendering, YouTube publishing, or analytics are executed in Phase 11**. Produces mastered multi-track audio files.

---

## 2. Music Plan & SFX JSON Schema

```json
{
  "music_plan": {
    "track_id": "mus_a1b2c3",
    "genre": "Child-Friendly Acoustic Orchestral",
    "mood": "Cheerful & Playful",
    "bpm": 112,
    "key": "C Major",
    "instruments": ["Marimba", "Acoustic Guitar", "Pizzicato Strings", "Flute"],
    "duration_seconds": 60.0,
    "loop_enabled": true
  },
  "sound_effects": [
    {
      "sfx_id": "sfx_1_1_footsteps",
      "name": "Soft Dino Footsteps",
      "category": "Footsteps",
      "timestamp_seconds": 0.8,
      "volume_level": 0.4
    }
  ],
  "ambient_plan": {
    "ambient_id": "amb_d4e5f6",
    "environment_type": "Sunny Dinosaur Meadow",
    "volume_level": 0.15
  }
}
```

---

## 3. Mixed Audio Track JSON Schema

```json
{
  "mix_id": "mix_proj_123_1_e5f6g7",
  "project_id": "proj_123",
  "scene_number": 1,
  "music_plan": { ... },
  "sound_effects": [ ... ],
  "ambient_plan": { ... },
  "narration_volume": 1.0,
  "music_ducked_volume": 0.25,
  "ambient_volume": 0.15,
  "sfx_volume": 0.5,
  "master_loudness_lufs": -14.0,
  "duration_seconds": 5.0,
  "sample_rate": 44100,
  "audio_format": "MP3",
  "provider": "StableAudio-Open-v1",
  "status": "APPROVED",
  "storage_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
  "generation_time_seconds": 1.2
}
```

---

## 4. Verification Results

- [x] **Music Planner Service**: Accurately selects child-friendly acoustic genre, BPM, and mood.
- [x] **Sound Effects & Ambient Services**: Matches scene character poses to footstep/jump SFX and ambient soundscapes.
- [x] **Audio Mixer & Mastering Engine**: Applies -12dB music ducking and -14.0 LUFS loudness mastering.
- [x] **Backend Pytest Suite**: `26 passed in 0.28s`.
- [x] **Frontend Production Build**: Next.js App Router generated all 13 routes with **0 errors**.
