import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.text_editing import TextEditingService, TextEditingError
from app.models.slides import SlidePlan

@pytest.fixture
def text_service():
    return TextEditingService()

@pytest.fixture
def sample_slide():
    return SlidePlan(
        title="Test Slide",
        bullets=["First bullet", "Second bullet"],
        notes="Test notes"
    )

class TestTextEditingService:
    @pytest.mark.asyncio
    async def test_edit_slide_title(self, text_service, sample_slide):
        with patch.object(text_service, '_call_llm_for_text_edit') as mock_llm:
            mock_llm.return_value = "Updated Title"
            
            result = await text_service.edit_slide_title(sample_slide, "Make it better")
            
            assert result == "Updated Title"
            mock_llm.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_edit_slide_bullet(self, text_service, sample_slide):
        with patch.object(text_service, '_call_llm_for_text_edit') as mock_llm:
            mock_llm.return_value = ["First bullet", "Updated second bullet"]
            
            result = await text_service.edit_slide_bullet(sample_slide, 1, "Improve this")
            
            assert result == ["First bullet", "Updated second bullet"]
            mock_llm.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_edit_slide_notes(self, text_service, sample_slide):
        with patch.object(text_service, '_call_llm_for_text_edit') as mock_llm:
            mock_llm.return_value = "Enhanced notes with more detail"
            
            result = await text_service.edit_slide_notes(sample_slide, "Expand notes")
            
            assert result == "Enhanced notes with more detail"
            mock_llm.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_llm_error_handling(self, text_service, sample_slide):
        with patch.object(text_service, '_call_llm_for_text_edit') as mock_llm:
            mock_llm.side_effect = Exception("LLM API error")
            
            with pytest.raises(TextEditingError):
                await text_service.edit_slide_title(sample_slide, "Test")
    
    def test_parse_bullets_response_json(self, text_service):
        content = '["Bullet 1", "Bullet 2", "Bullet 3"]'
        result = text_service._parse_bullets_response(content)
        assert result == ["Bullet 1", "Bullet 2", "Bullet 3"]
    
    def test_parse_bullets_response_newlines(self, text_service):
        content = "• First bullet\n- Second bullet\n* Third bullet"
        result = text_service._parse_bullets_response(content)
        assert result == ["First bullet", "Second bullet", "Third bullet"]
    
    def test_parse_bullets_response_invalid(self, text_service):
        content = "Invalid content without bullets"
        with pytest.raises(TextEditingError):
            text_service._parse_bullets_response(content)
