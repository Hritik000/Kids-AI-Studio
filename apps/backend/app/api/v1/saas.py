from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from app.models.project import APIResponse, APIError
from app.models.saas import SubscriptionPlan, UserSubscription, Workspace, APIKeyItem, NotificationItem, AnalyticsSummary
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.services.billing_service import BillingService, AVAILABLE_PLANS
from app.services.workspace_service import WorkspaceService
from app.services.api_key_service import APIKeyService
from app.services.notification_service import NotificationService
from app.services.analytics_service import AnalyticsService

router = APIRouter()

class SubscribePayload(BaseModel):
    plan_id: str

class CreateWorkspacePayload(BaseModel):
    name: str
    type: str = "TEAM"

class CreateAPIKeyPayload(BaseModel):
    name: str

@router.get("/saas/billing/plans", response_model=APIResponse[List[SubscriptionPlan]])
async def list_subscription_plans(
    current_user: UserProfile = Depends(get_current_user)
):
    plans = list(AVAILABLE_PLANS.values())
    return APIResponse(success=True, data=plans)

@router.get("/saas/billing/subscription", response_model=APIResponse[UserSubscription])
async def get_user_subscription(
    current_user: UserProfile = Depends(get_current_user)
):
    sub = BillingService.get_user_subscription(current_user.id)
    return APIResponse(success=True, data=sub)

@router.post("/saas/billing/subscribe", response_model=APIResponse[UserSubscription])
async def subscribe_to_plan(
    payload: SubscribePayload,
    current_user: UserProfile = Depends(get_current_user)
):
    try:
        sub = BillingService.subscribe_to_plan(current_user.id, payload.plan_id)
        return APIResponse(success=True, data=sub)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="SUBSCRIBE_FAILED", message=str(e))
        )

@router.get("/saas/workspaces", response_model=APIResponse[List[Workspace]])
async def list_workspaces(
    current_user: UserProfile = Depends(get_current_user)
):
    workspaces = WorkspaceService.list_user_workspaces(current_user.id)
    return APIResponse(success=True, data=workspaces)

@router.post("/saas/workspaces", response_model=APIResponse[Workspace])
async def create_workspace(
    payload: CreateWorkspacePayload,
    current_user: UserProfile = Depends(get_current_user)
):
    ws = WorkspaceService.create_workspace(current_user.id, payload.name, payload.type)
    return APIResponse(success=True, data=ws)

@router.get("/saas/api-keys", response_model=APIResponse[List[APIKeyItem]])
async def list_api_keys(
    current_user: UserProfile = Depends(get_current_user)
):
    keys = APIKeyService.list_api_keys(current_user.id)
    return APIResponse(success=True, data=keys)

@router.post("/saas/api-keys", response_model=APIResponse[APIKeyItem])
async def create_api_key(
    payload: CreateAPIKeyPayload,
    current_user: UserProfile = Depends(get_current_user)
):
    key = APIKeyService.create_api_key(current_user.id, payload.name)
    return APIResponse(success=True, data=key)

@router.delete("/saas/api-keys/{key_id}", response_model=APIResponse[Dict[str, Any]])
async def revoke_api_key(
    key_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    success = APIKeyService.revoke_api_key(current_user.id, key_id)
    if not success:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="API key not found")
        )
    return APIResponse(success=True, data={"message": f"API key {key_id} revoked"})

@router.get("/saas/notifications", response_model=APIResponse[List[NotificationItem]])
async def list_notifications(
    current_user: UserProfile = Depends(get_current_user)
):
    notes = NotificationService.list_notifications(current_user.id)
    return APIResponse(success=True, data=notes)

@router.post("/saas/notifications/{notification_id}/read", response_model=APIResponse[Dict[str, Any]])
async def mark_notification_read(
    notification_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    success = NotificationService.mark_as_read(current_user.id, notification_id)
    return APIResponse(success=True, data={"read": success})

@router.get("/saas/analytics/summary", response_model=APIResponse[AnalyticsSummary])
async def get_analytics_summary(
    current_user: UserProfile = Depends(get_current_user)
):
    summary = AnalyticsService.get_summary(current_user.id)
    return APIResponse(success=True, data=summary)
