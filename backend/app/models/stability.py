from __future__ import annotations

from typing import Optional, List

from pydantic import Field, ConfigDict, BaseModel as PydanticBaseModel


class TextPrompt(PydanticBaseModel):
    """A text prompt for image generation."""
    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        from_attributes=True,
        # No alias generation - use snake_case directly
        alias_generator=None,
    )
    
    text: str
    weight: float = Field(default=1.0, ge=-10.0, le=10.0)


class StabilityGenerationRequest(PydanticBaseModel):
    """Request model for Stability AI text-to-image generation."""
    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        from_attributes=True,
        # No alias generation - use snake_case directly
        alias_generator=None,
    )
    
    text_prompts: List[TextPrompt]
    cfg_scale: float = Field(default=7.0, ge=0.0, le=35.0)
    height: int = Field(default=1024, ge=128, le=1536)
    width: int = Field(default=1024, ge=128, le=1536)
    samples: int = Field(default=1, ge=1, le=10)
    steps: int = Field(default=30, ge=10, le=150)
    style_preset: Optional[str] = Field(default=None)
    sampler: Optional[str] = Field(default="K_DPM_2_ANCESTRAL")
    seed: Optional[int] = Field(default=0, ge=0, le=4294967295)
    extras: Optional[dict] = Field(default=None)


class ImageArtifact(PydanticBaseModel):
    """A generated image artifact."""
    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        from_attributes=True,
        # No alias generation - use snake_case directly
        alias_generator=None,
    )
    
    base64: str
    seed: int
    finishReason: str


class StabilityGenerationResponse(PydanticBaseModel):
    """Response model for Stability AI text-to-image generation."""
    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        from_attributes=True,
        # No alias generation - use snake_case directly
        alias_generator=None,
    )
    
    artifacts: List[ImageArtifact]


# Legacy models for backward compatibility (deprecated)
from app.models.base import BaseModel

class LegacyStabilityGenerationRequest(BaseModel):
    """Legacy request model - deprecated."""
    prompt: str
    output_format: str = Field(default="png")
    style_preset: Optional[str] = Field(default=None, alias="stylePreset")


class LegacyStabilityGenerationResponse(BaseModel):
    """Legacy response model - deprecated."""
    url: str

