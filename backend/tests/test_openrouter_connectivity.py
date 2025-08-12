import os
import pytest
import httpx


@pytest.mark.asyncio
@pytest.mark.live
@pytest.mark.live_llm
async def test_openrouter_direct_chat_completions(require_live_llm, no_http_mocks):
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-4o-mini")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if os.getenv("OPENROUTER_HTTP_REFERER"):
        headers["HTTP-Referer"] = os.getenv("OPENROUTER_HTTP_REFERER")
    if os.getenv("OPENROUTER_APP_TITLE"):
        headers["X-Title"] = os.getenv("OPENROUTER_APP_TITLE")

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Return the word PONG"}
        ],
        "temperature": 0,
    }

    async with httpx.AsyncClient(base_url=base_url, timeout=30.0, headers=headers) as client:
        resp = await client.post("/chat/completions", json=payload)
        assert resp.status_code == 200, f"status={resp.status_code} body={resp.text[:200]}"
        data = resp.json()
        assert "choices" in data and isinstance(data["choices"], list) and data["choices"], "missing choices"
        content = data["choices"][0].get("message", {}).get("content", "")
        assert isinstance(content, str) and content, "empty content"

