import os
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


@pytest.mark.asyncio
@pytest.mark.live
@pytest.mark.live_llm
async def test_generate_outline_live_llm(monkeypatch):
    if not (os.getenv("RUN_LIVE_LLM") == "1" and os.getenv("OPENROUTER_API_KEY")):
        pytest.skip("live LLM test requires RUN_LIVE_LLM=1 and OPENROUTER_API_KEY")
    # ensure we do not mock http in this test
    try:
        respx_router = respx.get_router()
        if respx_router and respx_router.is_started:
            respx_router.stop()
    except Exception:
        pass

    req = ChatRequest(prompt="Test live outline", slide_count=3, model="openrouter/gpt-4o-mini", language="en")
    resp = await generate_outline(req)
    assert resp.slides and len(resp.slides) == 3
    for slide in resp.slides:
        assert slide.title and isinstance(slide.bullets, list)