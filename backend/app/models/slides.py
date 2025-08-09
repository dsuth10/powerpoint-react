from pydantic import BaseModel, Field
from typing import List, Optional

class ImageMeta(BaseModel):
    """
    Metadata for an image to be included in a slide.

    Attributes:
        url (str): The image URL.
        alt (str): Alt text for accessibility.
        provider (str): Image provider name (e.g., 'runware').
    """
    url: str = Field(..., description="The image URL.")
    alt: str = Field(..., description="Alt text for accessibility.")
    provider: str = Field(..., description="Image provider name (e.g., 'runware').")

    model_config = {"strict": True, "populate_by_name": True}

class SlidePlan(BaseModel):
    """
    Plan for a single slide in the generated presentation.

    Attributes:
        title (str): Slide title.
        body (str): Main slide content.
        image (Optional[ImageMeta]): Optional image metadata.
        notes (Optional[str]): Optional speaker notes.
    """
    title: str = Field(..., description="Slide title.")
    body: str = Field(..., description="Main slide content.")
    image: Optional[ImageMeta] = Field(None, description="Optional image metadata.")
    notes: Optional[str] = Field(None, description="Optional speaker notes.")

    model_config = {"strict": True, "populate_by_name": True} 