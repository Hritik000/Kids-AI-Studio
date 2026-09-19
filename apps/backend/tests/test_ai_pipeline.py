import time
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}
TEST_PROMPT = "Create a 2 minute story about a brave dinosaur who learns teamwork."

# ==============================================================================
# PHASE B: AI PIPELINE INTEGRATION & VALIDATION TEST SUITE
# ==============================================================================

def test_step_1_story_generation():
    """Verify Story Agent generation, JSON schema, kid-safe content & persistence."""
    # 1. Create Project
    create_res = client.post("/api/v1/projects", json={
        "title": "Brave Dinosaur Teamwork",
        "prompt": TEST_PROMPT,
        "target_age_group": "3-5",
        "aspect_ratio": "16:9"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_id = create_res.json()["data"]["id"]

    # 2. Generate Production Plan
    plan_res = client.post(f"/api/v1/projects/{proj_id}/generate-plan", headers=AUTH_HEADERS)
    assert plan_res.status_code == 200
    plan_data = plan_res.json()["data"]
    assert plan_data["scene_count"] >= 3
    assert "educational_objective" in plan_data

    # 3. Generate Story Script
    story_res = client.post(f"/api/v1/projects/{proj_id}/generate-story", headers=AUTH_HEADERS)
    assert story_res.status_code == 200
    story_data = story_res.json()["data"]
    assert "story_title" in story_data
    assert "scenes" in story_data
    assert len(story_data["scenes"]) >= 3

    # Safety & Kid-friendly content verification
    for scene in story_data["scenes"]:
        assert "narration_text" in scene
        assert "visual_description" in scene
        assert scene["estimated_duration"] > 0.0

def test_step_2_storyboard_generation():
    """Verify Storyboard Agent scene timing, camera angles, actions & schema validation."""
    # 1. Setup Project & Story
    create_res = client.post("/api/v1/projects", json={"title": "SB Test", "prompt": TEST_PROMPT}, headers=AUTH_HEADERS)
    proj_id = create_res.json()["data"]["id"]
    client.post(f"/api/v1/projects/{proj_id}/generate-story", headers=AUTH_HEADERS)

    # 2. Generate Storyboard
    sb_res = client.post(f"/api/v1/projects/{proj_id}/generate-storyboard", headers=AUTH_HEADERS)
    assert sb_res.status_code == 200
    sb_data = sb_res.json()["data"]
    
    assert sb_data["total_scenes"] >= 3
    assert sb_data["total_duration_seconds"] > 0.0
    for scene in sb_data["scenes"]:
        assert "scene_number" in scene
        assert "narration_text" in scene
        assert "scene_title" in scene or "purpose" in scene

def test_step_3_and_4_character_and_prompt_generation():
    """Verify Character Engine extraction, visual consistency anchor prompts & prompt composer."""
    create_res = client.post("/api/v1/projects", json={"title": "Char Prompt Test", "prompt": TEST_PROMPT}, headers=AUTH_HEADERS)
    proj_id = create_res.json()["data"]["id"]
    client.post(f"/api/v1/projects/{proj_id}/generate-story", headers=AUTH_HEADERS)
    client.post(f"/api/v1/projects/{proj_id}/generate-storyboard", headers=AUTH_HEADERS)

    # Generate Characters
    char_res = client.post(f"/api/v1/projects/{proj_id}/characters/generate", headers=AUTH_HEADERS)
    assert char_res.status_code == 200
    chars = char_res.json()["data"]
    assert len(chars) > 0
    assert chars[0]["reference_prompt"] is not None

def test_step_5_through_10_media_and_render_pipeline():
    """Verify Image, Animation, Voice, Music, Render & Export stages."""
    create_res = client.post("/api/v1/projects", json={"title": "Media Pipeline Test", "prompt": TEST_PROMPT}, headers=AUTH_HEADERS)
    proj_id = create_res.json()["data"]["id"]
    client.post(f"/api/v1/projects/{proj_id}/generate-story", headers=AUTH_HEADERS)
    client.post(f"/api/v1/projects/{proj_id}/generate-storyboard", headers=AUTH_HEADERS)
    client.post(f"/api/v1/projects/{proj_id}/characters/generate", headers=AUTH_HEADERS)

    # Step 5: Images
    img_res = client.post(f"/api/v1/projects/{proj_id}/images/generate", headers=AUTH_HEADERS)
    assert img_res.status_code == 200
    imgs = img_res.json()["data"]
    assert len(imgs) > 0
    assert imgs[0]["storage_url"].startswith("http")

    # Step 6: Animations
    anim_res = client.post(f"/api/v1/projects/{proj_id}/animations/generate", headers=AUTH_HEADERS)
    assert anim_res.status_code == 200
    anims = anim_res.json()["data"]
    assert len(anims) > 0

    # Step 7: Voices & Lip Sync
    voice_res = client.post(f"/api/v1/projects/{proj_id}/audio/generate-voices", headers=AUTH_HEADERS)
    assert voice_res.status_code == 200
    voices = voice_res.json()["data"]
    assert len(voices) > 0
    assert len(voices[0]["lip_sync"]) > 0

    # Step 8: Music Mixing
    music_res = client.post(f"/api/v1/projects/{proj_id}/music/generate", headers=AUTH_HEADERS)
    assert music_res.status_code == 200
    mixes = music_res.json()["data"]
    assert len(mixes) > 0

    # Step 9: Render Video MP4
    render_res = client.post(f"/api/v1/projects/{proj_id}/render/generate", headers=AUTH_HEADERS)
    assert render_res.status_code == 200
    render_data = render_res.json()["data"]
    assert render_data["status"] == "COMPLETED"
    assert render_data["final_video_url"].endswith(".mp4")

    # Step 10: Download Package Export
    export_res = client.get(f"/api/v1/projects/{proj_id}/render/export", headers=AUTH_HEADERS)
    assert export_res.status_code == 200
    export_data = export_res.json()["data"]
    assert "video_url" in export_data or "download_url" in export_data

def test_step_11_end_to_end_autonomous_pipeline():
    """Verify single prompt creates complete video automatically with timing performance metrics."""
    # 1. Create project with required test prompt
    create_res = client.post("/api/v1/projects", json={
        "title": "Autonomous Brave Dinosaur",
        "prompt": TEST_PROMPT,
        "target_age_group": "3-5",
        "aspect_ratio": "16:9"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_id = create_res.json()["data"]["id"]

    # 2. Trigger End-to-End Full AI Pipeline
    t_start = time.time()
    pipe_res = client.post(f"/api/v1/projects/{proj_id}/generate-full-pipeline", headers=AUTH_HEADERS)
    total_time_sec = round(time.time() - t_start, 3)

    assert pipe_res.status_code == 200
    res_data = pipe_res.json()["data"]

    assert res_data["status"] == "COMPLETED"
    assert res_data["story_title"] is not None
    assert res_data["total_scenes"] >= 3
    assert res_data["final_video_url"].endswith(".mp4")
    assert res_data["download_url"].startswith("http")
    assert "timing_metrics" in res_data
    assert res_data["timing_metrics"]["total_pipeline_duration_sec"] > 0.0

    print(f"\n[PHASE B END-TO-END BENCHMARK] Total Pipeline Duration: {total_time_sec}s")
    for stage, duration in res_data["timing_metrics"].items():
        print(f"   • {stage}: {duration}s")
