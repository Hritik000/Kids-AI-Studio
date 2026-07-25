from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class NarrativeArc(BaseModel):
    beginning: str
    middle: str
    ending: str

class VisualPlan(BaseModel):
    environment: str
    time_of_day: str = "Daylight"
    weather: str = "Clear & Sunny"
    background: str
    foreground: str
    key_objects: List[str] = []
    color_palette: List[str] = []
    lighting_style: str = "Soft Warm Sunlight"
    mood: str = "Cheerful"
    atmosphere: str = "Magical"
    composition: str = "Rule of Thirds"

class CameraPlan(BaseModel):
    shot_type: str = "Medium Shot"  # Wide Shot, Medium Shot, Close Up, Extreme Close Up
    angle: str = "Eye Level"        # Low Angle, Eye Level, High Angle, Overhead
    movement: str = "Pan"          # Pan, Zoom, Tracking, Static
    camera_direction: str = "Left to Right"
    camera_speed: str = "Gentle"
    focal_point: str

class TransitionPlan(BaseModel):
    type: str = "Cross Fade"  # Cut, Fade, Cross Fade, Slide, Zoom, Match Cut
    duration_seconds: float = 1.0

class CharacterReference(BaseModel):
    character_name: str
    expression: str = "Happy & Curious"
    pose: str = "Standing comfortably"
    eye_direction: str = "Towards camera"
    interaction: str = "Exploring environment"
    visibility: str = "Full Body"
    importance: str = "Primary Hero"

class StoryboardScene(BaseModel):
    scene_number: int
    scene_title: str
    purpose: str
    learning_goal: str
    estimated_duration: float = 15.0
    energy_level: str = "Medium"  # Low, Medium, High
    scene_importance: str = "High"
    narrative_arc: NarrativeArc
    narration_text: str
    visual_plan: VisualPlan
    camera_plan: CameraPlan
    transition: TransitionPlan
    character_references: List[CharacterReference] = []

class Storyboard(BaseModel):
    project_id: str
    story_title: str
    total_scenes: int
    total_duration_seconds: float
    visual_style: str = "3D Pixar Render"
    global_color_palette: List[str] = []
    scenes: List[StoryboardScene]
    approved: bool = False
