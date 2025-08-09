from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.models.slides import SlidePlan
from app.services.llm import generate_outline, LLMError
from typing import List

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/generate", response_model=ChatResponse)
async def generate_chat_outline(request: ChatRequest):
    try:
        outline = await generate_outline(request.model_dump())
        # Expect outline structure: { "slides": [{...}], "sessionId": "..." }
        slides = [SlidePlan(**s) for s in outline.get("slides", [])]
        response = ChatResponse(slides=slides, sessionId=outline.get("sessionId"))
        return response
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e)) 