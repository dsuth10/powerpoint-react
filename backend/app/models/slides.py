from __future__ import annotations

from typing import List, Optional
from urllib.parse import urlsplit, urlunsplit

from pydantic import AnyUrl, Field, constr, field_validator, AliasChoices

from app.models.base import BaseModel


class ImageMeta(BaseModel):
    """Metadata for an image to be included in a slide."""

    url: constr(min_length=1) = Field(..., description="The image URL.")

    @field_validator("url")
    @classmethod
    def validate_and_normalize_url(cls, v: str) -> str:
        parts = urlsplit(v)
        if parts.scheme not in {"http", "https"}:
            raise ValueError("url must have http or https scheme")
        if not parts.netloc:
            raise ValueError("url must include a host")
        # Remove trailing slash from path only when path is empty or '/'
        path = parts.path or ""
        if path == "/":
            path = ""
        normalized = urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))
        return normalized
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