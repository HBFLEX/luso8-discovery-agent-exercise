import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_discovery_job_creation():
    payload = {
        "business_description": "We produce packaged tomatoes from local farmers in Malawi.",
        "target_market": "NG",
        "buyer_types": ["distributor", "supermarket"],
        "max_results": 5
    }

    response = client.post("/api/discovery", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "job_id" in data
    assert data["status"] in ["queued", "running", "done"]


def test_invalid_discovery_request():
    payload = {
        "business_description": "Too short",
        "buyer_types": ["invalid_type"],
        "max_results": 100
    }

    response = client.post("/api/discovery", json=payload)
    assert response.status_code == 422
