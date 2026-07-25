from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class SubscriptionPlan(BaseModel):
    plan_id: str
    name: str  # Free | Starter | Creator | Pro | Enterprise
    monthly_price_usd: float
    credits_per_month: int
    max_team_members: int
    storage_limit_gb: float
    features: List[str]

class UserSubscription(BaseModel):
    subscription_id: str
    user_id: str
    plan_id: str
    status: str = "ACTIVE"  # ACTIVE | CANCELED | PAST_DUE
    credits_remaining: int
    current_period_end: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Workspace(BaseModel):
    workspace_id: str
    name: str
    owner_id: str
    type: str = "PERSONAL"  # PERSONAL | TEAM | ORGANIZATION
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class WorkspaceMember(BaseModel):
    member_id: str
    workspace_id: str
    user_id: str
    role: str = "EDITOR"  # OWNER | ADMIN | EDITOR | VIEWER
    joined_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class APIKeyItem(BaseModel):
    key_id: str
    user_id: str
    name: str
    secret_key: str
    scopes: List[str] = ["read", "write"]
    last_used_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class NotificationItem(BaseModel):
    notification_id: str
    user_id: str
    title: str
    message: str
    type: str = "INFO"  # INFO | SUCCESS | WARNING | ERROR
    read: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AnalyticsSummary(BaseModel):
    total_projects: int
    total_stories_generated: int
    total_images_generated: int
    total_video_clips_generated: int
    total_audio_tracks_generated: int
    total_render_minutes: float
    render_success_rate: float
    ai_provider_health: str
    credits_remaining: int
    active_subscription: str
