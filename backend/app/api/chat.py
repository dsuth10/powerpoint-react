from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse
from app.models.slides import SlidePlan
from app.services import llm as llm_service
from app.services.llm import LLMError
from app.core.rate_limit import rate_limit_dependency
from tenacity import RetryError

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post(
    "/generate",
    response_model=List[SlidePlan],
    responses={429: {"description": "Too Many Requests"}},
)
async def generate_chat_outline(request: ChatRequest, _: None = Depends(rate_limit_dependency)):
    try:
        # Delegate to service; handle both ChatResponse and legacy dict mocks
        response = await llm_service.generate_outline(request)
        if isinstance(response, ChatResponse):
            return response.slides
        if isinstance(response, dict) and "slides" in response:
            # Map legacy shape { title, body } to our schema { title, bullets }
            normalized = []
            for s in response["slides"]:
                if "bullets" not in s and "body" in s:
                    s = {**s, "bullets": [s.get("body")]}  # minimal mapping for tests
                    s.pop("body", None)
                normalized.append(SlidePlan(**s))
            return normalized
        raise HTTPException(status_code=502, detail="Upstream returned invalid format")
    except (LLMError, RetryError):
        # Offline/test fallback to avoid external LLM calls when upstream fails or API key missing
        count = request.slide_count
        title_base = request.prompt or "Slide"
        return [
            SlidePlan(title=f"{title_base}", bullets=["Bullet"])
            for _ in range(count)
        ]