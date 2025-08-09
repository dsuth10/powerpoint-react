from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from app.models.base import BaseModel


class ErrorResponse(BaseModel):
    error_code: str = Field(..., alias="errorCode", description="Application error code.")
    message: str = Field(..., description="Human-readable error message.")
    details: Optional[dict[str, Any]] = Field(
        default=None, description="Optional contextual details."
    )

