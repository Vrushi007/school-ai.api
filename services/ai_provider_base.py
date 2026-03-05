from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from models import KPDescription


class AIServiceProvider(ABC):
    """
    Abstract base class for AI service providers.
    All AI providers (OpenAI, SarvamAI, etc.) must implement this interface.
    """

    @abstractmethod
    async def generate_lesson_plan(
        self,
        subject_name: str,
        class_name: str,
        chapter_title: str,
        number_of_sessions: int,
        default_session_duration: str
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Generate a lesson plan for a chapter.
        
        Returns:
            Tuple of (success, parsed_data, error_message)
        """
        pass

    @abstractmethod
    async def generate_detailed_session_content(
        self,
        title: str,
        subject_name: str,
        class_name: str,
        duration: str,
        summary: str,
        objectives: List[str],
        kp_list_with_description: List[KPDescription]
    ) -> Any:
        """
        Generate detailed session content with teaching materials.
        
        Returns:
            Session content as dictionary
        """
        pass

    @abstractmethod
    async def generate_questions(
        self,
        class_name: str,
        subject_name: str,
        chapters: List[str],
        total_marks: int
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Generate question paper for given chapters.
        
        Returns:
            Tuple of (success, questions_data, error_message)
        """
        pass

    @abstractmethod
    async def get_student_answer(
        self,
        question: str,
        conversation_history: List[Dict[str, str]] = None,
        subject_name: str = None,
        class_name: str = None
    ) -> Tuple[bool, str, str]:
        """
        Get AI tutor response for student question.
        
        Returns:
            Tuple of (success, answer, error_message)
        """
        pass

    @abstractmethod
    async def generate_knowledge_points(
        self,
        board: str,
        grade: int,
        subject: str,
        chapter: str,
        section: str = None
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Generate knowledge points for a chapter/section.
        
        Returns:
            Tuple of (success, knowledge_points_data, error_message)
        """
        pass

    @abstractmethod
    async def group_kps_into_sessions(
        self,
        board: str,
        chapter: str,
        class_name: str,
        subject: str,
        number_of_sessions: int,
        session_duration: str,
        knowledge_points: List[Dict[str, Any]]
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Group knowledge points into teaching sessions.
        
        Returns:
            Tuple of (success, grouped_sessions, error_message)
        """
        pass

    @abstractmethod
    async def generate_session_summary(
        self,
        board: str,
        chapter: str,
        class_name: str,
        subject: str,
        session_title: str,
        knowledge_points: List[Dict[str, Any]]
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Generate session summary and objectives from knowledge points.
        
        Returns:
            Tuple of (success, summary_data, error_message)
        """
        pass
