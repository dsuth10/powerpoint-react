import httpx
import logging
import base64
import os
import uuid
import time
from typing import Any, Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random, retry_if_exception
from app.core.config import settings
from app.models.slides import SlidePlan, ImageMeta
from app.models.stability import (
    StabilityGenerationRequest, 
    StabilityGenerationResponse,
    TextPrompt,
    ImageArtifact
)
import asyncio

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
    """Build a prompt for image generation based on slide content."""
    bullets = "; ".join(slide.bullets)
    base = f"Title: {slide.title}. Bullets: {bullets}."
    if style:
        base += f" Style: {style}."
    # Basic normalization for cache keys
    prompt = " ".join(base.split()).strip().lower()
    logger.info(f"Built image prompt for slide '{slide.title}': {prompt}")
    return prompt

def _build_stability_payload(prompt: str, style: Optional[str] = None) -> dict:
    """Build the request payload for Stability AI API with snake_case field names."""
    # Manually construct payload with snake_case field names
    payload = {
        "text_prompts": [{"text": prompt, "weight": 1.0}],
        "cfg_scale": 7.0,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
        "style_preset": style,
        "sampler": "K_DPM_2_ANCESTRAL",
        "seed": 0,
        "extras": None
    }
    
    logger.info(f"Built Stability payload: {payload}")
    return payload

def _save_base64_image(base64_data: str, slide_title: str) -> str:
    """Save a base64 image to disk and return the public URL."""
    try:
        # Decode base64 data
        image_data = base64.b64decode(base64_data)
        
        # Create static directory if it doesn't exist
        static_dir = os.path.join(settings.STATIC_DIR, settings.STATIC_IMAGES_SUBDIR)
        os.makedirs(static_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.png"
        local_path = os.path.join(static_dir, filename)
        
        # Save image to disk
        with open(local_path, "wb") as f:
            f.write(image_data)
        
        # Generate public URL
        public_url = f"{settings.PUBLIC_BASE_URL}{settings.STATIC_URL_PATH}/{settings.STATIC_IMAGES_SUBDIR}/{filename}"
        
        logger.info(f"Saved image for slide '{slide_title}' to {local_path}")
        return public_url
        
    except Exception as e:
        logger.error(f"Error saving base64 image for slide '{slide_title}': {e}")
        raise ImageError(f"Failed to save image: {str(e)}")

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
    wait=wait_exponential(multiplier=1, min=2, max=10) + wait_random(0, 1),
    retry=retry_if_exception(lambda e: not isinstance(e, ImageError)),
)
async def generate_image_for_slide(slide: SlidePlan, style: Optional[str] = None) -> ImageMeta:
    """Generate an image for a slide using the current Stability AI API."""
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
            endpoint = f"/v1/generation/{settings.STABILITY_ENGINE_ID}/text-to-image"
            
            logger.info(f"Sending request to Stability API endpoint: {endpoint}")
            logger.info(f"Request payload: {payload}")
            
            response = await client.post(endpoint, json=payload)
            
            logger.info(f"Stability API response status: {response.status_code}")
            logger.info(f"Stability API response headers: {dict(response.headers)}")
            
            if response.status_code == 429:
                logger.warning("Rate limited by Stability API - returning placeholder")
                return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
            
            if response.status_code == 400:
                logger.error(f"Bad request to Stability API. Response: {response.text}")
                logger.error(f"Request payload was: {payload}")
                return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
            
            response.raise_for_status()
            
            # Parse response
            data = StabilityGenerationResponse(**response.json())
            logger.info(f"Stability API response data: {data.model_dump()}")
            
            if not data.artifacts:
                logger.warning(f"No artifacts in response for slide '{slide.title}', using placeholder")
                return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
            
            # Get the first artifact
            artifact = data.artifacts[0]
            
            if artifact.finishReason != "SUCCESS":
                logger.warning(f"Image generation failed for slide '{slide.title}': {artifact.finishReason}")
                return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
            
            # Save the base64 image to disk
            public_url = _save_base64_image(artifact.base64, slide.title)
            
            # Create image metadata
            meta = ImageMeta(
                url=public_url, 
                alt_text=slide.title, 
                provider="stability-ai"
            )
            
            # Cache the result
            _cache_set(prompt, meta)
            
            logger.info(f"Generated image for slide '{slide.title}': {meta}")
            return meta
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error generating image for slide '{slide.title}': {e}")
            # Fallback to placeholder on client/server errors during live calls
            return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
        except Exception as e:
            logger.error(f"Exception generating image for slide '{slide.title}': {e}")
            return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")

async def generate_images(slides: List[SlidePlan], style: Optional[str] = None) -> List[ImageMeta]:
    """Generate images for multiple slides concurrently."""
    logger.info(f"Generating images for {len(slides)} slides")
    logger.info(f"API Key present: {bool(settings.STABILITY_API_KEY)}")
    
    if not settings.STABILITY_API_KEY:
        logger.warning("No Stability API key found, returning placeholders")
        return [ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder") for slide in slides]
    
    # Reduce concurrency to avoid rate limiting
    sem = asyncio.Semaphore(min(settings.IMAGE_MAX_CONCURRENCY, 2))
    logger.info(f"Using semaphore with max concurrency: {min(settings.IMAGE_MAX_CONCURRENCY, 2)}")

    async def _one(s: SlidePlan) -> ImageMeta:
        async with sem:
            try:
                logger.info(f"Starting image generation for slide: {s.title}")
                result = await generate_image_for_slide(s, style)
                logger.info(f"Completed image generation for slide '{s.title}': {result}")
                return result
            except Exception as e:
                logger.error(f"Unexpected error for slide '{s.title}': {e}")
                return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=s.title, provider="placeholder")

    tasks = [asyncio.create_task(_one(s)) for s in slides]
    results = await asyncio.gather(*tasks)
    
    logger.info(f"Completed image generation for all {len(slides)} slides")
    for i, (slide, result) in enumerate(zip(slides, results)):
        logger.info(f"Slide {i+1} '{slide.title}': {result}")
    
    return results