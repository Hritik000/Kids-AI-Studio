-- Animated scene clips table schema
-- Based on app/models/animation.py AnimatedSceneClip model

-- Animated scene clips table
CREATE TABLE IF NOT EXISTS animated_scene_clips (
    animation_id VARCHAR PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    scene_number INT NOT NULL,
    motion_plan JSONB NOT NULL,
    composed_motion_prompt TEXT NOT NULL,
    provider VARCHAR NOT NULL,
    seed INT NOT NULL,
    width INT DEFAULT 1280,
    height INT DEFAULT 720,
    aspect_ratio VARCHAR DEFAULT '16:9',
    duration_seconds FLOAT DEFAULT 5.0,
    frame_rate INT DEFAULT 24,
    generation_time_seconds FLOAT,
    status VARCHAR DEFAULT 'GENERATED' CHECK (status IN ('GENERATED', 'APPROVED', 'REJECTED', 'FAILED')),
    storage_url TEXT NOT NULL,
    thumbnail_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()) NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_animated_scene_clips_project_id ON animated_scene_clips(project_id);
CREATE INDEX IF NOT EXISTS idx_animated_scene_clips_scene_number ON animated_scene_clips(scene_number);
CREATE INDEX IF NOT EXISTS idx_animated_scene_clips_status ON animated_scene_clips(status);
CREATE INDEX IF NOT EXISTS idx_animated_scene_clips_created_at ON animated_scene_clips(created_at);

-- Comments
COMMENT ON TABLE animated_scene_clips IS 'Table storing animated video clips for project scenes';
COMMENT ON COLUMN animated_scene_clips.animation_id IS 'Unique identifier for the animated clip';
COMMENT ON COLUMN animated_scene_clips.project_id IS 'Reference to the project this clip belongs to';
COMMENT ON COLUMN animated_scene_clips.scene_number IS 'Scene number this clip corresponds to';
COMMENT ON COLUMN animated_scene_clips.motion_plan IS 'JSONB structure detailing the motion plan for the animation';
COMMENT ON COLUMN animated_scene_clips.composed_motion_prompt IS 'The final prompt used for animation generation';
COMMENT ON COLUMN animated_scene_clips.provider IS 'AI provider used for animation generation (e.g., Wan 2.2, Pika, Runway)';
COMMENT ON COLUMN animated_scene_clips.seed IS 'Random seed used for generation';
COMMENT ON COLUMN animated_scene_clips.width IS 'Width of the animated clip in pixels';
COMMENT ON COLUMN animated_scene_clips.height IS 'Height of the animated clip in pixels';
COMMENT ON COLUMN animated_scene_clips.aspect_ratio IS 'Aspect ratio of the animated clip';
COMMENT ON COLUMN animated_scene_clips.duration_seconds IS 'Duration of the animated clip in seconds';
COMMENT ON COLUMN animated_scene_clips.frame_rate IS 'Frame rate of the animated clip';
COMMENT ON COLUMN animated_scene_clips.generation_time_seconds IS 'Time taken to generate the animation in seconds';
COMMENT ON COLUMN animated_scene_clips.status IS 'Status of the animation generation process';
COMMENT ON COLUMN animated_scene_clips.storage_url IS 'URL where the full animation is stored';
COMMENT ON COLUMN animated_scene_clips.thumbnail_url IS 'URL where the thumbnail is stored';
COMMENT ON COLUMN animated_scene_clips.created_at IS 'Timestamp when animation was generated';