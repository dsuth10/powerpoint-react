# Slide Editing Implementation Plan

**Date:** January 2025  
**Status:** Planning Phase  
**Priority:** High  
**Dependencies:** Task 4 (LLM Service), Task 5 (Image Generation)

## Overview

This plan implements AI-assisted inline editing capabilities for PowerPoint slides, allowing users to edit titles, bullet points, notes, and images through dedicated API endpoints. The implementation leverages the existing FastAPI architecture, Pydantic v2 models, LLM service, and image generation system.

## Architecture Alignment

The implementation follows the established patterns in the codebase:
- **FastAPI** with Pydantic v2 models and strict validation
- **Existing LLM service** for AI-assisted text editing
- **Multi-provider image system** for image replacement
- **Rate limiting** and authentication integration
- **Async processing** with proper error handling
- **Comprehensive testing** with pytest and coverage requirements

## 1. Edit Models (`backend/app/models/slides.py`)

### 1.1 EditSlideRequest Model

```python
from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator

class EditTarget(str, Enum):
    """Types of content that can be edited on a slide."""
    TITLE = "title"
    BULLET = "bullet"
    NOTES = "notes"
    IMAGE = "image"

class EditSlideRequest(BaseModel):
    """Request model for editing slide content."""
    
    slide_index: int = Field(..., ge=0, description="Zero-based index of the slide to edit")
    target: EditTarget = Field(..., description="Type of content to edit")
    content: str = Field(..., min_length=1, max_length=1000, description="New content or prompt for AI generation")
    bullet_index: Optional[int] = Field(None, ge=0, description="Index of specific bullet point (required for bullet edits)")
    image_prompt: Optional[str] = Field(None, description="Prompt for new image generation (for image edits)")
    provider: Optional[str] = Field(None, description="Image provider preference (dalle, stability-ai)")
    
    @field_validator("bullet_index")
    @classmethod
    def validate_bullet_index_for_bullet_target(cls, v: Optional[int], info) -> Optional[int]:
        if info.data.get("target") == EditTarget.BULLET and v is None:
            raise ValueError("bullet_index is required when editing bullet points")
        return v
    
    @field_validator("image_prompt")
    @classmethod
    def validate_image_prompt_for_image_target(cls, v: Optional[str], info) -> Optional[str]:
        if info.data.get("target") == EditTarget.IMAGE and not v:
            raise ValueError("image_prompt is required when editing images")
        return v

class EditSlideResponse(BaseModel):
    """Response model for slide editing operations."""
    
    success: bool = Field(..., description="Whether the edit was successful")
    slide_index: int = Field(..., description="Index of the edited slide")
    target: EditTarget = Field(..., description="Type of content that was edited")
    updated_slide: SlidePlan = Field(..., description="Updated slide with new content")
    message: str = Field(..., description="Success or error message")
    image_meta: Optional[ImageMeta] = Field(None, description="New image metadata (for image edits)")
```

### 1.2 Batch Edit Models

```python
class BatchEditRequest(BaseModel):
    """Request model for editing multiple slides at once."""
    
    edits: List[EditSlideRequest] = Field(..., min_items=1, max_items=10, description="List of edits to apply")
    
    @field_validator("edits")
    @classmethod
    def validate_unique_slide_targets(cls, v: List[EditSlideRequest]) -> List[EditSlideRequest]:
        """Ensure no duplicate slide-target combinations."""
        seen = set()
        for edit in v:
            key = (edit.slide_index, edit.target, edit.bullet_index)
            if key in seen:
                raise ValueError(f"Duplicate edit for slide {edit.slide_index}, target {edit.target}")
            seen.add(key)
        return v

class BatchEditResponse(BaseModel):
    """Response model for batch editing operations."""
    
    success: bool = Field(..., description="Whether all edits were successful")
    results: List[EditSlideResponse] = Field(..., description="Results for each edit operation")
    errors: List[str] = Field(default_factory=list, description="Any errors that occurred")
```

## 2. Text Editing Service (`backend/app/services/text_editing.py`)

### 2.1 Core Text Editing Service

```python
import logging
from typing import List, Optional
from app.services.llm import get_async_client
from app.models.slides import SlidePlan
from app.models.slides import EditTarget, EditSlideRequest

logger = logging.getLogger(__name__)

class TextEditingService:
    """Service for AI-assisted text editing of slide content."""
    
    def __init__(self):
        self.client = get_async_client()
    
    async def edit_slide_title(self, slide: SlidePlan, new_content: str) -> str:
        """Edit slide title using AI assistance."""
        prompt = f"""
        Edit the slide title to: "{new_content}"
        
        Current slide context:
        - Title: {slide.title}
        - Bullets: {slide.bullets}
        - Notes: {slide.notes or 'None'}
        
        Requirements:
        - Keep the title concise (max 100 characters)
        - Maintain relevance to the slide content
        - Use clear, professional language
        - Return only the new title text
        """
        
        return await self._call_llm_for_text_edit(prompt, "title")
    
    async def edit_slide_bullet(self, slide: SlidePlan, bullet_index: int, new_content: str) -> List[str]:
        """Edit a specific bullet point using AI assistance."""
        current_bullets = slide.bullets.copy()
        current_bullet = current_bullets[bullet_index] if bullet_index < len(current_bullets) else ""
        
        prompt = f"""
        Edit bullet point {bullet_index + 1} to: "{new_content}"
        
        Current slide context:
        - Title: {slide.title}
        - All bullets: {current_bullets}
        - Current bullet to edit: "{current_bullet}"
        
        Requirements:
        - Keep bullets concise (max 200 characters each)
        - Maintain consistency with other bullets
        - Use clear, actionable language
        - Return the complete updated list of bullets as JSON array
        """
        
        updated_bullets = await self._call_llm_for_text_edit(prompt, "bullets")
        return updated_bullets
    
    async def edit_slide_notes(self, slide: SlidePlan, new_content: str) -> str:
        """Edit slide notes using AI assistance."""
        prompt = f"""
        Edit the speaker notes to: "{new_content}"
        
        Current slide context:
        - Title: {slide.title}
        - Bullets: {slide.bullets}
        - Current notes: {slide.notes or 'None'}
        
        Requirements:
        - Expand on the bullet points with detailed explanations
        - Include relevant examples or data points
        - Use professional presentation language
        - Keep notes comprehensive but focused
        - Return only the new notes text
        """
        
        return await self._call_llm_for_text_edit(prompt, "notes")
    
    async def _call_llm_for_text_edit(self, prompt: str, edit_type: str) -> Union[str, List[str]]:
        """Make LLM call for text editing with proper error handling."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"You are an expert presentation editor. Edit the {edit_type} according to the user's request. Return only the edited content in the appropriate format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            payload = {
                "model": "openai/gpt-4o-mini",  # Use fast model for editing
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            async with self.client as client:
                response = await client.post("/chat/completions", json=payload)
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Parse response based on edit type
                if edit_type == "bullets":
                    return self._parse_bullets_response(content)
                else:
                    return content
                    
        except Exception as e:
            logger.error(f"LLM text editing failed: {e}")
            raise TextEditingError(f"Failed to edit {edit_type}: {str(e)}")
    
    def _parse_bullets_response(self, content: str) -> List[str]:
        """Parse LLM response for bullet points."""
        try:
            # Try to extract JSON array
            import json
            import re
            
            # Look for JSON array pattern
            json_match = re.search(r'\[.*?\]', content, re.DOTALL)
            if json_match:
                bullets = json.loads(json_match.group())
                if isinstance(bullets, list):
                    return [str(bullet) for bullet in bullets]
            
            # Fallback: split by newlines and clean up
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            return [line.lstrip('- ').lstrip('* ').lstrip('• ') for line in lines]
            
        except Exception as e:
            logger.error(f"Failed to parse bullets response: {e}")
            raise TextEditingError("Failed to parse bullet points from LLM response")

class TextEditingError(Exception):
    """Custom exception for text editing errors."""
    pass
```

## 3. Image Editing Integration (`backend/app/services/image_editing.py`)

### 3.1 Image Editing Service

```python
import logging
from typing import Optional
from app.models.slides import SlidePlan, ImageMeta
from app.services.images import generate_image_for_slide
from app.services.text_editing import TextEditingService

logger = logging.getLogger(__name__)

class ImageEditingService:
    """Service for editing slide images."""
    
    def __init__(self):
        self.text_service = TextEditingService()
    
    async def edit_slide_image(
        self, 
        slide: SlidePlan, 
        image_prompt: str, 
        provider: Optional[str] = None
    ) -> ImageMeta:
        """Replace slide image with AI-generated content."""
        try:
            # Create a temporary slide with the new image prompt
            temp_slide = SlidePlan(
                title=slide.title,
                bullets=slide.bullets,
                notes=slide.notes
            )
            
            # Generate new image using existing image service
            new_image = await generate_image_for_slide(
                slide=temp_slide,
                style=image_prompt,  # Use prompt as style
                provider=provider
            )
            
            logger.info(f"Generated new image for slide '{slide.title}': {new_image}")
            return new_image
            
        except Exception as e:
            logger.error(f"Image editing failed for slide '{slide.title}': {e}")
            raise ImageEditingError(f"Failed to edit image: {str(e)}")

class ImageEditingError(Exception):
    """Custom exception for image editing errors."""
    pass
```

## 4. API Endpoints (`backend/app/api/slides.py`)

### 4.1 Single Edit Endpoint

```python
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
        logger.error(f"Unexpected error in edit_slide_content: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 4.2 Batch Edit Endpoint

```python
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
```

### 4.3 Preview Edit Endpoint

```python
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
```

## 5. Frontend Integration (`frontend/src/components/slides/`)

### 5.1 Edit Controls Component

```typescript
// frontend/src/components/slides/EditControls.tsx
import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, Input, Select, Textarea, Modal } from '@/components/ui';
import { editSlideContent, editMultipleSlides } from '@/hooks/api/slides';
import { useSlidesStore } from '@/stores/slides-store';

interface EditControlsProps {
  slideIndex: number;
  slide: SlidePlan;
}

export const EditControls: React.FC<EditControlsProps> = ({ slideIndex, slide }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editType, setEditType] = useState<'title' | 'bullet' | 'notes' | 'image'>('title');
  const [content, setContent] = useState('');
  const [bulletIndex, setBulletIndex] = useState<number | null>(null);
  const [imagePrompt, setImagePrompt] = useState('');
  const [provider, setProvider] = useState<string>('auto');
  
  const queryClient = useQueryClient();
  const { slides, updateSlide } = useSlidesStore();
  
  const editMutation = useMutation({
    mutationFn: editSlideContent,
    onSuccess: (response) => {
      updateSlide(slideIndex, response.updated_slide);
      setIsEditing(false);
      queryClient.invalidateQueries({ queryKey: ['slides'] });
    },
    onError: (error) => {
      console.error('Edit failed:', error);
      // Show error toast
    }
  });
  
  const handleEdit = () => {
    const request = {
      slide_index: slideIndex,
      target: editType,
      content,
      bullet_index: editType === 'bullet' ? bulletIndex : undefined,
      image_prompt: editType === 'image' ? imagePrompt : undefined,
      provider: editType === 'image' ? provider : undefined
    };
    
    editMutation.mutate({ request, slides });
  };
  
  return (
    <div className="edit-controls">
      <Button onClick={() => setIsEditing(true)} variant="outline" size="sm">
        Edit Slide
      </Button>
      
      <Modal open={isEditing} onOpenChange={setIsEditing}>
        <div className="edit-modal">
          <h3>Edit Slide {slideIndex + 1}</h3>
          
          <Select value={editType} onValueChange={setEditType}>
            <option value="title">Title</option>
            <option value="bullet">Bullet Point</option>
            <option value="notes">Notes</option>
            <option value="image">Image</option>
          </Select>
          
          {editType === 'title' && (
            <Input
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Enter new title..."
            />
          )}
          
          {editType === 'bullet' && (
            <div>
              <Select 
                value={bulletIndex?.toString() || ''} 
                onValueChange={(v) => setBulletIndex(parseInt(v))}
              >
                {slide.bullets.map((_, i) => (
                  <option key={i} value={i}>{`Bullet ${i + 1}`}</option>
                ))}
              </Select>
              <Textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Enter new bullet content..."
              />
            </div>
          )}
          
          {editType === 'notes' && (
            <Textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Enter new notes..."
            />
          )}
          
          {editType === 'image' && (
            <div>
              <Textarea
                value={imagePrompt}
                onChange={(e) => setImagePrompt(e.target.value)}
                placeholder="Describe the new image you want..."
              />
              <Select value={provider} onValueChange={setProvider}>
                <option value="auto">Auto (DALL-E Preferred)</option>
                <option value="dalle">DALL-E</option>
                <option value="stability-ai">Stability AI</option>
              </Select>
            </div>
          )}
          
          <div className="edit-actions">
            <Button onClick={handleEdit} disabled={editMutation.isPending}>
              {editMutation.isPending ? 'Editing...' : 'Apply Edit'}
            </Button>
            <Button onClick={() => setIsEditing(false)} variant="outline">
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
```

### 5.2 API Hooks

```typescript
// frontend/src/hooks/api/slides.ts
export const editSlideContent = async ({ 
  request, 
  slides 
}: { 
  request: EditSlideRequest; 
  slides: SlidePlan[] 
}): Promise<EditSlideResponse> => {
  const response = await apiClient.POST('/slides/edit', {
    body: { request, slides }
  });
  return response;
};

export const editMultipleSlides = async ({ 
  request, 
  slides 
}: { 
  request: BatchEditRequest; 
  slides: SlidePlan[] 
}): Promise<BatchEditResponse> => {
  const response = await apiClient.POST('/slides/edit-batch', {
    body: { request, slides }
  });
  return response;
};

export const previewSlideEdit = async ({ 
  request, 
  slides 
}: { 
  request: EditSlideRequest; 
  slides: SlidePlan[] 
}): Promise<EditSlideResponse> => {
  const response = await apiClient.POST('/slides/edit-preview', {
    body: { request, slides }
  });
  return response;
};
```

## 6. Testing Strategy

### 6.1 Unit Tests (`backend/tests/test_text_editing.py`)

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.services.text_editing import TextEditingService, TextEditingError
from app.models.slides import SlidePlan

@pytest.fixture
def text_service():
    return TextEditingService()

@pytest.fixture
def sample_slide():
    return SlidePlan(
        title="Test Slide",
        bullets=["First bullet", "Second bullet"],
        notes="Test notes"
    )

class TestTextEditingService:
    @pytest.mark.asyncio
    async def test_edit_slide_title(self, text_service, sample_slide):
        with patch.object(text_service, '_call_llm_for_text_edit') as mock_llm:
            mock_llm.return_value = "Updated Title"
            
            result = await text_service.edit_slide_title(sample_slide, "Make it better")
            
            assert result == "Updated Title"
            mock_llm.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_edit_slide_bullet(self, text_service, sample_slide):
        with patch.object(text_service, '_call_llm_for_text_edit') as mock_llm:
            mock_llm.return_value = ["First bullet", "Updated second bullet"]
            
            result = await text_service.edit_slide_bullet(sample_slide, 1, "Improve this")
            
            assert result == ["First bullet", "Updated second bullet"]
            mock_llm.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_edit_slide_notes(self, text_service, sample_slide):
        with patch.object(text_service, '_call_llm_for_text_edit') as mock_llm:
            mock_llm.return_value = "Enhanced notes with more detail"
            
            result = await text_service.edit_slide_notes(sample_slide, "Expand notes")
            
            assert result == "Enhanced notes with more detail"
            mock_llm.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_llm_error_handling(self, text_service, sample_slide):
        with patch.object(text_service, '_call_llm_for_text_edit') as mock_llm:
            mock_llm.side_effect = Exception("LLM API error")
            
            with pytest.raises(TextEditingError):
                await text_service.edit_slide_title(sample_slide, "Test")
```

### 6.2 Integration Tests (`backend/tests/test_slide_editing_api.py`)

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.slides import SlidePlan, EditTarget

client = TestClient(app)

@pytest.fixture
def sample_slides():
    return [
        SlidePlan(
            title="Introduction",
            bullets=["Welcome", "Agenda"],
            notes="Opening remarks"
        ),
        SlidePlan(
            title="Main Content",
            bullets=["Point 1", "Point 2"],
            notes="Detailed explanation"
        )
    ]

class TestSlideEditingAPI:
    def test_edit_slide_title(self, sample_slides):
        request = {
            "slide_index": 0,
            "target": "title",
            "content": "Make it more engaging"
        }
        
        response = client.post("/api/v1/slides/edit", json={
            "request": request,
            "slides": [slide.model_dump() for slide in sample_slides]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["target"] == "title"
        assert data["updated_slide"]["title"] != sample_slides[0].title
    
    def test_edit_slide_bullet(self, sample_slides):
        request = {
            "slide_index": 0,
            "target": "bullet",
            "content": "Make this bullet more specific",
            "bullet_index": 0
        }
        
        response = client.post("/api/v1/slides/edit", json={
            "request": request,
            "slides": [slide.model_dump() for slide in sample_slides]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["target"] == "bullet"
    
    def test_edit_slide_image(self, sample_slides):
        request = {
            "slide_index": 0,
            "target": "image",
            "content": "placeholder",
            "image_prompt": "A professional business meeting scene",
            "provider": "dalle"
        }
        
        response = client.post("/api/v1/slides/edit", json={
            "request": request,
            "slides": [slide.model_dump() for slide in sample_slides]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["target"] == "image"
        assert data["image_meta"] is not None
    
    def test_invalid_slide_index(self, sample_slides):
        request = {
            "slide_index": 999,
            "target": "title",
            "content": "Test"
        }
        
        response = client.post("/api/v1/slides/edit", json={
            "request": request,
            "slides": [slide.model_dump() for slide in sample_slides]
        })
        
        assert response.status_code == 400
        assert "out of range" in response.json()["detail"]
    
    def test_missing_bullet_index(self, sample_slides):
        request = {
            "slide_index": 0,
            "target": "bullet",
            "content": "Test"
            # Missing bullet_index
        }
        
        response = client.post("/api/v1/slides/edit", json={
            "request": request,
            "slides": [slide.model_dump() for slide in sample_slides]
        })
        
        assert response.status_code == 400
        assert "bullet_index is required" in response.json()["detail"]
```

### 6.3 Frontend Tests (`frontend/src/components/slides/EditControls.test.tsx`)

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { EditControls } from './EditControls';
import { useSlidesStore } from '@/stores/slides-store';

const mockSlide = {
  title: "Test Slide",
  bullets: ["Bullet 1", "Bullet 2"],
  notes: "Test notes"
};

const mockSlides = [mockSlide];

jest.mock('@/hooks/api/slides', () => ({
  editSlideContent: jest.fn()
}));

describe('EditControls', () => {
  beforeEach(() => {
    useSlidesStore.setState({
      slides: mockSlides,
      updateSlide: jest.fn()
    });
  });

  it('renders edit button', () => {
    render(<EditControls slideIndex={0} slide={mockSlide} />);
    expect(screen.getByText('Edit Slide')).toBeInTheDocument();
  });

  it('opens edit modal when button is clicked', () => {
    render(<EditControls slideIndex={0} slide={mockSlide} />);
    
    fireEvent.click(screen.getByText('Edit Slide'));
    
    expect(screen.getByText('Edit Slide 1')).toBeInTheDocument();
    expect(screen.getByText('Title')).toBeInTheDocument();
  });

  it('allows editing title', async () => {
    render(<EditControls slideIndex={0} slide={mockSlide} />);
    
    fireEvent.click(screen.getByText('Edit Slide'));
    
    const titleInput = screen.getByPlaceholderText('Enter new title...');
    fireEvent.change(titleInput, { target: { value: 'New Title' } });
    
    fireEvent.click(screen.getByText('Apply Edit'));
    
    await waitFor(() => {
      expect(screen.queryByText('Edit Slide 1')).not.toBeInTheDocument();
    });
  });
});
```

## 7. Implementation Sequence

### Phase 1: Core Models and Services (Week 1)
1. **Edit Models**: Implement `EditSlideRequest`, `EditSlideResponse`, and related models
2. **Text Editing Service**: Create `TextEditingService` with LLM integration
3. **Image Editing Service**: Create `ImageEditingService` with existing image provider integration
4. **Unit Tests**: Comprehensive unit tests for all services

### Phase 2: API Endpoints (Week 2)
1. **Single Edit Endpoint**: Implement `/slides/edit` endpoint
2. **Batch Edit Endpoint**: Implement `/slides/edit-batch` endpoint
3. **Preview Endpoint**: Implement `/slides/edit-preview` endpoint
4. **Integration Tests**: Test all endpoints with real data

### Phase 3: Frontend Integration (Week 3)
1. **Edit Controls Component**: Create React component for editing UI
2. **API Hooks**: Implement TanStack Query hooks for editing operations
3. **Store Integration**: Update Zustand store to handle slide updates
4. **Frontend Tests**: Unit and integration tests for React components

### Phase 4: Polish and Documentation (Week 4)
1. **Error Handling**: Comprehensive error handling and user feedback
2. **Performance Optimization**: Optimize for large slide decks
3. **Documentation**: API documentation and user guides
4. **Final Testing**: End-to-end testing and bug fixes

## 8. Configuration Updates

### 8.1 Backend Configuration (`backend/app/core/config.py`)

```python
# Add to existing settings
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Text editing settings
    TEXT_EDITING_MODEL: str = "openai/gpt-4o-mini"
    TEXT_EDITING_TEMPERATURE: float = 0.3
    TEXT_EDITING_MAX_TOKENS: int = 500
    
    # Edit rate limiting
    EDIT_RATE_LIMIT_PER_MINUTE: int = 30
    BATCH_EDIT_RATE_LIMIT_PER_MINUTE: int = 10
    
    # Edit validation
    MAX_EDIT_CONTENT_LENGTH: int = 1000
    MAX_BATCH_EDITS: int = 10
```

### 8.2 Frontend Configuration (`frontend/src/config/editing.ts`)

```typescript
export const EDITING_CONFIG = {
  maxContentLength: 1000,
  maxBatchEdits: 10,
  supportedProviders: ['dalle', 'stability-ai', 'auto'] as const,
  defaultProvider: 'auto' as const,
  editTypes: ['title', 'bullet', 'notes', 'image'] as const,
} as const;
```

## 9. Performance Considerations

### 9.1 Caching Strategy
- **LLM Response Caching**: Cache similar edit requests to reduce API calls
- **Image Generation Caching**: Cache generated images to avoid regeneration
- **Slide State Caching**: Cache slide state during editing sessions

### 9.2 Rate Limiting
- **Per-user rate limiting**: Limit edit requests per user
- **Provider-specific limits**: Respect image provider rate limits
- **Batch operation limits**: Limit concurrent batch operations

### 9.3 Error Recovery
- **Graceful degradation**: Fall back to manual editing if AI fails
- **Partial success handling**: Handle partial failures in batch operations
- **Retry logic**: Implement exponential backoff for transient failures

## 10. Security Considerations

### 10.1 Input Validation
- **Content sanitization**: Sanitize user input to prevent injection attacks
- **Length limits**: Enforce strict limits on edit content
- **Type validation**: Validate all input types and formats

### 10.2 Access Control
- **User authentication**: Ensure only authenticated users can edit
- **Session validation**: Validate user sessions for edit operations
- **Resource ownership**: Ensure users can only edit their own slides

### 10.3 API Security
- **Rate limiting**: Prevent abuse through rate limiting
- **Input validation**: Validate all API inputs
- **Error handling**: Avoid information leakage in error messages

## 11. API Documentation

### 11.1 OpenAPI Schema

The implementation will automatically generate OpenAPI documentation for all new endpoints:

- `POST /api/v1/slides/edit` - Edit single slide content
- `POST /api/v1/slides/edit-batch` - Edit multiple slides
- `POST /api/v1/slides/edit-preview` - Preview edits without applying

### 11.2 Request/Response Examples

```json
// Edit slide title
POST /api/v1/slides/edit
{
  "request": {
    "slide_index": 0,
    "target": "title",
    "content": "Make the title more engaging and professional"
  },
  "slides": [...]
}

// Edit bullet point
POST /api/v1/slides/edit
{
  "request": {
    "slide_index": 0,
    "target": "bullet",
    "content": "Make this bullet more specific and actionable",
    "bullet_index": 1
  },
  "slides": [...]
}

// Edit image
POST /api/v1/slides/edit
{
  "request": {
    "slide_index": 0,
    "target": "image",
    "content": "placeholder",
    "image_prompt": "A modern office with people collaborating",
    "provider": "dalle"
  },
  "slides": [...]
}
```

## 12. Success Metrics

### 12.1 Technical Metrics
- **API Response Time**: < 2 seconds for single edits, < 5 seconds for batch edits
- **Error Rate**: < 1% for successful edits
- **Test Coverage**: ≥ 90% for all new code
- **Documentation Coverage**: 100% of public APIs documented

### 12.2 User Experience Metrics
- **Edit Success Rate**: > 95% of edit attempts succeed
- **User Satisfaction**: Positive feedback on edit quality
- **Adoption Rate**: > 80% of users try editing features within first week

## 13. Risk Mitigation

### 13.1 Technical Risks
- **LLM API Failures**: Implement fallback to manual editing
- **Image Generation Failures**: Use placeholder images as fallback
- **Performance Issues**: Implement caching and rate limiting

### 13.2 User Experience Risks
- **Poor Edit Quality**: Implement user feedback mechanisms
- **Complex UI**: Provide clear, intuitive editing interface
- **Slow Performance**: Optimize for responsiveness

## 14. Future Enhancements

### 14.1 Advanced Features
- **Undo/Redo**: Implement edit history and undo functionality
- **Collaborative Editing**: Real-time collaborative slide editing
- **Edit Templates**: Pre-defined edit patterns for common scenarios
- **Bulk Operations**: Edit multiple slides with same pattern

### 14.2 AI Improvements
- **Context-Aware Editing**: Consider presentation context for better edits
- **Style Consistency**: Maintain consistent style across all slides
- **Content Suggestions**: AI-powered content improvement suggestions

## 15. Conclusion

This comprehensive plan provides a detailed roadmap for implementing slide editing functionality that integrates seamlessly with the existing architecture while maintaining the high standards of the codebase. The implementation follows established patterns for FastAPI, Pydantic models, testing, and frontend development.

The plan ensures:
- **Consistency** with existing codebase patterns
- **Scalability** for future enhancements
- **Reliability** through comprehensive testing
- **Security** through proper validation and access control
- **Performance** through optimization and caching strategies

Implementation will proceed in phases to ensure quality and allow for iterative feedback and improvements.
