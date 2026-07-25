import asyncio
import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.director import DirectorAgentService
from app.services.story import StoryAgentService
from app.services.validator import ValidationService, QualityValidationError

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}

def test_director_agent_plan_generation():
    async def _test():
        director = DirectorAgentService()
        plan = await director.generate_production_plan(
            project_id="proj_test_123",
            topic="Space Astronauts Learn Shapes",
            target_age_group="3-5"
        )
        assert plan["project_id"] == "proj_test_123"
        assert "educational_objective" in plan
        assert plan["scene_count"] >= 2
        assert len(plan["character_requirements"]) >= 1
    
    asyncio.run(_test())

def test_story_agent_script_generation():
    async def _test():
        director = DirectorAgentService()
        plan = await director.generate_production_plan(
            project_id="proj_test_123",
            topic="Dinosaurs Learn Colors",
            target_age_group="3-5"
        )

        story_agent = StoryAgentService()
        story = await story_agent.generate_story_script(production_plan=plan)

        assert "story_title" in story
        assert "story_summary" in story
        assert len(story["scenes"]) == plan["scene_count"]
        for scene in story["scenes"]:
            assert "narration_text" in scene
            assert "visual_description" in scene

    asyncio.run(_test())

def test_validation_safety_audit():
    unsafe_story = {
        "story_title": "Scary Monster Night",
        "story_summary": "A scary monster comes out to fight",
        "educational_goal": "None",
        "characters": [],
        "scenes": [
            {
                "scene_number": 1,
                "narration_text": "A ghost appears!",
                "visual_description": "Dark scary monster"
            }
        ]
    }
    with pytest.raises(QualityValidationError) as exc:
        ValidationService.validate_story_script(unsafe_story)
    assert "Child safety audit failed" in str(exc.value)

def test_ai_pipeline_api_endpoints():
    # 1. Create a dummy project
    create_res = client.post("/api/v1/projects", json={
        "title": "Ocean Friends Learn Numbers",
        "prompt": "Ocean animals count from 1 to 5",
        "target_age_group": "3-5"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_id = create_res.json()["data"]["id"]

    # 2. Generate Production Plan via Director Agent API
    plan_res = client.post(f"/api/v1/projects/{proj_id}/generate-plan", headers=AUTH_HEADERS)
    assert plan_res.status_code == 200
    assert plan_res.json()["success"] is True
    plan_data = plan_res.json()["data"]
    assert plan_data["scene_count"] > 0

    # 3. Generate Story Script via Story Agent API
    story_res = client.post(f"/api/v1/projects/{proj_id}/generate-story", headers=AUTH_HEADERS)
    assert story_res.status_code == 200
    assert story_res.json()["success"] is True
    story_data = story_res.json()["data"]
    assert "story_title" in story_data

    # 4. Fetch Stored Production Plan & Story
    get_plan = client.get(f"/api/v1/projects/{proj_id}/plan", headers=AUTH_HEADERS)
    assert get_plan.status_code == 200
    assert get_plan.json()["data"]["project_id"] == proj_id

    get_story = client.get(f"/api/v1/projects/{proj_id}/story", headers=AUTH_HEADERS)
    assert get_story.status_code == 200
    assert "story_title" in get_story.json()["data"]

    # 5. Check Pipeline Status
    status_res = client.get(f"/api/v1/projects/{proj_id}/pipeline-status", headers=AUTH_HEADERS)
    assert status_res.status_code == 200
    assert status_res.json()["data"]["has_story_script"] is True
    assert status_res.json()["data"]["status"] == "STORY_READY"
