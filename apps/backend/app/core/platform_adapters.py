import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.models.distribution import ConnectedAccount

class PlatformAdapter(ABC):
    @abstractmethod
    async def publish_video(
        self,
        account: ConnectedAccount,
        video_url: str,
        thumbnail_url: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> Dict[str, Any]:
        pass

class YouTubeAdapter(PlatformAdapter):
    async def publish_video(
        self,
        account: ConnectedAccount,
        video_url: str,
        thumbnail_url: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> Dict[str, Any]:
        post_id = f"yt_vid_{uuid.uuid4().hex[:8]}"
        return {
            "platform": "YouTube",
            "platform_post_id": post_id,
            "post_url": f"https://youtube.com/watch?v={post_id}",
            "status": "PUBLISHED"
        }

class TikTokAdapter(PlatformAdapter):
    async def publish_video(
        self,
        account: ConnectedAccount,
        video_url: str,
        thumbnail_url: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> Dict[str, Any]:
        post_id = f"tt_vid_{uuid.uuid4().hex[:8]}"
        return {
            "platform": "TikTok",
            "platform_post_id": post_id,
            "post_url": f"https://tiktok.com/@{account.channel_name}/video/{post_id}",
            "status": "PUBLISHED"
        }

class InstagramAdapter(PlatformAdapter):
    async def publish_video(
        self,
        account: ConnectedAccount,
        video_url: str,
        thumbnail_url: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> Dict[str, Any]:
        post_id = f"ig_reel_{uuid.uuid4().hex[:8]}"
        return {
            "platform": "Instagram",
            "platform_post_id": post_id,
            "post_url": f"https://instagram.com/reel/{post_id}",
            "status": "PUBLISHED"
        }

class FacebookAdapter(PlatformAdapter):
    async def publish_video(
        self,
        account: ConnectedAccount,
        video_url: str,
        thumbnail_url: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> Dict[str, Any]:
        post_id = f"fb_reel_{uuid.uuid4().hex[:8]}"
        return {
            "platform": "Facebook",
            "platform_post_id": post_id,
            "post_url": f"https://facebook.com/watch/?v={post_id}",
            "status": "PUBLISHED"
        }

class LinkedInAdapter(PlatformAdapter):
    async def publish_video(
        self,
        account: ConnectedAccount,
        video_url: str,
        thumbnail_url: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> Dict[str, Any]:
        post_id = f"li_vid_{uuid.uuid4().hex[:8]}"
        return {
            "platform": "LinkedIn",
            "platform_post_id": post_id,
            "post_url": f"https://linkedin.com/feed/update/{post_id}",
            "status": "PUBLISHED"
        }

class MockPlatformAdapter(PlatformAdapter):
    async def publish_video(
        self,
        account: ConnectedAccount,
        video_url: str,
        thumbnail_url: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> Dict[str, Any]:
        post_id = f"mock_{account.platform.lower()}_{uuid.uuid4().hex[:8]}"
        return {
            "platform": account.platform,
            "platform_post_id": post_id,
            "post_url": f"https://{account.platform.lower()}.com/post/{post_id}",
            "status": "PUBLISHED"
        }

def get_platform_adapter(platform: str) -> PlatformAdapter:
    platform_upper = platform.upper()
    if "YOUTUBE" in platform_upper:
        return YouTubeAdapter()
    elif "TIKTOK" in platform_upper:
        return TikTokAdapter()
    elif "INSTAGRAM" in platform_upper:
        return InstagramAdapter()
    elif "FACEBOOK" in platform_upper:
        return FacebookAdapter()
    elif "LINKEDIN" in platform_upper:
        return LinkedInAdapter()
    else:
        return MockPlatformAdapter()
