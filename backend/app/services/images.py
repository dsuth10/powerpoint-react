import os
import httpx
from typing import Any, Dict
from tenacity import retry, stop_after_attempt, wait_exponential

RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY", "test-key")
RUNWARE_URL = "https://api.runware.ai/v1/generate"

class ImageError(Exception):
    """Custom exception for image service errors."""
    pass

async def get_async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=30.0, headers={"Authorization": f"Bearer {RUNWARE_API_KEY}"})

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
async def generate_image(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calls the Runware API to generate an image.
    Retries up to 3 times with exponential backoff on failure.
    """
    async with get_async_client() as client:
        try:
            response = await client.post(RUNWARE_URL, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Mask secret in logs
            raise ImageError(f"Image request failed: {str(e)}") from e 