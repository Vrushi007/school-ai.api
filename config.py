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


# Global configuration instance
openai_config = OpenAIConfig()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="School AI API",
        description="AI-powered educational content generation API using OpenAI",
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


def get_openai_config() -> OpenAIConfig:
    """Get the OpenAI configuration instance"""
    return openai_config