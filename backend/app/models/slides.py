from __future__ import annotations

from typing import List, Optional

from pydantic import AnyUrl, Field, constr, field_validator

from app.models.base import BaseModel


class ImageMeta(BaseModel):
    """Metadata for an image to be included in a slide."""

    url: AnyUrl = Field(..., description="The image URL.")
    alt_text: constr(min_length=1) = Field(
        ..., alias="altText", description="Alt text for accessibility."
    )
    provider: constr(min_length=1) = Field(
        ..., description="Image provider name (e.g., 'runware')."
    )


class SlidePlan(BaseModel):
    """Plan for a single slide in the generated presentation."""

    title: constr(min_length=1, max_length=100) = Field(..., description="Slide title.")
    bullets: List[constr(min_length=1, max_length=200)] = Field(
        ..., description="Bullet points for the slide."
    )
    image: Optional[ImageMeta] = Field(None, description="Optional image metadata.")
    notes: Optional[str] = Field(None, description="Optional speaker notes.")

    @field_validator("bullets")
    @classmethod
    def validate_bullets_not_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("bullets must contain at least one item")
        return v