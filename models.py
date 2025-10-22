from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class LessonPlanRequest(BaseModel):
    subject_name: str = Field(..., description="Subject name (e.g., Mathematics, Science)")
    class_name: str = Field(..., description="Class/Grade (e.g., 5th, 10th)")
    chapter_title: str = Field(..., description="Chapter title")
    number_of_sessions: int = Field(..., gt=0, description="Number of sessions")
    default_session_duration: str = Field(..., description="Default session duration (e.g., 45 minutes)")


class SessionData(BaseModel):
    title: str
    summary: str
    duration: str
    objectives: List[str]


class DetailedSessionRequest(BaseModel):
    session_data: SessionData
    subject_name: str
    class_name: str


class QuestionGenerationRequest(BaseModel):
    class_name: str = Field(..., description="Class/Grade (e.g., 5th, 10th)")
    subject_name: str = Field(..., description="Subject name")
    chapters: List[str] = Field(..., description="List of chapters to cover")
    question_requirements: str = Field(..., description="Specific requirements for questions")


class APIResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    message: str


# Student Chatbot Models
class ConversationMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class StudentQuestionRequest(BaseModel):
    question: str = Field(..., description="Student's question")
    subject_name: Optional[str] = Field(None, description="Subject context (optional)")
    class_name: Optional[str] = Field(None, description="Class/Grade context (optional)")
    conversation_history: Optional[List[ConversationMessage]] = Field(
        default=[], 
        description="Previous conversation history for context"
    )


class StudentAnswerResponse(BaseModel):
    answer: str = Field(..., description="AI's detailed answer")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier for tracking")
    updated_history: List[ConversationMessage] = Field(..., description="Updated conversation history")