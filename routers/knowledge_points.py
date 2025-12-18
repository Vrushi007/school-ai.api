import logging
from fastapi import APIRouter, HTTPException, status

from models import KnowledgePointRequest, APIResponse
from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["knowledge-points"])

# Initialize OpenAI service
openai_service = OpenAIService()


@router.post("/generate-knowledge-points", response_model=APIResponse)
async def generate_knowledge_points(request: KnowledgePointRequest):
    """
    Generate knowledge points for a curriculum chapter using OpenAI API
    
    This endpoint decomposes curriculum content into atomic, teachable,
    and assessable Knowledge Points (KPs) aligned with CBSE/NCERT standards,
    Bloom's Taxonomy, and Item Response Theory (IRT) difficulty metrics.
    """
    try:
        logger.info(f"Generating knowledge points for {request.board} - {request.subject} Grade {request.grade}, Chapter: {request.chapter}")
        
        # Call OpenAI service
        success, parsed_result, error = await openai_service.generate_knowledge_points(
            board=request.board,
            grade=request.grade,
            subject=request.subject,
            chapter=request.chapter,
            section=request.section
        )
        
        if not success:
            logger.error(f"Failed to parse knowledge points response: {error}")
            return APIResponse(
                success=False,
                message="Failed to parse AI response",
                error=f"JSON parsing error: {error}",
                data={"raw_response": parsed_result}  # Include raw response for debugging
            )
        
        return APIResponse(
            success=True,
            data={"knowledge_points": parsed_result},
            message="Knowledge points generated successfully"
        )
        
    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service configuration error"
        )
    except Exception as e:
        logger.error(f"Error generating knowledge points: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to generate knowledge points",
            error=str(e)
        )
