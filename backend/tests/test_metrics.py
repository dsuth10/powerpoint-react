from fastapi.testclient import TestClient
from app.main import app


def test_metrics_route():
    client = TestClient(app)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    # Instrumentator v7 exposes histogram without _count suffix by default
    assert b"# TYPE http_request_duration_seconds histogram" in resp.content