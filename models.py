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