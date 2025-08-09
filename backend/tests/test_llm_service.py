import pytest
import respx
from httpx import Response
from app.services.llm import generate_outline, LLMError
import asyncio

@pytest.mark.asyncio
@respx.mock
async def test_generate_outline_success():
    respx.post("https://openrouter.ai/api/v1/generate").mock(return_value=Response(200, json={"ok": True, "slides": [1,2,3]}))
    payload = {"prompt": "AI", "numSlides": 3, "language": "en"}
    result = await generate_outline(payload)
    assert result["ok"] is True
    assert "slides" in result

@pytest.mark.asyncio
@respx.mock
async def test_generate_outline_failure():
    respx.post("https://openrouter.ai/api/v1/generate").mock(return_value=Response(500, json={"error": "fail"}))
    payload = {"prompt": "AI", "numSlides": 3, "language": "en"}
    with pytest.raises(LLMError):
        await generate_outline(payload) 