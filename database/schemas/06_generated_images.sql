-- Generated images table schema
-- Based on app/models/character.py GeneratedImage model

-- Generated images table
CREATE TABLE IF NOT EXISTS generated_images (
    image_id VARCHAR PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    scene_number INT NOT NULL,
    composed_prompt TEXT NOT NULL,
    negative_prompt TEXT NOT NULL,
    provider VARCHAR NOT NULL,
    seed INT NOT NULL,
    width INT DEFAULT 1280,
    height INT DEFAULT 720,
    aspect_ratio VARCHAR DEFAULT '16:9',
    generation_time_seconds FLOAT,
    status VARCHAR DEFAULT 'GENERATED' CHECK (status IN ('GENERATED', 'APPROVED', 'REJECTED', 'FAILED')),
    storage_url TEXT NOT NULL,
    thumbnail_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()) NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_generated_images_project_id ON generated_images(project_id);
CREATE INDEX IF NOT EXISTS idx_generated_images_scene_number ON generated_images(scene_number);
CREATE INDEX IF NOT EXISTS idx_generated_images_status ON generated_images(status);
CREATE INDEX IF NOT EXISTS idx_generated_images_created_at ON generated_images(created_at);

-- Comments
COMMENT ON TABLE generated_images IS 'Table storing generated images for project scenes';
COMMENT ON COLUMN generated_images.image_id IS 'Unique identifier for the generated image';
COMMENT ON COLUMN generated_images.project_id IS 'Reference to the project this image belongs to';
COMMENT ON COLUMN generated_images.scene_number IS 'Scene number this image corresponds to';
COMMENT ON COLUMN generated_images.composed_prompt IS 'The final prompt used for image generation';
COMMENT ON COLUMN generated_images.negative_prompt IS 'Negative prompt used for image generation';
COMMENT ON COLUMN generated_images.provider IS 'AI provider used for generation (e.g., FLUX, DALL-E, Stable Diffusion)';
COMMENT ON COLUMN generated_images.seed IS 'Random seed used for generation';
COMMENT ON COLUMN generated_images.width IS 'Width of the generated image in pixels';
COMMENT ON COLUMN generated_images.height IS 'Height of the generated image in pixels';
COMMENT ON COLUMN generated_images.aspect_ratio IS 'Aspect ratio of the generated image';
COMMENT ON COLUMN generated_images.generation_time_seconds IS 'Time taken to generate the image in seconds';
COMMENT ON COLUMN generated_images.status IS 'Status of the image generation process';
COMMENT ON COLUMN generated_images.storage_url IS 'URL where the full image is stored';
COMMENT ON COLUMN generated_images.thumbnail_url IS 'URL where the thumbnail is stored';
COMMENT ON COLUMN generated_images.created_at IS 'Timestamp when image was generated';