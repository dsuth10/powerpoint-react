import pytest
import respx
from httpx import Response

from app.models.chat import ChatRequest
from app.services.llm import LLMError, generate_outline


@pytest.mark.asyncio
@respx.mock
async def test_generate_outline_success(monkeypatch):
    respx.post("https://openrouter.ai/api/v1/generate").mock(
        return_value=Response(200, json={
            "slides": [
                {"title": "Intro", "bullets": ["A", "B"]},
                {"title": "Next", "bullets": ["C"]}
            ],
            "sessionId": "00000000-0000-0000-0000-000000000000"
        })
    )
    req = ChatRequest(prompt="AI", slide_count=3, model="openrouter/gpt-4o-mini", language="en")
    resp = await generate_outline(req)
    assert len(resp.slides) == 2


@pytest.mark.asyncio
@respx.mock
async def test_generate_outline_http_error():
    respx.post("https://openrouter.ai/api/v1/generate").mock(return_value=Response(500, json={"error": "fail"}))
    req = ChatRequest(prompt="AI", slide_count=3, model="openrouter/gpt-4o-mini", language="en")
    with pytest.raises(LLMError):
        await generate_outline(req)


@pytest.mark.asyncio
@respx.mock
async def test_generate_outline_rate_limit():
    respx.post("https://openrouter.ai/api/v1/generate").mock(return_value=Response(429, json={"error": "rate"}, headers={"Retry-After": "5"}))
    req = ChatRequest(prompt="AI", slide_count=3, model="openrouter/gpt-4o-mini", language="en")
    with pytest.raises(LLMError):
        await generate_outline(req)