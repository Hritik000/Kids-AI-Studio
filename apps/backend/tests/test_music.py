import asyncio
import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.music_planner import MusicPlannerService
from app.services.sound_effects import SoundEffectService
from app.services.ambient_audio import AmbientAudioService
from app.services.music_validator import MusicValidationService, MusicValidationError

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}

def test_music_planner_service():
    storyboard = {
        "visual_style": "3D Pixar Render",
        "total_duration_seconds": 45.0,
        "scenes": [
            {"visual_plan": {"mood": "Cheerful & Playful"}}
        ]
    }
    plan = MusicPlannerService.plan_music_for_project(storyboard)
    assert plan.bpm == 112
    assert "Marimba" in plan.instruments
    assert plan.duration_seconds == 45.0

def test_sound_effects_and_ambient():
    scene = {
        "visual_plan": {"environment": "Jungle Forest"},
        "character_references": [{"pose": "Running"}]
    }
    sfx = SoundEffectService.generate_sound_effects_for_scene(scene, 1)
    amb = AmbientAudioService.generate_ambient_plan_for_scene(scene)

    assert len(sfx) >= 1
    assert sfx[0].category == "Footsteps"
    assert amb.environment_type == "Jungle Forest"

def test_music_validation_service():
    invalid_mix = {
        "mix_id": "mix_123",
        "project_id": "proj_123",
        "scene_number": 1,
        "storage_url": "invalid_url_without_http",
        "music_plan": {"track_id": "mus_1"},
        "duration_seconds": 5.0
    }
    with pytest.raises(MusicValidationError) as exc:
        MusicValidationService.validate_mixed_track(invalid_mix)
    assert "Invalid mixed audio storage URL" in str(exc.value)

def test_music_api_lifecycle():
    # 1. Create Project
    create_res = client.post("/api/v1/projects", json={
        "title": "Dino Music Score",
        "prompt": "Baby dinosaur dances to jungle music",
        "target_age_group": "3-5"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_id = create_res.json()["data"]["id"]

    # 2. Complete previous steps: Story -> Storyboard
    client.post(f"/api/v1/projects/{proj_id}/generate-story", headers=AUTH_HEADERS)
    client.post(f"/api/v1/projects/{proj_id}/generate-storyboard", headers=AUTH_HEADERS)

    # 3. Generate Music & Audio Mix API
    mix_res = client.post(f"/api/v1/projects/{proj_id}/music/generate", headers=AUTH_HEADERS)
    assert mix_res.status_code == 200
    assert mix_res.json()["success"] is True
    tracks = mix_res.json()["data"]
    assert len(tracks) >= 1
    first_mix_id = tracks[0]["mix_id"]

    # 4. Fetch Music Tracks List API
    list_tracks = client.get(f"/api/v1/projects/{proj_id}/music", headers=AUTH_HEADERS)
    assert list_tracks.status_code == 200
    assert len(list_tracks.json()["data"]) == len(tracks)

    # 5. Approve Audio Mix API
    app_res = client.post(f"/api/v1/projects/{proj_id}/music/approve/{first_mix_id}", headers=AUTH_HEADERS)
    assert app_res.status_code == 200
    assert app_res.json()["data"]["status"] == "APPROVED"

    # 6. Check Music Pipeline Status API
    status_res = client.get(f"/api/v1/projects/{proj_id}/music/status", headers=AUTH_HEADERS)
    assert status_res.status_code == 200
    assert status_res.json()["data"]["has_music"] is True
    assert status_res.json()["data"]["approved_tracks"] == 1
