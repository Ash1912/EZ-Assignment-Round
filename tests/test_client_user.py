import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# --- Test Signup ---
def test_signup():
    response = client.post("/client/signup", json={
        "email": "testclient@example.com",
        "password": "strongpassword",
        "role": "client"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "testclient@example.com"

# --- Test Login ---
def test_login():
    response = client.post("/client/login", json={
        "email": "testclient@example.com",
        "password": "strongpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

# --- Test List Files ---
def test_list_files():
    response = client.get("/client/files")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# --- Test Download File ---
def test_download_file():
    response = client.get("/client/download-file/1")  # Assuming file ID 1 exists
    assert response.status_code == 200
    assert "download-link" in response.json()
