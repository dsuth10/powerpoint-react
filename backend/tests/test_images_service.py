import os
import pytest
import respx
from httpx import Response

from app.models.slides import SlidePlan
from app.services.images import ImageError, build_prompt, generate_image_for_slide, generate_images


@pytest.mark.asyncio
@respx.mock
async def test_generate_image_for_slide_success():
    respx.post("https://api.stability.ai/v2/images/generations").mock(
        return_value=Response(200, json={"url": "http://img"})
    )
    slide = SlidePlan(title="T", bullets=["A", "B"], image=None, notes=None)
    meta = await generate_image_for_slide(slide)
    assert meta.url == "http://img"
    assert meta.provider == "stability-ai"


@pytest.mark.asyncio
@respx.mock
async def test_generate_image_for_slide_rate_limit():
    respx.post("https://api.stability.ai/v2/images/generations").mock(
        return_value=Response(429, json={"error": "rate"}, headers={"Retry-After": "5"})
    )
    slide = SlidePlan(title="T", bullets=["A"], image=None, notes=None)
    with pytest.raises(ImageError):
        await generate_image_for_slide(slide)


@pytest.mark.asyncio
@respx.mock
async def test_generate_images_batch_order_preserved():
    calls = []

    def _responder(request):
        calls.append(1)
        return Response(200, json={"url": f"http://img/{len(calls)}"})

    respx.post("https://api.stability.ai/v2/images/generations").mock(side_effect=_responder)
    slides = [
        SlidePlan(title="S1", bullets=["A"], image=None, notes=None),
        SlidePlan(title="S2", bullets=["B"], image=None, notes=None),
    ]
    results = await generate_images(slides)
    assert len(results) == 2
    assert results[0].url.endswith("/1")
    assert results[1].url.endswith("/2")


@pytest.mark.asyncio
@pytest.mark.live
@pytest.mark.live_images
async def test_generate_image_for_slide_live(monkeypatch):
    if not (os.getenv("RUN_LIVE_IMAGES") == "1" and os.getenv("STABILITY_API_KEY")):
        pytest.skip("live image test requires RUN_LIVE_IMAGES=1 and STABILITY_API_KEY")
    # ensure we do not mock http in this test
    try:
        respx_router = respx.get_router()
        if respx_router and respx_router.is_started:
            respx_router.stop()
    except Exception:
        pass

    slide = SlidePlan(title="Live Image", bullets=["A"], image=None, notes=None)
    meta = await generate_image_for_slide(slide)
    assert meta.url and meta.url.startswith("http")
    assert meta.provider in ("stability-ai", "placeholder")