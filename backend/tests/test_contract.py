import schemathesis
import pytest
from app.main import app
from fastapi.testclient import TestClient

schema_path = "/api/v1/openapi.json"
client = TestClient(app)
# Use schemathesis ASGI loader
schema = schemathesis.from_asgi(app=app, schema_path=schema_path)

@schema.parametrize()
def test_api_contract(case):
    response = case.call_asgi()
    case.validate_response(response) 