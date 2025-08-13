import os
import pytest
import httpx
import json
import logging
from unittest.mock import patch, MagicMock

from app.models.chat import ChatRequest
from app.services.llm import generate_outline, _call_openrouter, _extract_first_json_object
from app.core.config import settings

# Set up logging for the test
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
@pytest.mark.live
@pytest.mark.live_llm
async def test_llm_diagnostic_comprehensive(require_live_llm, no_http_mocks):
    """
    Comprehensive diagnostic test to identify LLM API issues.
    This test will log every step of the process to help identify where things are failing.
    """
    logger.info("=== Starting Comprehensive LLM Diagnostic Test ===")
    
    # Test 1: Environment Configuration
    logger.info("1. Checking environment configuration...")
    logger.info(f"OPENROUTER_API_KEY present: {bool(os.getenv('OPENROUTER_API_KEY'))}")
    logger.info(f"OPENROUTER_BASE_URL: {os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')}")
    logger.info(f"OPENROUTER_DEFAULT_MODEL: {os.getenv('OPENROUTER_DEFAULT_MODEL', 'openai/gpt-4o-mini')}")
    logger.info(f"OPENROUTER_REQUIRE_UPSTREAM: {os.getenv('OPENROUTER_REQUIRE_UPSTREAM', 'False')}")
    
    # Test 2: Direct API Connectivity
    logger.info("2. Testing direct API connectivity...")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-4o-mini")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if os.getenv("OPENROUTER_HTTP_REFERER"):
        headers["HTTP-Referer"] = os.getenv("OPENROUTER_HTTP_REFERER")
    if os.getenv("OPENROUTER_APP_TITLE"):
        headers["X-Title"] = os.getenv("OPENROUTER_APP_TITLE")
    
    logger.info(f"Headers: {list(headers.keys())}")
    
    # Simple test payload
    simple_payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Return the word PONG"}
        ],
        "temperature": 0,
    }
    
    logger.info(f"Simple test payload: {json.dumps(simple_payload, indent=2)}")
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0, headers=headers) as client:
        try:
            resp = await client.post("/chat/completions", json=simple_payload)
            logger.info(f"Simple test response status: {resp.status_code}")
            logger.info(f"Simple test response headers: {dict(resp.headers)}")
            
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Simple test response: {json.dumps(data, indent=2)}")
                content = data["choices"][0].get("message", {}).get("content", "")
                logger.info(f"Simple test content: {content}")
                assert "PONG" in content, f"Expected PONG in response, got: {content}"
                logger.info("✓ Simple API connectivity test passed")
            else:
                logger.error(f"Simple test failed with status {resp.status_code}: {resp.text}")
                pytest.fail(f"Simple API connectivity test failed: {resp.status_code}")
                
        except Exception as e:
            logger.error(f"Simple API connectivity test exception: {e}")
            pytest.fail(f"Simple API connectivity test exception: {e}")
    
    # Test 3: Structured Slide Generation
    logger.info("3. Testing structured slide generation...")
    structured_payload = {
        "model": model,
        "messages": [
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
                "content": "Create 2 slides about: Artificial Intelligence. Language: en. Ensure each slide includes robust speaker notes (no placeholders).",
            },
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }
    
    logger.info(f"Structured test payload: {json.dumps(structured_payload, indent=2)}")
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0, headers=headers) as client:
        try:
            resp = await client.post("/chat/completions", json=structured_payload)
            logger.info(f"Structured test response status: {resp.status_code}")
            logger.info(f"Structured test response headers: {dict(resp.headers)}")
            
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Structured test response: {json.dumps(data, indent=2)}")
                
                content = data["choices"][0].get("message", {}).get("content", "")
                logger.info(f"Structured test content: {content}")
                
                # Test JSON extraction
                ok, parsed_obj = _extract_first_json_object(content)
                logger.info(f"JSON extraction result: ok={ok}, parsed_obj type={type(parsed_obj)}")
                
                if ok and isinstance(parsed_obj, dict):
                    logger.info(f"Parsed JSON: {json.dumps(parsed_obj, indent=2)}")
                    
                    # Validate structure
                    slides = parsed_obj.get("slides", [])
                    logger.info(f"Found {len(slides)} slides in response")
                    
                    for i, slide in enumerate(slides):
                        logger.info(f"Slide {i+1}: {json.dumps(slide, indent=2)}")
                        
                        # Check for images
                        if "image" in slide:
                            image = slide["image"]
                            logger.info(f"Slide {i+1} has image: {image}")
                            assert "url" in image, f"Image missing URL: {image}"
                            assert "altText" in image, f"Image missing altText: {image}"
                            assert "provider" in image, f"Image missing provider: {image}"
                        else:
                            logger.info(f"Slide {i+1} has no image")
                        
                        # Check for notes
                        if "notes" in slide and slide["notes"]:
                            logger.info(f"Slide {i+1} has notes: {slide['notes'][:100]}...")
                        else:
                            logger.info(f"Slide {i+1} has no notes or empty notes")
                    
                    logger.info("✓ Structured slide generation test passed")
                else:
                    logger.error(f"Failed to extract valid JSON from content: {content}")
                    pytest.fail("Structured slide generation test failed: invalid JSON")
            else:
                logger.error(f"Structured test failed with status {resp.status_code}: {resp.text}")
                pytest.fail(f"Structured slide generation test failed: {resp.status_code}")
                
        except Exception as e:
            logger.error(f"Structured slide generation test exception: {e}")
            pytest.fail(f"Structured slide generation test exception: {e}")
    
    # Test 4: Service Integration
    logger.info("4. Testing service integration...")
    request = ChatRequest(
        prompt="Artificial Intelligence",
        slide_count=2,
        model=model,
        language="en"
    )
    
    try:
        response = await generate_outline(request)
        logger.info(f"Service integration response type: {type(response)}")
        logger.info(f"Service integration slides count: {len(response.slides)}")
        
        for i, slide in enumerate(response.slides):
            logger.info(f"Service slide {i+1}: title='{slide.title}', bullets={len(slide.bullets)}, has_image={slide.image is not None}, has_notes={bool(slide.notes)}")
            if slide.image:
                logger.info(f"Service slide {i+1} image: {slide.image}")
            if slide.notes:
                logger.info(f"Service slide {i+1} notes: {slide.notes[:100]}...")
        
        logger.info("✓ Service integration test passed")
        
    except Exception as e:
        logger.error(f"Service integration test exception: {e}")
        pytest.fail(f"Service integration test exception: {e}")
    
    logger.info("=== Comprehensive LLM Diagnostic Test Complete ===")


@pytest.mark.asyncio
@pytest.mark.live
@pytest.mark.live_llm
async def test_llm_image_generation_specific(require_live_llm, no_http_mocks):
    """
    Specific test to focus on image generation in LLM responses.
    """
    logger.info("=== Starting LLM Image Generation Test ===")
    
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-4o-mini")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Test payload specifically requesting images
    image_payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You generate presentation slide outlines with comprehensive speaker notes and images. "
                    "Respond ONLY with strict JSON matching this schema: "
                    "{\"slides\":[{\"title\":string,\"bullets\":[string],\"image\":{\"url\":string,\"altText\":string,\"provider\":string},\"notes\":string}],\"sessionId\"?:string}. "
                    "IMPORTANT: Every slide MUST include an image with a real, publicly accessible URL. "
                    "Use high-quality, relevant images from public sources like Unsplash, Pexels, or similar. "
                    "Requirements: bullets must be concise; detailed content belongs in 'notes' to avoid on-slide truncation."
                ),
            },
            {
                "role": "user",
                "content": "Create 1 slide about: Machine Learning. Language: en. Include a relevant image and comprehensive speaker notes.",
            },
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }
    
    logger.info(f"Image test payload: {json.dumps(image_payload, indent=2)}")
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0, headers=headers) as client:
        try:
            resp = await client.post("/chat/completions", json=image_payload)
            logger.info(f"Image test response status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Image test response: {json.dumps(data, indent=2)}")
                
                content = data["choices"][0].get("message", {}).get("content", "")
                logger.info(f"Image test content: {content}")
                
                ok, parsed_obj = _extract_first_json_object(content)
                if ok and isinstance(parsed_obj, dict):
                    slides = parsed_obj.get("slides", [])
                    logger.info(f"Found {len(slides)} slides in image test")
                    
                    for i, slide in enumerate(slides):
                        logger.info(f"Image test slide {i+1}: {json.dumps(slide, indent=2)}")
                        
                        if "image" in slide:
                            image = slide["image"]
                            logger.info(f"✓ Slide {i+1} has image: {image}")
                            
                            # Validate image structure
                            assert "url" in image, f"Image missing URL: {image}"
                            assert "altText" in image, f"Image missing altText: {image}"
                            assert "provider" in image, f"Image missing provider: {image}"
                            
                            # Check if URL is accessible
                            try:
                                img_resp = await client.get(image["url"])
                                logger.info(f"Image URL status: {img_resp.status_code}")
                                if img_resp.status_code == 200:
                                    logger.info(f"✓ Image URL is accessible: {image['url']}")
                                else:
                                    logger.warning(f"⚠ Image URL returned {img_resp.status_code}: {image['url']}")
                            except Exception as e:
                                logger.warning(f"⚠ Could not verify image URL {image['url']}: {e}")
                        else:
                            logger.error(f"✗ Slide {i+1} missing image")
                            pytest.fail(f"Slide {i+1} missing required image")
                    
                    logger.info("✓ LLM Image Generation Test passed")
                else:
                    logger.error(f"Failed to extract valid JSON from content: {content}")
                    pytest.fail("LLM Image Generation Test failed: invalid JSON")
            else:
                logger.error(f"Image test failed with status {resp.status_code}: {resp.text}")
                pytest.fail(f"LLM Image Generation Test failed: {resp.status_code}")
                
        except Exception as e:
            logger.error(f"LLM Image Generation Test exception: {e}")
            pytest.fail(f"LLM Image Generation Test exception: {e}")
    
    logger.info("=== LLM Image Generation Test Complete ===")
