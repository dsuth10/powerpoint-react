from pydantic import BaseModel, Field
from typing import Optional

class PPTXJob(BaseModel):
    """
    Model representing a PPTX build job.

    Attributes:
        job_id (str): Unique job identifier (UUID).
        status (str): Job status (e.g., 'pending', 'in_progress', 'completed', 'failed').
        download_url (Optional[str]): URL to download the generated PPTX file.
        error (Optional[str]): Error message if the job failed.
    """
    job_id: str = Field(..., alias="jobId", description="Unique job identifier (UUID).")
    status: str = Field(..., description="Job status (e.g., 'pending', 'in_progress', 'completed', 'failed').")
    download_url: Optional[str] = Field(None, alias="downloadUrl", description="URL to download the generated PPTX file.")
    error: Optional[str] = Field(None, description="Error message if the job failed.")

    model_config = {"strict": True, "populate_by_name": True} 