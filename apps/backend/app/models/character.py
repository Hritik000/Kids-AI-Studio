from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class CharacterProfile(BaseModel):
    character_id: str
    project_id: str
    name: str
    species: str = "Dinosaur"
    age_group: str = "Child / Young"
    gender: str = "Neutral"
    personality: str = "Playful, curious, cheerful"
    role: str = "Protagonist"
    backstory: Optional[str] = "Enthusiastic explorer in the dinosaur valley"
    height: str = "Medium"
    body_shape: str = "Rounded, soft-featured baby dinosaur"
    eye_shape: str = "Large, expressive round eyes"
    eye_color: str = "Sparkling Dark Brown"
    hair_style: str = "N/A"
    hair_color: str = "N/A"
    skin_color: str = "Lime Green with orange polka dots"
    clothing: str = "Bright blue explorer cap"
    shoes: str = "N/A"
    accessories: List[str] = ["Tiny Explorer Backpack"]
    primary_colors: List[str] = ["Lime Green", "Orange", "Bright Blue"]
    expressions: List[str] = ["Joyful", "Curious", "Surprised", "Triumphant"]
    signature_pose: str = "Jumping with arms open and big smile"
    reference_prompt: str
    negative_prompt: str = "dark, scary, realistic human, blurry, distorted"
    reference_image_url: Optional[str] = None
    visual_style: str = "3D Pixar Render"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class GeneratedImage(BaseModel):
    image_id: str
    project_id: str
    scene_number: int
    prompt_version: str = "v1.0"
    composed_prompt: str
    negative_prompt: str
    provider: str = "FLUX-v1"
    seed: int = 42
    width: int = 1280
    height: int = 720
    aspect_ratio: str = "16:9"
    generation_time_seconds: float = 2.5
    status: str = "GENERATED"  # GENERATED | APPROVED | REJECTED | FAILED
    storage_url: str
    thumbnail_url: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
