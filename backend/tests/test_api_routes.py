import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

def test_health_route():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "git_sha" in data

@patch("app.services.llm.generate_outline")
def test_chat_generate_route(mock_llm):
    mock_llm.return_value = {"slides": [{"title": "T", "body": "B", "image": None, "notes": None}]}
    payload = {"prompt": "AI", "numSlides": 1, "language": "en"}
    resp = client.post("/api/v1/chat/generate", json=payload)
    assert resp.status_code == 200
    slides = resp.json()
    assert isinstance(slides, list)
    assert slides[0]["title"] == "T"

@patch("app.services.pptx.build_pptx")
def test_slides_build_route(mock_pptx):
    mock_pptx.return_value = "mock-path"
    payload = [{"title": "T", "body": "B", "image": None, "notes": None}]
    resp = client.post("/api/v1/slides/build", json=payload)
    assert resp.status_code == 200
    job = resp.json()
    assert "jobId" in job
    assert job["status"] == "pending" 