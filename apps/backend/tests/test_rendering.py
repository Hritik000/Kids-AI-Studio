import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.timeline_builder import TimelineBuilderService
from app.services.transition_engine import TransitionEngineService
from app.services.render_validator import RenderValidationService, RenderValidationError

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}

def test_timeline_builder_service():
    storyboard = {
        "scenes": [
            {"scene_number": 1, "estimated_duration": 5.0},
            {"scene_number": 2, "estimated_duration": 4.5}
        ]
    }
    animations = [{"scene_number": 1, "storage_url": "http://example.com/anim1.mp4"}]
    voices = [{"scene_number": 1, "storage_url": "http://example.com/voice1.mp3"}]
    music_mixes = [{"scene_number": 1, "storage_url": "http://example.com/mix1.mp3"}]

    timeline = TimelineBuilderService.build_timeline(
        project_id="proj_test_123",
        storyboard=storyboard,
        animations=animations,
        voices=voices,
        music_mixes=music_mixes,
        aspect_ratio="16:9"
    )

    assert timeline.total_duration_seconds == 9.5
    assert len(timeline.scenes) == 2
    assert timeline.scenes[0].transition_type == "CrossFade"
    assert timeline.scenes[1].transition_type == "Cut"

def test_transition_engine_and_validator():
    transitions = TransitionEngineService.get_supported_transitions()
    assert "CrossFade" in transitions
    assert "Cut" in transitions

    invalid_task = {
        "render_id": "rnd_123",
        "project_id": "proj_123",
        "timeline_id": "tl_123",
        "final_video_url": "invalid_url_no_http",
        "preview_url": "http://example.com/prev.mp4"
    }
    with pytest.raises(RenderValidationError) as exc:
        RenderValidationService.validate_render_task(invalid_task)
    assert "Invalid final video storage URL" in str(exc.value)

def test_rendering_api_lifecycle():
    # 1. Create Project
    create_res = client.post("/api/v1/projects", json={
        "title": "Dino Render Film",
        "prompt": "Baby dinosaur dances in HD render",
        "target_age_group": "3-5"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_id = create_res.json()["data"]["id"]

    # 2. Complete previous steps: Story -> Storyboard
    client.post(f"/api/v1/projects/{proj_id}/generate-story", headers=AUTH_HEADERS)
    client.post(f"/api/v1/projects/{proj_id}/generate-storyboard", headers=AUTH_HEADERS)

    # 3. Build Timeline API
    tl_res = client.post(f"/api/v1/projects/{proj_id}/timeline/build", headers=AUTH_HEADERS)
    assert tl_res.status_code == 200
    assert tl_res.json()["success"] is True
    timeline_data = tl_res.json()["data"]
    assert len(timeline_data["scenes"]) >= 1

    # 4. Fetch Timeline API
    get_tl = client.get(f"/api/v1/projects/{proj_id}/timeline", headers=AUTH_HEADERS)
    assert get_tl.status_code == 200
    assert get_tl.json()["data"]["timeline_id"] == timeline_data["timeline_id"]

    # 5. Execute Video Render API
    render_res = client.post(f"/api/v1/projects/{proj_id}/render/generate", headers=AUTH_HEADERS)
    assert render_res.status_code == 200
    assert render_res.json()["success"] is True
    render_task = render_res.json()["data"]
    assert render_task["status"] == "COMPLETED"
    rnd_id = render_task["render_id"]

    # 6. List Renders API
    list_renders = client.get(f"/api/v1/projects/{proj_id}/render", headers=AUTH_HEADERS)
    assert list_renders.status_code == 200
    assert len(list_renders.json()["data"]) >= 1

    # 7. Approve Render API
    app_res = client.post(f"/api/v1/projects/{proj_id}/render/approve/{rnd_id}", headers=AUTH_HEADERS)
    assert app_res.status_code == 200
    assert app_res.json()["data"]["status"] == "APPROVED"

    # 8. Export Project Package API
    exp_res = client.get(f"/api/v1/projects/{proj_id}/render/export", headers=AUTH_HEADERS)
    assert exp_res.status_code == 200
    assert exp_res.json()["data"]["video_url"] == render_task["final_video_url"]

    # 9. Get Render Pipeline Status API
    status_res = client.get(f"/api/v1/projects/{proj_id}/render/status", headers=AUTH_HEADERS)
    assert status_res.status_code == 200
    assert status_res.json()["data"]["has_render"] is True
