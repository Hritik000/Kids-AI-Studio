from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_auth_flow():
    # 1. Register new user
    reg_payload = {
        "full_name": "Test User",
        "email": "testuser@kidsai.studio",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "terms_accepted": True
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert "access_token" in res["data"]
    token = res["data"]["access_token"]
    
    # 2. Get Me (Authenticated)
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["success"] is True
    assert me_data["data"]["email"] == "testuser@kidsai.studio"

def test_unauthorized_access():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
