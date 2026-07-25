# Database Schema — KidsAI Studio v2.0

## PostgreSQL Tables

### `users`
- `id`: UUID PRIMARY KEY
- `email`: VARCHAR UNIQUE
- `full_name`: VARCHAR
- `avatar_url`: TEXT
- `role`: VARCHAR DEFAULT 'USER'
- `created_at`: TIMESTAMPTZ DEFAULT NOW()
- `updated_at`: TIMESTAMPTZ DEFAULT NOW()

### `projects`
- `id`: VARCHAR PRIMARY KEY
- `title`: VARCHAR NOT NULL
- `description`: TEXT
- `prompt`: TEXT NOT NULL
- `target_age_group`: VARCHAR DEFAULT '3-5'
- `language`: VARCHAR DEFAULT 'English (US)'
- `video_length`: VARCHAR DEFAULT 'Standard (2-3 min)'
- `aspect_ratio`: VARCHAR DEFAULT '16:9'
- `video_style`: VARCHAR DEFAULT '3D Pixar Render'
- `voice`: VARCHAR DEFAULT 'Storyteller Emma'
- `status`: VARCHAR DEFAULT 'DRAFT'
- `thumbnail_url`: TEXT
- `favorite`: BOOLEAN DEFAULT FALSE
- `archived`: BOOLEAN DEFAULT FALSE
- `owner_id`: UUID REFERENCES users(id)
- `created_at`: TIMESTAMPTZ DEFAULT NOW()
- `updated_at`: TIMESTAMPTZ DEFAULT NOW()
- `last_opened_at`: TIMESTAMPTZ

### `production_plans` (Phase 6)
- `id`: UUID PRIMARY KEY
- `project_id`: VARCHAR REFERENCES projects(id) ON DELETE CASCADE
- `educational_objective`: TEXT NOT NULL
- `scene_count`: INT NOT NULL
- `narration_style`: VARCHAR
- `visual_style`: VARCHAR
- `character_requirements`: JSONB
- `music_mood_plan`: TEXT
- `animation_style_plan`: TEXT
- `thumbnail_concept_plan`: TEXT
- `seo_strategy_plan`: JSONB
- `quality_rules`: JSONB
- `created_at`: TIMESTAMPTZ DEFAULT NOW()

### `story_scripts` (Phase 6)
- `id`: UUID PRIMARY KEY
- `project_id`: VARCHAR REFERENCES projects(id) ON DELETE CASCADE
- `story_title`: VARCHAR NOT NULL
- `story_summary`: TEXT NOT NULL
- `educational_goal`: TEXT NOT NULL
- `ending_call_to_action`: TEXT
- `characters`: JSONB NOT NULL
- `scenes`: JSONB NOT NULL
- `created_at`: TIMESTAMPTZ DEFAULT NOW()

### `storyboards` (Phase 7)
- `id`: UUID PRIMARY KEY
- `project_id`: VARCHAR REFERENCES projects(id) ON DELETE CASCADE
- `story_title`: VARCHAR NOT NULL
- `total_scenes`: INT NOT NULL
- `total_duration_seconds`: FLOAT NOT NULL
- `visual_style`: VARCHAR NOT NULL
- `global_color_palette`: JSONB NOT NULL
- `scenes`: JSONB NOT NULL
- `approved`: BOOLEAN DEFAULT FALSE
- `created_at`: TIMESTAMPTZ DEFAULT NOW()
- `updated_at`: TIMESTAMPTZ DEFAULT NOW()

### `character_profiles` (Phase 8)
- `character_id`: VARCHAR PRIMARY KEY
- `project_id`: VARCHAR REFERENCES projects(id) ON DELETE CASCADE
- `name`: VARCHAR NOT NULL
- `species`: VARCHAR NOT NULL
- `age_group`: VARCHAR
- `gender`: VARCHAR
- `personality`: TEXT
- `role`: VARCHAR
- `backstory`: TEXT
- `skin_color`: VARCHAR
- `clothing`: VARCHAR
- `primary_colors`: JSONB
- `reference_prompt`: TEXT NOT NULL
- `negative_prompt`: TEXT NOT NULL
- `reference_image_url`: TEXT
- `created_at`: TIMESTAMPTZ DEFAULT NOW()

### `generated_images` (Phase 8)
- `image_id`: VARCHAR PRIMARY KEY
- `project_id`: VARCHAR REFERENCES projects(id) ON DELETE CASCADE
- `scene_number`: INT NOT NULL
- `composed_prompt`: TEXT NOT NULL
- `negative_prompt`: TEXT NOT NULL
- `provider`: VARCHAR NOT NULL
- `seed`: INT NOT NULL
- `width`: INT DEFAULT 1280
- `height`: INT DEFAULT 720
- `aspect_ratio`: VARCHAR DEFAULT '16:9'
- `generation_time_seconds`: FLOAT
- `status`: VARCHAR DEFAULT 'GENERATED'
- `storage_url`: TEXT NOT NULL
- `thumbnail_url`: TEXT NOT NULL
- `created_at`: TIMESTAMPTZ DEFAULT NOW()

### `animated_scene_clips` (Phase 9)
- `animation_id`: VARCHAR PRIMARY KEY
- `project_id`: VARCHAR REFERENCES projects(id) ON DELETE CASCADE
- `scene_number`: INT NOT NULL
- `motion_plan`: JSONB NOT NULL
- `composed_motion_prompt`: TEXT NOT NULL
- `provider`: VARCHAR NOT NULL
- `seed`: INT NOT NULL
- `width`: INT DEFAULT 1280
- `height`: INT DEFAULT 720
- `aspect_ratio`: VARCHAR DEFAULT '16:9'
- `duration_seconds`: FLOAT DEFAULT 5.0
- `frame_rate`: INT DEFAULT 24
- `generation_time_seconds`: FLOAT
- `status`: VARCHAR DEFAULT 'GENERATED'
- `storage_url`: TEXT NOT NULL
- `thumbnail_url`: TEXT NOT NULL
- `created_at`: TIMESTAMPTZ DEFAULT NOW()

### `voice_narration_assets` (Phase 10)
- `audio_id`: VARCHAR PRIMARY KEY
- `project_id`: VARCHAR REFERENCES projects(id) ON DELETE CASCADE
- `scene_number`: INT NOT NULL
- `dialogue_segments`: JSONB NOT NULL
- `lip_sync`: JSONB NOT NULL
- `voice_name`: VARCHAR DEFAULT 'Storyteller Emma'
- `voice_type`: VARCHAR DEFAULT 'Child Friendly Narrator'
- `emotion`: VARCHAR DEFAULT 'Cheerful & Inviting'
- `language`: VARCHAR DEFAULT 'English (US)'
- `duration_seconds`: FLOAT DEFAULT 5.0
- `sample_rate`: INT DEFAULT 24000
- `audio_format`: VARCHAR DEFAULT 'MP3'
- `provider`: VARCHAR NOT NULL
- `status`: VARCHAR DEFAULT 'GENERATED'
- `storage_url`: TEXT NOT NULL
- `generation_time_seconds`: FLOAT
- `created_at`: TIMESTAMPTZ DEFAULT NOW()

### `mixed_audio_tracks` (Phase 11)
- `mix_id`: VARCHAR PRIMARY KEY
- `project_id`: VARCHAR REFERENCES projects(id) ON DELETE CASCADE
- `scene_number`: INT NOT NULL
- `music_plan`: JSONB NOT NULL
- `sound_effects`: JSONB NOT NULL
- `ambient_plan`: JSONB NOT NULL
- `narration_volume`: FLOAT DEFAULT 1.0
- `music_ducked_volume`: FLOAT DEFAULT 0.25
- `ambient_volume`: FLOAT DEFAULT 0.15
- `sfx_volume`: FLOAT DEFAULT 0.5
- `master_loudness_lufs`: FLOAT DEFAULT -14.0
- `duration_seconds`: FLOAT DEFAULT 5.0
- `sample_rate`: INT DEFAULT 44100
- `audio_format`: VARCHAR DEFAULT 'MP3'
- `provider`: VARCHAR NOT NULL
- `status`: VARCHAR DEFAULT 'GENERATED'
- `storage_url`: TEXT NOT NULL
- `generation_time_seconds`: FLOAT
- `created_at`: TIMESTAMPTZ DEFAULT NOW()

### `video_timelines` (Phase 12)
- `timeline_id`: VARCHAR PRIMARY KEY
- `project_id`: VARCHAR REFERENCES projects(id) ON DELETE CASCADE
- `aspect_ratio`: VARCHAR DEFAULT '16:9'
- `resolution`: VARCHAR DEFAULT '1080p'
- `frame_rate`: INT DEFAULT 24
- `total_duration_seconds`: FLOAT NOT NULL
- `scenes`: JSONB NOT NULL
- `created_at`: TIMESTAMPTZ DEFAULT NOW()

### `render_tasks` (Phase 12)
- `render_id`: VARCHAR PRIMARY KEY
- `project_id`: VARCHAR REFERENCES projects(id) ON DELETE CASCADE
- `timeline_id`: VARCHAR REFERENCES video_timelines(timeline_id) ON DELETE CASCADE
- `status`: VARCHAR DEFAULT 'COMPLETED'
- `resolution`: VARCHAR DEFAULT '1080p'
- `codec`: VARCHAR DEFAULT 'H.264'
- `output_format`: VARCHAR DEFAULT 'MP4'
- `file_size_bytes`: BIGINT NOT NULL
- `preview_url`: TEXT NOT NULL
- `final_video_url`: TEXT NOT NULL
- `generation_time_seconds`: FLOAT
- `created_at`: TIMESTAMPTZ DEFAULT NOW()

### `publishing_asset_bundles` (Phase 13)
- `bundle_id`: VARCHAR PRIMARY KEY
- `project_id`: VARCHAR REFERENCES projects(id) ON DELETE CASCADE
- `thumbnails`: JSONB NOT NULL
- `seo`: JSONB NOT NULL
- `status`: VARCHAR DEFAULT 'GENERATED'
- `created_at`: TIMESTAMPTZ DEFAULT NOW()

### `connected_accounts` (Phase 14)
- `account_id`: VARCHAR PRIMARY KEY
- `platform`: VARCHAR NOT NULL
- `display_name`: VARCHAR NOT NULL
- `channel_name`: VARCHAR NOT NULL
- `avatar_url`: TEXT NOT NULL
- `connection_status`: VARCHAR DEFAULT 'CONNECTED'
- `permissions`: JSONB NOT NULL
- `last_synced_at`: TIMESTAMPTZ DEFAULT NOW()

### `publishing_queue_items` (Phase 14)
- `queue_id`: VARCHAR PRIMARY KEY
- `project_id`: VARCHAR REFERENCES projects(id) ON DELETE CASCADE
- `account_id`: VARCHAR REFERENCES connected_accounts(account_id) ON DELETE CASCADE
- `platform`: VARCHAR NOT NULL
- `plan`: JSONB NOT NULL
- `status`: VARCHAR DEFAULT 'QUEUED'
- `progress_percentage`: FLOAT DEFAULT 0.0
- `platform_post_id`: VARCHAR
- `post_url`: TEXT
- `error_message`: TEXT
- `attempt_count`: INT DEFAULT 1
- `published_at`: TIMESTAMPTZ
- `created_at`: TIMESTAMPTZ DEFAULT NOW()

### `optimization_reports` (Phase 16)
- `project_id`: VARCHAR PRIMARY KEY REFERENCES projects(id) ON DELETE CASCADE
- `overall_score`: FLOAT NOT NULL
- `pacing_score`: FLOAT NOT NULL
- `educational_score`: FLOAT NOT NULL
- `visual_score`: FLOAT NOT NULL
- `audio_score`: FLOAT NOT NULL
- `strengths`: JSONB NOT NULL
- `weaknesses`: JSONB NOT NULL
- `suggestions`: JSONB NOT NULL
- `created_at`: TIMESTAMPTZ DEFAULT NOW()

### `trend_reports` (Phase 16)
- `trend_id`: VARCHAR PRIMARY KEY
- `topic`: VARCHAR NOT NULL
- `category`: VARCHAR NOT NULL
- `search_volume_score`: FLOAT NOT NULL
- `competition_level`: VARCHAR NOT NULL
- `opportunity_score`: FLOAT NOT NULL
- `target_age_group`: VARCHAR NOT NULL
- `seasonal_keywords`: JSONB NOT NULL

### `workflow_automations` (Phase 16)
- `workflow_id`: VARCHAR PRIMARY KEY
- `name`: VARCHAR NOT NULL
- `trigger_event`: VARCHAR NOT NULL
- `actions`: JSONB NOT NULL
- `is_active`: BOOLEAN DEFAULT TRUE
- `created_at`: TIMESTAMPTZ DEFAULT NOW()
