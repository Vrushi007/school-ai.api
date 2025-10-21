import logging
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(request, exc: HTTPException):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": "HTTP error occurred",
            "error": exc.detail
        }
    )


async def general_exception_handler(request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error": "An unexpected error occurred"
        }
    )