import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import (
    LessonPlanRequest, 
    DetailedSessionRequest, 
    QuestionGenerationRequest,
    APIResponse,
    HealthResponse
)
from openai_service import OpenAIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
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

# Initialize OpenAI service
openai_service = OpenAIService()


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API health check"""
    return HealthResponse(
        status="healthy",
        message="School AI API is running successfully"
    )


@app.get("/health", response_model=HealthResponse)
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


@app.post("/api/generate-lesson-plan", response_model=APIResponse)
async def generate_lesson_plan(request: LessonPlanRequest):
    """
    Generate a lesson plan using OpenAI API
    
    This endpoint creates a structured lesson plan with multiple sessions
    based on the provided subject, class, chapter, and session requirements.
    """
    try:
        logger.info(f"Generating lesson plan for {request.subject_name} - {request.chapter_title}")
        
        # Call OpenAI service
        success, parsed_result, error = openai_service.generate_lesson_plan(
            subject_name=request.subject_name,
            class_name=request.class_name,
            chapter_title=request.chapter_title,
            number_of_sessions=request.number_of_sessions,
            default_session_duration=request.default_session_duration
        )
        
        if not success:
            logger.error(f"Failed to parse lesson plan response: {error}")
            return APIResponse(
                success=False,
                message="Failed to parse AI response",
                error=f"JSON parsing error: {error}",
                data={"raw_response": parsed_result}  # Include raw response for debugging
            )
        
        return APIResponse(
            success=True,
            data={"lesson_plan": parsed_result},
            message="Lesson plan generated successfully"
        )
        
    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service configuration error"
        )
    except Exception as e:
        logger.error(f"Error generating lesson plan: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to generate lesson plan",
            error=str(e)
        )


@app.post("/api/generate-detailed-content-for-session", response_model=APIResponse)
async def generate_session_content(request: DetailedSessionRequest):
    """
    Generate detailed content for a specific session using OpenAI API
    
    This endpoint creates comprehensive lesson content including introduction,
    main content, activities, assessment, resources, and differentiation strategies.
    """
    try:
        logger.info(f"Generating session content for: {request.session_data.title}")
        
        # Convert session_data to dict for the service
        session_data_dict = request.session_data.dict()
        
        # Call OpenAI service
        success, parsed_result, error = openai_service.generate_detailed_session_content(
            session_data=session_data_dict,
            subject_name=request.subject_name,
            class_name=request.class_name
        )
        
        if not success:
            logger.error(f"Failed to parse session content response: {error}")
            return APIResponse(
                success=False,
                message="Failed to parse AI response",
                error=f"JSON parsing error: {error}",
                data={"raw_response": parsed_result}  # Include raw response for debugging
            )
        
        return APIResponse(
            success=True,
            data={"session_content": parsed_result},
            message="Session content generated successfully"
        )
        
    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service configuration error"
        )
    except Exception as e:
        logger.error(f"Error generating session content: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to generate session content",
            error=str(e)
        )


@app.post("/api/generate-questions", response_model=APIResponse)
async def generate_questions(request: QuestionGenerationRequest):
    """
    Generate questions using OpenAI API
    
    This endpoint creates a comprehensive set of questions covering specified chapters
    with various difficulty levels and question types suitable for the target class.
    """
    try:
        logger.info(f"Generating questions for {request.subject_name} - Class {request.class_name}")
        
        # Call OpenAI service
        success, parsed_result, error = openai_service.generate_questions(
            class_name=request.class_name,
            subject_name=request.subject_name,
            chapters=request.chapters,
            question_requirements=request.question_requirements
        )
        
        if not success:
            logger.error(f"Failed to parse questions response: {error}")
            return APIResponse(
                success=False,
                message="Failed to parse AI response",
                error=f"JSON parsing error: {error}",
                data={"raw_response": parsed_result}  # Include raw response for debugging
            )
        
        return APIResponse(
            success=True,
            data={"questions": parsed_result},
            message="Questions generated successfully"
        )
        
    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service configuration error"
        )
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to generate questions",
            error=str(e)
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": "HTTP error occurred",
            "error": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabled reload to avoid multiprocessing issues on macOS with Python 3.13
        log_level="info"
    )