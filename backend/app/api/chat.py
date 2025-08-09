from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest
from app.models.slides import SlidePlan
from app.services.llm import generate_outline, LLMError
from typing import List

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatResponse(List[SlidePlan]):
    """Response model for chat-based outline generation (list of SlidePlan)."""
    pass

@router.post("/generate", response_model=List[SlidePlan])
async def generate_chat_outline(request: ChatRequest):
    try:
        outline = await generate_outline(request.model_dump())
        # Assume outline["slides"] is a list of dicts matching SlidePlan
        slides = [SlidePlan(**s) for s in outline.get("slides", [])]
        return slides
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e)) 