from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from app.core.errors import add_error_handlers

app = FastAPI()
add_error_handlers(app)

@app.get("/raise-http")
def raise_http():
    raise HTTPException(status_code=418, detail="I'm a teapot")

@app.get("/raise-generic")
def raise_generic():
    raise ValueError("Unexpected error")

client = TestClient(app)

def test_http_exception_handler():
    resp = client.get("/raise-http")
    assert resp.status_code == 418
    assert resp.json()["detail"] == "I'm a teapot"

def test_generic_exception_handler():
    resp = client.get("/raise-generic")
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Internal server error" 