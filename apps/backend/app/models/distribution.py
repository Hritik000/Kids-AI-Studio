from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class ConnectedAccount(BaseModel):
    account_id: str
    platform: str  # YouTube | YouTube Shorts | TikTok | Instagram | Facebook | LinkedIn | X
    display_name: str
    channel_name: str
    avatar_url: str
    connection_status: str = "CONNECTED"  # CONNECTED | EXPIRED | DISCONNECTED
    permissions: List[str] = ["upload_video", "manage_metadata"]
    last_synced_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PlatformPublishPlan(BaseModel):
    plan_id: str
    project_id: str
    platform: str
    scheduled_time: Optional[str] = None
    publish_mode: str = "IMMEDIATE"  # IMMEDIATE | SCHEDULED
    custom_title: str
    custom_description: str
    custom_tags: List[str]
    visibility: str = "PUBLIC"  # PUBLIC | UNLISTED | PRIVATE

class PublishingQueueItem(BaseModel):
    queue_id: str
    project_id: str
    account_id: str
    platform: str
    plan: PlatformPublishPlan
    status: str = "QUEUED"  # QUEUED | PREPARING | UPLOADING | PUBLISHED | FAILED | CANCELLED | RETRYING
    progress_percentage: float = 0.0
    platform_post_id: Optional[str] = None
    post_url: Optional[str] = None
    error_message: Optional[str] = None
    attempt_count: int = 1
    published_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
