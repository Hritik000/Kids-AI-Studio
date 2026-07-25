from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class ThumbnailVariant(BaseModel):
    variant_id: str
    version_name: str  # Version A | Version B | Version C | Version D
    style_type: str  # Character Focus | Action Scene | Bright Cartoon | Educational
    prompt: str
    storage_url: str
    ctr_score: float = 92.5
    selected: bool = False

class TitleOption(BaseModel):
    title_id: str
    title_text: str
    category: str  # SEO Optimized | Curiosity Driven | Educational
    ctr_score: float = 94.0
    character_count: int

class ChapterItem(BaseModel):
    timestamp: str = "00:00"
    title: str
    summary: str

class SEOPackage(BaseModel):
    seo_id: str
    project_id: str
    selected_title: str
    title_options: List[TitleOption]
    short_description: str
    long_description: str
    chapters: List[ChapterItem]
    primary_keywords: List[str]
    secondary_keywords: List[str]
    hashtags: List[str]
    category: str = "Education"
    coppa_compliant: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PublishingAssetBundle(BaseModel):
    bundle_id: str
    project_id: str
    thumbnails: List[ThumbnailVariant]
    seo: SEOPackage
    status: str = "GENERATED"  # GENERATED | APPROVED | REJECTED
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
