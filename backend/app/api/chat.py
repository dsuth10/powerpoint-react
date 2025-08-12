from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse
from app.models.slides import SlidePlan
from app.services import llm as llm_service
from app.services import images as images_service
from app.services.llm import LLMError
from app.core.rate_limit import rate_limit_dependency
from tenacity import RetryError

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post(
    "/generate",
    response_model=List[SlidePlan],
    responses={429: {"description": "Too Many Requests"}},
)
async def generate_chat_outline(request: ChatRequest, _: None = Depends(rate_limit_dependency)):
    slides_out: List[SlidePlan]

    # Outline generation (LLM or offline fallback)
    if not settings.OPENROUTER_API_KEY:
        count = request.slide_count
        slides_out = [SlidePlan(title=f"Slide {i+1}", bullets=["Bullet"]) for i in range(count)]
    else:
        try:
            # Delegate to service; handle both ChatResponse and legacy dict mocks
            response = await llm_service.generate_outline(request)
            if isinstance(response, ChatResponse):
                slides_out = response.slides
            elif isinstance(response, dict) and "slides" in response:
                normalized = []
                for s in response["slides"]:
                    if "bullets" not in s and "body" in s:
                        s = {**s, "bullets": [s.get("body")]}
                        s.pop("body", None)
                    normalized.append(SlidePlan(**s))
                slides_out = normalized
            else:
                raise HTTPException(status_code=502, detail="Upstream returned invalid format")
        except (LLMError, RetryError):
            count = request.slide_count
            slides_out = [SlidePlan(title=f"Slide {i+1}", bullets=["Bullet"]) for i in range(count)]

    # Enrich slides with images when Stability is configured
    if settings.STABILITY_API_KEY:
        try:
            metas = await images_service.generate_images(slides_out)
            for idx, meta in enumerate(metas):
                # Assign generated image metadata onto each slide
                slides_out[idx].image = meta
        except Exception:
            # Ignore image generation failures and return text-only slides
            pass

    return slides_out