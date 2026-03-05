import logging
from fastapi import APIRouter, HTTPException, status, Depends

from models import KnowledgePointRequest, APIResponse
from services.ai_service_factory import get_ai_service
from utils.auth_dependencies import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["knowledge-points"])


@router.post("/generate-knowledge-points", response_model=APIResponse)
async def generate_knowledge_points(
    request: KnowledgePointRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    Generate knowledge points for a curriculum chapter using AI
    
    This endpoint decomposes curriculum content into atomic, teachable,
    and assessable Knowledge Points (KPs) aligned with curriculum standards,
    Bloom's Taxonomy, and Item Response Theory (IRT) difficulty metrics.
    
    The AI provider can be specified in the request. If not specified,
    it uses the AI_PROVIDER environment variable.
    """
    try:
        logger.info(f"Generating knowledge points for {request.board} - {request.subject} Grade {request.grade}, Chapter: {request.chapter}")
        
        # Get AI service based on request provider or env variable
        if request.provider:
            logger.info(f"Using requested provider: {request.provider}")
        ai_service = get_ai_service(provider=request.provider)
        
        # Call AI service
        success, parsed_result, error = await ai_service.generate_knowledge_points(
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
            data=parsed_result,
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
