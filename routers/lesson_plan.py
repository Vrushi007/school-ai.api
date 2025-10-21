import logging
from fastapi import APIRouter, HTTPException, status

from models import LessonPlanRequest, APIResponse
from openai_service import OpenAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["lesson-plan"])

# Initialize OpenAI service
openai_service = OpenAIService()


@router.post("/generate-lesson-plan", response_model=APIResponse)
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