#!/usr/bin/env python3
"""
LLM Diagnostic Script

This script runs comprehensive diagnostics on the LLM service to identify
why we're not getting actual images and responses from the LLMs.

Usage:
    python scripts/run_llm_diagnostics.py

Environment Variables Required:
    - OPENROUTER_API_KEY: Your OpenRouter API key
    - STABILITY_API_KEY: Your Stability AI API key (optional)
    - RUN_LIVE_LLM=1: Enable live LLM tests
    - RUN_LIVE_IMAGES=1: Enable live image tests

Output:
    - Detailed logs to console
    - Diagnostic report to llm_diagnostic_report.txt
"""

import os
import sys
import asyncio
import logging
import json
import httpx
from datetime import datetime
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.models.chat import ChatRequest
from app.services.llm import generate_outline, _call_openrouter, _extract_first_json_object
from app.core.config import settings

# Set up comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('llm_diagnostic_report.txt', mode='w')
    ]
)

logger = logging.getLogger(__name__)

class DiagnosticReport:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        
    def add_result(self, test_name: str, success: bool, details: str, error: str = None):
        self.results.append({
            'test_name': test_name,
            'success': success,
            'details': details,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
        
    def print_summary(self):
        print("\n" + "="*80)
        print("LLM DIAGNOSTIC REPORT SUMMARY")
        print("="*80)
        print(f"Start Time: {self.start_time}")
        print(f"End Time: {datetime.now()}")
        print(f"Total Tests: {len(self.results)}")
        
        passed = sum(1 for r in self.results if r['success'])
        failed = len(self.results) - passed
        
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print("\nFAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  ❌ {result['test_name']}: {result['error']}")
        
        print("\nDETAILED RESULTS:")
        for result in self.results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test_name']}")
            print(f"     Details: {result['details']}")
            if result['error']:
                print(f"     Error: {result['error']}")
            print()

async def test_environment_configuration(report: DiagnosticReport):
    """Test 1: Environment Configuration"""
    logger.info("=== Test 1: Environment Configuration ===")
    
    try:
        # Check required environment variables
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        stability_key = os.getenv('STABILITY_API_KEY')
        run_live_llm = os.getenv('RUN_LIVE_LLM') == '1'
        run_live_images = os.getenv('RUN_LIVE_IMAGES') == '1'
        
        logger.info(f"OPENROUTER_API_KEY present: {bool(openrouter_key)}")
        logger.info(f"STABILITY_API_KEY present: {bool(stability_key)}")
        logger.info(f"RUN_LIVE_LLM: {run_live_llm}")
        logger.info(f"RUN_LIVE_IMAGES: {run_live_images}")
        
        # Check settings
        logger.info(f"Settings OPENROUTER_API_KEY: {bool(settings.OPENROUTER_API_KEY)}")
        logger.info(f"Settings STABILITY_API_KEY: {bool(settings.STABILITY_API_KEY)}")
        logger.info(f"Settings OPENROUTER_BASE_URL: {settings.OPENROUTER_BASE_URL}")
        logger.info(f"Settings OPENROUTER_DEFAULT_MODEL: {settings.OPENROUTER_DEFAULT_MODEL}")
        logger.info(f"Settings OPENROUTER_REQUIRE_UPSTREAM: {settings.OPENROUTER_REQUIRE_UPSTREAM}")
        
        success = bool(openrouter_key) and run_live_llm
        details = f"OpenRouter key: {'✓' if openrouter_key else '✗'}, Live LLM: {'✓' if run_live_llm else '✗'}"
        
        report.add_result("Environment Configuration", success, details)
        
    except Exception as e:
        logger.error(f"Environment configuration test failed: {e}")
        report.add_result("Environment Configuration", False, "Exception occurred", str(e))

async def test_direct_api_connectivity(report: DiagnosticReport):
    """Test 2: Direct API Connectivity"""
    logger.info("=== Test 2: Direct API Connectivity ===")
    
    try:
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-4o-mini")
        
        if not api_key:
            report.add_result("Direct API Connectivity", False, "No API key available")
            return
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        # Simple test payload
        simple_payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Return the word PONG"}
            ],
            "temperature": 0,
        }
        
        logger.info(f"Testing direct API call to {base_url}")
        logger.info(f"Payload: {json.dumps(simple_payload, indent=2)}")
        
        async with httpx.AsyncClient(base_url=base_url, timeout=30.0, headers=headers) as client:
            resp = await client.post("/chat/completions", json=simple_payload)
            
            logger.info(f"Response status: {resp.status_code}")
            logger.info(f"Response headers: {dict(resp.headers)}")
            
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Response: {json.dumps(data, indent=2)}")
                
                content = data["choices"][0].get("message", {}).get("content", "")
                logger.info(f"Content: {content}")
                
                if "PONG" in content:
                    report.add_result("Direct API Connectivity", True, f"Successfully got response: {content}")
                else:
                    report.add_result("Direct API Connectivity", False, f"Unexpected content: {content}")
            else:
                error_msg = f"HTTP {resp.status_code}: {resp.text}"
                logger.error(error_msg)
                report.add_result("Direct API Connectivity", False, f"HTTP error", error_msg)
                
    except Exception as e:
        logger.error(f"Direct API connectivity test failed: {e}")
        report.add_result("Direct API Connectivity", False, "Exception occurred", str(e))

async def test_structured_slide_generation(report: DiagnosticReport):
    """Test 3: Structured Slide Generation"""
    logger.info("=== Test 3: Structured Slide Generation ===")
    
    try:
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-4o-mini")
        
        if not api_key:
            report.add_result("Structured Slide Generation", False, "No API key available")
            return
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        # Structured test payload
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
        
        logger.info(f"Testing structured slide generation")
        logger.info(f"Payload: {json.dumps(structured_payload, indent=2)}")
        
        async with httpx.AsyncClient(base_url=base_url, timeout=30.0, headers=headers) as client:
            resp = await client.post("/chat/completions", json=structured_payload)
            
            logger.info(f"Response status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Response: {json.dumps(data, indent=2)}")
                
                content = data["choices"][0].get("message", {}).get("content", "")
                logger.info(f"Content: {content}")
                
                # Test JSON extraction
                ok, parsed_obj = _extract_first_json_object(content)
                logger.info(f"JSON extraction result: ok={ok}, parsed_obj type={type(parsed_obj)}")
                
                if ok and isinstance(parsed_obj, dict):
                    logger.info(f"Parsed JSON: {json.dumps(parsed_obj, indent=2)}")
                    
                    # Validate structure
                    slides = parsed_obj.get("slides", [])
                    logger.info(f"Found {len(slides)} slides in response")
                    
                    has_images = 0
                    has_notes = 0
                    
                    for i, slide in enumerate(slides):
                        logger.info(f"Slide {i+1}: {json.dumps(slide, indent=2)}")
                        
                        # Check for images
                        if "image" in slide:
                            image = slide["image"]
                            logger.info(f"Slide {i+1} has image: {image}")
                            has_images += 1
                        
                        # Check for notes
                        if "notes" in slide and slide["notes"]:
                            logger.info(f"Slide {i+1} has notes: {slide['notes'][:100]}...")
                            has_notes += 1
                    
                    details = f"Generated {len(slides)} slides, {has_images} with images, {has_notes} with notes"
                    report.add_result("Structured Slide Generation", True, details)
                else:
                    report.add_result("Structured Slide Generation", False, f"Failed to extract valid JSON from content: {content}")
            else:
                error_msg = f"HTTP {resp.status_code}: {resp.text}"
                logger.error(error_msg)
                report.add_result("Structured Slide Generation", False, f"HTTP error", error_msg)
                
    except Exception as e:
        logger.error(f"Structured slide generation test failed: {e}")
        report.add_result("Structured Slide Generation", False, "Exception occurred", str(e))

async def test_service_integration(report: DiagnosticReport):
    """Test 4: Service Integration"""
    logger.info("=== Test 4: Service Integration ===")
    
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-4o-mini")
        
        if not api_key:
            report.add_result("Service Integration", False, "No API key available")
            return
        
        request = ChatRequest(
            prompt="Artificial Intelligence",
            slide_count=2,
            model=model,
            language="en"
        )
        
        logger.info(f"Testing service integration with request: {request.prompt}")
        
        response = await generate_outline(request)
        logger.info(f"Service response type: {type(response)}")
        logger.info(f"Service response slides count: {len(response.slides)}")
        
        has_images = 0
        has_notes = 0
        
        for i, slide in enumerate(response.slides):
            logger.info(f"Service slide {i+1}: title='{slide.title}', bullets={len(slide.bullets)}, has_image={slide.image is not None}, has_notes={bool(slide.notes)}")
            if slide.image:
                logger.info(f"Service slide {i+1} image: {slide.image}")
                has_images += 1
            if slide.notes:
                logger.info(f"Service slide {i+1} notes: {slide.notes[:100]}...")
                has_notes += 1
        
        details = f"Generated {len(response.slides)} slides, {has_images} with images, {has_notes} with notes"
        report.add_result("Service Integration", True, details)
        
    except Exception as e:
        logger.error(f"Service integration test failed: {e}")
        report.add_result("Service Integration", False, "Exception occurred", str(e))

async def test_image_generation_specific(report: DiagnosticReport):
    """Test 5: Image Generation Specific"""
    logger.info("=== Test 5: Image Generation Specific ===")
    
    try:
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-4o-mini")
        
        if not api_key:
            report.add_result("Image Generation Specific", False, "No API key available")
            return
        
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
        
        logger.info(f"Testing image generation specific")
        logger.info(f"Payload: {json.dumps(image_payload, indent=2)}")
        
        async with httpx.AsyncClient(base_url=base_url, timeout=30.0, headers=headers) as client:
            resp = await client.post("/chat/completions", json=image_payload)
            
            logger.info(f"Response status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Response: {json.dumps(data, indent=2)}")
                
                content = data["choices"][0].get("message", {}).get("content", "")
                logger.info(f"Content: {content}")
                
                ok, parsed_obj = _extract_first_json_object(content)
                if ok and isinstance(parsed_obj, dict):
                    slides = parsed_obj.get("slides", [])
                    logger.info(f"Found {len(slides)} slides in image test")
                    
                    all_have_images = True
                    accessible_images = 0
                    
                    for i, slide in enumerate(slides):
                        logger.info(f"Image test slide {i+1}: {json.dumps(slide, indent=2)}")
                        
                        if "image" in slide:
                            image = slide["image"]
                            logger.info(f"✓ Slide {i+1} has image: {image}")
                            
                            # Validate image structure
                            if "url" in image and "altText" in image and "provider" in image:
                                # Check if URL is accessible
                                try:
                                    img_resp = await client.get(image["url"])
                                    logger.info(f"Image URL status: {img_resp.status_code}")
                                    if img_resp.status_code == 200:
                                        logger.info(f"✓ Image URL is accessible: {image['url']}")
                                        accessible_images += 1
                                    else:
                                        logger.warning(f"⚠ Image URL returned {img_resp.status_code}: {image['url']}")
                                except Exception as e:
                                    logger.warning(f"⚠ Could not verify image URL {image['url']}: {e}")
                            else:
                                logger.error(f"✗ Slide {i+1} image missing required fields")
                                all_have_images = False
                        else:
                            logger.error(f"✗ Slide {i+1} missing image")
                            all_have_images = False
                    
                    details = f"Generated {len(slides)} slides, all have images: {all_have_images}, accessible images: {accessible_images}"
                    report.add_result("Image Generation Specific", all_have_images, details)
                else:
                    report.add_result("Image Generation Specific", False, f"Failed to extract valid JSON from content: {content}")
            else:
                error_msg = f"HTTP {resp.status_code}: {resp.text}"
                logger.error(error_msg)
                report.add_result("Image Generation Specific", False, f"HTTP error", error_msg)
                
    except Exception as e:
        logger.error(f"Image generation specific test failed: {e}")
        report.add_result("Image Generation Specific", False, "Exception occurred", str(e))

async def main():
    """Run all diagnostic tests"""
    logger.info("Starting LLM Diagnostic Tests")
    logger.info(f"Timestamp: {datetime.now()}")
    
    report = DiagnosticReport()
    
    # Run all tests
    await test_environment_configuration(report)
    await test_direct_api_connectivity(report)
    await test_structured_slide_generation(report)
    await test_service_integration(report)
    await test_image_generation_specific(report)
    
    # Print summary
    report.print_summary()
    
    logger.info("LLM Diagnostic Tests Complete")

if __name__ == "__main__":
    asyncio.run(main())
