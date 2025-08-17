"""
Image provider registry for managing available providers.
"""
import logging
from typing import Optional, List, Dict
from . import ImageProvider, ImageProviderFactory
from .stability import StabilityProvider
from .dalle import DalleProvider

logger = logging.getLogger(__name__)

def register_providers():
    """Register all available image providers."""
    logger.info("Registering image providers...")
    
    # Register Stability AI provider
    ImageProviderFactory.register_provider("stability-ai", StabilityProvider)
    logger.info("Registered Stability AI provider")
    
    # Register DALL-E provider
    ImageProviderFactory.register_provider("dalle", DalleProvider)
    logger.info("Registered DALL-E provider")
    
    # Log available providers
    available = ImageProviderFactory.get_available_providers()
    logger.info(f"Available providers: {list(available.keys())}")

def get_provider(name: str) -> Optional[ImageProvider]:
    """Get a specific provider by name."""
    return ImageProviderFactory.get_provider(name)

def get_available_providers() -> Dict[str, ImageProvider]:
    """Get all available providers."""
    return ImageProviderFactory.get_available_providers()

def get_best_available_provider(preferred_provider: Optional[str] = None) -> Optional[ImageProvider]:
    """Get the best available provider, with fallback logic."""
    from app.core.config import settings
    
    available = get_available_providers()
    
    if not available:
        logger.warning("No image providers available")
        return None
    
    # If preferred provider is specified and available, use it
    if preferred_provider and preferred_provider in available:
        logger.info(f"Using preferred provider: {preferred_provider}")
        return available[preferred_provider]
    
    # Try default provider
    default_provider = settings.DEFAULT_IMAGE_PROVIDER
    if default_provider in available:
        logger.info(f"Using default provider: {default_provider}")
        return available[default_provider]
    
    # Try fallback order
    for provider_name in settings.IMAGE_PROVIDER_FALLBACK_ORDER:
        if provider_name in available:
            logger.info(f"Using fallback provider: {provider_name}")
            return available[provider_name]
    
    # Use first available provider
    first_available = list(available.keys())[0]
    logger.info(f"Using first available provider: {first_available}")
    return available[first_available]

def list_providers() -> List[str]:
    """List all registered provider names."""
    return ImageProviderFactory.list_providers()

def get_provider_status() -> Dict[str, bool]:
    """Get status of all providers (available/not available)."""
    all_providers = ImageProviderFactory.list_providers()
    status = {}
    
    for provider_name in all_providers:
        provider = ImageProviderFactory.get_provider(provider_name)
        status[provider_name] = provider.is_available() if provider else False
    
    return status

