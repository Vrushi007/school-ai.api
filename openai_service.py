import os
import time
from typing import List, Dict, Any, Tuple
from openai import AsyncOpenAI
from dotenv import load_dotenv
from utils.json_parser import JSONParser
from utils.openai_helper import OpenAIHelper
from utils.openai_logger import openai_timing_logger, log_openai_timing
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
        self.client = AsyncOpenAI(api_key=self.config.api_key)
    
    def _check_client(self):
        """Check if client is properly initialized"""
        if not self.client:
            raise RuntimeError("OpenAI client is not initialized")
    
    async def generate_lesson_plan(self, subject_name: str, class_name: str, chapter_title: str, 
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

        # Calculate request size for metrics
        total_prompt_length = len(PromptTemplates.LESSON_PLAN_SYSTEM) + len(user_message)
        
        # Track timing and log the API call
        start_time = time.time()
        try:
            response = await self.client.responses.create(
                model=self.config.model_name,
                input=[
                    {
                        "role": "system",
                        "content": PromptTemplates.LESSON_PLAN_SYSTEM
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
            )
            
            duration = time.time() - start_time
            raw_content = OpenAIHelper.extract_output_text(response)
            # Parse the result
            success, data, error = JSONParser.parse_lesson_plan(raw_content)
            
            # Log successful API call with detailed metrics
            openai_timing_logger.log_api_call(
                function_name="generate_lesson_plan",
                model=self.config.model_name,
                duration=duration,
                tokens_used=getattr(response.usage, 'total_tokens', None),
                success=success,
                error_message=error if not success else None,
                request_size=total_prompt_length,
                subject=subject_name,
                class_name=class_name,
                chapter_title=chapter_title,
                num_sessions=number_of_sessions,
                response_length=len(raw_content) if raw_content else 0
            )
            
            return success, data, error
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            # Log failed API call
            openai_timing_logger.log_api_call(
                function_name="generate_lesson_plan",
                model=self.config.model_name,
                duration=duration,
                success=False,
                error_message=error_msg,
                request_size=total_prompt_length,
                subject=subject_name,
                class_name=class_name,
                chapter_title=chapter_title
            )
            
            return False, {}, error_msg
    
    async def generate_detailed_session_content(self, session_data: Dict[str, Any], 
                                            subject_name: str, class_name: str) -> str:
        """
        Generate detailed content for a specific session using OpenAI API
        Returns: Clean, validated JSON string for UI to parse
        """
        import json
        import re
        
        self._check_client()
        
        user_message = PromptTemplates.get_session_content_prompt(
            session_data=session_data,
            subject_name=subject_name,
            class_name=class_name
        )
        
        # Calculate request size for metrics
        total_prompt_length = len(PromptTemplates.SESSION_CONTENT_SYSTEM) + len(user_message)
        session_title = session_data.get('title', 'Unknown Session')
        
        # Track timing and log the API call
        start_time = time.time()
        try:
            response = await self.client.responses.create(
                model=self.config.model_name,
                input=[
                    {
                        "role": "system",
                        "content": PromptTemplates.SESSION_CONTENT_SYSTEM
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                # response_format={"type": "json_object"}
            )
            
            duration = time.time() - start_time
            raw_content = OpenAIHelper.extract_output_text(response)
            
            # Clean and validate JSON before sending to UI
            json_parse_success = True
            error_message = None
            
            try:
                # Since we're using response_format="json_object", response should be pure JSON
                # But still handle markdown code blocks as fallback
                json_content = raw_content.strip()
                
                # Check if content is wrapped in markdown code blocks
                json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', json_content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1).strip()
                
                # Try to parse as-is first (for pure JSON responses)
                try:
                    parsed_data = json.loads(json_content)
                    result = parsed_data
                except json.JSONDecodeError:
                    # If that fails, try cleaning up common JSON issues
                    cleaned_json = re.sub(r',\s*}', '}', json_content)
                    cleaned_json = re.sub(r',\s*]', ']', cleaned_json)
                    parsed_data = json.loads(cleaned_json)
                    result = parsed_data
                
            except json.JSONDecodeError as e:
                # If all parsing attempts fail, return the raw content and let UI handle the error
                json_parse_success = False
                error_message = f"JSON parsing failed: {e}"
                print(error_message)
                print(f"Raw content: {raw_content[:200]}...")
                result = raw_content
            
            # Log the API call with detailed metrics
            openai_timing_logger.log_api_call(
                function_name="generate_detailed_session_content",
                model=self.config.model_name,
                duration=duration,
                tokens_used=getattr(response.usage, 'total_tokens', None),
                success=json_parse_success,
                error_message=error_message,
                request_size=total_prompt_length,
                subject=subject_name,
                class_name=class_name,
                session_title=session_title,
                response_length=len(raw_content) if raw_content else 0,
                json_format=True
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            # Log failed API call
            openai_timing_logger.log_api_call(
                function_name="generate_detailed_session_content",
                model=self.config.model_name,
                duration=duration,
                success=False,
                error_message=error_msg,
                request_size=total_prompt_length,
                subject=subject_name,
                class_name=class_name,
                session_title=session_title
            )
            
            raise
    
    async def generate_questions(self, class_name: str, subject_name: str, 
                         chapters: List[str], total_marks: int) -> Tuple[bool, Dict[str, Any], str]:
        """
        Generate questions using OpenAI API
        Returns: (success: bool, data: dict, error: str/None)
        """
        self._check_client()
        
        user_message = PromptTemplates.get_questions_prompt(
            class_name=class_name,
            subject_name=subject_name,
            chapters=chapters,
            total_marks=total_marks
        )

        # Calculate request size for metrics
        total_prompt_length = len(PromptTemplates.QUESTIONS_SYSTEM) + len(user_message)
        
        # Track timing and log the API call
        start_time = time.time()
        try:
            response = await self.client.responses.create(
                model=self.config.model_name,
                # response_format={"type": "json_object"},
                input=[
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
            
            duration = time.time() - start_time
            raw_content = OpenAIHelper.extract_output_text(response)
            
            # Parse the result
            success, data, error = JSONParser.parse_questions(raw_content)
            
            # Log successful API call with detailed metrics
            openai_timing_logger.log_api_call(
                function_name="generate_questions",
                model=self.config.model_name,
                duration=duration,
                tokens_used=getattr(response.usage, 'total_tokens', None),
                success=success,
                error_message=error if not success else None,
                request_size=total_prompt_length,
                subject=subject_name,
                class_name=class_name,
                chapters_count=len(chapters),
                total_marks=total_marks,
                response_length=len(raw_content) if raw_content else 0,
                json_format=True
            )
            
            return success, data, error
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            # Log failed API call
            openai_timing_logger.log_api_call(
                function_name="generate_questions",
                model=self.config.model_name,
                duration=duration,
                success=False,
                error_message=error_msg,
                request_size=total_prompt_length,
                subject=subject_name,
                class_name=class_name,
                chapters_count=len(chapters),
                total_marks=total_marks
            )
            
            return False, {}, error_msg
    
    async def get_student_answer(
    self, 
    question: str, 
    conversation_history: List[Dict[str, str]] = None, 
    subject_name: str = None, 
    class_name: str = None
) -> Tuple[bool, str, str]:
    
        self._check_client()
        
        # Build system prompt
        system_prompt = PromptTemplates.get_student_tutor_system_prompt(
            subject_name=subject_name,
            class_name=class_name
        )
        
        # Build input
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        messages.append({"role": "user", "content": question})

        total_prompt_length = sum(len(m["content"]) for m in messages)
        conversation_length = len(conversation_history) if conversation_history else 0

        start_time = time.time()

        try:
            response = await self.client.responses.create(
                model=self.config.model_name,
                input=messages,                    # ← FIXED
                max_output_tokens=1500             # ← FIXED
            )

            # Extract text safely
            answer = None
            for item in response.output:
                if getattr(item, "content", None):
                    answer = item.content[0].text
                    break

            if not answer:
                raise ValueError("No answer content found in response.")

            duration = time.time() - start_time

            # Logging…
            openai_timing_logger.log_api_call(
                function_name="get_student_answer",
                model=self.config.model_name,
                duration=duration,
                tokens_used=getattr(response.usage, 'total_tokens', None),
                success=True,
                request_size=total_prompt_length,
                subject=subject_name or "general",
                class_name=class_name or "general",
                question_length=len(question),
                conversation_turns=conversation_length,
                response_length=len(answer),
                max_tokens=1500,
            )

            return True, answer, None

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)

            openai_timing_logger.log_api_call(
                function_name="get_student_answer",
                model=self.config.model_name,
                duration=duration,
                success=False,
                error_message=error_msg,
                request_size=total_prompt_length,
                subject=subject_name or "general",
                class_name=class_name or "general",
                question_length=len(question),
                conversation_turns=conversation_length
            )

            return False, "", error_msg
