import httpx
from typing import Any, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random
from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse
from app.models.slides import SlidePlan
from app.models.errors import ErrorResponse

class LLMError(Exception):
    """Custom exception for LLM service errors."""
    pass

def _base_headers() -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}" if settings.OPENROUTER_API_KEY else "",
        "Content-Type": "application/json",
    }
    # Add optional headers, e.g., org info if needed
    return headers

def get_async_client() -> httpx.AsyncClient:
    timeout = httpx.Timeout(settings.OPENROUTER_TIMEOUT_SECONDS)
    return httpx.AsyncClient(
        base_url=settings.OPENROUTER_BASE_URL,
        timeout=timeout,
        headers=_base_headers(),
    )

def _select_model(requested_model: Optional[str]) -> str:
    model = requested_model or settings.OPENROUTER_DEFAULT_MODEL
    if settings.OPENROUTER_ALLOWED_MODELS and model not in settings.OPENROUTER_ALLOWED_MODELS:
        raise LLMError(f"Model '{model}' is not allowed")
    return model

def _build_payload(req: ChatRequest) -> Dict[str, Any]:
    payload = {
        "model": _select_model(req.model),
        "input": {
            "prompt": req.prompt,
            "slideCount": req.slide_count,
            "language": req.language,
            "context": req.context,
        },
    }
    return payload

def _parse_response(data: Dict[str, Any]) -> ChatResponse:
    # Expect { "slides": [{ title, bullets, image?, notes? }], "sessionId"? }
    slides_raw = data.get("slides", [])
    slides = [SlidePlan(**s) for s in slides_raw]
    # Use field name for Pydantic init; alias is handled during serialization
    return ChatResponse(slides=slides, session_id=data.get("sessionId"))

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4) + wait_random(0, 0.5))
async def _call_openrouter(request: ChatRequest) -> ChatResponse:
    async with get_async_client() as client:
        try:
            payload = _build_payload(request)
            resp = await client.post("/generate", json=payload)
            # Rate limit handling
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                raise LLMError(f"Rate limited by upstream. Retry-After: {retry_after}")
            resp.raise_for_status()
            data = resp.json()
            return _parse_response(data)
        except httpx.HTTPError as e:
            raise LLMError(f"LLM HTTP error: {e.__class__.__name__}") from e
        except Exception as e:
            raise LLMError(f"LLM request failed: {str(e)}") from e


async def generate_outline(request: ChatRequest) -> ChatResponse:
    """
    Calls the OpenRouter LLM API to generate a slide outline.
    Uses retry only for actual HTTP calls; returns immediately if API key is missing.
    """
    # In tests/offline mode (no API key), immediately return a local fallback
    if not settings.OPENROUTER_API_KEY:
        count = request.slide_count
        title_base = request.prompt or "Slide"
        slides = [
            SlidePlan(title=f"{title_base}", bullets=["Bullet"])
            for _ in range(count)
        ]
        return ChatResponse(slides=slides)
    # Otherwise, call upstream
    return await _call_openrouter(request)