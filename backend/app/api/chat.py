from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse
from app.models.slides import SlidePlan
from app.services import llm as llm_service
from app.services import images as images_service
from app.services.llm import LLMError
from app.core.rate_limit import rate_limit_dependency
from tenacity import RetryError

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post(
    "/generate",
    response_model=List[SlidePlan],
    responses={429: {"description": "Too Many Requests"}},
)
async def generate_chat_outline(request: ChatRequest, _: None = Depends(rate_limit_dependency)):
    logger.info(f"Chat generate endpoint called with request: {request.prompt[:100]}...")
    logger.info(f"Request details: slide_count={request.slide_count}, model={request.model}, language={request.language}")
    logger.info(f"API Key present: {bool(settings.OPENROUTER_API_KEY)}")
    logger.info(f"Require upstream: {settings.OPENROUTER_REQUIRE_UPSTREAM}")
    
    slides_out: List[SlidePlan]

    # Outline generation (LLM or offline fallback)
    if not settings.OPENROUTER_API_KEY:
        logger.warning("No OpenRouter API key found, using offline fallback")
        count = request.slide_count
        slides_out = [SlidePlan(title=f"Slide {i+1}", bullets=["Bullet"]) for i in range(count)]
        logger.info(f"Generated {len(slides_out)} offline fallback slides")
    else:
        try:
            logger.info("Calling LLM service for outline generation...")
            # Delegate to service; handle both ChatResponse and legacy dict mocks
            response = await llm_service.generate_outline(request)
            logger.info(f"LLM service returned response type: {type(response)}")
            
            if isinstance(response, ChatResponse):
                slides_out = response.slides
                logger.info(f"Parsed ChatResponse with {len(slides_out)} slides")
            elif isinstance(response, dict) and "slides" in response:
                logger.info("Parsing legacy dict response format")
                normalized = []
                for s in response["slides"]:
                    if "bullets" not in s and "body" in s:
                        s = {**s, "bullets": [s.get("body")]}
                        s.pop("body", None)
                    normalized.append(SlidePlan(**s))
                slides_out = normalized
                logger.info(f"Normalized {len(slides_out)} slides from legacy format")
            else:
                logger.error(f"Unexpected response format: {type(response)}")
                raise HTTPException(status_code=502, detail="Upstream returned invalid format")
                
        except (LLMError, RetryError) as e:
            logger.error(f"LLM service failed: {e}")
            # If upstream is required, surface an error instead of returning minimal placeholders
            if settings.OPENROUTER_REQUIRE_UPSTREAM:
                logger.error("Require upstream is enabled, returning 502 error")
                raise HTTPException(status_code=502, detail="LLM upstream required and failed")
            logger.warning("Falling back to offline minimal outline")
            count = request.slide_count
            slides_out = [SlidePlan(title=f"Slide {i+1}", bullets=["Bullet"]) for i in range(count)]

    # Log slide details before image enrichment
    for i, slide in enumerate(slides_out):
        logger.info(f"Slide {i+1}: title='{slide.title}', bullets={len(slide.bullets)}, has_image={slide.image is not None}, has_notes={bool(slide.notes)}")
        if slide.image:
            logger.info(f"Slide {i+1} image: {slide.image}")
        if slide.notes:
            logger.info(f"Slide {i+1} notes: {slide.notes[:100]}...")

    # Enrich slides with images when Stability is configured
    if settings.STABILITY_API_KEY:
        logger.info("Stability API key found, attempting image generation...")
        try:
            metas = await images_service.generate_images(slides_out)
            logger.info(f"Image service returned {len(metas)} image metadata")
            for idx, meta in enumerate(metas):
                # Assign generated image metadata onto each slide
                slides_out[idx].image = meta
                logger.info(f"Assigned image to slide {idx+1}: {meta}")
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            # Ignore image generation failures and return text-only slides
            pass
    else:
        logger.info("No Stability API key found, skipping image generation")

    # Log final slide details
    logger.info(f"Returning {len(slides_out)} slides")
    for i, slide in enumerate(slides_out):
        logger.info(f"Final slide {i+1}: title='{slide.title}', bullets={len(slide.bullets)}, has_image={slide.image is not None}, has_notes={bool(slide.notes)}")

    return slides_out