from __future__ import annotations

from typing import List, Optional
from uuid import uuid4, UUID

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse

from app.models.common import PPTXJob
from app.models.slides import SlidePlan, ImageMeta, PowerPointRequest, PowerPointResponse
from app.core.rate_limit import rate_limit_dependency
from app.core.config import settings
from app.services import pptx as pptx_service
from app.socketio_app import emit_progress, emit_completed
from app.services.images import generate_images
from app.services.pptx import build_pptx
from app.services.image_providers.registry import get_provider_status, list_providers, get_available_providers
from app.core.auth import get_current_user

router = APIRouter(prefix="/slides", tags=["slides"])

@router.get("/providers", response_model=dict)
async def get_image_providers():
    """Get available image providers and their status."""
    try:
        status = get_provider_status()
        available = get_available_providers()
        
        return {
            "providers": status,
            "available": list(available.keys()),
            "all_registered": list_providers()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get providers: {str(e)}")

@router.post("/generate", response_model=PowerPointResponse)
async def generate_powerpoint(
    request: PowerPointRequest,
    provider: Optional[str] = Query(None, description="Image provider to use (stability-ai, dalle)"),
    current_user: str = Depends(get_current_user)
):
    """Generate a PowerPoint presentation with images."""
    try:
        # Generate images for slides
        images = await generate_images(request.slides, request.style, provider)
        
        # Update slides with generated images
        slides_with_images = []
        for i, slide in enumerate(request.slides):
            slide_with_image = slide.model_copy()
            if i < len(images):
                slide_with_image.image = images[i]
            slides_with_images.append(slide_with_image)
        
        # Create PowerPoint
        pptx_path = build_pptx(slides_with_images)
        
        # Read the file data
        with open(pptx_path, 'rb') as f:
            pptx_data = f.read()
        
        return PowerPointResponse(
            pptx_data=pptx_data,
            images=images,
            title=request.title
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PowerPoint: {str(e)}")

@router.post("/generate-images", response_model=List[ImageMeta])
async def generate_slide_images(
    slides: List[SlidePlan],
    style: Optional[str] = Query(None, description="Image style"),
    provider: Optional[str] = Query(None, description="Image provider to use (stability-ai, dalle)"),
    current_user: str = Depends(get_current_user)
):
    """Generate images for slides only."""
    try:
        images = await generate_images(slides, style, provider)
        return images
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate images: {str(e)}")

@router.post("/build", response_model=PPTXJob)
async def build_slides(
    payload: List[SlidePlan],
    session_id: Optional[str] = None,
    current_user: str = Depends(get_current_user),
    _: None = Depends(rate_limit_dependency),
) -> PPTXJob:
    """
    Build a PowerPoint presentation from slide plans.
    Returns a job ID for tracking progress.
    """
    job_id = str(uuid4())
    
    # Store job info for progress tracking
    pptx_service.jobs[job_id] = {
        "status": "pending",
        "progress": 0,
        "total": len(payload),
        "session_id": session_id,
    }
    
    # Start async processing
    pptx_service.process_slides_async(job_id, payload, session_id)
    
    return PPTXJob(
        job_id=job_id,
        status="pending",
        message="Building PowerPoint presentation...",
    )


@router.get("/download/{job_id}")
async def download_pptx(
    job_id: UUID,
    current_user: str = Depends(get_current_user),
) -> FileResponse:
    """
    Download a completed PowerPoint presentation.
    """
    job_info = pptx_service.jobs.get(str(job_id))
    if not job_info:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_info["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    file_path = job_info.get("file_path")
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"presentation-{job_id}.pptx",
    )