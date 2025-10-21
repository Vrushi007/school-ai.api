import logging
from fastapi import APIRouter, HTTPException, status

from models import DetailedSessionRequest, APIResponse
from openai_service import OpenAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["session-content"])

# Initialize OpenAI service
openai_service = OpenAIService()


@router.post("/generate-detailed-content-for-session", response_model=APIResponse)
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