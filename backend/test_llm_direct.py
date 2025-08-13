#!/usr/bin/env python3
"""
Direct LLM Test Script

This script directly tests the LLM service without needing the full FastAPI server.
It loads environment variables from .env and tests the LLM integration.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_llm_direct():
    """Test the LLM service directly"""
    try:
        # Import after setting up the path
        from app.models.chat import ChatRequest
        from app.services.llm import generate_outline
        from app.core.config import settings
        
        logger.info("=== Direct LLM Test ===")
        logger.info(f"Settings OPENROUTER_API_KEY: {bool(settings.OPENROUTER_API_KEY)}")
        logger.info(f"Settings OPENROUTER_BASE_URL: {settings.OPENROUTER_BASE_URL}")
        logger.info(f"Settings OPENROUTER_DEFAULT_MODEL: {settings.OPENROUTER_DEFAULT_MODEL}")
        logger.info(f"Settings OPENROUTER_REQUIRE_UPSTREAM: {settings.OPENROUTER_REQUIRE_UPSTREAM}")
        
        if not settings.OPENROUTER_API_KEY:
            logger.error("❌ No OpenRouter API key found in settings")
            return False
            
        # Create a test request
        request = ChatRequest(
            prompt="Artificial Intelligence",
            slide_count=2,
            model=settings.OPENROUTER_DEFAULT_MODEL,
            language="en"
        )
        
        logger.info(f"Testing with request: {request.prompt}")
        
        # Call the LLM service
        response = await generate_outline(request)
        
        logger.info(f"✅ Success! Generated {len(response.slides)} slides")
        
        for i, slide in enumerate(response.slides):
            logger.info(f"Slide {i+1}: {slide.title}")
            logger.info(f"  Bullets: {len(slide.bullets)}")
            logger.info(f"  Has image: {slide.image is not None}")
            logger.info(f"  Has notes: {bool(slide.notes)}")
            
            if slide.image:
                logger.info(f"  Image: {slide.image}")
            if slide.notes:
                logger.info(f"  Notes: {slide.notes[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """Main test function"""
    logger.info("Starting direct LLM test...")
    
    success = await test_llm_direct()
    
    if success:
        logger.info("✅ Direct LLM test completed successfully!")
    else:
        logger.error("❌ Direct LLM test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
