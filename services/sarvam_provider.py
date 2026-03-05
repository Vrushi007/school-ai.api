import os
import time
import re
import hashlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple
from models import KPDescription
from dotenv import load_dotenv
from utils.json_parser import JSONParser
from utils.openai_logger import openai_timing_logger
from prompts import PromptTemplates
from services.ai_provider_base import AIServiceProvider

# Import SarvamAI SDK
try:
    from sarvamai import SarvamAI
except ImportError:
    SarvamAI = None

load_dotenv()


class SarvamAIProvider(AIServiceProvider):
    """SarvamAI implementation of AI service provider using official SDK"""
    
    def __init__(self):
        if SarvamAI is None:
            raise ImportError(
                "SarvamAI SDK is not installed. "
                "Install it with: pip install sarvamai"
            )
        
        self.api_key = os.getenv("SARVAM_API_KEY")
        self.model_name = os.getenv("SARVAM_MODEL_DEFAULT", "sarvam-2b-v0.5")
        self.model_name_5 = os.getenv("SARVAM_MODEL_5", "sarvam-2b-v0.5")
        
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY environment variable is not set")
        
        # Initialize SarvamAI client
        self.client = SarvamAI(api_subscription_key=self.api_key)
        
        # Thread pool executor for running sync calls in async context
        self._executor = ThreadPoolExecutor(max_workers=5)

    @staticmethod
    def _clean_response_content(content: str) -> str:
        """
        Clean SarvamAI response content by removing markdown code blocks and <think> tags.
        SarvamAI often:
        1. Shows reasoning in <think>...</think> tags
        2. Wraps JSON in ```json ... ``` blocks
        
        Args:
            content: Raw content from API response
            
        Returns:
            Cleaned content with markdown blocks and think tags removed
        """
        if not content:
            return content
        
        # Strip leading/trailing whitespace
        content = content.strip()
        
        # Remove <think> blocks - extract content after </think>
        think_end_match = re.search(r'</think>\s*(.*)', content, re.DOTALL | re.IGNORECASE)
        if think_end_match:
            content = think_end_match.group(1).strip()
        
        # Remove markdown code blocks: ```json ... ``` or ``` ... ```
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
        if json_match:
            return json_match.group(1).strip()
        
        return content

    def _sync_api_call(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None, 
        max_tokens: int = None,
        temperature: float = 0.7,
        reasoning_effort: str = "medium"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Synchronous API call to SarvamAI.
        This is called from async context via executor.
        
        Returns:
            Tuple of (content, metadata) where metadata includes usage stats
        """
        try:
            # Build parameters
            params = {
                "messages": messages,
                "temperature": temperature,
                "reasoning_effort": reasoning_effort
            }
            
            # Note: SarvamAI SDK doesn't accept 'model' parameter in completions()
            # The model is determined by the API key/subscription
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            # Make API call using SarvamAI SDK (synchronous)
            response = self.client.chat.completions(**params)
            
            # Extract content from response
            if not hasattr(response, 'choices') or len(response.choices) == 0:
                raise ValueError("No choices found in SarvamAI response")
            
            message = response.choices[0].message
            if not hasattr(message, 'content') or not message.content:
                raise ValueError("No content found in SarvamAI response")
            
            # Clean the content (remove markdown code blocks if present)
            cleaned_content = SarvamAIProvider._clean_response_content(message.content)
            
            # Extract metadata
            metadata = {
                'finish_reason': getattr(response.choices[0], 'finish_reason', None),
                'usage': None,
                'model': getattr(response, 'model', None)
            }
            
            # Extract usage information if available
            if hasattr(response, 'usage') and response.usage:
                metadata['usage'] = {
                    'prompt_tokens': getattr(response.usage, 'prompt_tokens', None),
                    'completion_tokens': getattr(response.usage, 'completion_tokens', None),
                    'total_tokens': getattr(response.usage, 'total_tokens', None)
                }
            
            return cleaned_content, metadata
                
        except Exception as e:
            raise Exception(f"SarvamAI request failed: {str(e)}")

    async def _make_api_call(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None, 
        max_tokens: int = None,
        temperature: float = 0.7,
        reasoning_effort: str = "medium"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Async wrapper around synchronous SarvamAI API call.
        Runs the sync call in a thread pool to avoid blocking.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use (optional)
            max_tokens: Maximum tokens in response (optional)
            temperature: Sampling temperature (default: 0.7)
            reasoning_effort: Reasoning effort level: "low", "medium", "high" (default: "medium")
        
        Returns:
            Tuple of (content, metadata) where metadata includes usage stats and finish_reason
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: self._sync_api_call(messages, model, max_tokens, temperature, reasoning_effort)
        )

    @staticmethod
    def _generate_deterministic_kp_id(board: str, grade: int, subject: str, chapter: str, kp_index: int) -> str:
        """Generate deterministic KP ID using content hash"""
        prefix = f"{board.lower()}{grade}_{subject.lower().replace(' ', '_')}"
        content = f"{chapter.lower().replace(' ', '_')}_{kp_index}"
        hash_digest = hashlib.md5(content.encode()).hexdigest()[:6]
        return f"{prefix}_{hash_digest}_kp{kp_index:02d}"

    @staticmethod
    def _post_process_knowledge_points(board: str, grade: int, subject: str, chapter: str, 
                                       knowledge_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Post-process AI response: add kp_ids and flatten with metadata for DB storage"""
        processed_kps = []
        
        for idx, kp in enumerate(knowledge_points, 1):
            kp["kp_id"] = SarvamAIProvider._generate_deterministic_kp_id(board, grade, subject, chapter, idx)
            kp["board"] = board
            kp["grade"] = grade
            kp["subject"] = subject
            kp["chapter"] = chapter
            processed_kps.append(kp)
        
        return {
            "knowledge_points": processed_kps
        }

    async def generate_lesson_plan(self, subject_name: str, class_name: str, chapter_title: str,
                                   number_of_sessions: int, default_session_duration: str) -> Tuple[bool, Dict[str, Any], str]:
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
            raw_content, metadata = await self._make_api_call([
                {"role": "system", "content": PromptTemplates.LESSON_PLAN_SYSTEM},
                {"role": "user", "content": user_message}
            ], model=self.model_name, max_tokens=3000)
            
            duration = time.time() - start_time
            success, data, error = JSONParser.parse_lesson_plan(raw_content)
            
            # Extract token usage from metadata
            tokens_used = None
            if metadata and metadata.get('usage'):
                tokens_used = metadata['usage'].get('total_tokens')
            
            # Log the call (using same logger for consistency)
            openai_timing_logger.log_api_call(
                function_name="generate_lesson_plan",
                model=f"sarvam_{self.model_name}",
                duration=duration,
                tokens_used=tokens_used,
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
                model=f"sarvam_{self.model_name}",
                duration=duration,
                success=False,
                error_message=error_msg,
                request_size=total_prompt_length,
                subject=subject_name,
                class_name=class_name,
                chapter_title=chapter_title
            )
            return False, {}, error_msg

    async def generate_detailed_session_content(self, title: str, subject_name: str, class_name: str, 
                                               duration: str, summary: str, objectives: List[str], 
                                               kp_list_with_description: List[KPDescription]) -> Any:
        kps_formatted = "\n".join([
            f"{i}. Title: {kp.title}, Description: {kp.description}"
            for i, kp in enumerate(kp_list_with_description, 1)
        ])
        
        user_message = PromptTemplates.get_session_content_prompt(
            title=title,
            subject_name=subject_name,
            class_name=class_name,
            duration=duration,
            summary=summary,
            objectives="\n".join([f"- {obj}" for obj in objectives]),
            kp_list_with_description=kps_formatted
        )
        total_prompt_length = len(PromptTemplates.SESSION_CONTENT_SYSTEM) + len(user_message)
        start_time = time.time()
        
        try:
            raw_content, metadata = await self._make_api_call([
                {"role": "system", "content": PromptTemplates.SESSION_CONTENT_SYSTEM},
                {"role": "user", "content": user_message}
            ], model=self.model_name, max_tokens=10000, temperature=0.7, reasoning_effort="high")
            
            response_metadata = {
                "sessionTitle": title,
                "subject": subject_name,
                "class": class_name,
                "duration": duration,
                "summary": summary,
                "objectives": "\t".join([f"- {obj}" for obj in objectives]),
            }
            
            json_parse_success, result, error_message = JSONParser.extract_json_from_response(
                raw_content, result_metadata=response_metadata, parse=True, fallback_to_raw=True
            )
            
            if not json_parse_success:
                print(error_message)
                print(f"Raw content: {raw_content[:200]}...")
            
            # Extract token usage from metadata
            tokens_used = None
            if metadata and metadata.get('usage'):
                tokens_used = metadata['usage'].get('total_tokens')
            
            openai_timing_logger.log_api_call(
                function_name="generate_detailed_session_content",
                model=f"sarvam_{self.model_name}",
                duration=time.time() - start_time,
                tokens_used=tokens_used,
                success=json_parse_success,
                error_message=error_message,
                request_size=total_prompt_length,
                subject=subject_name,
                class_name=class_name,
                session_title=title,
                response_length=len(raw_content) if raw_content else 0,
                json_format=True
            )
            return result
        except Exception as e:
            error_msg = str(e)
            openai_timing_logger.log_api_call(
                function_name="generate_detailed_session_content",
                model=f"sarvam_{self.model_name}",
                duration=time.time() - start_time,
                success=False,
                error_message=error_msg,
                request_size=total_prompt_length,
                subject=subject_name,
                class_name=class_name,
                session_title=title
            )
            raise

    async def generate_questions(self, class_name: str, subject_name: str,
                                  chapters: List[str], total_marks: int) -> Tuple[bool, Dict[str, Any], str]:
        # Import here to avoid circular dependency
        from services.openai_helper import OpenAIHelper
        bp = OpenAIHelper.allocate_marks_and_generate_blueprint(total_marks)

        user_message = PromptTemplates.get_questions_prompt(
            class_name=class_name,
            subject_name=subject_name,
            chapters=chapters,
            total_marks=total_marks,
            allocation=bp["questions_per_section"]
        )
        total_prompt_length = len(PromptTemplates.QUESTIONS_SYSTEM) + len(user_message)
        start_time = time.time()
        
        try:
            raw_content, metadata = await self._make_api_call([
                {"role": "system", "content": PromptTemplates.QUESTIONS_SYSTEM},
                {"role": "user", "content": user_message}
            ], model=self.model_name, max_tokens=6000)
            
            duration = time.time() - start_time
            request_metadata = {
                "class": class_name,
                "subject": subject_name,
                "chapters": ", ".join(chapters),
                "totalMarks": total_marks,
                "blueprint": bp["blueprint"]
            }
            
            success, data, error = JSONParser.parse_questions(raw_content, request_metadata)
            
            # Extract token usage from metadata
            tokens_used = None
            if metadata and metadata.get('usage'):
                tokens_used = metadata['usage'].get('total_tokens')
            
            openai_timing_logger.log_api_call(
                function_name="generate_questions",
                model=f"sarvam_{self.model_name}",
                duration=duration,
                tokens_used=tokens_used,
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
            error_msg = str(e)
            openai_timing_logger.log_api_call(
                function_name="generate_questions",
                model=f"sarvam_{self.model_name}",
                duration=time.time() - start_time,
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
            answer, metadata = await self._make_api_call(messages, model=self.model_name, max_tokens=1500)
            
            if not answer:
                raise ValueError("No answer content found in response.")
            
            duration = time.time() - start_time
            
            # Extract token usage from metadata
            tokens_used = None
            if metadata and metadata.get('usage'):
                tokens_used = metadata['usage'].get('total_tokens')
            
            openai_timing_logger.log_api_call(
                function_name="get_student_answer",
                model=f"sarvam_{self.model_name}",
                duration=duration,
                tokens_used=tokens_used,
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
                model=f"sarvam_{self.model_name}",
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
    
    async def generate_knowledge_points(self, board: str, grade: int, subject: str, chapter: str,
                                       section: str = None) -> Tuple[bool, Dict[str, Any], str]:
        user_message = PromptTemplates.get_knowledge_points_prompt(
            board=board,
            grade=grade,
            subject=subject,
            chapter=chapter,
            section=section
        )
        total_prompt_length = len(PromptTemplates.KNOWLEDGE_POINTS_SYSTEM) + len(user_message)
        start_time = time.time()
        
        try:
            raw_content, metadata = await self._make_api_call([
                {"role": "system", "content": PromptTemplates.KNOWLEDGE_POINTS_SYSTEM},
                {"role": "user", "content": user_message}
            ], model=self.model_name_5, max_tokens=10000, reasoning_effort="high")
            
            # Debug: Print response for knowledge points
            print("=" * 80)
            print("SARVAM KP GENERATION RAW RESPONSE:")
            print(raw_content)
            print("=" * 80)
            
            duration = time.time() - start_time
            success, data, error = JSONParser.extract_json_from_response(
                raw_content, parse=True, fallback_to_raw=True
            )
            
            if not success:
                print("KP JSON PARSING FAILED:")
                print(f"Error: {error}")
                print(f"Raw content preview: {raw_content[:500]}...")
                print("=" * 80)
            
            # Post-process: add kp_ids and wrap in syllabus structure
            if success and isinstance(data, dict) and "knowledge_points" in data:
                knowledge_points = data.get("knowledge_points", [])
                processed_data = self._post_process_knowledge_points(
                    board=board,
                    grade=grade,
                    subject=subject,
                    chapter=chapter,
                    knowledge_points=knowledge_points
                )
                data = processed_data
            
            # Extract token usage from metadata
            tokens_used = None
            if metadata and metadata.get('usage'):
                tokens_used = metadata['usage'].get('total_tokens')
            
            openai_timing_logger.log_api_call(
                function_name="generate_knowledge_points",
                model=f"sarvam_{self.model_name_5}",
                duration=duration,
                tokens_used=tokens_used,
                success=success,
                error_message=error if not success else None,
                request_size=total_prompt_length,
                board=board,
                subject=subject,
                grade=grade,
                chapter=chapter,
                section=section or "all",
                response_length=len(raw_content) if raw_content else 0
            )
            return success, data, error
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            openai_timing_logger.log_api_call(
                function_name="generate_knowledge_points",
                model=f"sarvam_{self.model_name_5}",
                duration=duration,
                success=False,
                error_message=error_msg,
                request_size=total_prompt_length,
                board=board,
                subject=subject,
                grade=grade,
                chapter=chapter,
                section=section or "all"
            )
            return False, {}, error_msg

    async def group_kps_into_sessions(self, board: str, chapter: str, class_name: str, subject: str,
                                     number_of_sessions: int, session_duration: str,
                                     knowledge_points: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any], str]:
        """Group knowledge points into teaching sessions"""
        system_prompt = PromptTemplates.get_kp_grouping_system_prompt(board=board)
        
        user_message = PromptTemplates.get_kp_grouping_prompt(
            board=board,
            chapter=chapter,
            class_name=class_name,
            subject=subject,
            number_of_sessions=number_of_sessions,
            session_duration=session_duration,
            knowledge_points=knowledge_points
        )
        total_prompt_length = len(system_prompt) + len(user_message)
        start_time = time.time()
        
        try:
            raw_content, metadata = await self._make_api_call([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ], model=self.model_name, max_tokens=4000)
            
            duration = time.time() - start_time
            success, data, error = JSONParser.extract_json_from_response(
                raw_content, parse=True, fallback_to_raw=True
            )
            
            # Extract token usage from metadata
            tokens_used = None
            if metadata and metadata.get('usage'):
                tokens_used = metadata['usage'].get('total_tokens')
            
            openai_timing_logger.log_api_call(
                function_name="group_kps_into_sessions",
                model=f"sarvam_{self.model_name}",
                duration=duration,
                tokens_used=tokens_used,
                success=success,
                error_message=error if not success else None,
                request_size=total_prompt_length,
                board=board,
                subject=subject,
                class_name=class_name,
                chapter=chapter,
                num_sessions=number_of_sessions,
                num_kps=len(knowledge_points),
                response_length=len(raw_content) if raw_content else 0
            )
            return success, data, error
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            openai_timing_logger.log_api_call(
                function_name="group_kps_into_sessions",
                model=f"sarvam_{self.model_name}",
                duration=duration,
                success=False,
                error_message=error_msg,
                request_size=total_prompt_length,
                board=board,
                subject=subject,
                class_name=class_name,
                chapter=chapter,
                num_sessions=number_of_sessions,
                num_kps=len(knowledge_points)
            )
            return False, {}, error_msg

    async def generate_session_summary(self, board: str, chapter: str, class_name: str, subject: str,
                                      session_title: str, knowledge_points: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any], str]:
        """Generate session summary and objectives from knowledge points"""
        user_message = PromptTemplates.get_session_summary_prompt(
            board=board,
            chapter=chapter,
            class_name=class_name,
            subject=subject,
            session_title=session_title,
            knowledge_points=knowledge_points
        )
        total_prompt_length = len(PromptTemplates.SESSION_SUMMARY_SYSTEM) + len(user_message)
        start_time = time.time()
        
        try:
            raw_content, metadata = await self._make_api_call([
                {"role": "system", "content": PromptTemplates.SESSION_SUMMARY_SYSTEM},
                {"role": "user", "content": user_message}
            ], model=self.model_name, max_tokens=2000)
            
            duration = time.time() - start_time
            success, data, error = JSONParser.extract_json_from_response(
                raw_content, parse=True, fallback_to_raw=True
            )
            
            # Extract token usage from metadata
            tokens_used = None
            if metadata and metadata.get('usage'):
                tokens_used = metadata['usage'].get('total_tokens')
            
            openai_timing_logger.log_api_call(
                function_name="generate_session_summary",
                model=f"sarvam_{self.model_name}",
                duration=duration,
                tokens_used=tokens_used,
                success=success,
                error_message=error if not success else None,
                request_size=total_prompt_length,
                board=board,
                chapter=chapter,
                subject=subject,
                class_name=class_name,
                session_title=session_title,
                num_kps=len(knowledge_points),
                response_length=len(raw_content) if raw_content else 0
            )
            return success, data, error
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            openai_timing_logger.log_api_call(
                function_name="generate_session_summary",
                model=f"sarvam_{self.model_name}",
                duration=duration,
                success=False,
                error_message=error_msg,
                request_size=total_prompt_length,
                board=board,
                chapter=chapter,
                subject=subject,
                class_name=class_name,
                session_title=session_title,
                num_kps=len(knowledge_points)
            )
            return False, {}, error_msg
