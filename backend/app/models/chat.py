from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import Field, conint, constr

from app.models.base import BaseModel
from app.models.slides import SlidePlan


class ChatRequest(BaseModel):
    """Request model for chat-based outline generation."""

    prompt: constr(min_length=1) = Field(
        ..., description="The user prompt for slide outline generation."
    )
    slide_count: conint(ge=1, le=20) = Field(
        ..., description="Desired number of slides (1-20)."
    )
    model: constr(min_length=1) = Field(
        ..., description="LLM model identifier (e.g., 'openrouter/gpt-4o-mini')."
    )
    language: Optional[constr(min_length=2, max_length=5)] = Field(
        None, description="ISO 639-1 language code (e.g., 'en')."
    )
    context: Optional[str] = Field(
        None, description="Optional context/background for the presentation."
    )


class ChatResponse(BaseModel):
    """Response model for chat-based outline generation."""

    slides: List[SlidePlan] = Field(..., description="Generated slide plans.")
    session_id: Optional[UUID] = Field(
        None, alias="sessionId", description="Optional session identifier."
    )