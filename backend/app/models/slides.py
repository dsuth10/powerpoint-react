from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator, HttpUrl, constr
from pydantic import AliasChoices

from .base import BaseModel as BaseModelWithConfig

class ImageMeta(BaseModelWithConfig):
    """Metadata for a generated image."""

    url: HttpUrl = Field(..., description="Image URL.")
    alt_text: str = Field(..., alias="altText", description="Alt text for the image.")
    provider: str = Field(
        ..., description="Image provider name (e.g., 'runware')."
    )


class SlidePlan(BaseModelWithConfig):
    """Plan for a single slide in the generated presentation."""

    title: constr(min_length=1, max_length=100) = Field(..., description="Slide title.")
    bullets: List[constr(min_length=1, max_length=200)] = Field(
        ..., description="Bullet points for the slide.", validation_alias=AliasChoices("bullets", "body")
    )
    image: Optional[ImageMeta] = Field(None, description="Optional image metadata.")
    notes: Optional[str] = Field(None, description="Optional speaker notes.")

    @field_validator("bullets")
    @classmethod
    def validate_bullets_not_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("bullets must contain at least one item")
        return v


class PowerPointRequest(BaseModelWithConfig):
    """Request model for PowerPoint generation."""

    slides: List[SlidePlan] = Field(..., description="Slides to include in the presentation.")
    title: str = Field(..., description="Presentation title.")
    style: Optional[str] = Field(None, description="Image style for the presentation.")


class PowerPointResponse(BaseModelWithConfig):
    """Response model for PowerPoint generation."""

    pptx_data: bytes = Field(..., description="PowerPoint file data.")
    images: List[ImageMeta] = Field(..., description="Generated images.")
    title: str = Field(..., description="Presentation title.")


class EditTarget(str, Enum):
    """Types of content that can be edited on a slide."""
    TITLE = "title"
    BULLET = "bullet"
    NOTES = "notes"
    IMAGE = "image"


class EditSlideRequest(BaseModelWithConfig):
    """Request model for editing slide content."""
    
    slide_index: int = Field(..., ge=0, description="Zero-based index of the slide to edit")
    target: EditTarget = Field(..., description="Type of content to edit")
    content: str = Field(..., min_length=1, max_length=1000, description="New content or prompt for AI generation")
    bullet_index: Optional[int] = Field(None, ge=0, description="Index of specific bullet point (required for bullet edits)")
    image_prompt: Optional[str] = Field(None, description="Prompt for new image generation (for image edits)")
    provider: Optional[str] = Field(None, description="Image provider preference (dalle, stability-ai)")
    
    @model_validator(mode='after')
    def validate_target_requirements(self) -> 'EditSlideRequest':
        """Validate that required fields are present based on target type."""
        if self.target == EditTarget.BULLET and self.bullet_index is None:
            raise ValueError("bullet_index is required when editing bullet points")
        elif self.target == EditTarget.IMAGE and not self.image_prompt:
            raise ValueError("image_prompt is required when editing images")
        return self


class EditSlideResponse(BaseModelWithConfig):
    """Response model for slide editing operations."""
    
    success: bool = Field(..., description="Whether the edit was successful")
    slide_index: int = Field(..., description="Index of the edited slide")
    target: EditTarget = Field(..., description="Type of content that was edited")
    updated_slide: SlidePlan = Field(..., description="Updated slide with new content")
    message: str = Field(..., description="Success or error message")
    image_meta: Optional[ImageMeta] = Field(None, description="New image metadata (for image edits)")


class BatchEditRequest(BaseModelWithConfig):
    """Request model for editing multiple slides at once."""
    
    edits: List[EditSlideRequest] = Field(..., min_items=1, max_items=10, description="List of edits to apply")
    
    @field_validator("edits")
    @classmethod
    def validate_unique_slide_targets(cls, v: List[EditSlideRequest]) -> List[EditSlideRequest]:
        """Ensure no duplicate slide-target combinations."""
        seen = set()
        for edit in v:
            key = (edit.slide_index, edit.target, edit.bullet_index)
            if key in seen:
                raise ValueError(f"Duplicate edit for slide {edit.slide_index}, target {edit.target}")
            seen.add(key)
        return v


class BatchEditResponse(BaseModelWithConfig):
    """Response model for batch editing operations."""
    
    success: bool = Field(..., description="Whether all edits were successful")
    results: List[EditSlideResponse] = Field(..., description="Results for each edit operation")
    errors: List[str] = Field(default_factory=list, description="Any errors that occurred")