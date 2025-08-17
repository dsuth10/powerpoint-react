import logging
import asyncio
from typing import List, Optional
from app.core.config import settings
from app.models.slides import SlidePlan, ImageMeta
from .image_providers.registry import register_providers, get_best_available_provider

# Set up logging
logger = logging.getLogger(__name__)

# Register providers on module import
register_providers()

async def generate_image_for_slide(slide: SlidePlan, style: Optional[str] = None, provider: Optional[str] = None) -> ImageMeta:
    """Generate an image for a slide using the best available provider."""
    logger.info(f"Generating image for slide: {slide.title}")
    
    # Get the best available provider
    image_provider = get_best_available_provider(provider)
    
    if not image_provider:
        logger.warning("No image providers available, returning placeholder")
        return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")
    
    try:
        logger.info(f"Using provider: {image_provider.get_provider_name()}")
        result = await image_provider.generate_image(slide, style)
        logger.info(f"Generated image for slide '{slide.title}': {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating image for slide '{slide.title}': {e}")
        return ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder")

async def generate_images(slides: List[SlidePlan], style: Optional[str] = None, provider: Optional[str] = None) -> List[ImageMeta]:
    """Generate images for multiple slides concurrently."""
    logger.info(f"Generating images for {len(slides)} slides")
    
    # Get the best available provider
    image_provider = get_best_available_provider(provider)
    
    if not image_provider:
        logger.warning("No image providers available, returning placeholders")
        return [ImageMeta(url=settings.STABILITY_PLACEHOLDER_URL, alt_text=slide.title, provider="placeholder") for slide in slides]
    
    # Reduce concurrency to avoid rate limiting
    sem = asyncio.Semaphore(min(settings.IMAGE_MAX_CONCURRENCY, 2))
    logger.info(f"Using semaphore with max concurrency: {min(settings.IMAGE_MAX_CONCURRENCY, 2)}")

    async def _one(s: SlidePlan) -> ImageMeta:
        async with sem:
            try:
                logger.info(f"Starting image generation for slide: {s.title}")
                result = await image_provider.generate_image(s, style)
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