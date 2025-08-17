"""
Image provider interface and factory for multi-provider image generation.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.models.slides import SlidePlan, ImageMeta

class ImageProvider(ABC):
    """Abstract base class for image providers."""
    
    @abstractmethod
    async def generate_image(self, slide: SlidePlan, style: Optional[str] = None) -> ImageMeta:
        """Generate an image for a slide."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available (API key configured, etc.)."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass

class ImageProviderFactory:
    """Factory for creating image providers."""
    
    _providers: Dict[str, type[ImageProvider]] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type[ImageProvider]) -> None:
        """Register a provider class."""
        cls._providers[name] = provider_class
    
    @classmethod
    def get_provider(cls, name: str) -> Optional[ImageProvider]:
        """Get a provider instance by name."""
        if name not in cls._providers:
            return None
        return cls._providers[name]()
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, ImageProvider]:
        """Get all available providers."""
        available = {}
        for name, provider_class in cls._providers.items():
            provider = provider_class()
            if provider.is_available():
                available[name] = provider
        return available
    
    @classmethod
    def list_providers(cls) -> list[str]:
        """List all registered provider names."""
        return list(cls._providers.keys())

