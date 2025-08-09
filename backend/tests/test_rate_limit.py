import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_rate_limit_exceeded():
    for i in range(100):
        resp = client.post("/api/v1/chat/generate", json={"prompt": "AI", "numSlides": 1, "language": "en"})
        assert resp.status_code in (200, 429)
    # 101st request should be rate-limited
    resp = client.post("/api/v1/chat/generate", json={"prompt": "AI", "numSlides": 1, "language": "en"})
    assert resp.status_code == 429
    assert resp.json()["detail"] == "Rate limit exceeded"

def test_rate_limit_separate_ips():
    for ip in ["1.1.1.1", "2.2.2.2"]:
        for i in range(100):
            resp = client.post("/api/v1/chat/generate", json={"prompt": "AI", "numSlides": 1, "language": "en"}, headers={"x-forwarded-for": ip})
            assert resp.status_code in (200, 429)
        # 101st request for each IP should be rate-limited
        resp = client.post("/api/v1/chat/generate", json={"prompt": "AI", "numSlides": 1, "language": "en"}, headers={"x-forwarded-for": ip})
        assert resp.status_code == 429 