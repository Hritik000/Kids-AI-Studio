from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer demo_token_user_demo_123"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_project_crud_lifecycle():
    # 1. Create Project
    create_payload = {
        "title": "Space Explorer Adventure",
        "prompt": "Little astronauts explore shapes on Mars",
        "target_age_group": "3-5",
        "language": "English (US)",
        "video_length": "Standard (2-3 min)",
        "aspect_ratio": "16:9",
        "video_style": "3D Pixar Render",
        "voice": "Storyteller Emma",
        "save_as_draft": True
    }
    res = client.post("/api/v1/projects", json=create_payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["success"] is True
    project = res_data["data"]
    proj_id = project["id"]
    assert project["title"] == "Space Explorer Adventure"
    assert project["status"] == "DRAFT"

    # 2. Update Project (Auto-Save / Edit)
    update_payload = {
        "title": "Space Explorer Adventure v2",
        "prompt": "Updated prompt text for space adventure"
    }
    update_res = client.put(f"/api/v1/projects/{proj_id}", json=update_payload, headers=AUTH_HEADERS)
    assert update_res.status_code == 200
    assert update_res.json()["data"]["title"] == "Space Explorer Adventure v2"

    # 3. Toggle Favorite
    fav_res = client.post(f"/api/v1/projects/{proj_id}/favorite", headers=AUTH_HEADERS)
    assert fav_res.status_code == 200
    assert fav_res.json()["data"]["favorite"] is True

    # 4. Duplicate Project
    dup_res = client.post(f"/api/v1/projects/{proj_id}/duplicate", headers=AUTH_HEADERS)
    assert dup_res.status_code == 200
    dup_data = dup_res.json()["data"]
    assert "Copy" in dup_data["title"]

    # 5. Archive Project
    arc_res = client.post(f"/api/v1/projects/{proj_id}/archive", headers=AUTH_HEADERS)
    assert arc_res.status_code == 200
    assert arc_res.json()["data"]["archived"] is True

    # 6. Restore Project
    rest_res = client.post(f"/api/v1/projects/{proj_id}/restore", headers=AUTH_HEADERS)
    assert rest_res.status_code == 200
    assert rest_res.json()["data"]["archived"] is False

    # 7. Delete Project
    del_res = client.delete(f"/api/v1/projects/{proj_id}", headers=AUTH_HEADERS)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

def test_list_search_and_filter():
    res = client.get("/api/v1/projects?q=Dinosaurs&sort=newest", headers=AUTH_HEADERS)
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert res_data["total"] >= 1
    assert "Dinosaurs" in res_data["items"][0]["title"]
