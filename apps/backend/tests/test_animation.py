import asyncio
import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.motion_planner import MotionPlannerService
from app.services.animation_validator import AnimationValidationService, AnimationValidationError

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}

def test_motion_planner_service():
    storyboard_scene = {
        "estimated_duration": 6.0,
        "camera_plan": {
            "shot_type": "Wide Shot",
            "movement": "Tracking Shot",
            "camera_speed": "Gentle"
        },
        "visual_plan": {
            "weather": "Sunny",
            "time_of_day": "Morning"
        },
        "character_references": [
            {
                "character_name": "Rexy",
                "pose": "Running",
                "expression": "Excited"
            }
        ],
        "transition": {
            "type": "Cross Fade"
        }
    }
    plan = MotionPlannerService.plan_motion_for_scene(storyboard_scene, [])
    assert plan.camera_path == "Tracking Shot"
    assert "Rexy" in plan.character_motion
    assert plan.duration_seconds == 6.0
    assert plan.frame_rate == 24

def test_animation_validation_service():
    invalid_clip = {
        "animation_id": "anim_123",
        "project_id": "proj_123",
        "scene_number": 1,
        "composed_motion_prompt": "Zoom in on Rexy",
        "storage_url": "invalid_url_without_http",
        "duration_seconds": 5.0
    }
    with pytest.raises(AnimationValidationError) as exc:
        AnimationValidationService.validate_animation(invalid_clip)
    assert "Invalid video storage URL" in str(exc.value)

def test_animation_api_lifecycle():
    # 1. Create Project
    create_res = client.post("/api/v1/projects", json={
        "title": "Dino Motion Adventure",
        "prompt": "Baby dinosaur runs through valley",
        "target_age_group": "3-5"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_id = create_res.json()["data"]["id"]

    # 2. Complete previous steps: Story -> Storyboard -> Characters -> Images
    client.post(f"/api/v1/projects/{proj_id}/generate-story", headers=AUTH_HEADERS)
    client.post(f"/api/v1/projects/{proj_id}/generate-storyboard", headers=AUTH_HEADERS)
    client.post(f"/api/v1/projects/{proj_id}/characters/generate", headers=AUTH_HEADERS)
    client.post(f"/api/v1/projects/{proj_id}/images/generate", headers=AUTH_HEADERS)

    # 3. Generate Scene Animations API
    anim_res = client.post(f"/api/v1/projects/{proj_id}/animations/generate", headers=AUTH_HEADERS)
    assert anim_res.status_code == 200
    assert anim_res.json()["success"] is True
    clips = anim_res.json()["data"]
    assert len(clips) >= 1
    first_anim_id = clips[0]["animation_id"]

    # 4. Fetch Scene Animations List API
    list_clips = client.get(f"/api/v1/projects/{proj_id}/animations", headers=AUTH_HEADERS)
    assert list_clips.status_code == 200
    assert len(list_clips.json()["data"]) == len(clips)

    # 5. Approve Scene Animation API
    app_res = client.post(f"/api/v1/projects/{proj_id}/animations/approve/{first_anim_id}", headers=AUTH_HEADERS)
    assert app_res.status_code == 200
    assert app_res.json()["data"]["status"] == "APPROVED"

    # 6. Check Animation Status API
    status_res = client.get(f"/api/v1/projects/{proj_id}/animations/status", headers=AUTH_HEADERS)
    assert status_res.status_code == 200
    assert status_res.json()["data"]["has_animations"] is True
    assert status_res.json()["data"]["approved_clips"] == 1
