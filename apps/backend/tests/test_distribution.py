import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.account_manager import AccountManagerService
from app.services.distribution_validator import DistributionValidatorService, DistributionValidationError

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}

def test_account_manager_service():
    accounts = AccountManagerService.list_accounts()
    assert len(accounts) >= 2
    assert accounts[0].platform in ["YouTube", "TikTok"]

    new_acc = AccountManagerService.connect_account("Instagram", "kidsai_reels")
    assert new_acc.platform == "Instagram"
    assert new_acc.channel_name == "kidsai_reels"

def test_distribution_validator():
    invalid_url = ""
    with pytest.raises(DistributionValidationError) as exc:
        DistributionValidatorService.validate_publish_request(invalid_url, "Title", "YouTube")
    assert "Valid video URL is required" in str(exc.value)

def test_distribution_api_lifecycle():
    # 1. Create Project
    create_res = client.post("/api/v1/projects", json={
        "title": "Distribution Dino Test",
        "prompt": "Baby dinosaur publishes video to YouTube",
        "target_age_group": "3-5"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_id = create_res.json()["data"]["id"]

    # 2. List Connected Accounts API
    acc_res = client.get("/api/v1/distribution/accounts", headers=AUTH_HEADERS)
    assert acc_res.status_code == 200
    acc_list = acc_res.json()["data"]
    assert len(acc_list) >= 1
    acc_id = acc_list[0]["account_id"]
    platform = acc_list[0]["platform"]

    # 3. Publish Now API
    pub_res = client.post(f"/api/v1/projects/{proj_id}/distribution/publish-now", json={
        "account_id": acc_id,
        "platform": platform,
        "video_url": "http://example.com/dino_video.mp4",
        "title": "Dino Video Test",
        "description": "Fun dino story",
        "tags": ["dino", "kids"]
    }, headers=AUTH_HEADERS)
    assert pub_res.status_code == 200
    assert pub_res.json()["success"] is True
    queue_item = pub_res.json()["data"]
    assert queue_item["status"] == "PUBLISHED"
    assert queue_item["post_url"] is not None

    # 4. List Publishing Queue API
    queue_res = client.get(f"/api/v1/projects/{proj_id}/distribution/queue", headers=AUTH_HEADERS)
    assert queue_res.status_code == 200
    assert len(queue_res.json()["data"]) >= 1

    # 5. Get Distribution Status API
    status_res = client.get(f"/api/v1/projects/{proj_id}/distribution/status", headers=AUTH_HEADERS)
    assert status_res.status_code == 200
    assert status_res.json()["data"]["has_distributions"] is True
    assert status_res.json()["data"]["published_count"] == 1
