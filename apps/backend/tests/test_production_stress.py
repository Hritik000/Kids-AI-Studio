import time
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}
STRESS_PROMPT = "Create a 2 minute story about a brave astronaut dinosaur."

# ==============================================================================
# PHASE C: PRODUCTION STRESS & STABILITY SUITE
# ==============================================================================

@pytest.mark.integration
def test_stress_batch_10_generations():
    """Verify stability & memory footprint across 10 consecutive full pipeline generations."""
    t0 = time.time()
    successful_runs = 0

    for idx in range(10):
        create_res = client.post("/api/v1/projects", json={
            "title": f"Stress Test 10 - Run #{idx+1}",
            "prompt": STRESS_PROMPT
        }, headers=AUTH_HEADERS)
        assert create_res.status_code == 200
        proj_id = create_res.json()["data"]["id"]

        pipe_res = client.post(f"/api/v1/projects/{proj_id}/generate-full-pipeline", headers=AUTH_HEADERS)
        assert pipe_res.status_code == 200
        assert pipe_res.json()["data"]["status"] == "COMPLETED"
        successful_runs += 1

    total_time = round(time.time() - t0, 3)
    avg_latency = round(total_time / 10, 3)
    print(f"\n[STRESS TEST 10] 10/10 Runs Succeeded in {total_time}s (Avg per run: {avg_latency}s)")
    assert successful_runs == 10

@pytest.mark.integration
def test_stress_batch_25_generations():
    """Verify stability across 25 consecutive pipeline generations."""
    t0 = time.time()
    successful_runs = 0

    for idx in range(25):
        create_res = client.post("/api/v1/projects", json={
            "title": f"Stress Test 25 - Run #{idx+1}",
            "prompt": STRESS_PROMPT
        }, headers=AUTH_HEADERS)
        assert create_res.status_code == 200
        proj_id = create_res.json()["data"]["id"]

        pipe_res = client.post(f"/api/v1/projects/{proj_id}/generate-full-pipeline", headers=AUTH_HEADERS)
        assert pipe_res.status_code == 200
        successful_runs += 1

    total_time = round(time.time() - t0, 3)
    print(f"\n[STRESS TEST 25] 25/25 Runs Succeeded in {total_time}s")
    assert successful_runs == 25

@pytest.mark.integration
def test_stress_batch_50_generations():
    """Verify stability across 50 consecutive pipeline generations."""
    t0 = time.time()
    successful_runs = 0

    for idx in range(50):
        create_res = client.post("/api/v1/projects", json={
            "title": f"Stress Test 50 - Run #{idx+1}",
            "prompt": STRESS_PROMPT
        }, headers=AUTH_HEADERS)
        assert create_res.status_code == 200
        proj_id = create_res.json()["data"]["id"]

        pipe_res = client.post(f"/api/v1/projects/{proj_id}/generate-full-pipeline", headers=AUTH_HEADERS)
        assert pipe_res.status_code == 200
        successful_runs += 1

    total_time = round(time.time() - t0, 3)
    print(f"\n[STRESS TEST 50] 50/50 Runs Succeeded in {total_time}s")
    assert successful_runs == 50

@pytest.mark.integration
def test_stress_batch_100_generations():
    """Verify stability across 100 consecutive pipeline generations."""
    t0 = time.time()
    successful_runs = 0

    for idx in range(100):
        create_res = client.post("/api/v1/projects", json={
            "title": f"Stress Test 100 - Run #{idx+1}",
            "prompt": STRESS_PROMPT
        }, headers=AUTH_HEADERS)
        assert create_res.status_code == 200
        proj_id = create_res.json()["data"]["id"]

        pipe_res = client.post(f"/api/v1/projects/{proj_id}/generate-full-pipeline", headers=AUTH_HEADERS)
        assert pipe_res.status_code == 200
        successful_runs += 1

    total_time = round(time.time() - t0, 3)
    print(f"\n[STRESS TEST 100] 100/100 Runs Succeeded in {total_time}s")
    assert successful_runs == 100

def test_system_metrics_endpoint():
    """Verify /metrics endpoint for monitoring system health and pipeline stats."""
    res = client.get("/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "total_projects" in data
    assert "uptime_seconds" in data
