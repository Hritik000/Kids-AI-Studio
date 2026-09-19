import time
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

VALID_TOKEN = "demo_token_user_demo_123"
ADMIN_TOKEN = "demo_token_admin"
INVALID_TOKEN = "invalid_malformed_token_999"
AUTH_HEADERS = {"Authorization": f"Bearer {VALID_TOKEN}"}
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}

# ==============================================================================
# 1. AUTHENTICATION & SECURITY TESTS
# ==============================================================================

def test_missing_auth_header():
    """Verify that unauthenticated requests to protected endpoints return 401 Unauthorized."""
    res = client.get("/api/v1/projects")
    assert res.status_code == 401
    assert "token missing" in res.json().get("detail", "").lower()

def test_invalid_token_format():
    """Verify that malformed or unrecognized tokens return 401 Unauthorized."""
    res = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {INVALID_TOKEN}"})
    assert res.status_code == 401
    assert "could not validate credentials" in res.json().get("detail", "").lower()

def test_valid_token_authentication():
    """Verify that valid Bearer tokens successfully return user profile."""
    res = client.get("/api/v1/auth/me", headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["email"] == "creator@kidsai.studio"

def test_admin_token_role():
    """Verify that admin tokens receive ADMIN role privileges."""
    res = client.get("/api/v1/auth/me", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    assert res.json()["data"]["role"] == "ADMIN"


# ==============================================================================
# 2. DATABASE & CRUD OPERATIONS TESTS
# ==============================================================================

def test_create_project_input_validation():
    """Verify that empty or malformed JSON payloads return 422 Unprocessable Entity."""
    res = client.post("/api/v1/projects", json={}, headers=AUTH_HEADERS)
    assert res.status_code == 422

def test_full_project_crud_lifecycle():
    """Verify Create, Read, Update, Duplicate, Archive, Restore, Delete flow."""
    # 1. Create Project
    create_res = client.post("/api/v1/projects", json={
        "title": "Infra Test Safari",
        "prompt": "Jungle animals learn numbers",
        "target_age_group": "3-5",
        "aspect_ratio": "16:9"
    }, headers=AUTH_HEADERS)
    assert create_res.status_code == 200
    proj_data = create_res.json()["data"]
    proj_id = proj_data["id"]
    assert proj_data["title"] == "Infra Test Safari"
    assert proj_data["status"] == "DRAFT"

    # 2. Get Single Project
    get_res = client.get(f"/api/v1/projects/{proj_id}", headers=AUTH_HEADERS)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == proj_id

    # 3. Update Project
    update_res = client.put(f"/api/v1/projects/{proj_id}", json={
        "title": "Infra Test Safari (Updated Title)"
    }, headers=AUTH_HEADERS)
    assert update_res.status_code == 200
    assert update_res.json()["data"]["title"] == "Infra Test Safari (Updated Title)"

    # 4. Duplicate Project
    dup_res = client.post(f"/api/v1/projects/{proj_id}/duplicate", headers=AUTH_HEADERS)
    assert dup_res.status_code == 200
    dup_id = dup_res.json()["data"]["id"]
    assert dup_id != proj_id
    assert "(Copy)" in dup_res.json()["data"]["title"]

    # 5. Archive & Restore
    arch_res = client.post(f"/api/v1/projects/{proj_id}/archive", headers=AUTH_HEADERS)
    assert arch_res.status_code == 200
    assert arch_res.json()["data"]["archived"] is True

    rest_res = client.post(f"/api/v1/projects/{proj_id}/restore", headers=AUTH_HEADERS)
    assert rest_res.status_code == 200
    assert rest_res.json()["data"]["archived"] is False

    # 6. Favorite Toggle
    fav_res = client.post(f"/api/v1/projects/{proj_id}/favorite", headers=AUTH_HEADERS)
    assert fav_res.status_code == 200
    assert fav_res.json()["data"]["favorite"] is True

    # 7. Delete Projects
    del_res1 = client.delete(f"/api/v1/projects/{proj_id}", headers=AUTH_HEADERS)
    del_res2 = client.delete(f"/api/v1/projects/{dup_id}", headers=AUTH_HEADERS)
    assert del_res1.status_code == 200
    assert del_res2.status_code == 200

def test_nonexistent_project_crud_errors():
    """Verify that operating on non-existent project IDs returns structured NOT_FOUND error."""
    bad_id = "proj_does_not_exist_999"
    
    get_res = client.get(f"/api/v1/projects/{bad_id}", headers=AUTH_HEADERS)
    assert get_res.status_code == 200
    assert get_res.json()["success"] is False
    assert get_res.json()["error"]["code"] == "NOT_FOUND"

    put_res = client.put(f"/api/v1/projects/{bad_id}", json={"title": "Test"}, headers=AUTH_HEADERS)
    assert put_res.json()["success"] is False

    del_res = client.delete(f"/api/v1/projects/{bad_id}", headers=AUTH_HEADERS)
    assert del_res.json()["success"] is False


# ==============================================================================
# 3. FRONTEND <-> BACKEND & ERROR HANDLING TESTS
# ==============================================================================

def test_cors_headers_preflight():
    """Verify that OPTIONS preflight requests return permissive CORS headers."""
    res = client.options("/api/v1/projects", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    })
    assert res.status_code == 200
    assert "access-control-allow-origin" in res.headers

def test_health_check_endpoint():
    """Verify system health endpoint responsiveness."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "KidsAI Studio" in data["app"]


# ==============================================================================
# 4. PERFORMANCE & LATENCY BENCHMARK
# ==============================================================================

def test_api_response_latency_under_100ms():
    """Verify that core infrastructure endpoints respond in under 100ms."""
    start_time = time.time()
    res = client.get("/api/v1/projects", headers=AUTH_HEADERS)
    elapsed_ms = (time.time() - start_time) * 1000
    
    assert res.status_code == 200
    assert elapsed_ms < 100.0, f"API latency too high: {elapsed_ms:.2f}ms"
