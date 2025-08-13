import httpx
import logging
from typing import Any, Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random, retry_if_exception
from app.core.config import settings
from app.models.slides import SlidePlan, ImageMeta
from app.models.stability import StabilityGenerationRequest, StabilityGenerationResponse
import asyncio
import time
import os
import uuid

# Set up logging
logger = logging.getLogger(__name__)

class ImageError(Exception):
    """Custom exception for image service errors."""
    pass

def _headers() -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {settings.STABILITY_API_KEY}" if settings.STABILITY_API_KEY else "",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    logger.info(f"Image service headers configured: {list(headers.keys())}")
    return headers

def get_async_client() -> httpx.AsyncClient:
    client = httpx.AsyncClient(
        base_url=settings.STABILITY_BASE_URL,
        timeout=settings.STABILITY_TIMEOUT_SECONDS,
        headers=_headers(),
    )
    logger.info(f"Image service client created with base_url={settings.STABILITY_BASE_URL}, timeout={settings.STABILITY_TIMEOUT_SECONDS}s")
    return client

def build_prompt(slide: SlidePlan, style: Optional[str] = None) -> str:
    bullets = "; ".join(slide.bullets)
    base = f"Title: {slide.title}. Bullets: {bullets}."
    if style:
        base += f" Style: {style}."
    # Basic normalization for cache keys
    prompt = " ".join(base.split()).strip().lower()
    logger.info(f"Built image prompt for slide '{slide.title}': {prompt}")
    return prompt

def _build_stability_payload(prompt: str, style: Optional[str] = None) -> StabilityGenerationRequest:
    payload = StabilityGenerationRequest(prompt=prompt, stylePreset=style)
    logger.info(f"Built Stability payload: {payload.model_dump(by_alias=True)}")
    return payload

_cache: dict[str, tuple[float, ImageMeta]] = {}

def _cache_get(key: str) -> Optional[ImageMeta]:
    entry = _cache.get(key)
    if not entry:
        logger.debug(f"Cache miss for key: {key}")
        return None
    ts, value = entry
    if time.time() - ts > settings.IMAGE_CACHE_TTL_SECONDS:
        logger.debug(f"Cache entry expired for key: {key}")
        _cache.pop(key, None)
        return None
    logger.info(f"Cache hit for key: {key}")
    return value

def _cache_set(key: str, value: ImageMeta) -> None:
    # Evict if over size cap
    if len(_cache) >= settings.IMAGE_CACHE_MAX_ENTRIES:
        # pop arbitrary oldest
        oldest_key = min(_cache.keys(), key=lambda k: _cache[k][0])
        logger.debug(f"Evicting oldest cache entry: {oldest_key}")
        _cache.pop(oldest_key, None)
    _cache[key] = (time.time(), value)
    logger.info(f"Cached image for key: {key}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4) + wait_random(0, 0.5),
    retry=retry_if_exception(lambda e: not isinstance(e, ImageError)),
)
async def generate_image_for_slide(slide: SlidePlan, style: Optional[str] = None) -> ImageMeta:
    logger.info(f"Generating image for slide: {slide.title}")
    logger.info(f"API Key present: {bool(settings.STABILITY_API_KEY)}")
    
    async with get_async_client() as client:
        try:
            prompt = build_prompt(slide, style)
            # Cache lookup
            cached = _cache_get(prompt)
            if cached:
                logger.info(f"Returning cached image for slide '{slide.title}': {cached}")
                return cached

            payload = _build_stability_payload(prompt, style)
            logger.info(f"Sending request to Stability API for slide '{slide.title}'")
            
            # Primary attempt: legacy JSON endpoint used in tests
            resp = await client.post("/images/generations", json=payload.model_dump(by_alias=True))
            logger.info(f"Legacy endpoint response status: {resp.status_code}")
            logger.info(f"Legacy endpoint response headers: {dict(resp.headers)}")
            
            if resp.status_code == 429:
                logger.error("Rate limited by Stability API")
                raise ImageError("Rate limited by Stability API")
            if resp.status_code == 404:
                logger.info("Legacy endpoint returned 404, trying v2beta endpoint")
                # Try v2beta stable-image endpoint as fallback
                v2beta_payload: Dict[str, Any] = {
                    "prompt": prompt,
                    "output_format": "png",
                }
                if style:
                    v2beta_payload["style_preset"] = style
                
                logger.info(f"V2beta payload: {v2beta_payload}")
                
                # Prefer image bytes back
                v2_resp = await client.post(
                    "/v2beta/stable-image/generate/core",
                    json=v2beta_payload,
                    headers={"Accept": "image/*"},
                )
                
                logger.info(f"V2beta response status: {v2_resp.status_code}")
                logger.info(f"V2beta response headers: {dict(v2_resp.headers)}")
                
                if v2_resp.status_code == 429:
                    logger.error("V2beta rate limited by Stability API")
                    raise ImageError("Rate limited by Stability API")
                v2_resp.raise_for_status()
                content_type = v2_resp.headers.get("Content-Type", "")
                logger.info(f"V2beta content type: {content_type}")
                
                if content_type.startswith("image/"):
                    logger.info("V2beta returned image content, saving to file")
                    os.makedirs(os.path.join(settings.STATIC_DIR, settings.STATIC_IMAGES_SUBDIR), exist_ok=True)
                    filename = f"{uuid.uuid4()}.png"
                    local_path = os.path.join(settings.STATIC_DIR, settings.STATIC_IMAGES_SUBDIR, filename)
                    with open(local_path, "wb") as f:
                        f.write(v2_resp.content)
                    public_url = f"{settings.PUBLIC_BASE_URL}{settings.STATIC_URL_PATH}/{settings.STATIC_IMAGES_SUBDIR}/{filename}"
                    meta = ImageMeta(url=public_url, alt_text=slide.title, provider="stability-ai")
                    _cache_set(prompt, meta)
                    logger.info(f"Generated image for slide '{slide.title}': {meta}")
                    return meta
                
                # If JSON shape, attempt to parse minimal url
                try:
                    logger.info("V2beta returned JSON, attempting to parse")
                    data_json = v2_resp.json()
                    logger.info(f"V2beta JSON response: {data_json}")
                    data = StabilityGenerationResponse(**data_json)
                    url = (data.url or '').rstrip('/')
                    if url:
                        meta = ImageMeta(url=url, alt_text=slide.title, provider="stability-ai")
                        _cache_set(prompt, meta)
                        logger.info(f"Generated image from V2beta JSON for slide '{slide.title}': {meta}")
                        return meta
                except Exception as e:
                    logger.error(f"Failed to parse V2beta JSON response: {e}")
                    pass
                
                # Fall through to placeholder
                logger.warning(f"Falling back to placeholder for slide '{slide.title}'")
                return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
            
            # Legacy json path success
            resp.raise_for_status()
            data = StabilityGenerationResponse(**resp.json())
            logger.info(f"Legacy endpoint response data: {data.model_dump()}")
            url = (data.url or '').rstrip('/')
            if not url:
                logger.warning(f"No URL in legacy response for slide '{slide.title}', using placeholder")
                return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
            meta = ImageMeta(url=url, alt_text=slide.title, provider="stability-ai")
            _cache_set(prompt, meta)
            logger.info(f"Generated image from legacy endpoint for slide '{slide.title}': {meta}")
            return meta
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error generating image for slide '{slide.title}': {e}")
            # Fallback to placeholder on client/server errors during live calls
            return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
        except Exception as e:
            logger.error(f"Exception generating image for slide '{slide.title}': {e}")
            raise ImageError(f"Image request failed: {str(e)}") from e

async def generate_images(slides: List[SlidePlan], style: Optional[str] = None) -> List[ImageMeta]:
    logger.info(f"Generating images for {len(slides)} slides")
    logger.info(f"API Key present: {bool(settings.STABILITY_API_KEY)}")
    
    if not settings.STABILITY_API_KEY:
        logger.warning("No Stability API key found, returning placeholders")
        return [ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder") for slide in slides]
    
    sem = asyncio.Semaphore(settings.IMAGE_MAX_CONCURRENCY)
    logger.info(f"Using semaphore with max concurrency: {settings.IMAGE_MAX_CONCURRENCY}")

    async def _one(s: SlidePlan) -> ImageMeta:
        async with sem:
            try:
                logger.info(f"Starting image generation for slide: {s.title}")
                result = await generate_image_for_slide(s, style)
                logger.info(f"Completed image generation for slide '{s.title}': {result}")
                return result
            except ImageError as e:
                logger.error(f"ImageError for slide '{s.title}': {e}")
                return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=s.title, provider="placeholder")
            except Exception as e:
                logger.error(f"Unexpected error for slide '{s.title}': {e}")
                return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=s.title, provider="placeholder")

    tasks = [asyncio.create_task(_one(s)) for s in slides]
    results = await asyncio.gather(*tasks)
    
    logger.info(f"Completed image generation for all {len(slides)} slides")
    for i, (slide, result) in enumerate(zip(slides, results)):
        logger.info(f"Slide {i+1} '{slide.title}': {result}")
    
    return results