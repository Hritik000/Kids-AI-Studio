import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.thumbnail_planner import ThumbnailPlannerService
from app.services.seo_agent import SEOAgentService
from app.services.publishing_validator import PublishingValidatorService, PublishingValidationError

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}

def test_thumbnail_planner_service():
    storyboard = {"visual_style": "3D Pixar Render", "scenes": [{"narration_text": "Rexy loves learning"}]}
    thumbs = ThumbnailPlannerService.plan_thumbnail_variants(storyboard, "Rexy's Adventure")
    assert len(thumbs) == 4
    assert thumbs[0].version_name == "Version A"
    assert thumbs[0].selected is True
    assert thumbs[1].version_name == "Version B"

def test_seo_agent_service():
    seo = SEOAgentService.generate_seo_package("proj_123", "Rexy Dino Learning", "Baby dinosaur learns ABCs")
    assert len(seo.title_options) == 3
    assert seo.coppa_compliant is True
    assert len(seo.hashtags) >= 4
    assert len(seo.chapters) >= 2

def test_publishing_validator_service():
    invalid_bundle = {
        "bundle_id": "pub_123",
        "project_id": "proj_123",
        "thumbnails": [],
        "seo": {"selected_title": "Short title"}
    }
    with pytest.raises(PublishingValidationError) as exc:
        PublishingValidatorService.validate_publishing_bundle(invalid_bundle)
    assert "At least 1 thumbnail variant is required" in str(exc.value)

def test_publishing_api_lifecycle():
    # 1. Create Project
    create_res = client.post("/api/v1/projects", json={
        "title": "Publishing Dinosaur Test",
        "prompt": "Baby dinosaur learns numbers",
        "target_age_group": "3-5"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_id = create_res.json()["data"]["id"]

    # 2. Complete previous steps: Story -> Storyboard
    client.post(f"/api/v1/projects/{proj_id}/generate-story", headers=AUTH_HEADERS)
    client.post(f"/api/v1/projects/{proj_id}/generate-storyboard", headers=AUTH_HEADERS)

    # 3. Generate Publishing Assets API
    gen_res = client.post(f"/api/v1/projects/{proj_id}/publishing/generate", headers=AUTH_HEADERS)
    assert gen_res.status_code == 200
    assert gen_res.json()["success"] is True
    bundle = gen_res.json()["data"]
    assert len(bundle["thumbnails"]) == 4
    assert len(bundle["seo"]["title_options"]) == 3

    # 4. Fetch Publishing Assets API
    get_res = client.get(f"/api/v1/projects/{proj_id}/publishing", headers=AUTH_HEADERS)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["bundle_id"] == bundle["bundle_id"]

    # 5. Select Thumbnail Variant API
    second_thumb_id = bundle["thumbnails"][1]["variant_id"]
    sel_res = client.post(f"/api/v1/projects/{proj_id}/publishing/select-thumbnail/{second_thumb_id}", headers=AUTH_HEADERS)
    assert sel_res.status_code == 200
    assert sel_res.json()["data"]["selected"] is True

    # 6. Approve Publishing Assets API
    app_res = client.post(f"/api/v1/projects/{proj_id}/publishing/approve", headers=AUTH_HEADERS)
    assert app_res.status_code == 200
    assert app_res.json()["data"]["status"] == "APPROVED"

    # 7. Get Publishing Status API
    status_res = client.get(f"/api/v1/projects/{proj_id}/publishing/status", headers=AUTH_HEADERS)
    assert status_res.status_code == 200
    assert status_res.json()["data"]["has_publishing_assets"] is True
    assert status_res.json()["data"]["thumbnail_variants_count"] == 4
