from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import AnyUrl, Field

from app.models.base import BaseModel


class PPTXJob(BaseModel):
    """Model representing a PPTX build job."""

    job_id: UUID = Field(..., alias="jobId", description="Unique job identifier.")
    status: Literal["pending", "in_progress", "completed", "failed"] = Field(
        ..., description="Job status."
    )
    result_url: Optional[AnyUrl] = Field(
        None, alias="resultUrl", description="URL to download the generated PPTX file."
    )
    error_message: Optional[str] = Field(
        None, alias="errorMessage", description="Error message if the job failed."
    )