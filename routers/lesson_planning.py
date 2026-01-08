import logging
from fastapi import APIRouter, HTTPException, status

from helpers.youtube import YouTubeHelper
from models import LessonPlanRequest, DetailedSessionRequest, GroupKPsRequest, SessionSummaryRequest, APIResponse
from services.openai_service import OpenAIService

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
        logger.info(f"Generating session content for: {request.title}")
        
        # Call OpenAI service to get response
        response = await openai_service.generate_detailed_session_content(
            title=request.title,
            subject_name=request.subject_name,
            class_name=request.class_name,
            duration=request.duration,
            summary=request.summary,
            objectives=request.objectives,
            kp_list_with_description=request.kp_list
        )

        keywords = response["resources"]["youtubeSearchKeywords"]
        youtube_results = youtube_service.search_videos_by_keywords(keywords)

        response["resources"]["youtubeVideos"] = youtube_results
        
        logger.info(f"Generated session content for: {request.title}")
        return APIResponse(
            success=True,
            data={
                "content": response,
                "metadata": {
                    "session_title": request.title,
                    "subject": request.subject_name,
                    "class": request.class_name,
                    "duration": request.duration,
                    "objectives_count": len(request.objectives)
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


@router.post("/group-kps-into-sessions", response_model=APIResponse)
async def group_kps_into_sessions(request: GroupKPsRequest):
    """
    Group knowledge points into teaching sessions using AI
    
    This endpoint takes a list of knowledge points and intelligently groups them
    into the specified number of teaching sessions, respecting prerequisite
    dependencies and maintaining a coherent learning progression.
    
    Returns sessions with session numbers, titles, and associated KP IDs.
    """
    try:
        logger.info(f"Grouping KPs into {request.number_of_sessions} sessions for {request.board} {request.subject} - {request.chapter}")
        
        # Convert Pydantic models to dicts for service layer
        kps_as_dicts = [kp.dict() for kp in request.knowledge_points]
        
        # Call OpenAI service with board parameter
        success, parsed_result, error = await openai_service.group_kps_into_sessions(
            board=request.board,
            chapter=request.chapter,
            class_name=request.class_name,
            subject=request.subject,
            number_of_sessions=request.number_of_sessions,
            session_duration=request.session_duration,
            knowledge_points=kps_as_dicts
        )
        
        if not success:
            logger.error(f"Failed to group KPs: {error}")
            return APIResponse(
                success=False,
                message="Failed to parse AI response",
                error=f"JSON parsing error: {error}",
                data={"raw_response": parsed_result}  # Include raw response for debugging
            )
        
        return APIResponse(
            success=True,
            data={
                "sessions": parsed_result.get("sessions", []),
                "metadata": {
                    "board": request.board,
                    "chapter": request.chapter,
                    "subject": request.subject,
                    "class": request.class_name,
                    "total_sessions": request.number_of_sessions,
                    "total_kps": len(request.knowledge_points)
                }
            },
            message="Knowledge points grouped into sessions successfully"
        )
        
    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service configuration error"
        )
    except Exception as e:
        logger.error(f"Error grouping KPs into sessions: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to group knowledge points",
            error=str(e)
        )


@router.post("/generate-session-summary", response_model=APIResponse)
async def generate_session_summary(request: SessionSummaryRequest):
    """
    Generate a concise instructional overview for a teaching session
    
    This endpoint takes a session title and list of knowledge points and generates
    a teacher-focused summary and instructional objectives. The output is designed
    for teacher preparation, not student-facing materials.
    
    Returns a summary (2-4 sentences) and objectives (2-4 items).
    """
    try:
        logger.info(f"Generating session summary for: {request.session_title} ({request.board} {request.subject})")
        
        # Convert Pydantic models to dicts for service layer
        kps_as_dicts = [kp.dict() for kp in request.knowledge_points]
        
        # Call OpenAI service
        success, parsed_result, error = await openai_service.generate_session_summary(
            board=request.board,
            chapter=request.chapter,
            class_name=request.class_name,
            subject=request.subject,
            session_title=request.session_title,
            knowledge_points=kps_as_dicts
        )
        
        if not success:
            logger.error(f"Failed to generate session summary: {error}")
            return APIResponse(
                success=False,
                message="Failed to parse AI response",
                error=f"JSON parsing error: {error}",
                data={"raw_response": parsed_result}  # Include raw response for debugging
            )
        
        return APIResponse(
            success=True,
            data={
                "summary": parsed_result.get("summary", ""),
                "objectives": parsed_result.get("objectives", []),
                "metadata": {
                    "board": request.board,
                    "chapter": request.chapter,
                    "class": request.class_name,
                    "subject": request.subject,
                    "session_title": request.session_title,
                    "total_kps": len(request.knowledge_points)
                }
            },
            message="Session summary generated successfully"
        )
        
    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service configuration error"
        )
    except Exception as e:
        logger.error(f"Error generating session summary: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to generate session summary",
            error=str(e)
        )