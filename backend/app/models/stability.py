from __future__ import annotations

from typing import Optional

from pydantic import Field

from app.models.base import BaseModel


class StabilityGenerationRequest(BaseModel):
    prompt: str
    output_format: str = Field(default="png")
    style_preset: Optional[str] = Field(default=None, alias="stylePreset")


class StabilityGenerationResponse(BaseModel):
    # Minimal shape assuming URL returned by our gateway/endpoint
    url: str

