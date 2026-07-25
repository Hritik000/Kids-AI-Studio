from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class MusicPlan(BaseModel):
    track_id: str
    genre: str = "Acoustic Storybook"
    mood: str = "Cheerful & Playful"
    bpm: int = 110
    key: str = "C Major"
    instruments: List[str] = ["Marimba", "Acoustic Guitar", "Woodwinds"]
    duration_seconds: float = 60.0
    loop_enabled: bool = True

class SoundEffectItem(BaseModel):
    sfx_id: str
    name: str
    category: str = "Footsteps"
    timestamp_seconds: float = 1.0
    volume_level: float = 0.5

class AmbientAudioPlan(BaseModel):
    ambient_id: str
    environment_type: str = "Sunny Meadow"
    volume_level: float = 0.15

class MixedAudioTrack(BaseModel):
    mix_id: str
    project_id: str
    scene_number: int
    music_plan: MusicPlan
    sound_effects: List[SoundEffectItem]
    ambient_plan: AmbientAudioPlan
    narration_volume: float = 1.0
    music_ducked_volume: float = 0.25
    ambient_volume: float = 0.15
    sfx_volume: float = 0.5
    master_loudness_lufs: float = -14.0
    duration_seconds: float = 5.0
    sample_rate: int = 44100
    audio_format: str = "MP3"
    provider: str = "StableAudio-Open-v1"
    status: str = "GENERATED"  # GENERATED | APPROVED | REJECTED
    storage_url: str
    generation_time_seconds: float = 1.2
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
