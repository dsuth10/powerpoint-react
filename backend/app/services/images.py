import httpx
from typing import Any, Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random, retry_if_exception
from app.core.config import settings
from app.models.slides import SlidePlan, ImageMeta
from app.models.stability import StabilityGenerationRequest, StabilityGenerationResponse
import asyncio
import time
import os
import uuid

class ImageError(Exception):
    """Custom exception for image service errors."""
    pass

def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.STABILITY_API_KEY}" if settings.STABILITY_API_KEY else "",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def get_async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=settings.STABILITY_BASE_URL,
        timeout=settings.STABILITY_TIMEOUT_SECONDS,
        headers=_headers(),
    )

def build_prompt(slide: SlidePlan, style: Optional[str] = None) -> str:
    bullets = "; ".join(slide.bullets)
    base = f"Title: {slide.title}. Bullets: {bullets}."
    if style:
        base += f" Style: {style}."
    # Basic normalization for cache keys
    return " ".join(base.split()).strip().lower()

def _build_stability_payload(prompt: str, style: Optional[str] = None) -> StabilityGenerationRequest:
    return StabilityGenerationRequest(prompt=prompt, stylePreset=style)

_cache: dict[str, tuple[float, ImageMeta]] = {}

def _cache_get(key: str) -> Optional[ImageMeta]:
    entry = _cache.get(key)
    if not entry:
        return None
    ts, value = entry
    if time.time() - ts > settings.IMAGE_CACHE_TTL_SECONDS:
        _cache.pop(key, None)
        return None
    return value

def _cache_set(key: str, value: ImageMeta) -> None:
    # Evict if over size cap
    if len(_cache) >= settings.IMAGE_CACHE_MAX_ENTRIES:
        # pop arbitrary oldest
        oldest_key = min(_cache.keys(), key=lambda k: _cache[k][0])
        _cache.pop(oldest_key, None)
    _cache[key] = (time.time(), value)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4) + wait_random(0, 0.5),
    retry=retry_if_exception(lambda e: not isinstance(e, ImageError)),
)
async def generate_image_for_slide(slide: SlidePlan, style: Optional[str] = None) -> ImageMeta:
    async with get_async_client() as client:
        try:
            prompt = build_prompt(slide, style)
            # Cache lookup
            cached = _cache_get(prompt)
            if cached:
                return cached

            payload = _build_stability_payload(prompt, style)
            # Primary attempt: legacy JSON endpoint used in tests
            resp = await client.post("/images/generations", json=payload.model_dump(by_alias=True))
            if resp.status_code == 429:
                raise ImageError("Rate limited by Stability API")
            if resp.status_code == 404:
                # Try v2beta stable-image endpoint as fallback
                v2beta_payload: Dict[str, Any] = {
                    "prompt": prompt,
                    "output_format": "png",
                }
                if style:
                    v2beta_payload["style_preset"] = style
                # Prefer image bytes back
                v2_resp = await client.post(
                    "/v2beta/stable-image/generate/core",
                    json=v2beta_payload,
                    headers={"Accept": "image/*"},
                )
                if v2_resp.status_code == 429:
                    raise ImageError("Rate limited by Stability API")
                v2_resp.raise_for_status()
                content_type = v2_resp.headers.get("Content-Type", "")
                if content_type.startswith("image/"):
                    os.makedirs(os.path.join(settings.STATIC_DIR, settings.STATIC_IMAGES_SUBDIR), exist_ok=True)
                    filename = f"{uuid.uuid4()}.png"
                    local_path = os.path.join(settings.STATIC_DIR, settings.STATIC_IMAGES_SUBDIR, filename)
                    with open(local_path, "wb") as f:
                        f.write(v2_resp.content)
                    public_url = f"{settings.PUBLIC_BASE_URL}{settings.STATIC_URL_PATH}/{settings.STATIC_IMAGES_SUBDIR}/{filename}"
                    meta = ImageMeta(url=public_url, alt_text=slide.title, provider="stability-ai")
                    _cache_set(prompt, meta)
                    return meta
                # If JSON shape, attempt to parse minimal url
                try:
                    data_json = v2_resp.json()
                    data = StabilityGenerationResponse(**data_json)
                    url = (data.url or '').rstrip('/')
                    if url:
                        meta = ImageMeta(url=url, alt_text=slide.title, provider="stability-ai")
                        _cache_set(prompt, meta)
                        return meta
                except Exception:
                    pass
                # Fall through to placeholder
                return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
            # Legacy json path success
            resp.raise_for_status()
            data = StabilityGenerationResponse(**resp.json())
            url = (data.url or '').rstrip('/')
            if not url:
                return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
            meta = ImageMeta(url=url, alt_text=slide.title, provider="stability-ai")
            _cache_set(prompt, meta)
            return meta
        except httpx.HTTPError as e:
            # Fallback to placeholder on client/server errors during live calls
            return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
        except Exception as e:
            raise ImageError(f"Image request failed: {str(e)}") from e

async def generate_images(slides: List[SlidePlan], style: Optional[str] = None) -> List[ImageMeta]:
    sem = asyncio.Semaphore(settings.IMAGE_MAX_CONCURRENCY)

    async def _one(s: SlidePlan) -> ImageMeta:
        async with sem:
            try:
                return await generate_image_for_slide(s, style)
            except ImageError:
                return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=s.title, provider="placeholder")

    tasks = [asyncio.create_task(_one(s)) for s in slides]
    results = await asyncio.gather(*tasks)
    return results