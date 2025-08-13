import httpx
import json
import re
import logging
from typing import Tuple
from typing import Any, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random, RetryError
from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse
from app.models.slides import SlidePlan
from app.models.errors import ErrorResponse

# Set up logging
logger = logging.getLogger(__name__)

class LLMError(Exception):
    """Custom exception for LLM service errors."""
    pass

def _base_headers() -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}" if settings.OPENROUTER_API_KEY else "",
        "Content-Type": "application/json",
    }
    # Add optional OpenRouter headers for attribution per their guidelines
    if settings.OPENROUTER_HTTP_REFERER:
        headers["HTTP-Referer"] = settings.OPENROUTER_HTTP_REFERER
    if settings.OPENROUTER_APP_TITLE:
        headers["X-Title"] = settings.OPENROUTER_APP_TITLE
    
    logger.info(f"LLM Headers configured: {list(headers.keys())}")
    return headers

def get_async_client() -> httpx.AsyncClient:
    timeout = httpx.Timeout(settings.OPENROUTER_TIMEOUT_SECONDS)
    client = httpx.AsyncClient(
        base_url=settings.OPENROUTER_BASE_URL,
        timeout=timeout,
        headers=_base_headers(),
    )
    logger.info(f"LLM Client created with base_url={settings.OPENROUTER_BASE_URL}, timeout={settings.OPENROUTER_TIMEOUT_SECONDS}s")
    return client

def _select_model(requested_model: Optional[str]) -> str:
    model = requested_model or settings.OPENROUTER_DEFAULT_MODEL
    if settings.OPENROUTER_ALLOWED_MODELS and model not in settings.OPENROUTER_ALLOWED_MODELS:
        logger.error(f"Model '{model}' not in allowed models: {settings.OPENROUTER_ALLOWED_MODELS}")
        raise LLMError(f"Model '{model}' is not allowed")
    logger.info(f"Selected model: {model}")
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
    logger.info(f"Built legacy payload for model {payload['model']}")
    return payload

def _parse_response(data: Dict[str, Any]) -> ChatResponse:
    # Expect { "slides": [{ title, bullets, image?, notes? }], "sessionId"? }
    logger.info(f"Parsing LLM response: {json.dumps(data, indent=2)}")
    
    slides_raw = data.get("slides", [])
    logger.info(f"Found {len(slides_raw)} slides in response")
    
    slides = []
    for i, slide_data in enumerate(slides_raw):
        logger.info(f"Processing slide {i+1}: {slide_data}")
        slide = SlidePlan(**slide_data)
        slides.append(slide)
        if slide.image:
            logger.info(f"Slide {i+1} has image: {slide.image}")
        if slide.notes:
            logger.info(f"Slide {i+1} has notes: {slide.notes[:100]}...")
    
    # Use field name for Pydantic init; alias is handled during serialization
    response = ChatResponse(slides=slides, session_id=data.get("sessionId"))
    logger.info(f"Successfully parsed response with {len(slides)} slides")
    return response


def _extract_first_json_object(text: str) -> Tuple[bool, Dict[str, Any] | None]:
    """Attempt to extract the first JSON object from arbitrary text.

    Returns (ok, obj). Handles cases like ```json { ... } ``` or prose before/after.
    """
    logger.info(f"Extracting JSON from text (length: {len(text)}): {text[:200]}...")
    
    # Quick path: try direct parse
    try:
        result = json.loads(text)
        logger.info("Direct JSON parse successful")
        return True, result
    except Exception as e:
        logger.debug(f"Direct JSON parse failed: {e}")

    # Strip common code fences
    fenced = re.search(r"```json\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
    if fenced:
        try:
            result = json.loads(fenced.group(1))
            logger.info("JSON extracted from code fence")
            return True, result
        except Exception as e:
            logger.debug(f"Code fence JSON parse failed: {e}")

    # Find first balanced {...}
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start : i + 1]
                    try:
                        result = json.loads(candidate)
                        logger.info("JSON extracted from balanced braces")
                        return True, result
                    except Exception as e:
                        logger.debug(f"Balanced braces JSON parse failed: {e}")
                        break
        start = text.find("{", start + 1)

    logger.error(f"Failed to extract JSON from text: {text}")
    return False, None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4) + wait_random(0, 0.5))
async def _call_openrouter(request: ChatRequest) -> ChatResponse:
    logger.info(f"Starting LLM API call for request: {request.prompt[:100]}...")
    logger.info(f"Request details: model={request.model}, slide_count={request.slide_count}, language={request.language}")
    
    async with get_async_client() as client:
        try:
            # Primary: official Chat Completions API
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You generate presentation slide outlines with comprehensive speaker notes. "
                        "Respond ONLY with strict JSON matching this schema: "
                        "{\"slides\":[{\"title\":string,\"bullets\":[string],\"image\"?:{\"url\":string,\"altText\":string,\"provider\":string},\"notes\"?:string}],\"sessionId\"?:string}. "
                        "Requirements: bullets must be concise; detailed content belongs in 'notes' to avoid on-slide truncation. If including image, provide a real, publicly accessible URL and meaningful altText."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Create {request.slide_count} slides about: {request.prompt}. Language: {request.language}. "
                        "Ensure each slide includes robust speaker notes (no placeholders)."
                    ),
                },
            ]
            chat_payload = {
                "model": _select_model(request.model),
                "messages": messages,
                "temperature": 0.3,
                # Encourage strict JSON output across providers
                "response_format": {"type": "json_object"},
            }
            
            logger.info(f"Sending chat completions request to {settings.OPENROUTER_BASE_URL}/chat/completions")
            logger.info(f"Payload: {json.dumps(chat_payload, indent=2)}")
            
            chat_resp = await client.post("/chat/completions", json=chat_payload)
            
            logger.info(f"Chat completions response status: {chat_resp.status_code}")
            logger.info(f"Response headers: {dict(chat_resp.headers)}")
            
            if chat_resp.status_code == 429:
                retry_after = chat_resp.headers.get("Retry-After")
                logger.error(f"Rate limited by upstream. Retry-After: {retry_after}")
                raise LLMError(f"Rate limited by upstream. Retry-After: {retry_after}")
            
            chat_resp.raise_for_status()
            chat_json = chat_resp.json()
            
            logger.info(f"Chat completions response: {json.dumps(chat_json, indent=2)}")
            
            content = (
                chat_json.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            
            logger.info(f"Extracted content from response: {content}")
            
            ok, parsed_obj = _extract_first_json_object(content)
            if not ok or not isinstance(parsed_obj, dict):
                logger.error(f"Failed to parse JSON from content: {content}")
                raise LLMError("Malformed LLM response: no JSON content")
            
            parsed = parsed_obj
            logger.info(f"Successfully parsed JSON object: {json.dumps(parsed, indent=2)}")
            return _parse_response(parsed)
            
        except Exception as e:
            logger.error(f"Primary chat completions API failed: {e}")
            # Fallback: legacy /generate used in unit tests
            try:
                logger.info("Attempting fallback to legacy /generate endpoint")
                payload = _build_payload(request)
                logger.info(f"Fallback payload: {json.dumps(payload, indent=2)}")
                
                resp = await client.post("/generate", json=payload)
                
                logger.info(f"Fallback response status: {resp.status_code}")
                logger.info(f"Fallback response headers: {dict(resp.headers)}")
                
                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    logger.error(f"Fallback rate limited. Retry-After: {retry_after}")
                    raise LLMError(f"Rate limited by upstream. Retry-After: {retry_after}")
                
                resp.raise_for_status()
                data = resp.json()
                
                logger.info(f"Fallback response: {json.dumps(data, indent=2)}")
                return _parse_response(data)
                
            except httpx.HTTPError as e:
                logger.error(f"Fallback HTTP error: {e.__class__.__name__} - {e}")
                raise LLMError(f"LLM HTTP error: {e.__class__.__name__}") from e
            except Exception as e:
                logger.error(f"Fallback request failed: {str(e)}")
                raise LLMError(f"LLM request failed: {str(e)}") from e


async def generate_outline(request: ChatRequest) -> ChatResponse:
    """
    Calls the OpenRouter LLM API to generate a slide outline.
    Uses retry only for actual HTTP calls; returns immediately if API key is missing.
    """
    logger.info(f"generate_outline called with request: {request.prompt[:100]}...")
    logger.info(f"API Key present: {bool(settings.OPENROUTER_API_KEY)}")
    logger.info(f"Require upstream: {settings.OPENROUTER_REQUIRE_UPSTREAM}")
    
    # In tests/offline mode (no API key), immediately return a local fallback
    if not settings.OPENROUTER_API_KEY:
        logger.warning("No OpenRouter API key found, returning offline fallback")
        count = request.slide_count
        # Ensure titles respect max length constraints
        slides = [
            SlidePlan(title=f"Slide {i+1}", bullets=["Bullet"])
            for i in range(count)
        ]
        return ChatResponse(slides=slides)
    
    # Otherwise, call upstream; on failure, optionally raise (require upstream) or fall back to offline minimal outline
    try:
        logger.info("Calling OpenRouter API...")
        result = await _call_openrouter(request)
        logger.info(f"OpenRouter API call successful, returned {len(result.slides)} slides")
        return result
    except (LLMError, RetryError) as e:
        logger.error(f"OpenRouter API call failed: {e}")
        if settings.OPENROUTER_REQUIRE_UPSTREAM:
            logger.error("Require upstream is enabled, re-raising error")
            # Surface failure to the route; caller will translate to HTTP error
            raise
        logger.warning("Falling back to offline minimal outline")
        count = request.slide_count
        slides = [
            SlidePlan(title=f"Slide {i+1}", bullets=["Bullet"])
            for i in range(count)
        ]
        return ChatResponse(slides=slides)