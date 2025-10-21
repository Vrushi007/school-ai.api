from fastapi import HTTPException

from config import create_app, get_logger
from exceptions import http_exception_handler, general_exception_handler
from routers import health, lesson_planning, questions

# Initialize FastAPI app
app = create_app()
logger = get_logger()

# Include routers
app.include_router(health.router)
app.include_router(lesson_planning.router)
app.include_router(questions.router)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


def start_server():
    """Start the FastAPI server"""
    import uvicorn
    import os
    
    # Use PORT environment variable if available (for hosting platforms like Render)
    # Otherwise default to 8000 for local development
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disabled reload to avoid multiprocessing issues on macOS with Python 3.13
        log_level="info"
    )


if __name__ == "__main__":
    start_server()