from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from app.models.project import APIResponse, APIError
from app.models.distribution import ConnectedAccount, PublishingQueueItem
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.api.v1.projects import projects_db
from app.api.v1.publishing import publishing_bundles_db
from app.api.v1.rendering import renders_db
from app.services.account_manager import AccountManagerService
from app.services.publishing_queue import PublishingQueueService, publishing_queue_db

router = APIRouter()

class ConnectAccountPayload(BaseModel):
    platform: str
    channel_name: str

class PublishNowPayload(BaseModel):
    account_id: str
    platform: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class SchedulePublishPayload(PublishNowPayload):
    scheduled_time: str

@router.get("/distribution/accounts", response_model=APIResponse[List[ConnectedAccount]])
async def list_connected_accounts(
    current_user: UserProfile = Depends(get_current_user)
):
    accounts = AccountManagerService.list_accounts()
    return APIResponse(success=True, data=accounts)

@router.post("/distribution/accounts/connect", response_model=APIResponse[ConnectedAccount])
async def connect_account(
    payload: ConnectAccountPayload,
    current_user: UserProfile = Depends(get_current_user)
):
    acc = AccountManagerService.connect_account(payload.platform, payload.channel_name)
    return APIResponse(success=True, data=acc)

@router.delete("/distribution/accounts/{account_id}", response_model=APIResponse[Dict[str, Any]])
async def disconnect_account(
    account_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    success = AccountManagerService.disconnect_account(account_id)
    if not success:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Account not found")
        )
    return APIResponse(success=True, data={"message": f"Account {account_id} disconnected"})

@router.post("/projects/{project_id}/distribution/publish-now", response_model=APIResponse[PublishingQueueItem])
async def publish_now(
    project_id: str,
    payload: PublishNowPayload,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    pub_bundle = publishing_bundles_db.get(project_id)
    renders = renders_db.get(project_id, [])
    latest_render = renders[-1] if renders else None

    vid_url = payload.video_url or (latest_render.final_video_url if latest_render else "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4")
    thumb_url = payload.thumbnail_url or (project.thumbnail_url or "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800&auto=format&fit=crop&q=80")
    title_text = payload.title or (pub_bundle.seo.selected_title if pub_bundle else project.title)
    desc_text = payload.description or (pub_bundle.seo.long_description if pub_bundle else project.prompt)
    tags_list = payload.tags or (pub_bundle.seo.primary_keywords if pub_bundle else ["kids", "learning"])

    try:
        queue_item = await PublishingQueueService.publish_now(
            project_id=project_id,
            account_id=payload.account_id,
            platform=payload.platform,
            video_url=vid_url,
            thumbnail_url=thumb_url,
            title=title_text,
            description=desc_text,
            tags=tags_list
        )
        return APIResponse(success=True, data=queue_item)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="PUBLISH_FAILED", message=str(e))
        )

@router.post("/projects/{project_id}/distribution/schedule", response_model=APIResponse[PublishingQueueItem])
async def schedule_publish(
    project_id: str,
    payload: SchedulePublishPayload,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    pub_bundle = publishing_bundles_db.get(project_id)
    renders = renders_db.get(project_id, [])
    latest_render = renders[-1] if renders else None

    vid_url = payload.video_url or (latest_render.final_video_url if latest_render else "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4")
    thumb_url = payload.thumbnail_url or (project.thumbnail_url or "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800&auto=format&fit=crop&q=80")
    title_text = payload.title or (pub_bundle.seo.selected_title if pub_bundle else project.title)
    desc_text = payload.description or (pub_bundle.seo.long_description if pub_bundle else project.prompt)
    tags_list = payload.tags or (pub_bundle.seo.primary_keywords if pub_bundle else ["kids", "learning"])

    try:
        queue_item = await PublishingQueueService.schedule_publish(
            project_id=project_id,
            account_id=payload.account_id,
            platform=payload.platform,
            video_url=vid_url,
            thumbnail_url=thumb_url,
            title=title_text,
            description=desc_text,
            tags=tags_list,
            scheduled_time=payload.scheduled_time
        )
        return APIResponse(success=True, data=queue_item)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="SCHEDULE_FAILED", message=str(e))
        )

@router.get("/projects/{project_id}/distribution/queue", response_model=APIResponse[List[PublishingQueueItem]])
async def list_publishing_queue(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    queue = publishing_queue_db.get(project_id, [])
    return APIResponse(success=True, data=queue)

@router.get("/projects/{project_id}/distribution/history", response_model=APIResponse[List[PublishingQueueItem]])
async def list_publishing_history(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    queue = publishing_queue_db.get(project_id, [])
    history = [q for q in queue if q.status in ["PUBLISHED", "FAILED", "CANCELLED"]]
    return APIResponse(success=True, data=history)

@router.post("/projects/{project_id}/distribution/cancel/{queue_id}", response_model=APIResponse[PublishingQueueItem])
async def cancel_publish_task(
    project_id: str,
    queue_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    try:
        cancelled = PublishingQueueService.cancel_publish(project_id, queue_id)
        return APIResponse(success=True, data=cancelled)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="CANCEL_FAILED", message=str(e))
        )

@router.post("/projects/{project_id}/distribution/retry/{queue_id}", response_model=APIResponse[PublishingQueueItem])
async def retry_publish_task(
    project_id: str,
    queue_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    try:
        retried = await PublishingQueueService.retry_publish(project_id, queue_id)
        return APIResponse(success=True, data=retried)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="RETRY_FAILED", message=str(e))
        )

@router.get("/projects/{project_id}/distribution/status", response_model=APIResponse[Dict[str, Any]])
async def get_distribution_status(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    queue = publishing_queue_db.get(project_id, [])
    published_count = len([q for q in queue if q.status == "PUBLISHED"])

    return APIResponse(
        success=True,
        data={
            "project_id": project_id,
            "total_distributions": len(queue),
            "published_count": published_count,
            "has_distributions": len(queue) > 0
        }
    )
