from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class OptimizationSuggestion(BaseModel):
    category: str  # TITLE | THUMBNAIL | STORY | PACING | EDUCATIONAL
    severity: str  # HIGH | MEDIUM | LOW
    current_value: str
    suggested_value: str
    explanation: str

class OptimizationReport(BaseModel):
    project_id: str
    overall_score: float  # 0.0 - 100.0
    pacing_score: float
    educational_score: float
    visual_score: float
    audio_score: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[OptimizationSuggestion]
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PerformancePrediction(BaseModel):
    project_id: str
    predicted_ctr: float  # e.g., 12.4%
    predicted_retention_pct: float  # e.g., 78.5%
    expected_watch_time_sec: float
    publishing_risk: str  # LOW | MEDIUM | HIGH
    confidence_score: float  # 0.0 - 1.0
    explanations: List[str]
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class TrendReport(BaseModel):
    trend_id: str
    topic: str
    category: str  # SCIENCE | ANIMALS | MATH | MORAL | ALPHABET
    search_volume_score: float
    competition_level: str  # LOW | MEDIUM | HIGH
    opportunity_score: float
    target_age_group: str
    seasonal_keywords: List[str]

class WorkflowAutomationItem(BaseModel):
    workflow_id: str
    name: str
    trigger_event: str  # RENDER_COMPLETED | SEO_APPROVED | THUMBNAIL_REJECTED
    actions: List[str]
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ContentTemplateItem(BaseModel):
    template_id: str
    name: str
    category: str  # STORY | CHARACTER | THUMBNAIL | ANIMATION | WORKFLOW
    description: str
    tags: List[str]
    payload: Dict[str, Any]
    downloads_count: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AIModelConfigItem(BaseModel):
    model_id: str
    provider: str  # OpenAI | Anthropic | FLUX | Wan 2.2 | Kokoro | Stable Audio
    model_type: str  # LLM | IMAGE | ANIMATION | VOICE | MUSIC
    display_name: str
    latency_ms: float
    cost_per_unit: float
    status: str = "OPERATIONAL"  # OPERATIONAL | DEGRADED | MAINTENANCE
    is_default: bool = False
