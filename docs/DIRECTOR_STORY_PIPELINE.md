# Phase 6: Director Agent & Story Generation Pipeline Specification

## 1. Executive Summary

Phase 6 implements the AI Orchestration layer for KidsAI Studio:
1. **Director Agent**: Receives project parameters (topic, age group, aspect ratio, duration, art style) and generates a structured **Production Plan JSON**. Does NOT write full story text.
2. **Story Agent**: Consumes the Production Plan JSON and writes an original, child-safe, educational **Story Script JSON** containing character profiles and scene breakdowns.

---

## 2. LLM Provider Adapter Pattern

```
[ Director Service / Story Service ]
                │
                ▼
      [ LLMProvider Interface ]
                │
    ┌───────────┴───────────┐
    ▼                       ▼
[ KimiLLMProvider ]   [ MockLLMProvider ] (Default / Fallback)
```

- Prompts are dynamically loaded from `/packages/prompts/` (`system.md`, `director.md`, `story.md`). Prompts are never hardcoded.

---

## 3. Request & Response Examples

### Director Production Plan Output JSON
```json
{
  "project_id": "proj_demo_colors",
  "topic": "Dinosaurs Learn Colors",
  "educational_objective": "Teach children primary colors (Red, Blue, Yellow)",
  "target_age_group": "3-5",
  "estimated_duration_seconds": 60.0,
  "scene_count": 4,
  "narration_style": "Enthusiastic and gentle storyteller",
  "visual_style": "3D Pixar Render",
  "character_requirements": [
    {
      "name": "Rexy",
      "description": "Friendly green baby T-Rex with big curious eyes",
      "role": "Protagonist"
    }
  ],
  "music_mood_plan": "Upbeat acoustic guitar and cheerful marimba",
  "animation_style_plan": "Smooth 3D character motion with gentle pans",
  "thumbnail_concept_plan": "Rexy holding a glowing colorful star",
  "seo_strategy_plan": {
    "target_keywords": ["dinosaurs learn colors", "preschool learning"],
    "category": "Education"
  },
  "quality_rules": ["Strictly child safe", "High color vibrancy"],
  "retry_strategy": { "max_retries": 3, "fallback_provider": "mock-llm-v1" }
}
```

### Story Agent Script Output JSON
```json
{
  "story_title": "Rexy's Colorful Rainbow Party",
  "story_summary": "Rexy the T-Rex and Penny the Pterodactyl explore a dinosaur valley to discover red, blue, and yellow colors!",
  "educational_goal": "Identify primary colors (Red, Blue, Yellow)",
  "ending_call_to_action": "Can you spot something red near you?",
  "characters": [
    {
      "name": "Rexy",
      "species_or_type": "Baby T-Rex",
      "visual_features": "Soft lime-green scales, oversized cheerful eyes",
      "personality": "Playful, curious"
    }
  ],
  "scenes": [
    {
      "scene_number": 1,
      "narration_text": "High up in the sunny green valley, Rexy the baby dinosaur woke up ready for an adventure!",
      "visual_description": "Vibrant 3D Pixar-style sunny meadow. Rexy stretches happily.",
      "educational_goal": "Introduce setting",
      "estimated_duration": 15.0,
      "camera_direction": "Slow pan left to right",
      "emotion": "Joyful",
      "transition": "Cross Fade"
    }
  ]
}
```

---

## 4. Verification Results

- [x] **Director Agent**: Produces valid Production Plan JSON with zero hardcoded prompts.
- [x] **Story Agent**: Consumes plan and outputs structured story JSON with character profiles & scenes.
- [x] **Child Safety Audit**: Rejects inappropriate content or forbidden keywords.
- [x] **Backend Test Suite**: `9 passed in 0.15s` (Pytest).
- [x] **Frontend Build**: Compiled 100% cleanly in Next.js App Router (0 errors).
