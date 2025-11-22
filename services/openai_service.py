import os
import time
from typing import List, Dict, Any, Tuple
from openai import AsyncOpenAI
from dotenv import load_dotenv
from utils.json_parser import JSONParser
from services.openai_helper import OpenAIHelper
from utils.openai_logger import openai_timing_logger
from config import get_openai_config
from prompts import PromptTemplates

load_dotenv()

class OpenAIService:
    def __init__(self):
        self.client = None
        self.config = get_openai_config()
        self._initialize_client()

    def _initialize_client(self):
        self.client = AsyncOpenAI(api_key=self.config.api_key)

    def _check_client(self):
        if not self.client:
            raise RuntimeError("OpenAI client is not initialized")

    async def generate_lesson_plan(self, subject_name: str, class_name: str, chapter_title: str,
                                   number_of_sessions: int, default_session_duration: str) -> Tuple[bool, Dict[str, Any], str]:
        self._check_client()
        user_message = PromptTemplates.get_lesson_plan_prompt(
            subject_name=subject_name,
            class_name=class_name,
            chapter_title=chapter_title,
            number_of_sessions=number_of_sessions,
            default_session_duration=default_session_duration
        )
        total_prompt_length = len(PromptTemplates.LESSON_PLAN_SYSTEM) + len(user_message)
        start_time = time.time()
        try:
            response = await self.client.responses.create(
                model=self.config.model_name,
                input=[
                    {"role": "system", "content": PromptTemplates.LESSON_PLAN_SYSTEM},
                    {"role": "user", "content": user_message}
                ],
            )
            duration = time.time() - start_time
            raw_content = OpenAIHelper.extract_output_text(response)
            success, data, error = JSONParser.parse_lesson_plan(raw_content)
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
                                                subject_name: str, class_name: str) -> Any:
        self._check_client()
        user_message = PromptTemplates.get_session_content_prompt(
            session_data=session_data,
            subject_name=subject_name,
            class_name=class_name
        )
        total_prompt_length = len(PromptTemplates.SESSION_CONTENT_SYSTEM) + len(user_message)
        session_title = session_data.get('title', 'Unknown Session')
        start_time = time.time()
        try:
            response = await self.client.responses.create(
                model=self.config.model_name,
                input=[
                    {"role": "system", "content": PromptTemplates.SESSION_CONTENT_SYSTEM},
                    {"role": "user", "content": user_message}
                ],
            )
            duration = time.time() - start_time
            raw_content = OpenAIHelper.extract_output_text(response)
            response_metadata = {
                "sessionTitle": session_data.get('title'),
                "subject": subject_name,
                "class": class_name,
                "duration": session_data.get('duration'),
                "summary": session_data.get('summary'),
                "objectives": session_data.get('objectives', []),
            }
            json_parse_success, result, error_message = JSONParser.extract_json_from_response(
                raw_content, result_metadata=response_metadata, parse=True, fallback_to_raw=True
            )
            if not json_parse_success:
                print(error_message)
                print(f"Raw content: {raw_content[:200]}...")
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
        self._check_client()
        user_message = PromptTemplates.get_questions_prompt(
            class_name=class_name,
            subject_name=subject_name,
            chapters=chapters,
            total_marks=total_marks
        )
        total_prompt_length = len(PromptTemplates.QUESTIONS_SYSTEM) + len(user_message)
        start_time = time.time()
        try:
            response = await self.client.responses.create(
                model=self.config.model_name,
                input=[
                    {"role": "system", "content": PromptTemplates.QUESTIONS_SYSTEM},
                    {"role": "user", "content": user_message}
                ]
            )
            duration = time.time() - start_time
            raw_content = OpenAIHelper.extract_output_text(response)
            request_metadata = {
                "class": class_name,
                "subject": subject_name,
                "chapters": ", ".join(chapters),
                "totalMarks": total_marks,
            }
            success, data, error = JSONParser.parse_questions(raw_content, request_metadata)
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

    async def get_student_answer(self, question: str, conversation_history: List[Dict[str, str]] = None,
                                 subject_name: str = None, class_name: str = None) -> Tuple[bool, str, str]:
        self._check_client()
        system_prompt = PromptTemplates.get_student_tutor_system_prompt(
            subject_name=subject_name,
            class_name=class_name
        )
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
                input=messages,
                max_output_tokens=1500
            )
            answer = None
            for item in response.output:
                if getattr(item, "content", None):
                    answer = item.content[0].text
                    break
            if not answer:
                raise ValueError("No answer content found in response.")
            duration = time.time() - start_time
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
