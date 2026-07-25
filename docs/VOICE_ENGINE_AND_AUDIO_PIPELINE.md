# Phase 10: Voice Generation, Dialogue, Lip Sync & Audio Pipeline Specification

## 1. Executive Summary

Phase 10 builds the Voice Generation, Dialogue, Lip Sync & Audio Pipeline:
- **Input**: Approved Story Script & Storyboard Scenes.
- **Process**:
  1. Dialogue Planner splits scene narration into timed `DialogueSegment` items with emotional metadata and word emphasis.
  2. Voice Provider Adapter (Kokoro TTS / ElevenLabs / Mock) synthesizes child-friendly speech narration.
  3. Lip Sync Engine generates viseme mouth shape timelines (`A`, `E`, `I`, `O`, `U`, `M`, `Rest`) and random eye blink markers.
  4. Audio Validator verifies duration, sample rate (24000/44100Hz), and audio URL integrity.
- **Constraint**: **NO music, sound effects, subtitles, or video composition are executed in Phase 10**. Produces individual scene audio narration & visemes.

---

## 2. Dialogue Segment & Viseme Timeline JSON Schema

```json
{
  "dialogue_segments": [
    {
      "segment_id": "seg_s1_1_a1b2",
      "scene_number": 1,
      "speaker_name": "Narrator",
      "speaker_role": "Narrator",
      "text": "Rexy found a giant red flower!",
      "emotional_tone": "Cheerful & Inviting",
      "speech_speed": 1.0,
      "pause_duration_seconds": 0.3,
      "emphasis_words": ["giant", "flower"]
    }
  ],
  "lip_sync": {
    "visemes": [
      { "timestamp_seconds": 0.2, "mouth_shape": "R", "duration_seconds": 0.14 },
      { "timestamp_seconds": 0.34, "mouth_shape": "E", "duration_seconds": 0.16 },
      { "timestamp_seconds": 0.5, "mouth_shape": "Rest", "duration_seconds": 0.2 }
    ],
    "blink_timestamps": [1.5, 4.0]
  }
}
```

---

## 3. Voice Narration Asset JSON Schema

```json
{
  "audio_id": "aud_proj_123_1_c4d5e6",
  "project_id": "proj_123",
  "scene_number": 1,
  "dialogue_segments": [ ... ],
  "lip_sync": { ... },
  "voice_name": "Storyteller Emma",
  "voice_type": "Child Friendly Narrator",
  "emotion": "Cheerful & Inviting",
  "language": "English (US)",
  "duration_seconds": 5.0,
  "sample_rate": 24000,
  "audio_format": "MP3",
  "provider": "KokoroTTS-v1-Mock",
  "status": "APPROVED",
  "storage_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
  "generation_time_seconds": 0.08
}
```

---

## 4. Verification Results

- [x] **Dialogue Planner Service**: Accurately splits narration text into timed dialogue turns.
- [x] **Voice Provider Adapter**: Kokoro TTS and ElevenLabs adapters with fallback logic.
- [x] **Lip Sync Engine**: Calculates viseme mouth shape keyframes and blink markers.
- [x] **Backend Pytest Suite**: `22 passed in 0.21s`.
- [x] **Frontend Production Build**: Next.js App Router generated all 13 routes with **0 errors**.
