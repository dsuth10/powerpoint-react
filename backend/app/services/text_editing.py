import logging
import json
import re
from typing import List, Optional, Union
from app.services.llm import get_async_client
from app.models.slides import SlidePlan, EditTarget, EditSlideRequest

logger = logging.getLogger(__name__)

class TextEditingError(Exception):
    """Custom exception for text editing errors."""
    pass

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
