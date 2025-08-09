import pytest
import respx
from httpx import Response
from app.services.images import generate_image, ImageError
import asyncio

@pytest.mark.asyncio
@respx.mock
async def test_generate_image_success():
    respx.post("https://api.runware.ai/v1/generate").mock(return_value=Response(200, json={"ok": True, "url": "http://img"}))
    payload = {"prompt": "cat"}
    result = await generate_image(payload)
    assert result["ok"] is True
    assert "url" in result

@pytest.mark.asyncio
@respx.mock
async def test_generate_image_failure():
    respx.post("https://api.runware.ai/v1/generate").mock(return_value=Response(500, json={"error": "fail"}))
    payload = {"prompt": "cat"}
    with pytest.raises(ImageError):
        await generate_image(payload) 