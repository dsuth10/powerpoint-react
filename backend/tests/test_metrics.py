from fastapi.testclient import TestClient
from app.main import app

def test_metrics_route():
    client = TestClient(app)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"http_request_duration_seconds_count" in resp.content 