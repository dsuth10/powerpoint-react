from fastapi import APIRouter, HTTPException
from app.models.slides import SlidePlan
from app.models.common import PPTXJob
from uuid import uuid4
from typing import List

router = APIRouter(prefix="/slides", tags=["slides"])

@router.post("/build", response_model=PPTXJob)
async def build_slides(slides: List[SlidePlan]):
    # In production, enqueue job and emit progress via WS. Here, mock job creation.
    job_id = str(uuid4())
    return PPTXJob(job_id=job_id, status="pending", download_url=None, error=None) 