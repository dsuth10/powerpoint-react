import os
import httpx
from typing import Any, Dict
from tenacity import retry, stop_after_attempt, wait_exponential

OPENROUTER_KEY = os.getenv("OPENROUTER_KEY", "test-key")
OPENROUTER_URL = "https://openrouter.ai/api/v1/generate"

class LLMError(Exception):
    """Custom exception for LLM service errors."""
    pass

async def get_async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=30.0, headers={"Authorization": f"Bearer {OPENROUTER_KEY}"})

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
async def generate_outline(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calls the OpenRouter LLM API to generate a slide outline.
    Retries up to 3 times with exponential backoff on failure.
    """
    async with get_async_client() as client:
        try:
            response = await client.post(OPENROUTER_URL, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Mask secret in logs
            raise LLMError(f"LLM request failed: {str(e)}") from e 