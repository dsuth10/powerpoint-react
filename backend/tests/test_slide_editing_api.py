import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.models.slides import SlidePlan, EditTarget

client = TestClient(app)

@pytest.fixture
def sample_slides():
    return [
        SlidePlan(
            title="Introduction",
            bullets=["Welcome", "Agenda"],
            notes="Opening remarks"
        ),
        SlidePlan(
            title="Main Content",
            bullets=["Point 1", "Point 2"],
            notes="Detailed explanation"
        )
    ]

class TestSlideEditingAPI:
    def test_edit_slide_title(self, sample_slides):
        with patch('app.services.text_editing.TextEditingService.edit_slide_title') as mock_edit:
            mock_edit.return_value = "Enhanced Introduction"
            
            request = {
                "slide_index": 0,
                "target": "title",
                "content": "Make it more engaging"
            }
            
            response = client.post("/api/v1/slides/edit", json={
                "request": request,
                "slides": [slide.model_dump() for slide in sample_slides]
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["target"] == "title"
            assert data["updated_slide"]["title"] == "Enhanced Introduction"
    
    def test_edit_slide_bullet(self, sample_slides):
        with patch('app.services.text_editing.TextEditingService.edit_slide_bullet') as mock_edit:
            mock_edit.return_value = ["Welcome", "Enhanced agenda"]
            
            request = {
                "slide_index": 0,
                "target": "bullet",
                "content": "Make this bullet more specific",
                "bullet_index": 1
            }
            
            response = client.post("/api/v1/slides/edit", json={
                "request": request,
                "slides": [slide.model_dump() for slide in sample_slides]
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["target"] == "bullet"
            assert data["updated_slide"]["bullets"] == ["Welcome", "Enhanced agenda"]
    
    def test_edit_slide_notes(self, sample_slides):
        with patch('app.services.text_editing.TextEditingService.edit_slide_notes') as mock_edit:
            mock_edit.return_value = "Enhanced opening remarks with more detail"
            
            request = {
                "slide_index": 0,
                "target": "notes",
                "content": "Expand the notes"
            }
            
            response = client.post("/api/v1/slides/edit", json={
                "request": request,
                "slides": [slide.model_dump() for slide in sample_slides]
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["target"] == "notes"
            assert data["updated_slide"]["notes"] == "Enhanced opening remarks with more detail"
    
    def test_edit_slide_image(self, sample_slides):
        with patch('app.services.image_editing.ImageEditingService.edit_slide_image') as mock_edit:
            mock_edit.return_value = {
                "url": "https://example.com/new-image.jpg",
                "altText": "New professional image",
                "provider": "dalle"
            }
            
            request = {
                "slide_index": 0,
                "target": "image",
                "content": "placeholder",
                "image_prompt": "A professional business meeting scene",
                "provider": "dalle"
            }
            
            response = client.post("/api/v1/slides/edit", json={
                "request": request,
                "slides": [slide.model_dump() for slide in sample_slides]
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["target"] == "image"
            assert data["image_meta"] is not None
    
    def test_invalid_slide_index(self, sample_slides):
        request = {
            "slide_index": 999,
            "target": "title",
            "content": "Test"
        }
        
        response = client.post("/api/v1/slides/edit", json={
            "request": request,
            "slides": [slide.model_dump() for slide in sample_slides]
        })
        
        assert response.status_code == 400
        assert "out of range" in response.json()["detail"]
    
    def test_missing_bullet_index(self, sample_slides):
        request = {
            "slide_index": 0,
            "target": "bullet",
            "content": "Test"
            # Missing bullet_index
        }
        
        response = client.post("/api/v1/slides/edit", json={
            "request": request,
            "slides": [slide.model_dump() for slide in sample_slides]
        })
        
        assert response.status_code == 400
        assert "bullet_index is required" in response.json()["detail"]
    
    def test_missing_image_prompt(self, sample_slides):
        request = {
            "slide_index": 0,
            "target": "image",
            "content": "placeholder"
            # Missing image_prompt
        }
        
        response = client.post("/api/v1/slides/edit", json={
            "request": request,
            "slides": [slide.model_dump() for slide in sample_slides]
        })
        
        assert response.status_code == 400
        assert "image_prompt is required" in response.json()["detail"]
    
    def test_invalid_bullet_index(self, sample_slides):
        request = {
            "slide_index": 0,
            "target": "bullet",
            "content": "Test",
            "bullet_index": 999
        }
        
        response = client.post("/api/v1/slides/edit", json={
            "request": request,
            "slides": [slide.model_dump() for slide in sample_slides]
        })
        
        assert response.status_code == 400
        assert "out of range" in response.json()["detail"]
    
    def test_batch_edit_success(self, sample_slides):
        with patch('app.services.text_editing.TextEditingService.edit_slide_title') as mock_title:
            with patch('app.services.text_editing.TextEditingService.edit_slide_notes') as mock_notes:
                mock_title.return_value = "Enhanced Introduction"
                mock_notes.return_value = "Enhanced notes"
                
                request = {
                    "edits": [
                        {
                            "slide_index": 0,
                            "target": "title",
                            "content": "Make it better"
                        },
                        {
                            "slide_index": 1,
                            "target": "notes",
                            "content": "Expand notes"
                        }
                    ]
                }
                
                response = client.post("/api/v1/slides/edit-batch", json={
                    "request": request,
                    "slides": [slide.model_dump() for slide in sample_slides]
                })
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert len(data["results"]) == 2
                assert len(data["errors"]) == 0
    
    def test_batch_edit_partial_failure(self, sample_slides):
        with patch('app.services.text_editing.TextEditingService.edit_slide_title') as mock_title:
            mock_title.side_effect = Exception("LLM error")
            
            request = {
                "edits": [
                    {
                        "slide_index": 0,
                        "target": "title",
                        "content": "Make it better"
                    },
                    {
                        "slide_index": 999,  # Invalid index
                        "target": "title",
                        "content": "Test"
                    }
                ]
            }
            
            response = client.post("/api/v1/slides/edit-batch", json={
                "request": request,
                "slides": [slide.model_dump() for slide in sample_slides]
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert len(data["errors"]) > 0
    
    def test_preview_edit(self, sample_slides):
        with patch('app.services.text_editing.TextEditingService.edit_slide_title') as mock_edit:
            mock_edit.return_value = "Preview Title"
            
            request = {
                "slide_index": 0,
                "target": "title",
                "content": "Preview this"
            }
            
            response = client.post("/api/v1/slides/edit-preview", json={
                "request": request,
                "slides": [slide.model_dump() for slide in sample_slides]
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["updated_slide"]["title"] == "Preview Title"
