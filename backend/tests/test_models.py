import pytest
from app.models.chat import ChatRequest
from app.models.slides import SlidePlan, ImageMeta
from app.models.common import PPTXJob

def test_chat_request_model_dump_camel_case():
    req = ChatRequest(prompt="AI", num_slides=3, language="en", context="test")
    data = req.model_dump()
    assert "numSlides" in data
    assert data["numSlides"] == 3
    assert "prompt" in data
    assert "language" in data
    assert "context" in data

def test_slide_plan_and_image_meta():
    img = ImageMeta(url="http://x", alt="desc", provider="runware")
    slide = SlidePlan(title="T", body="B", image=img, notes="N")
    data = slide.model_dump()
    assert data["image"]["provider"] == "runware"
    assert data["title"] == "T"
    assert data["body"] == "B"
    assert data["notes"] == "N"

def test_pptx_job_model_dump():
    job = PPTXJob(job_id="abc", status="pending", download_url="http://x", error=None)
    data = job.model_dump()
    assert "jobId" in data
    assert "downloadUrl" in data
    assert data["status"] == "pending"
    assert data["jobId"] == "abc"
    assert data["downloadUrl"] == "http://x"

def test_chat_request_strict_validation():
    with pytest.raises(Exception):
        ChatRequest(prompt=123, num_slides="bad", language=1) 