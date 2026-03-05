import logging
from fastapi import APIRouter, HTTPException, status, Depends

from models import QuestionGenerationRequest, APIResponse
from services.ai_service_factory import get_ai_service
from utils.auth_dependencies import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["questions"])

# Get AI service (switches between OpenAI and SarvamAI based on env variable)
ai_service = get_ai_service()


@router.post("/generate-questions", response_model=APIResponse)
async def generate_questions(
    request: QuestionGenerationRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    Generate questions using OpenAI API
    
    This endpoint creates a comprehensive set of questions covering specified chapters
    with various difficulty levels and question types suitable for the target class.
    """
    try:
        logger.info(f"Generating questions for {request.subject_name} - Class {request.class_name}")
        
        # Call AI service
        success, parsed_result, error = await ai_service.generate_questions(
            class_name=request.class_name,
            subject_name=request.subject_name,
            chapters=request.chapters,
            total_marks=request.total_marks
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