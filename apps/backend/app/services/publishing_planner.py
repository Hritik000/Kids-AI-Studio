import uuid
from typing import Dict, Any, List, Optional
from app.models.distribution import PlatformPublishPlan

class PublishingPlannerService:
    @staticmethod
    def create_plan(
        project_id: str,
        platform: str,
        title: str,
        description: str,
        tags: List[str],
        publish_mode: str = "IMMEDIATE",
        scheduled_time: Optional[str] = None
    ) -> PlatformPublishPlan:
        adapted_title = title[:100]
        adapted_desc = description

        if platform.upper() == "TIKTOK":
            adapted_desc = f"{description[:150]}\n" + " ".join([f"#{t}" for t in tags[:5]])

        return PlatformPublishPlan(
            plan_id=f"pln_{project_id}_{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            platform=platform,
            scheduled_time=scheduled_time,
            publish_mode=publish_mode,
            custom_title=adapted_title,
            custom_description=adapted_desc,
            custom_tags=tags,
            visibility="PUBLIC"
        )
