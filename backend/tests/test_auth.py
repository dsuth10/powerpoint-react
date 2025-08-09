import pytest
from fastapi.testclient import TestClient
from app.core.auth import create_access_token, create_refresh_token, verify_token
from app.api.auth import router as auth_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(auth_router)
client = TestClient(app)

def test_jwt_token_issuance_and_verification():
    email = "user@example.com"
    access = create_access_token(email)
    refresh = create_refresh_token(email)
    data = verify_token(access, token_type="access")
    assert data.sub == email
    data2 = verify_token(refresh, token_type="refresh")
    assert data2.sub == email

def test_login_endpoint():
    resp = client.post("/auth/login", json={"email": "user@example.com"})
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

def test_refresh_endpoint():
    resp = client.post("/auth/login", json={"email": "user@example.com"})
    tokens = resp.json()
    refresh_token = tokens["refresh_token"]
    resp2 = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp2.status_code == 200
    tokens2 = resp2.json()
    assert "access_token" in tokens2
    assert "refresh_token" in tokens2 