import logging
from fastapi import APIRouter, HTTPException, status

from helpers.youtube import YouTubeHelper
from models import LessonPlanRequest, DetailedSessionRequest, APIResponse
from openai_service import OpenAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["lesson-planning"])

# Initialize OpenAI service
openai_service = OpenAIService()
youtube_service = YouTubeHelper()


@router.post("/generate-lesson-plan", response_model=APIResponse)
async def generate_lesson_plan(request: LessonPlanRequest):
    """
    Generate a lesson plan using OpenAI API
    
    This endpoint creates a structured lesson plan with multiple sessions
    based on the provided subject, class, chapter, and session requirements.
    This provides the summary/overview of the lesson plan.
    """
    try:
        logger.info(f"Generating lesson plan for {request.subject_name} - {request.chapter_title}")
        
        # Call OpenAI service
        success, parsed_result, error = await openai_service.generate_lesson_plan(
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


@router.post("/generate-detailed-content-for-session", response_model=APIResponse)
async def generate_session_content(request: DetailedSessionRequest):
    """
    Generate detailed content for a specific session using OpenAI API
    
    This endpoint creates comprehensive lesson content including introduction,
    main content, activities, assessment, resources, and differentiation strategies.
    This provides the detailed content for a specific session from the lesson plan.
    
    Returns the raw JSON response from OpenAI for the UI to parse and handle.
    """
    try:
        logger.info(f"Generating session content for: {request.session_data.title}")
        
        # Convert session_data to dict for the service
        session_data_dict = request.session_data.dict()
        
        # Call OpenAI service to get response
        response = await openai_service.generate_detailed_session_content(
            session_data=session_data_dict,
            subject_name=request.subject_name,
            class_name=request.class_name
        )

        keywords = response["resources"]["youtubeSearchKeywords"]
        youtube_results = youtube_service.search_videos_by_keywords(keywords)

        response["resources"]["youtubeVideos"] = youtube_results
        
        logger.info(f"Generated session content for: {request.session_data.title}")
        return APIResponse(
            success=True,
            data={
                "content": response,
                "metadata": {
                    "session_title": request.session_data.title,
                    "subject": request.subject_name,
                    "class": request.class_name,
                    "duration": request.session_data.duration,
                    "objectives_count": len(request.session_data.objectives) if request.session_data.objectives else 0
                }
            },
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