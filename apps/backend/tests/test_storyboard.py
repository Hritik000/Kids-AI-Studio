import asyncio
import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.storyboard import StoryboardAgentService
from app.services.storyboard_validator import StoryboardValidationService, StoryboardValidationError

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}

def test_storyboard_agent_generation():
    async def _test():
        story_script = {
            "story_title": "Dino Color Party",
            "scenes": [
                {
                    "scene_number": 1,
                    "narration_text": "Rexy saw a red flower.",
                    "visual_description": "Green baby T-Rex looking at a red flower"
                }
            ]
        }
        production_plan = {
            "target_age_group": "3-5",
            "visual_style": "3D Pixar Render"
        }

        sb_service = StoryboardAgentService()
        sb = await sb_service.generate_storyboard("proj_sb_test", story_script, production_plan)

        assert sb["project_id"] == "proj_sb_test"
        assert len(sb["scenes"]) >= 1
        scene1 = sb["scenes"][0]
        assert "visual_plan" in scene1
        assert "camera_plan" in scene1
        assert "transition" in scene1

    asyncio.run(_test())

def test_storyboard_validation_service():
    invalid_sb = {
        "project_id": "proj_invalid",
        "story_title": "Test Title",
        "total_scenes": 1,
        "scenes": [
            {
                "scene_number": 1,
                # Missing visual_plan and camera_plan
            }
        ]
    }
    with pytest.raises(StoryboardValidationError) as exc:
        StoryboardValidationService.validate_storyboard(invalid_sb)
    assert "missing 'visual_plan'" in str(exc.value)

def test_storyboard_api_lifecycle():
    # 1. Create Project
    create_res = client.post("/api/v1/projects", json={
        "title": "Jungle Animals Count",
        "prompt": "Jungle animals count bananas",
        "target_age_group": "3-5"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_id = create_res.json()["data"]["id"]

    # 2. Generate Story Script first
    client.post(f"/api/v1/projects/{proj_id}/generate-story", headers=AUTH_HEADERS)

    # 3. Generate Storyboard API
    sb_res = client.post(f"/api/v1/projects/{proj_id}/generate-storyboard", headers=AUTH_HEADERS)
    assert sb_res.status_code == 200
    assert sb_res.json()["success"] is True
    sb_data = sb_res.json()["data"]
    assert "global_color_palette" in sb_data

    # 4. Fetch Storyboard API
    get_sb = client.get(f"/api/v1/projects/{proj_id}/storyboard", headers=AUTH_HEADERS)
    assert get_sb.status_code == 200
    assert get_sb.json()["data"]["total_scenes"] > 0

    # 5. Regenerate Single Scene API
    regen_res = client.post(f"/api/v1/projects/{proj_id}/storyboard/regenerate-scene/1", headers=AUTH_HEADERS)
    assert regen_res.status_code == 200
    assert regen_res.json()["success"] is True

    # 6. Approve Storyboard API
    app_res = client.post(f"/api/v1/projects/{proj_id}/storyboard/approve", headers=AUTH_HEADERS)
    assert app_res.status_code == 200
    assert app_res.json()["data"]["approved"] is True

    # 7. Check Storyboard Status API
    status_res = client.get(f"/api/v1/projects/{proj_id}/storyboard/status", headers=AUTH_HEADERS)
    assert status_res.status_code == 200
    assert status_res.json()["data"]["approved"] is True
