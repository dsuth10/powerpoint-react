from __future__ import annotations

from typing import List, Optional
from uuid import uuid4, UUID

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import FileResponse

from app.models.common import PPTXJob
from app.models.slides import (
    SlidePlan, ImageMeta, PowerPointRequest, PowerPointResponse,
    EditSlideRequest, EditSlideResponse, BatchEditRequest, BatchEditResponse, EditTarget
)
from app.core.rate_limit import rate_limit_dependency
from app.core.config import settings
from app.services import pptx as pptx_service
from app.services.images import generate_images
from app.services.pptx import build_pptx
from app.services.image_providers.registry import get_provider_status, list_providers, get_available_providers
from app.services.text_editing import TextEditingService, TextEditingError
from app.services.image_editing import ImageEditingService, ImageEditingError
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
        job_id=UUID(job_id),
        status="pending",
        message="Building PowerPoint presentation...",
    )


@router.get("/job/{job_id}")
async def get_job_status(
    job_id: UUID,
    current_user: str = Depends(get_current_user),
) -> dict:
    """
    Get the status of a PowerPoint generation job.
    """
    job_info = pptx_service.jobs.get(str(job_id))
    if not job_info:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": str(job_id),
        "status": job_info["status"],
        "progress": job_info.get("progress", 0),
        "total": job_info.get("total", 1),
        "message": job_info.get("message", ""),
        "error": job_info.get("error"),
        "file_path": job_info.get("file_path"),
    }


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

@router.post("/edit", response_model=EditSlideResponse)
async def edit_slide_content(
    request: EditSlideRequest,
    slides: List[SlidePlan] = Body(..., description="Current slides to edit"),
    current_user: str = Depends(get_current_user),
    _: None = Depends(rate_limit_dependency),
) -> EditSlideResponse:
    """
    Edit a specific piece of content on a slide.
    Supports editing titles, bullet points, notes, and images.
    """
    try:
        # Validate slide index
        if request.slide_index >= len(slides):
            raise HTTPException(
                status_code=400, 
                detail=f"Slide index {request.slide_index} is out of range (0-{len(slides)-1})"
            )
        
        slide = slides[request.slide_index]
        updated_slide = slide.model_copy()
        
        # Handle different edit types
        if request.target == EditTarget.TITLE:
            text_service = TextEditingService()
            new_title = await text_service.edit_slide_title(slide, request.content)
            updated_slide.title = new_title
            
        elif request.target == EditTarget.BULLET:
            if request.bullet_index is None:
                raise HTTPException(status_code=400, detail="bullet_index is required for bullet edits")
            
            if request.bullet_index >= len(slide.bullets):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Bullet index {request.bullet_index} is out of range (0-{len(slide.bullets)-1})"
                )
            
            text_service = TextEditingService()
            new_bullets = await text_service.edit_slide_bullet(slide, request.bullet_index, request.content)
            updated_slide.bullets = new_bullets
            
        elif request.target == EditTarget.NOTES:
            text_service = TextEditingService()
            new_notes = await text_service.edit_slide_notes(slide, request.content)
            updated_slide.notes = new_notes
            
        elif request.target == EditTarget.IMAGE:
            if not request.image_prompt:
                raise HTTPException(status_code=400, detail="image_prompt is required for image edits")
            
            image_service = ImageEditingService()
            new_image = await image_service.edit_slide_image(
                slide, 
                request.image_prompt, 
                request.provider
            )
            updated_slide.image = new_image
        
        return EditSlideResponse(
            success=True,
            slide_index=request.slide_index,
            target=request.target,
            updated_slide=updated_slide,
            message=f"Successfully edited {request.target.value} on slide {request.slide_index + 1}",
            image_meta=updated_slide.image if request.target == EditTarget.IMAGE else None
        )
        
    except (TextEditingError, ImageEditingError) as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in edit_slide_content: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/edit-batch", response_model=BatchEditResponse)
async def edit_multiple_slides(
    request: BatchEditRequest,
    slides: List[SlidePlan] = Body(..., description="Current slides to edit"),
    current_user: str = Depends(get_current_user),
    _: None = Depends(rate_limit_dependency),
) -> BatchEditResponse:
    """
    Edit multiple slides in a single request.
    More efficient than multiple single edit requests.
    """
    results = []
    errors = []
    
    for edit_request in request.edits:
        try:
            # Validate slide index
            if edit_request.slide_index >= len(slides):
                errors.append(f"Slide index {edit_request.slide_index} is out of range")
                continue
            
            # Create single edit request and reuse logic
            single_response = await edit_slide_content(
                request=edit_request,
                slides=slides,
                current_user=current_user
            )
            results.append(single_response)
            
        except HTTPException as e:
            errors.append(f"Edit failed for slide {edit_request.slide_index}: {e.detail}")
        except Exception as e:
            errors.append(f"Unexpected error for slide {edit_request.slide_index}: {str(e)}")
    
    success = len(errors) == 0
    return BatchEditResponse(
        success=success,
        results=results,
        errors=errors
    )

@router.post("/edit-preview", response_model=EditSlideResponse)
async def preview_slide_edit(
    request: EditSlideRequest,
    slides: List[SlidePlan] = Body(..., description="Current slides to preview edit"),
    current_user: str = Depends(get_current_user),
) -> EditSlideResponse:
    """
    Preview an edit without applying it.
    Useful for showing users what the edit would look like.
    """
    # Same logic as edit_slide_content but with preview flag
    # This allows frontend to show preview before committing
    return await edit_slide_content(request, slides, current_user)