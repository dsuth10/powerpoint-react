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
from app.services import pptx as pptx_service

router = APIRouter(prefix="/slides", tags=["slides"])

@router.post(
    "/build",
    response_model=PPTXJob,
    responses={429: {"description": "Too Many Requests"}, 422: {"description": "Validation Error"}},
)
async def build_slides(slides: List[dict], _: None = Depends(rate_limit_dependency)):
    # Normalize legacy shape where 'body' was a string instead of 'bullets' list
    normalized: List[SlidePlan] = []
    for s in slides:
        if "bullets" not in s and isinstance(s.get("body"), str):
            s = {**s, "bullets": [s.get("body")]}
            s.pop("body", None)
        # Normalize image: accept string URL or incomplete dict and coerce to ImageMeta shape
        if "image" in s and s["image"] is not None:
            img = s["image"]
            try:
                if isinstance(img, str):
                    s["image"] = {
                        "url": img,
                        "altText": s.get("title") or "image",
                        "provider": "llm",
                    }
                elif isinstance(img, dict):
                    url = img.get("url")
                    if isinstance(url, str):
                        if not img.get("altText"):
                            img["altText"] = s.get("title") or "image"
                        if not img.get("provider"):
                            img["provider"] = "llm"
                        s["image"] = img
                    else:
                        # Invalid image payload; drop it to avoid validation errors
                        s.pop("image", None)
            except Exception:
                # If anything goes wrong during normalization, drop image to avoid breaking the build
                s.pop("image", None)
        normalized.append(SlidePlan(**s))

    # Synchronously build PPTX and return completed job with download URL
    built_path = pptx_service.build_pptx(normalized, output_dir=settings.PPTX_TEMP_DIR)
    # Rename to a fixed UUID-based name that matches download API contract
    job_id = UUID(str(uuid4()))
    target_path = (Path(settings.PPTX_TEMP_DIR) / f"{job_id}.pptx")
    try:
        Path(built_path).replace(target_path)
    except Exception:
        # If rename fails, keep original file and attempt to parse UUID from it
        try:
            job_id = UUID(Path(built_path).stem)
        except Exception:
            pass
    result_url = f"{settings.PUBLIC_BASE_URL}/api/v1/slides/download?jobId={job_id}"
    return PPTXJob(job_id=job_id, status="completed", result_url=result_url, error_message=None)


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