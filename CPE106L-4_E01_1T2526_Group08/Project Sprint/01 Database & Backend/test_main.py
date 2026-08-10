from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200

def test_create_user():
    data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "phone": "09999999999",
        "priority_level": 2
    }
    response = client.post("/users/", json=data)
    assert response.status_code == 200 or response.status_code == 201
    assert "name" in response.json()

def test_get_drivers():
    response = client.get("/drivers/")
    assert response.status_code == 200

def test_get_ride_requests():
    response = client.get("/ride-requests/")
    assert response.status_code == 200
