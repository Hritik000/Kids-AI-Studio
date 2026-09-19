-- Projects table schema
-- Based on app/models/project.py Project model

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    prompt TEXT NOT NULL,
    target_age_group VARCHAR(20) DEFAULT '3-5',
    language VARCHAR(50) DEFAULT 'English (US)',
    video_length VARCHAR(50) DEFAULT 'Standard (2-3 min)',
    aspect_ratio VARCHAR(10) DEFAULT '16:9',
    video_style VARCHAR(100) DEFAULT '3D Pixar Render',
    voice VARCHAR(100) DEFAULT 'Storyteller Emma',
    status VARCHAR(20) DEFAULT 'DRAFT' CHECK (status IN (
        'DRAFT', 'PLANNING', 'STORY_READY', 'STORYBOARD_READY', 
        'IMAGES_READY', 'ANIMATION_READY', 'VOICE_READY', 'MUSIC_READY',
        'RENDERING', 'QUALITY_CHECK', 'COMPLETED', 'PUBLISHED', 'FAILED', 'ARCHIVED'
    )),
    thumbnail_url TEXT,
    final_video_url TEXT,
    tags TEXT[] DEFAULT '{}',
    favorite BOOLEAN DEFAULT FALSE,
    archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()) NOT NULL,
    last_opened_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_projects_owner_id ON projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at);

-- Trigger to automatically update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc', now());
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE projects IS 'Table storing video project information';
COMMENT ON COLUMN projects.id IS 'Unique identifier for the project';
COMMENT ON COLUMN projects.owner_id IS 'Reference to the user who owns this project';
COMMENT ON COLUMN projects.title IS 'Project title';
COMMENT ON COLUMN projects.description IS 'Project description';
COMMENT ON COLUMN projects.prompt IS 'Original video prompt';
COMMENT ON COLUMN projects.target_age_group IS 'Target age group for the video';
COMMENT ON COLUMN projects.language IS 'Language of the video';
COMMENT ON COLUMN projects.video_length IS 'Duration of the video';
COMMENT ON COLUMN projects.aspect_ratio IS 'Aspect ratio of the video';
COMMENT ON COLUMN projects.video_style IS 'Visual style of the video';
COMMENT ON COLUMN projects.voice IS 'Voice narrator for the video';
COMMENT ON COLUMN projects.status IS 'Current status in the production pipeline';
COMMENT ON COLUMN projects.thumbnail_url IS 'URL to project thumbnail';
COMMENT ON COLUMN projects.final_video_url IS 'URL to final rendered video';
COMMENT ON COLUMN projects.tags IS 'Array of tags for categorization';
COMMENT ON COLUMN projects.favorite IS 'Whether user marked project as favorite';
COMMENT ON COLUMN projects.archived IS 'Whether project is archived';
COMMENT ON COLUMN projects.created_at IS 'Timestamp when project was created';
COMMENT ON COLUMN projects.updated_at IS 'Timestamp when project was last updated';
COMMENT ON COLUMN projects.last_opened_at IS 'Timestamp when project was last opened';
