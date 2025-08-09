import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.chat import ChatRequest, ChatResponse
from app.models.common import PPTXJob
from app.models.errors import ErrorResponse
from app.models.slides import ImageMeta, SlidePlan


def test_chat_request_alias_and_validation():
    req = ChatRequest(prompt="AI", slide_count=3, model="openrouter/some-model", language="en")
    data = req.model_dump()
    assert "slideCount" in data and data["slideCount"] == 3
    assert "prompt" in data and data["prompt"] == "AI"
    assert "model" in data
    # invalid
    with pytest.raises(Exception):
        ChatRequest(prompt="", slide_count=0, model="m")


def test_slide_plan_bullets_and_image_meta_aliases_and_validation():
    img = ImageMeta(url="http://example.com/img.png", alt_text="desc", provider="runware")
    slide = SlidePlan(title="Title", bullets=["A", "B"], image=img, notes="N")
    data = slide.model_dump()
    assert data["title"] == "Title"
    assert data["bullets"] == ["A", "B"]
    assert data["image"]["altText"] == "desc"
    # invalid url
    with pytest.raises(Exception):
        ImageMeta(url="not-a-url", alt_text="x", provider="y")
    # empty bullets list
    with pytest.raises(Exception):
        SlidePlan(title="T", bullets=[])


def test_pptx_job_types_and_aliases():
    job = PPTXJob(job_id=uuid.uuid4(), status="pending", result_url="http://example.com/file.pptx")
    data = job.model_dump()
    assert "jobId" in data
    assert "resultUrl" in data
    assert data["status"] == "pending"
    # invalid status
    with pytest.raises(Exception):
        PPTXJob(job_id=uuid.uuid4(), status="unknown")


def test_error_response_serialization():
    err = ErrorResponse(error_code="UPSTREAM_ERROR", message="Bad gateway", details={"provider": "llm"})
    data = err.model_dump()
    assert data["errorCode"] == "UPSTREAM_ERROR"
    assert data["message"] == "Bad gateway"
    assert data["details"]["provider"] == "llm"


def test_models_present_in_openapi():
    client = TestClient(app)
    schema = client.get("/api/v1/openapi.json").json()
    components = schema.get("components", {}).get("schemas", {})
    assert "ChatRequest" in components
    assert "SlidePlan" in components