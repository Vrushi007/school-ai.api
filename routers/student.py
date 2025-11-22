import logging
import uuid
from fastapi import APIRouter, HTTPException, status

from models import StudentQuestionRequest, StudentAnswerResponse, ConversationMessage, APIResponse
from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["student"])

# Initialize OpenAI service
openai_service = OpenAIService()


@router.post("/get-answers", response_model=APIResponse)
async def get_student_answer(request: StudentQuestionRequest):
    """
    Get detailed answers to student questions with conversation history
    
    This endpoint allows students to ask questions and receive detailed, educational answers.
    It maintains conversation context by including previous exchanges, making the chatbot
    more contextual and helpful for follow-up questions.
    """
    try:
        logger.info(f"Processing student question: {request.question[:100]}...")
        
        # Convert conversation history to the format expected by OpenAI service
        history_dict = []
        if request.conversation_history:
            for msg in request.conversation_history:
                history_dict.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Get answer from OpenAI service
        success, answer, error = await openai_service.get_student_answer(
            question=request.question,
            conversation_history=history_dict,
            subject_name=request.subject_name,
            class_name=request.class_name
        )
        
        if not success:
            logger.error(f"Failed to get answer from OpenAI: {error}")
            return APIResponse(
                success=False,
                message="Failed to get answer from AI service",
                error=error
            )
        
        # Create updated conversation history
        updated_history = []
        
        # Add existing history
        if request.conversation_history:
            updated_history.extend(request.conversation_history)
        
        # Add current question and answer
        updated_history.append(ConversationMessage(role="user", content=request.question))
        updated_history.append(ConversationMessage(role="assistant", content=answer))
        
        # Create response
        student_response = StudentAnswerResponse(
            answer=answer,
            conversation_id=str(uuid.uuid4()),  # Generate unique conversation ID
            updated_history=updated_history
        )
        
        return APIResponse(
            success=True,
            data={"response": student_response.dict()},
            message="Answer generated successfully"
        )
        
    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service configuration error"
        )
    except Exception as e:
        logger.error(f"Error getting student answer: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to get answer",
            error=str(e)
        )