import logging
from fastapi import APIRouter, HTTPException, status

from models import QuestionGenerationRequest, APIResponse
from openai_service import OpenAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["questions"])

# Initialize OpenAI service
openai_service = OpenAIService()


@router.post("/generate-questions", response_model=APIResponse)
async def generate_questions(request: QuestionGenerationRequest):
    """
    Generate questions using OpenAI API
    
    This endpoint creates a comprehensive set of questions covering specified chapters
    with various difficulty levels and question types suitable for the target class.
    """
    try:
        logger.info(f"Generating questions for {request.subject_name} - Class {request.class_name}")
        
        # Call OpenAI service
        success, parsed_result, error = await openai_service.generate_questions(
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