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