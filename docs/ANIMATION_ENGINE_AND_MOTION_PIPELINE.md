# Phase 9: Animation Engine & Motion Generation Pipeline Specification

## 1. Executive Summary

Phase 9 builds the Animation Engine & Motion Generation Pipeline:
- **Input**: Approved Scene Images (from Phase 8) & Storyboard Camera Plans.
- **Process**:
  1. Motion Planner maps camera paths (`Pan`, `Zoom`, `Tracking`, `Orbit`), character actions (`Idle`, `Walking`, `Jumping`), and environmental FX (`Wind`, `Clouds`).
  2. Animation Prompt Composer builds motion directives (`packages/prompts/animation.md`).
  3. Animation Provider Adapter (Wan 2.2 / Mock) renders 24fps animated video clips.
  4. Animation Validation Service verifies duration, frame rate (24/30fps), resolution (1280x720), and video URL integrity.
- **Constraint**: **NO voice, music, subtitles, or video composition are executed in Phase 9**. Produces individual scene video clips.

---

## 2. Motion Plan JSON Schema

```json
{
  "motion_type": "Tracking Shot & Running",
  "camera_path": "Tracking Shot",
  "camera_speed": "Gentle",
  "character_motion": "Rexy running with joyful wave",
  "environment_motion": "Soft breeze swaying background foliage during Morning, subtle moving clouds",
  "duration_seconds": 5.0,
  "frame_rate": 24,
  "speed": "Normal",
  "transition_style": "Cross Fade",
  "complexity": "Medium"
}
```

---

## 3. Animated Scene Clip JSON Schema

```json
{
  "animation_id": "anim_proj_123_1_b3c4d5",
  "project_id": "proj_123",
  "scene_number": 1,
  "motion_plan": { ... },
  "composed_motion_prompt": "Cinematic 3D animation of Rexy in Sunny Dinosaur Meadow. Camera motion: Tracking Shot at Gentle speed...",
  "provider": "Wan2.2-i2v-Mock",
  "seed": 101,
  "width": 1280,
  "height": 720,
  "aspect_ratio": "16:9",
  "duration_seconds": 5.0,
  "frame_rate": 24,
  "generation_time_seconds": 0.04,
  "status": "APPROVED",
  "storage_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
  "thumbnail_url": "https://placehold.co/400x225/1A1D27/FFFFFF/png?text=Animated+Scene+1"
}
```

---

## 4. Verification Results

- [x] **Motion Planner Service**: Accurately maps shot types to camera paths and character actions.
- [x] **Animation Provider Adapter**: Wan 2.2 and Mock providers with fallback logic.
- [x] **Animation Validation Service**: Validates clip duration, 24fps frame rate, and URL format.
- [x] **Backend Pytest Suite**: `18 passed in 0.19s`.
- [x] **Frontend Production Build**: Next.js App Router generated all 13 routes with **0 errors**.
