# Phase 7: Storyboard Agent & Scene Planning Specification

## 1. Executive Summary

Phase 7 builds the Storyboard Agent & Visual Scene Planning engine for KidsAI Studio:
- **Input**: Approved Story Script JSON (from Phase 6).
- **Process**: Converts text scenes into shot-by-shot visual, camera, transition, and character placement plans. Audits character and environmental continuity across all scenes.
- **Constraint**: **NO image files, voices, or video renders are generated in Phase 7**. Generates ONLY structured Storyboard JSON.

---

## 2. Storyboard Schema & Hierarchy

```
Storyboard (Root)
│
├── Global Metadata (project_id, total_scenes, total_duration_seconds, visual_style, global_color_palette)
│
└── Scenes (Array of StoryboardScene)
    ├── Narrative Arc (beginning, middle, ending)
    ├── Visual Plan (environment, time_of_day, weather, background, foreground, key_objects, color_palette, lighting_style, mood, atmosphere, composition)
    ├── Camera Plan (shot_type, angle, movement, camera_direction, camera_speed, focal_point)
    ├── Transition Directive (type, duration_seconds)
    └── Character References (character_name, expression, pose, eye_direction, interaction, visibility, importance)
```

---

## 3. Storyboard Output JSON Example

```json
{
  "project_id": "proj_demo_colors",
  "story_title": "Rexy's Colorful Rainbow Party",
  "total_scenes": 4,
  "total_duration_seconds": 60.0,
  "visual_style": "3D Pixar Render",
  "global_color_palette": ["Lime Green", "Bright Yellow", "Sky Blue", "Sunny Orange"],
  "scenes": [
    {
      "scene_number": 1,
      "scene_title": "Morning in the Dino Valley",
      "purpose": "Establish hero character and peaceful valley environment",
      "learning_goal": "Identify morning routine & peaceful setting",
      "estimated_duration": 15.0,
      "energy_level": "Medium",
      "scene_importance": "High",
      "narrative_arc": {
        "beginning": "Rexy wakes up in the lush green meadow",
        "middle": "Rexy stretches his arms happily at the golden morning sun",
        "ending": "Penny the Pterodactyl flies down to greet Rexy"
      },
      "narration_text": "High up in the sunny green valley, Rexy the baby dinosaur woke up ready for a colorful adventure!",
      "visual_plan": {
        "environment": "Sunny Dinosaur Meadow",
        "time_of_day": "Morning Golden Hour",
        "weather": "Clear & Sunny",
        "background": "Rolling emerald hills, gentle distant volcanoes, giant colorful sunflowers",
        "foreground": "Soft grass with sparkling dew drops",
        "key_objects": ["Giant Sunflower", "Sparkling Dew"],
        "color_palette": ["Lime Green", "Golden Yellow", "Sky Blue"],
        "lighting_style": "Soft Warm Golden Sunlight",
        "mood": "Cheerful & Inviting",
        "atmosphere": "Magical & Serene",
        "composition": "Rule of thirds centering Rexy on grass"
      },
      "camera_plan": {
        "shot_type": "Wide Shot",
        "angle": "Eye Level",
        "movement": "Slow Pan",
        "camera_direction": "Left to Right",
        "camera_speed": "Gentle",
        "focal_point": "Rexy the baby T-Rex"
      },
      "transition": {
        "type": "Cross Fade",
        "duration_seconds": 1.0
      },
      "character_references": [
        {
          "character_name": "Rexy",
          "expression": "Joyful & Energetic",
          "pose": "Stretching with arms wide open",
          "eye_direction": "Towards camera / viewer",
          "interaction": "Greeting the morning sun",
          "visibility": "Full Body",
          "importance": "Primary Hero"
        }
      ]
    }
  ]
}
```

---

## 4. Continuity & Quality Audit Rules

1. **Camera Completeness**: Verifies shot_type, angle, motion, and speed are present.
2. **Transition Completeness**: Validates transition type (Cut, Fade, Cross Fade, Slide, Zoom, Match Cut).
3. **Character Continuity Audit**: Tracks character appearances across all scenes to ensure expression, pose, and gaze instructions are assigned.
4. **Environment Continuity**: Enforces consistent time of day progression and master color palette compliance.

---

## 5. Verification Results

- [x] **Storyboard Agent**: Produces structured Storyboard JSON with 0 image generation calls.
- [x] **Continuity Auditor**: Passes scene consistency checks across visual, camera, and character layers.
- [x] **Backend Test Suite**: `12 passed in 0.23s` (Pytest).
- [x] **Frontend Compilation**: Next.js App Router generated all 13 routes with **0 errors**.
