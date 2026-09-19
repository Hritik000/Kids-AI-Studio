-- Storyboards table schema
-- Based on app/models/storyboard.py Storyboard model

-- Storyboards table
CREATE TABLE IF NOT EXISTS storyboards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    story_title VARCHAR(255) NOT NULL,
    total_scenes INTEGER NOT NULL,
    total_duration_seconds FLOAT NOT NULL,
    visual_style VARCHAR(100) DEFAULT '3D Pixar Render',
    global_color_palette TEXT[] DEFAULT '{}',
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()) NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_storyboards_project_id ON storyboards(project_id);
CREATE INDEX IF NOT EXISTS idx_storyboards_updated_at ON storyboards(updated_at);

-- Trigger to automatically update updated_at column
DROP TRIGGER IF EXISTS update_storyboards_updated_at ON storyboards;
CREATE TRIGGER update_storyboards_updated_at
    BEFORE UPDATE ON storyboards
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE storyboards IS 'Table storing storyboard information for projects';
COMMENT ON COLUMN storyboards.id IS 'Unique identifier for the storyboard';
COMMENT ON COLUMN storyboards.project_id IS 'Reference to the project this storyboard belongs to';
COMMENT ON COLUMN storyboards.story_title IS 'Title of the story';
COMMENT ON COLUMN storyboards.total_scenes IS 'Total number of scenes in the storyboard';
COMMENT ON COLUMN storyboards.total_duration_seconds IS 'Total duration of the storyboard in seconds';
COMMENT ON COLUMN storyboards.visual_style IS 'Visual style of the storyboard';
COMMENT ON COLUMN storyboards.global_color_palette IS 'Array of colors used in the storyboard';
COMMENT ON COLUMN storyboards.approved IS 'Whether the storyboard has been approved';
COMMENT ON COLUMN storyboards.created_at IS 'Timestamp when storyboard was created';
COMMENT ON COLUMN storyboards.updated_at IS 'Timestamp when storyboard was last updated';
