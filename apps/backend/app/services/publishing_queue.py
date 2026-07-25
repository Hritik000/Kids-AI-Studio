import uuid
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.models.distribution import PublishingQueueItem, ConnectedAccount, PlatformPublishPlan
from app.core.platform_adapters import get_platform_adapter
from app.services.account_manager import connected_accounts_db, AccountManagerService
from app.services.publishing_planner import PublishingPlannerService
from app.services.distribution_validator import DistributionValidatorService

# In-memory database for publishing queue items
publishing_queue_db: Dict[str, List[PublishingQueueItem]] = {}

class PublishingQueueService:
    @staticmethod
    async def publish_now(
        project_id: str,
        account_id: str,
        platform: str,
        video_url: str,
        thumbnail_url: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> PublishingQueueItem:
        DistributionValidatorService.validate_publish_request(video_url, title, platform)
        AccountManagerService.initialize_default_accounts()

        account = connected_accounts_db.get(account_id)
        if not account:
            # Fallback to mock account
            account = ConnectedAccount(
                account_id=account_id,
                platform=platform,
                display_name=f"{platform} Account",
                channel_name=f"{platform.lower()}_channel",
                avatar_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200&auto=format&fit=crop&q=80"
            )

        plan = PublishingPlannerService.create_plan(
            project_id=project_id,
            platform=platform,
            title=title,
            description=description,
            tags=tags,
            publish_mode="IMMEDIATE"
        )

        queue_item = PublishingQueueItem(
            queue_id=f"qu_{project_id}_{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            account_id=account_id,
            platform=platform,
            plan=plan,
            status="UPLOADING",
            progress_percentage=50.0
        )

        # Execute upload adapter
        adapter = get_platform_adapter(platform)
        result = await adapter.publish_video(
            account=account,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            title=plan.custom_title,
            description=plan.custom_description,
            tags=plan.custom_tags
        )

        queue_item.status = "PUBLISHED"
        queue_item.progress_percentage = 100.0
        queue_item.platform_post_id = result.get("platform_post_id")
        queue_item.post_url = result.get("post_url")
        queue_item.published_at = datetime.now(timezone.utc).isoformat()

        queue_list = publishing_queue_db.get(project_id, [])
        queue_list.append(queue_item)
        publishing_queue_db[project_id] = queue_list

        return queue_item

    @staticmethod
    async def schedule_publish(
        project_id: str,
        account_id: str,
        platform: str,
        video_url: str,
        thumbnail_url: str,
        title: str,
        description: str,
        tags: List[str],
        scheduled_time: str
    ) -> PublishingQueueItem:
        DistributionValidatorService.validate_publish_request(video_url, title, platform)

        plan = PublishingPlannerService.create_plan(
            project_id=project_id,
            platform=platform,
            title=title,
            description=description,
            tags=tags,
            publish_mode="SCHEDULED",
            scheduled_time=scheduled_time
        )

        queue_item = PublishingQueueItem(
            queue_id=f"qu_{project_id}_{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            account_id=account_id,
            platform=platform,
            plan=plan,
            status="QUEUED",
            progress_percentage=0.0
        )

        queue_list = publishing_queue_db.get(project_id, [])
        queue_list.append(queue_item)
        publishing_queue_db[project_id] = queue_list

        return queue_item

    @staticmethod
    def cancel_publish(project_id: str, queue_id: str) -> PublishingQueueItem:
        queue_list = publishing_queue_db.get(project_id, [])
        target = next((item for item in queue_list if item.queue_id == queue_id), None)
        if not target:
            raise ValueError(f"Queue item '{queue_id}' not found.")

        target.status = "CANCELLED"
        publishing_queue_db[project_id] = queue_list
        return target

    @staticmethod
    async def retry_publish(project_id: str, queue_id: str) -> PublishingQueueItem:
        queue_list = publishing_queue_db.get(project_id, [])
        target = next((item for item in queue_list if item.queue_id == queue_id), None)
        if not target:
            raise ValueError(f"Queue item '{queue_id}' not found.")

        target.status = "PUBLISHED"
        target.progress_percentage = 100.0
        target.attempt_count += 1
        target.published_at = datetime.now(timezone.utc).isoformat()
        publishing_queue_db[project_id] = queue_list
        return target
