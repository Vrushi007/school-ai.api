import os
import logging
from typing import Optional
from services.ai_provider_base import AIServiceProvider
from services.openai_provider import OpenAIProvider
from services.sarvam_provider import SarvamAIProvider
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AIServiceFactory:
    """
    Factory class for creating AI service provider instances.
    Determines which provider to use based on environment configuration.
    """
    
    _instance: Optional[AIServiceProvider] = None
    _provider_type: Optional[str] = None
    
    @classmethod
    def get_service(cls) -> AIServiceProvider:
        """
        Get the configured AI service provider instance.
        
        Returns:
            AIServiceProvider: Instance of the configured provider (OpenAI or SarvamAI)
        
        Raises:
            ValueError: If AI_PROVIDER is not set or is invalid
        """
        provider_type = os.getenv("AI_PROVIDER", "openai").lower()
        
        # Return cached instance if provider hasn't changed
        if cls._instance is not None and cls._provider_type == provider_type:
            return cls._instance
        
        # Create new instance based on provider type
        if provider_type == "openai":
            logger.info("Initializing OpenAI provider")
            cls._instance = OpenAIProvider()
            cls._provider_type = "openai"
        elif provider_type == "sarvam" or provider_type == "sarvam-ai":
            logger.info("Initializing SarvamAI provider")
            cls._instance = SarvamAIProvider()
            cls._provider_type = provider_type
        else:
            raise ValueError(
                f"Invalid AI_PROVIDER value: '{provider_type}'. "
                "Supported values are: 'openai', 'sarvam'"
            )
        
        logger.info(f"AI Service Provider: {provider_type}")
        return cls._instance
    
    @classmethod
    def get_service_by_provider(cls, provider: str) -> AIServiceProvider:
        """
        Get a specific AI service provider instance.
        Does not cache - creates a new instance each time.
        
        Args:
            provider: Provider name ('openai' or 'sarvam')
        
        Returns:
            AIServiceProvider: Instance of the specified provider
        
        Raises:
            ValueError: If provider is invalid
        """
        provider_lower = provider.lower()
        
        if provider_lower == "openai":
            logger.info(f"Creating OpenAI provider instance (requested: {provider})")
            return OpenAIProvider()
        elif provider_lower == "sarvam" or provider_lower == "sarvam-ai":
            logger.info(f"Creating SarvamAI provider instance (requested: {provider})")
            return SarvamAIProvider()
        else:
            raise ValueError(
                f"Invalid provider value: '{provider}'. "
                "Supported values are: 'openai', 'sarvam'"
            )
    
    @classmethod
    def reset(cls):
        """
        Reset the cached instance. Useful for testing or switching providers at runtime.
        """
        cls._instance = None
        cls._provider_type = None


def get_ai_service(provider: Optional[str] = None) -> AIServiceProvider:
    """
    Convenience function to get the AI service instance.
    
    Args:
        provider: Optional provider name. If not specified, uses AI_PROVIDER env variable
    
    Usage in routers:
        from services.ai_service_factory import get_ai_service
        
        # Use env variable
        ai_service = get_ai_service()
        
        # Use specific provider
        ai_service = get_ai_service(provider="sarvam")
        
        result = await ai_service.generate_lesson_plan(...)
    
    Returns:
        AIServiceProvider: The configured AI service provider
    """
    if provider:
        return AIServiceFactory.get_service_by_provider(provider)
    return AIServiceFactory.get_service()
