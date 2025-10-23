import os
from typing import List, Dict, Any, Tuple
from openai import OpenAI
from dotenv import load_dotenv
from utils.json_parser import JSONParser
from config import get_openai_config
from prompts import PromptTemplates

# Load environment variables
load_dotenv()

class OpenAIService:
    """Service class for handling OpenAI API interactions"""
    
    def __init__(self):
        self.client = None
        self.config = get_openai_config()
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client with API key"""
        self.client = OpenAI(api_key=self.config.api_key)
    
    def _check_client(self):
        """Check if client is properly initialized"""
        if not self.client:
            raise RuntimeError("OpenAI client is not initialized")
    
    def generate_lesson_plan(self, subject_name: str, class_name: str, chapter_title: str, 
                           number_of_sessions: int, default_session_duration: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Generate a lesson plan using OpenAI API
        Returns: (success: bool, data: dict, error: str/None)
        """
        self._check_client()
        
        user_message = PromptTemplates.get_lesson_plan_prompt(
            subject_name=subject_name,
            class_name=class_name,
            chapter_title=chapter_title,
            number_of_sessions=number_of_sessions,
            default_session_duration=default_session_duration
        )

        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {
                    "role": "system",
                    "content": PromptTemplates.LESSON_PLAN_SYSTEM
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        raw_content = response.choices[0].message.content
        return JSONParser.parse_lesson_plan(raw_content)
    
    def generate_detailed_session_content(self, session_data: Dict[str, Any], 
                                        subject_name: str, class_name: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Generate detailed content for a specific session using OpenAI API
        Returns: (success: bool, data: dict, error: str/None)
        """
        self._check_client()
        
        user_message = PromptTemplates.get_session_content_prompt(
            session_data=session_data,
            subject_name=subject_name,
            class_name=class_name
        )

        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {
                    "role": "system",
                    "content": PromptTemplates.SESSION_CONTENT_SYSTEM
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        raw_content = response.choices[0].message.content
        return JSONParser.parse_detailed_session_content(raw_content)
    
    def generate_questions(self, class_name: str, subject_name: str, 
                         chapters: List[str], question_requirements: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Generate questions using OpenAI API
        Returns: (success: bool, data: dict, error: str/None)
        """
        self._check_client()
        
        user_message = PromptTemplates.get_questions_prompt(
            class_name=class_name,
            subject_name=subject_name,
            chapters=chapters,
            question_requirements=question_requirements
        )

        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {
                    "role": "system",
                    "content": PromptTemplates.QUESTIONS_SYSTEM
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        raw_content = response.choices[0].message.content
        return JSONParser.parse_questions(raw_content)
    
    def get_student_answer(self, question: str, conversation_history: List[Dict[str, str]] = None, 
                          subject_name: str = None, class_name: str = None) -> Tuple[bool, str, str]:
        """
        Get a detailed answer to a student's question with conversation context
        Returns: (success: bool, answer: str, error: str/None)
        """
        self._check_client()
        
        # Build the conversation context
        system_prompt = PromptTemplates.get_student_tutor_system_prompt(
            subject_name=subject_name,
            class_name=class_name
        )
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # Add conversation history if provided
        if conversation_history:
            for message in conversation_history:
                messages.append({
                    "role": message.get("role", "user"),
                    "content": message.get("content", "")
                })
        
        # Add the current question
        messages.append({
            "role": "user",
            "content": question
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                max_tokens=1500,  # Allow for detailed responses
                temperature=0.7   # Balanced creativity and accuracy
            )
            
            answer = response.choices[0].message.content
            return True, answer, None
            
        except Exception as e:
            return False, "", str(e)