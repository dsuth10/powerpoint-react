import logging
from typing import Optional
from app.models.slides import SlidePlan, ImageMeta
from app.services.images import generate_image_for_slide
from app.services.text_editing import TextEditingService

logger = logging.getLogger(__name__)

class ImageEditingError(Exception):
    """Custom exception for image editing errors."""
    pass

class ImageEditingService:
    """Service for editing slide images."""
    
    def __init__(self):
        self.text_service = TextEditingService()
    
    async def edit_slide_image(
        self, 
        slide: SlidePlan, 
        image_prompt: str, 
        provider: Optional[str] = None
    ) -> ImageMeta:
        """Replace slide image with AI-generated content."""
        try:
            # Create a temporary slide with the new image prompt
            temp_slide = SlidePlan(
                title=slide.title,
                bullets=slide.bullets,
                notes=slide.notes
            )
            
            # Generate new image using existing image service
            new_image = await generate_image_for_slide(
                slide=temp_slide,
                style=image_prompt,  # Use prompt as style
                provider=provider
            )
            
            logger.info(f"Generated new image for slide '{slide.title}': {new_image}")
            return new_image
            
        except Exception as e:
            logger.error(f"Image editing failed for slide '{slide.title}': {e}")
            raise ImageEditingError(f"Failed to edit image: {str(e)}")
