"""
OpenAI DALL-E image provider implementation.
"""
import httpx
import logging
import base64
import os
import uuid
import time
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random
from app.core.config import settings
from app.models.slides import SlidePlan, ImageMeta
from . import ImageProvider

logger = logging.getLogger(__name__)

class DalleProvider(ImageProvider):
    """OpenAI DALL-E image generation provider."""
    
    def __init__(self):
        self.base_url = settings.OPENAI_BASE_URL
        self.timeout = settings.OPENAI_TIMEOUT_SECONDS
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_DALLE_MODEL
        self._cache = {}
    
    def get_provider_name(self) -> str:
        return "dalle"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _build_prompt(self, slide: SlidePlan, style: Optional[str] = None) -> str:
        """Build a prompt for DALL-E image generation."""
        bullets = "; ".join(slide.bullets)
        base = f"Create a professional, business-appropriate image for a PowerPoint slide titled '{slide.title}' with the following content: {bullets}"
        
        if style:
            base += f" Style: {style}."
        
        # Add DALL-E specific instructions
        base += " The image should be clean, modern, and suitable for a business presentation. Avoid text or words in the image."
        
        # Basic normalization for cache keys
        prompt = " ".join(base.split()).strip().lower()
        logger.info(f"Built DALL-E prompt for slide '{slide.title}': {prompt}")
        return prompt
    
    def _build_payload(self, prompt: str) -> dict:
        """Build the request payload for DALL-E API."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "standard",
            "response_format": "b64_json"
        }
        logger.info(f"Built DALL-E payload: {payload}")
        return payload
    
    def _save_image(self, base64_data: str, slide_title: str) -> str:
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
            
            logger.info(f"Saved DALL-E image for slide '{slide_title}' to {local_path}")
            return public_url
            
        except Exception as e:
            logger.error(f"Error saving DALL-E image for slide '{slide_title}': {e}")
            raise
    
    def _cache_get(self, key: str) -> Optional[ImageMeta]:
        entry = self._cache.get(key)
        if not entry:
            return None
        ts, value = entry
        if time.time() - ts > settings.IMAGE_CACHE_TTL_SECONDS:
            self._cache.pop(key, None)
            return None
        logger.info(f"DALL-E cache hit for key: {key}")
        return value
    
    def _cache_set(self, key: str, value: ImageMeta) -> None:
        if len(self._cache) >= settings.IMAGE_CACHE_MAX_ENTRIES:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
            self._cache.pop(oldest_key, None)
        self._cache[key] = (time.time(), value)
        logger.info(f"Cached DALL-E image for key: {key}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10) + wait_random(0, 1),
    )
    async def generate_image(self, slide: SlidePlan, style: Optional[str] = None) -> ImageMeta:
        """Generate an image for a slide using DALL-E."""
        logger.info(f"DALL-E: Generating image for slide: {slide.title}")
        
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._get_headers(),
        ) as client:
            try:
                prompt = self._build_prompt(slide, style)
                
                # Cache lookup
                cached = self._cache_get(prompt)
                if cached:
                    logger.info(f"DALL-E: Returning cached image for slide '{slide.title}'")
                    return cached
                
                payload = self._build_payload(prompt)
                endpoint = "/v1/images/generations"
                
                logger.info(f"DALL-E: Sending request to endpoint: {endpoint}")
                response = await client.post(endpoint, json=payload)
                
                logger.info(f"DALL-E: Response status: {response.status_code}")
                
                if response.status_code == 429:
                    logger.warning("DALL-E: Rate limited - returning placeholder")
                    return ImageMeta(url=settings.DALLE_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
                
                if response.status_code == 400:
                    logger.error(f"DALL-E: Bad request. Response: {response.text}")
                    return ImageMeta(url=settings.DALLE_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
                
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                if not data.get("data"):
                    logger.warning(f"DALL-E: No data for slide '{slide.title}'")
                    return ImageMeta(url=settings.DALLE_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
                
                image_data = data["data"][0]
                
                if "b64_json" not in image_data:
                    logger.warning(f"DALL-E: No b64_json for slide '{slide.title}'")
                    return ImageMeta(url=settings.DALLE_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
                
                # Save the image
                public_url = self._save_image(image_data["b64_json"], slide.title)
                
                # Create metadata
                meta = ImageMeta(
                    url=public_url,
                    alt_text=slide.title,
                    provider="dalle"
                )
                
                # Cache the result
                self._cache_set(prompt, meta)
                
                logger.info(f"DALL-E: Generated image for slide '{slide.title}': {meta}")
                return meta
                
            except httpx.HTTPError as e:
                logger.error(f"DALL-E: HTTP error for slide '{slide.title}': {e}")
                return ImageMeta(url=settings.DALLE_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
            except Exception as e:
                logger.error(f"DALL-E: Exception for slide '{slide.title}': {e}")
                return ImageMeta(url=settings.DALLE_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")

