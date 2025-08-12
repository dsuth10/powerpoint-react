import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import os
import respx

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


@pytest.mark.live
@pytest.mark.live_llm
def test_chat_generate_route_live_llm(require_live_llm, no_http_mocks):
    # Require upstream success (no silent fallback) for this test
    os.environ["OPENROUTER_REQUIRE_UPSTREAM"] = "true"
    # Ensure no HTTP mocking via respx is active
    try:
        router = respx.get_router()
        if router and router.is_started:
            router.stop()
    except Exception:
        pass

    payload = {"prompt": "Live route test", "numSlides": 2, "language": "en", "model": "openai/gpt-4o-mini"}
    try:
        resp = client.post("/api/v1/chat/generate", json=payload)
    finally:
        os.environ.pop("OPENROUTER_REQUIRE_UPSTREAM", None)
    assert resp.status_code == 200
    slides = resp.json()
    assert isinstance(slides, list) and len(slides) == 2
    for slide in slides:
        assert slide.get("title") and isinstance(slide.get("bullets", []), list)
    # Ensure not the offline minimal fallback shape for all slides
    minimal_like = all(
        (str(slide.get("title", "")).startswith("Slide ") and slide.get("bullets") == ["Bullet"]) for slide in slides
    )
    assert not minimal_like, "Response looks like offline fallback; upstream likely not used"