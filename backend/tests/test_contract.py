import schemathesis
import pytest
from app.main import app
from fastapi.testclient import TestClient

schema_url = "/api/v1/openapi.json"
client = TestClient(app)
schema = schemathesis.from_uri(schema_url, app=app)

@schema.parametrize()
def test_api_contract(case):
    response = case.call_asgi()
    case.validate_response(response) 