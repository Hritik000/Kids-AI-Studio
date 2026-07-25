import asyncio
import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.character import CharacterEngineService
from app.services.prompt_composer import PromptComposerService
from app.services.image_validator import ImageValidationService, ImageValidationError

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}

def test_character_engine_service():
    story_script = {
        "characters": [
            {
                "name": "Rexy",
                "species_or_type": "Baby T-Rex",
                "visual_features": "Soft green scales, cheerful orange spots",
                "personality": "Playful"
            }
        ]
    }
    profiles = CharacterEngineService.generate_character_profiles("proj_char_test", story_script)
    assert len(profiles) == 1
    assert profiles[0].name == "Rexy"
    assert "Rexy" in profiles[0].reference_prompt

def test_prompt_composer_service():
    storyboard_scene = {
        "visual_plan": {
            "environment": "Sunny Dinosaur Meadow",
            "time_of_day": "Morning",
            "lighting_style": "Warm Sunlight",
            "background": "Green hills",
            "foreground": "Soft grass",
            "color_palette": ["Lime Green", "Yellow"]
        },
        "camera_plan": {
            "shot_type": "Wide Shot",
            "angle": "Eye Level",
            "focal_point": "Rexy"
        },
        "character_references": [
            {
                "character_name": "Rexy",
                "expression": "Joyful",
                "pose": "Stretching"
            }
        ]
    }

    profiles = CharacterEngineService.generate_character_profiles("proj_char_test", {
        "characters": [{"name": "Rexy", "species_or_type": "T-Rex", "visual_features": "Green scales"}]
    })

    prompts = PromptComposerService.compose_scene_prompt(storyboard_scene, profiles, "3D Pixar Render")
    assert "3D Pixar Render" in prompts["positive_prompt"]
    assert "Rexy" in prompts["positive_prompt"]
    assert "dark" in prompts["negative_prompt"]

def test_character_and_image_api_lifecycle():
    # 1. Create Project
    create_res = client.post("/api/v1/projects", json={
        "title": "Safari Animals Learn Shapes",
        "prompt": "Safari animals explore shapes",
        "target_age_group": "3-5"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_id = create_res.json()["data"]["id"]

    # 2. Pipeline sequence: Story -> Storyboard -> Characters -> Scene Images
    client.post(f"/api/v1/projects/{proj_id}/generate-story", headers=AUTH_HEADERS)
    client.post(f"/api/v1/projects/{proj_id}/generate-storyboard", headers=AUTH_HEADERS)

    # 3. Generate Character Memory Profiles API
    char_res = client.post(f"/api/v1/projects/{proj_id}/characters/generate", headers=AUTH_HEADERS)
    assert char_res.status_code == 200
    assert char_res.json()["success"] is True
    assert len(char_res.json()["data"]) >= 1

    # 4. Generate Scene Images API
    img_res = client.post(f"/api/v1/projects/{proj_id}/images/generate", headers=AUTH_HEADERS)
    assert img_res.status_code == 200
    assert img_res.json()["success"] is True
    images = img_res.json()["data"]
    assert len(images) >= 1
    first_img_id = images[0]["image_id"]

    # 5. Fetch Scene Images List API
    list_imgs = client.get(f"/api/v1/projects/{proj_id}/images", headers=AUTH_HEADERS)
    assert list_imgs.status_code == 200
    assert len(list_imgs.json()["data"]) == len(images)

    # 6. Approve Scene Image API
    app_res = client.post(f"/api/v1/projects/{proj_id}/images/approve/{first_img_id}", headers=AUTH_HEADERS)
    assert app_res.status_code == 200
    assert app_res.json()["data"]["status"] == "APPROVED"

    # 7. Check Image Pipeline Status API
    status_res = client.get(f"/api/v1/projects/{proj_id}/images/status", headers=AUTH_HEADERS)
    assert status_res.status_code == 200
    assert status_res.json()["data"]["has_images"] is True
    assert status_res.json()["data"]["approved_images"] == 1
