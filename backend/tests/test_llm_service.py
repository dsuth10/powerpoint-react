import os
import pytest
import respx
from httpx import Response

from app.models.chat import ChatRequest
from app.services.llm import LLMError, generate_outline


@pytest.mark.asyncio
@respx.mock
async def test_generate_outline_success_via_fallback(monkeypatch):
    # Force HTTP code path
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    # Fallback endpoint returns valid JSON
    respx.post("https://openrouter.ai/api/v1/generate").mock(
        return_value=Response(200, json={
            "slides": [
                {"title": "Intro", "bullets": ["A", "B"]},
                {"title": "Next", "bullets": ["C"]}
            ],
            "sessionId": "00000000-0000-0000-0000-000000000000"
        })
    )
    req = ChatRequest(prompt="AI", slide_count=3, model="openai/gpt-4o-mini", language="en")
    resp = await generate_outline(req)
    assert len(resp.slides) == 2


@pytest.mark.asyncio
@respx.mock
async def test_generate_outline_http_error(monkeypatch):
    # Force HTTP path
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    # Make fallback also fail so the service bubbles an LLMError internally,
    # which generate_outline then converts to offline minimal output
    respx.post("https://openrouter.ai/api/v1/generate").mock(return_value=Response(500, json={"error": "fail"}))
    req = ChatRequest(prompt="AI", slide_count=3, model="openai/gpt-4o-mini", language="en")
    resp = await generate_outline(req)
    assert len(resp.slides) == 3


@pytest.mark.asyncio
@respx.mock
async def test_generate_outline_rate_limit(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    respx.post("https://openrouter.ai/api/v1/generate").mock(return_value=Response(429, json={"error": "rate"}, headers={"Retry-After": "5"}))
    req = ChatRequest(prompt="AI", slide_count=3, model="openai/gpt-4o-mini", language="en")
    resp = await generate_outline(req)
    assert len(resp.slides) == 3


@pytest.mark.asyncio
@respx.mock
async def test_primary_completions_parsing_and_fallback_on_malformed(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    # First, mock /chat/completions with content that does NOT contain JSON
    respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=Response(200, json={
            "choices": [
                {"message": {"content": "I am text without JSON"}}
            ]
        })
    )
    # Then ensure fallback /generate returns valid JSON
    respx.post("https://openrouter.ai/api/v1/generate").mock(
        return_value=Response(200, json={
            "slides": [
                {"title": "One", "bullets": ["A"]},
                {"title": "Two", "bullets": ["B"]}
            ]
        })
    )
    req = ChatRequest(prompt="AI", slide_count=2, model="openai/gpt-4o-mini", language="en")
    resp = await generate_outline(req)
    assert len(resp.slides) == 2


@pytest.mark.asyncio
@respx.mock
async def test_completions_error_then_fallback_success(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    # Primary completions fails
    respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=Response(500, json={"error": "oops"})
    )
    # Fallback generate succeeds
    respx.post("https://openrouter.ai/api/v1/generate").mock(
        return_value=Response(200, json={"slides": [{"title": "A", "bullets": ["b"]}]})
    )
    req = ChatRequest(prompt="AI", slide_count=1, model="openai/gpt-4o-mini", language="en")
    resp = await generate_outline(req)
    assert len(resp.slides) == 1


@pytest.mark.asyncio
@respx.mock
async def test_completions_success_parsing(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=Response(200, json={
            "choices": [
                {"message": {"content": "{\"slides\":[{\"title\":\"A\",\"bullets\":[\"b\"]},{\"title\":\"B\",\"bullets\":[\"c\"]}]}"}}
            ]
        })
    )
    req = ChatRequest(prompt="AI", slide_count=2, model="openai/gpt-4o-mini", language="en")
    resp = await generate_outline(req)
    assert len(resp.slides) == 2
    assert resp.slides[0].title == "A"


@pytest.mark.asyncio
@respx.mock
async def test_disallowed_model_triggers_fallback(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    # Ensure no network calls are actually made due to early model check
    req = ChatRequest(prompt="AI", slide_count=2, model="not-in-allowlist", language="en")
    resp = await generate_outline(req)
    # generate_outline catches LLMError from model check and falls back to offline minimal
    assert len(resp.slides) == 2


@pytest.mark.asyncio
async def test_offline_mode_without_api_key(monkeypatch):
    # Temporarily clear API key
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    req = ChatRequest(prompt="AI", slide_count=2, model="openrouter/gpt-4o-mini", language="en")
    resp = await generate_outline(req)
    assert len(resp.slides) == 2


@pytest.mark.asyncio
@pytest.mark.live
@pytest.mark.live_llm
async def test_generate_outline_live_llm(require_live_llm, no_http_mocks):
    # Require upstream success for this assertion (no silent fallback)
    os.environ["OPENROUTER_REQUIRE_UPSTREAM"] = "true"
    req = ChatRequest(prompt="Test live outline", slide_count=2, model="openai/gpt-4o-mini", language="en")
    try:
        resp = await generate_outline(req)
    finally:
        os.environ.pop("OPENROUTER_REQUIRE_UPSTREAM", None)
    assert resp.slides and len(resp.slides) == 2
    for slide in resp.slides:
        assert slide.title and isinstance(slide.bullets, list)
    # Hard-proof heuristic: ensure we didn't hit offline minimal fallback ("Slide {i+1}" + ["Bullet"]) for all slides
    minimal_like = all(
        (s.title.startswith("Slide ") and s.bullets == ["Bullet"]) for s in resp.slides
    )
    assert not minimal_like, "Response looks like offline fallback; upstream likely not used"