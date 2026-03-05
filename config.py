import logging
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)


class AIProviderConfig:
    """Configuration class for AI provider selection"""
    
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "openai").lower()
        
        if self.provider not in ["openai", "sarvam", "sarvam-ai"]:
            raise ValueError(
                f"Invalid AI_PROVIDER: '{self.provider}'. "
                "Supported values are: 'openai', 'sarvam'"
            )
    
    @property
    def is_openai(self) -> bool:
        """Check if OpenAI is the configured provider"""
        return self.provider == "openai"
    
    @property
    def is_sarvam(self) -> bool:
        """Check if SarvamAI is the configured provider"""
        return self.provider in ["sarvam", "sarvam-ai"]


class OpenAIConfig:
    """Configuration class for OpenAI settings"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_default = os.getenv("OPENAI_MODEL_DEFAULT", "gpt-4o-mini")
        self.model_5 = os.getenv("OPENAI_MODEL_5", "gpt-4o-mini")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    @property
    def model_name(self) -> str:
        """Get the default OpenAI model name"""
        return self.model_default
    
    @property
    def model_name_5(self) -> str:
        """Get the OpenAI model for knowledge points"""
        return self.model_5


class SarvamAIConfig:
    """Configuration class for SarvamAI settings"""
    
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        self.model_default = os.getenv("SARVAM_MODEL_DEFAULT", "sarvam-2b-v0.5")
        self.model_5 = os.getenv("SARVAM_MODEL_5", "sarvam-2b-v0.5")
        
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY environment variable is not set")
    
    @property
    def model_name(self) -> str:
        """Get the default SarvamAI model name"""
        return self.model_default
    
    @property
    def model_name_5(self) -> str:
        """Get the SarvamAI model for knowledge points"""
        return self.model_5


# Global configuration instances
ai_provider_config = AIProviderConfig()

# Initialize only the required provider config
openai_config = None
sarvam_config = None

if ai_provider_config.is_openai:
    openai_config = OpenAIConfig()
elif ai_provider_config.is_sarvam:
    sarvam_config = SarvamAIConfig()

# Initialize both configs for dynamic provider switching support
# This allows UI to switch between providers regardless of default AI_PROVIDER
try:
    if openai_config is None:
        openai_config = OpenAIConfig()
except Exception as e:
    logger.warning(f"OpenAI config initialization failed: {e}. OpenAI provider will not be available.")

try:
    if sarvam_config is None:
        sarvam_config = SarvamAIConfig()
except Exception as e:
    logger.warning(f"SarvamAI config initialization failed: {e}. SarvamAI provider will not be available.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="School AI API",
        description="AI-powered educational content generation API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


def get_logger():
    """Get the configured logger"""
    return logger


def get_ai_provider_config() -> AIProviderConfig:
    """Get the AI provider configuration instance"""
    return ai_provider_config


def get_openai_config() -> OpenAIConfig:
    """Get the OpenAI configuration instance"""
    if openai_config is None:
        raise RuntimeError(
            "OpenAI is not configured. Please set OPENAI_API_KEY in environment. "
            "Check that the API key is valid and properly configured."
        )
    return openai_config


def get_sarvam_config() -> SarvamAIConfig:
    """Get the SarvamAI configuration instance"""
    if sarvam_config is None:
        raise RuntimeError(
            "SarvamAI is not configured. Please set SARVAM_API_KEY in environment. "
            "Check that the API key is valid and properly configured."
        )
    return sarvam_config