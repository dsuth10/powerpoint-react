from __future__ import annotations

from typing import List
from uuid import uuid4, UUID

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from pathlib import Path

from app.models.common import PPTXJob
from app.models.slides import SlidePlan
from app.core.rate_limit import rate_limit_dependency
from app.core.config import settings

router = APIRouter(prefix="/slides", tags=["slides"])

@router.post(
    "/build",
    response_model=PPTXJob,
    responses={429: {"description": "Too Many Requests"}, 422: {"description": "Validation Error"}},
)
async def build_slides(slides: List[dict], _: None = Depends(rate_limit_dependency)):
    # In production, enqueue job and emit progress via WS. Here, mock job creation.
    # Normalize legacy shape where 'body' was a string instead of 'bullets' list
    normalized: List[SlidePlan] = []
    for s in slides:
        if "bullets" not in s and isinstance(s.get("body"), str):
            s = {**s, "bullets": [s.get("body")]}
            s.pop("body", None)
        normalized.append(SlidePlan(**s))

    job_id = UUID(str(uuid4()))
    return PPTXJob(job_id=job_id, status="pending", result_url=None, error_message=None)


@router.get(
    "/download",
    responses={404: {"description": "File Not Found"}},
)
def download_pptx(job_id: UUID = Query(..., alias="jobId")):
    """
    Serve a generated PPTX file by job ID.

    Looks for a file named "{jobId}.pptx" in the configured temporary directory.
    Returns 404 if the file does not exist.
    """
    file_path = Path(settings.PPTX_TEMP_DIR) / f"{job_id}.pptx"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"presentation-{job_id}.pptx",
    )