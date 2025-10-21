import logging
from fastapi import APIRouter, HTTPException, status

from models import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API health check"""
    return HealthResponse(
        status="healthy",
        message="School AI API is running successfully"
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Basic health check - could be extended to check OpenAI connectivity
        return HealthResponse(
            status="healthy", 
            message="API is operational"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )