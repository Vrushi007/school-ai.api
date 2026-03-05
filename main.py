from fastapi import HTTPException

from config import create_app, get_logger
from exceptions import http_exception_handler, general_exception_handler
from routers import health, lesson_planning, questions, student, knowledge_points

# Initialize FastAPI app
app = create_app()
logger = get_logger()

# Include routers
app.include_router(health.router)
app.include_router(lesson_planning.router)
app.include_router(questions.router)
app.include_router(student.router)
app.include_router(knowledge_points.router)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)