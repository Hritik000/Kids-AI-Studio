import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.creator_copilot import CreatorCopilotService
from app.services.trend_service import TrendService
from app.services.prediction_service import PredictionService

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}

def test_creator_copilot_service():
    report = CreatorCopilotService.analyze_project("proj_123", "Dino Story", "Dinosaur learns ABCs", 4)
    assert report.overall_score > 90.0
    assert len(report.suggestions) >= 3

    opt = CreatorCopilotService.optimize_prompt("Baby dinosaur playing")
    assert "3D Pixar Render" in opt["optimized_prompt"]

def test_trend_service():
    trends = TrendService.get_trending_topics()
    assert len(trends) >= 3
    assert trends[0].topic == "Dinosaurs & Prehistoric Earth"

def test_prediction_service():
    pred = PredictionService.predict_performance("proj_123")
    assert pred.predicted_ctr > 10.0
    assert pred.publishing_risk == "LOW"

def test_copilot_api_lifecycle():
    # 1. Create Project
    create_res = client.post("/api/v1/projects", json={
        "title": "Copilot Test Project",
        "prompt": "Test story for AI copilot analysis",
        "target_age_group": "3-5"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_id = create_res.json()["data"]["id"]

    # 2. Analyze Project API
    analyze_res = client.post(f"/api/v1/copilot/analyze-project/{proj_id}", headers=AUTH_HEADERS)
    assert analyze_res.status_code == 200
    assert analyze_res.json()["data"]["overall_score"] > 90.0

    # 3. Predict Performance API
    pred_res = client.post(f"/api/v1/copilot/predict-performance/{proj_id}", headers=AUTH_HEADERS)
    assert pred_res.status_code == 200
    assert pred_res.json()["data"]["predicted_ctr"] > 10.0

    # 4. List Trends API
    trends_res = client.get("/api/v1/copilot/trends", headers=AUTH_HEADERS)
    assert trends_res.status_code == 200
    assert len(trends_res.json()["data"]) >= 3

    # 5. List Workflows API
    wf_res = client.get("/api/v1/copilot/workflows", headers=AUTH_HEADERS)
    assert wf_res.status_code == 200
    assert len(wf_res.json()["data"]) >= 2

    # 6. List Templates API
    tmpl_res = client.get("/api/v1/copilot/templates", headers=AUTH_HEADERS)
    assert tmpl_res.status_code == 200
    assert len(tmpl_res.json()["data"]) >= 2

    # 7. List Models API
    models_res = client.get("/api/v1/copilot/models", headers=AUTH_HEADERS)
    assert models_res.status_code == 200
    assert len(models_res.json()["data"]) >= 3

    # 8. Optimize Prompt API
    opt_res = client.post("/api/v1/copilot/optimize-prompt", json={"raw_prompt": "Cute lion in jungle"}, headers=AUTH_HEADERS)
    assert opt_res.status_code == 200
    assert "3D Pixar Render" in opt_res.json()["data"]["optimized_prompt"]
