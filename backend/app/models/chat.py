from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    """
    Request model for chat-based outline generation.

    Attributes:
        prompt (str): The user prompt for slide outline generation.
        num_slides (int): Number of slides to generate (1-20).
        language (str): Output language (ISO 639-1 code, e.g. 'en').
        context (Optional[str]): Optional context or background for the presentation.
    
    Example:
        {
            "prompt": "The history of AI",
            "numSlides": 5,
            "language": "en",
            "context": "For a high school audience"
        }
    """
    prompt: str = Field(..., description="The user prompt for slide outline generation.")
    num_slides: int = Field(..., ge=1, le=20, alias="numSlides", description="Number of slides to generate (1-20).")
    language: str = Field(..., min_length=2, max_length=5, description="Output language (ISO 639-1 code, e.g. 'en').")
    context: Optional[str] = Field(None, description="Optional context or background for the presentation.")

    model_config = {"strict": True, "populate_by_name": True, "alias_generator": lambda s: ''.join([s[0].lower()]+[c if c.islower() else f"{c}" for c in s[1:]])}

    def model_dump(self, *args, **kwargs):
        # Always output camelCase keys for TypeScript clients
        kwargs.setdefault("by_alias", True)
        return super().model_dump(*args, **kwargs) 