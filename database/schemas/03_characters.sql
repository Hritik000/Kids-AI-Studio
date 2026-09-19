-- Characters table schema
-- Based on app/models/character.py CharacterProfile model

-- Characters table
CREATE TABLE IF NOT EXISTS characters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    character_id VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    species VARCHAR(100) DEFAULT 'Dinosaur',
    age_group VARCHAR(50) DEFAULT 'Child / Young',
    gender VARCHAR(20) DEFAULT 'Neutral',
    personality TEXT DEFAULT 'Playful, curious, cheerful',
    role VARCHAR(100) DEFAULT 'Protagonist',
    backstory TEXT,
    height VARCHAR(50) DEFAULT 'Medium',
    body_shape TEXT DEFAULT 'Rounded, soft-featured baby dinosaur',
    eye_shape TEXT DEFAULT 'Large, expressive round eyes',
    eye_color VARCHAR(50) DEFAULT 'Sparkling Dark Brown',
    hair_style VARCHAR(100) DEFAULT 'N/A',
    hair_color VARCHAR(100) DEFAULT 'N/A',
    skin_color VARCHAR(100) DEFAULT 'Lime Green with orange polka dots',
    clothing VARCHAR(200) DEFAULT 'Bright blue explorer cap',
    shoes VARCHAR(100) DEFAULT 'N/A',
    accessories TEXT[] DEFAULT '{"Tiny Explorer Backpack"}',
    primary_colors TEXT[] DEFAULT '{"Lime Green", "Orange", "Bright Blue"}',
    expressions TEXT[] DEFAULT '{"Joyful", "Curious", "Surprised", "Triumphant"}',
    signature_pose VARCHAR(200) DEFAULT 'Jumping with arms open and big smile',
    reference_prompt TEXT NOT NULL,
    negative_prompt TEXT DEFAULT 'dark, scary, realistic human, blurry, distorted',
    reference_image_url TEXT,
    visual_style VARCHAR(100) DEFAULT '3D Pixar Render',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()) NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_characters_project_id ON characters(project_id);
CREATE INDEX IF NOT EXISTS idx_characters_character_id ON characters(character_id);
CREATE INDEX IF NOT EXISTS idx_characters_updated_at ON characters(updated_at);

-- Trigger to automatically update updated_at column
DROP TRIGGER IF EXISTS update_characters_updated_at ON characters;
CREATE TRIGGER update_characters_updated_at
    BEFORE UPDATE ON characters
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE characters IS 'Table storing character profiles for projects';
COMMENT ON COLUMN characters.id IS 'Unique identifier for the character';
COMMENT ON COLUMN characters.project_id IS 'Reference to the project this character belongs to';
COMMENT ON COLUMN characters.character_id IS 'Unique character identifier within the project';
COMMENT ON COLUMN characters.name IS 'Character name';
COMMENT ON COLUMN characters.species IS 'Species of the character';
COMMENT ON COLUMN characters.age_group IS 'Age group of the character';
COMMENT ON COLUMN characters.gender IS 'Gender of the character';
COMMENT ON COLUMN characters.personality IS 'Personality traits of the character';
COMMENT ON COLUMN characters.role IS 'Role of the character in the story';
COMMENT ON COLUMN characters.backstory IS 'Backstory of the character';
COMMENT ON COLUMN characters.height IS 'Height of the character';
COMMENT ON COLUMN characters.body_shape IS 'Body shape description';
COMMENT ON COLUMN characters.eye_shape IS 'Eye shape description';
COMMENT ON COLUMN characters.eye_color IS 'Eye color';
COMMENT ON COLUMN characters.hair_style IS 'Hair style';
COMMENT ON COLUMN characters.hair_color IS 'Hair color';
COMMENT ON COLUMN characters.skin_color IS 'Skin color';
COMMENT ON COLUMN characters.clothing IS 'Clothing description';
COMMENT ON COLUMN characters.shoes IS 'Shoes description';
COMMENT ON COLUMN characters.accessories IS 'Array of accessories';
COMMENT ON COLUMN characters.primary_colors IS 'Array of primary colors';
COMMENT ON COLUMN characters.expressions IS 'Array of possible expressions';
COMMENT ON COLUMN characters.signature_pose IS 'Signature pose of the character';
COMMENT ON COLUMN characters.reference_prompt IS 'Prompt used to generate the character';
COMMENT ON COLUMN characters.negative_prompt IS 'Negative prompt for generation';
COMMENT ON COLUMN characters.reference_image_url IS 'URL to reference image';
COMMENT ON COLUMN characters.visual_style IS 'Visual style of the character';
COMMENT ON COLUMN characters.created_at IS 'Timestamp when character was created';
COMMENT ON COLUMN characters.updated_at IS 'Timestamp when character was last updated';
