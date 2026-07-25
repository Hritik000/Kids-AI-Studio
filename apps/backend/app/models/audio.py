from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class DialogueSegment(BaseModel):
    segment_id: str
    scene_number: int
    speaker_name: str = "Narrator"
    speaker_role: str = "Narrator"
    text: str
    emotional_tone: str = "Cheerful"
    speech_speed: float = 1.0
    pause_duration_seconds: float = 0.3
    emphasis_words: List[str] = []

class VisemeMarker(BaseModel):
    timestamp_seconds: float
    mouth_shape: str  # A, E, I, O, U, M, Rest
    duration_seconds: float = 0.15

class LipSyncMetadata(BaseModel):
    visemes: List[VisemeMarker] = []
    blink_timestamps: List[float] = []

class VoiceNarrationAsset(BaseModel):
    audio_id: str
    project_id: str
    scene_number: int
    dialogue_segments: List[DialogueSegment]
    lip_sync: LipSyncMetadata
    voice_name: str = "Storyteller Emma"
    voice_type: str = "Child Friendly Narrator"
    emotion: str = "Cheerful & Inviting"
    language: str = "English (US)"
    duration_seconds: float = 5.0
    sample_rate: int = 24000
    audio_format: str = "MP3"
    provider: str = "KokoroTTS-v1"
    status: str = "GENERATED"  # GENERATED | APPROVED | REJECTED
    storage_url: str
    generation_time_seconds: float = 0.8
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
