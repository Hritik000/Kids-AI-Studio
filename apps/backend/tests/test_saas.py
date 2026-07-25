import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.billing_service import BillingService
from app.services.workspace_service import WorkspaceService
from app.services.api_key_service import APIKeyService

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}

def test_billing_service():
    sub = BillingService.get_user_subscription("user_demo_123")
    assert sub.credits_remaining == 3500

    deducted = BillingService.deduct_credits("user_demo_123", 100)
    assert deducted is True
    assert BillingService.get_user_subscription("user_demo_123").credits_remaining == 3400

def test_workspace_service():
    ws = WorkspaceService.initialize_user_workspace("user_demo_123")
    assert ws.name == "Personal Workspace"
    assert ws.type == "PERSONAL"

def test_api_key_service():
    key = APIKeyService.create_api_key("user_demo_123", "Production Key")
    assert key.name == "Production Key"
    assert key.secret_key.startswith("kAI_live_")

    revoked = APIKeyService.revoke_api_key("user_demo_123", key.key_id)
    assert revoked is True

def test_saas_api_lifecycle():
    # 1. Billing Plans API
    plans_res = client.get("/api/v1/saas/billing/plans", headers=AUTH_HEADERS)
    assert plans_res.status_code == 200
    assert len(plans_res.json()["data"]) >= 4

    # 2. Get User Subscription API
    sub_res = client.get("/api/v1/saas/billing/subscription", headers=AUTH_HEADERS)
    assert sub_res.status_code == 200
    assert sub_res.json()["data"]["user_id"] in ["demo-user-id", "user_demo_123"]

    # 3. Workspaces API
    ws_res = client.get("/api/v1/saas/workspaces", headers=AUTH_HEADERS)
    assert ws_res.status_code == 200
    assert len(ws_res.json()["data"]) >= 1

    # 4. Create API Key API
    key_res = client.post("/api/v1/saas/api-keys", json={"name": "Test Key"}, headers=AUTH_HEADERS)
    assert key_res.status_code == 200
    assert key_res.json()["data"]["name"] == "Test Key"

    # 5. Analytics Summary API
    analytics_res = client.get("/api/v1/saas/analytics/summary", headers=AUTH_HEADERS)
    assert analytics_res.status_code == 200
    assert analytics_res.json()["data"]["render_success_rate"] == 99.4
