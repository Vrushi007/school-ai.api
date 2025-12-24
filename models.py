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
    total_marks: int = Field(..., description="Total marks for the questions")


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


# Knowledge Points Models
class KnowledgePointRequest(BaseModel):
    board: str = Field(default="CBSE", description="Curriculum board (e.g., CBSE, ICSE, State)")
    grade: int = Field(..., description="Grade/Class (e.g., 5, 10)")
    subject: str = Field(..., description="Subject name (e.g., Mathematics, Science)")
    chapter: str = Field(..., description="Chapter title")
    section: Optional[str] = Field(None, description="Specific section within chapter (optional)")


class AssessmentExample(BaseModel):
    example: str = Field(..., description="Observable assessment example")


class ConceptualTriple(BaseModel):
    triple: str = Field(..., description="Conceptual triple in format (subject, predicate, object)")


class KeyTermSynonym(BaseModel):
    term: str = Field(..., description="Key term")
    synonyms: List[str] = Field(..., description="List of synonyms or related terms")


class AssessmentCriterion(BaseModel):
    criterion: str = Field(..., description="Assessment criterion description")
    weightage: int = Field(..., description="Weightage percentage for this criterion")


class AutoGradingComponents(BaseModel):
    conceptual_triples: List[ConceptualTriple] = Field(..., description="Conceptual triples for knowledge representation")
    key_terms_and_synonyms: List[KeyTermSynonym] = Field(..., description="Key terms with synonyms")
    assessment_criteria: List[AssessmentCriterion] = Field(..., description="Assessment criteria with weightage")


class KnowledgePoint(BaseModel):
    kp_id: str = Field(..., description="Unique knowledge point identifier")
    kp_title: str = Field(..., description="Concise action-oriented title")
    kp_description: str = Field(..., description="What the student must demonstrably do")
    bloom_level: str = Field(..., description="Bloom's taxonomy level")
    irt_difficulty: float = Field(..., description="IRT difficulty score (-3.0 to +3.0)")
    difficulty_label: str = Field(..., description="Human-readable difficulty label")
    prerequisite_kps: List[str] = Field(default_factory=list, description="IDs of prerequisite knowledge points")
    misconception_tags: List[str] = Field(default_factory=list, description="Concept-specific misconception tags")
    assessment_examples: List[str] = Field(..., description="Two observable examples for assessment")
    detailed_explanation: str = Field(..., description="Comprehensive explanation of the knowledge point")
    auto_grading_components: AutoGradingComponents = Field(..., description="Components for auto-grading system")
    tags: List[str] = Field(..., description="Topic tags for categorization")
    real_world_applications: List[str] = Field(..., description="Real-world applications and examples")


class Section(BaseModel):
    section_title: str = Field(..., description="Section title")
    knowledge_points: List[KnowledgePoint] = Field(..., description="List of knowledge points")


class Syllabus(BaseModel):
    board: str = Field(..., description="Curriculum board")
    grade: int = Field(..., description="Grade/Class number")
    subject: str = Field(..., description="Subject name")
    chapter: str = Field(..., description="Chapter title")
    sections: List[Section] = Field(..., description="List of sections with knowledge points")


class KnowledgePointResponse(BaseModel):
    syllabus: Syllabus = Field(..., description="Syllabus structure with knowledge points")