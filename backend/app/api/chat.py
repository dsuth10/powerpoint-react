from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.models.slides import SlidePlan
from app.services.llm import generate_outline, LLMError
from typing import List

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/generate", response_model=ChatResponse)
async def generate_chat_outline(request: ChatRequest):
    try:
        # Delegate to service which returns ChatResponse
        response = await generate_outline(request)
        return response
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e)) 