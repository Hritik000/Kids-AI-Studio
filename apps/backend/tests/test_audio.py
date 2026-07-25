import asyncio
import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.dialogue_planner import DialoguePlannerService
from app.services.lip_sync import LipSyncEngineService
from app.services.audio_validator import AudioValidationService, AudioValidationError

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}

def test_dialogue_planner_service():
    storyboard_scene = {
        "narration_text": "Rexy found a giant red flower! He smelled it happily.",
        "visual_plan": {"mood": "Joyful"}
    }
    segments = DialoguePlannerService.plan_dialogue_for_scene(storyboard_scene, 1)
    assert len(segments) == 2
    assert "Rexy found a giant red flower" in segments[0].text
    assert segments[0].emotional_tone == "Joyful"

def test_lip_sync_service():
    segments = DialoguePlannerService.plan_dialogue_for_scene({
        "narration_text": "Hello little dinosaur friend!"
    }, 1)
    lip_sync = LipSyncEngineService.generate_lip_sync_timeline(segments, 5.0)
    assert len(lip_sync.visemes) > 0
    assert lip_sync.visemes[-1].mouth_shape == "Rest"
    assert len(lip_sync.blink_timestamps) > 0

def test_audio_validation_service():
    invalid_audio = {
        "audio_id": "aud_123",
        "project_id": "proj_123",
        "scene_number": 1,
        "storage_url": "invalid_url_without_http",
        "dialogue_segments": [{"text": "Hello"}],
        "duration_seconds": 5.0
    }
    with pytest.raises(AudioValidationError) as exc:
        AudioValidationService.validate_audio(invalid_audio)
    assert "Invalid audio storage URL" in str(exc.value)

def test_audio_api_lifecycle():
    # 1. Create Project
    create_res = client.post("/api/v1/projects", json={
        "title": "Dino Voice Tale",
        "prompt": "Baby dinosaur speaks with friends",
        "target_age_group": "3-5"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_id = create_res.json()["data"]["id"]

    # 2. Complete previous steps: Story -> Storyboard
    client.post(f"/api/v1/projects/{proj_id}/generate-story", headers=AUTH_HEADERS)
    client.post(f"/api/v1/projects/{proj_id}/generate-storyboard", headers=AUTH_HEADERS)

    # 3. Generate Voice Narration API
    voice_res = client.post(f"/api/v1/projects/{proj_id}/audio/generate-voices", headers=AUTH_HEADERS)
    assert voice_res.status_code == 200
    assert voice_res.json()["success"] is True
    clips = voice_res.json()["data"]
    assert len(clips) >= 1
    first_audio_id = clips[0]["audio_id"]

    # 4. Fetch Audio Narration List API
    list_clips = client.get(f"/api/v1/projects/{proj_id}/audio", headers=AUTH_HEADERS)
    assert list_clips.status_code == 200
    assert len(list_clips.json()["data"]) == len(clips)

    # 5. Approve Audio Narration API
    app_res = client.post(f"/api/v1/projects/{proj_id}/audio/approve/{first_audio_id}", headers=AUTH_HEADERS)
    assert app_res.status_code == 200
    assert app_res.json()["data"]["status"] == "APPROVED"

    # 6. Check Audio Status API
    status_res = client.get(f"/api/v1/projects/{proj_id}/audio/status", headers=AUTH_HEADERS)
    assert status_res.status_code == 200
    assert status_res.json()["data"]["has_audio"] is True
    assert status_res.json()["data"]["approved_clips"] == 1
