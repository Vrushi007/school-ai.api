import json
import re
from typing import Tuple, Any, Optional

class JSONParser:
    @staticmethod
    def extract_json_from_response(raw_content: str,result_metadata: dict = None, parse: bool = True, fallback_to_raw: bool = True) -> Tuple[bool, Any, Optional[str]]:
        """
        Extract and optionally parse JSON content from OpenAI response, handling markdown code blocks
        
        Args:
            raw_content: Raw response content from API
            parse: If True, parses the JSON and returns tuple; if False, returns just the extracted string
            fallback_to_raw: If True, returns raw content on parse failure (only used when parse=True)
            
        Returns:
            If parse=True: Tuple of (success: bool, parsed_data: Any, error_message: Optional[str])
            If parse=False: Extracted JSON string
        """
        if not raw_content or not isinstance(raw_content, str):
            if not parse:
                return ""
            return False, None, "Empty or invalid content provided"
        
        # Remove markdown code blocks if present
        # Look for ```json ... ``` or ``` ... ``` patterns
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_content, re.DOTALL)
        if json_match:
            json_content = json_match.group(1).strip()
        else:
            # If no code blocks found, use the raw content
            json_content = raw_content.strip()
        
        # If not parsing, just return the extracted string
        if not parse:
            return json_content
        
        # Parse the JSON with error handling and cleanup
        try:
            # Try to parse as-is first (for pure JSON responses)
            try:
                parsed_data = json.loads(json_content)
                return True, parsed_data if result_metadata is None else JSONParser.merge_dicts(result_metadata, parsed_data), None
                
            except json.JSONDecodeError:
                # Try cleaning up common JSON issues
                cleaned_json = JSONParser._clean_json_content(json_content)
                parsed_data = json.loads(cleaned_json)
                return True, parsed_data if result_metadata is None else JSONParser.merge_dicts(result_metadata, parsed_data), None
                
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing failed: {str(e)}"
            return False, raw_content if fallback_to_raw else None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error during JSON parsing: {str(e)}"
            return False, raw_content if fallback_to_raw else None, error_msg
    
    @staticmethod
    def _clean_json_content(json_content: str) -> str:
        """
        Clean common JSON formatting issues
        
        Args:
            json_content: Raw JSON content to clean
            
        Returns:
            Cleaned JSON string
        """
        # Remove trailing commas before closing brackets/braces
        cleaned = re.sub(r',\s*}', '}', json_content)
        cleaned = re.sub(r',\s*]', ']', cleaned)
        
        # Remove comments (// or /* */)
        cleaned = re.sub(r'//.*?$', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
        
        return cleaned
    
    @staticmethod
    def parse_lesson_plan(raw_content):
        """
        Parse lesson plan from OpenAI response
        Returns: (success: bool, data: dict/str, error: str/None)
        """
        return JSONParser.extract_json_from_response(raw_content, parse=True)
    
    @staticmethod
    def parse_questions(raw_content, request_metadata: dict = {}):
        """
        Parse questions from OpenAI response and calculate totalMarks for each section
        Returns: (success: bool, data: dict/str, error: str/None)
        """
        success, parsed_data, error = JSONParser.extract_json_from_response(
            raw_content, result_metadata=request_metadata, parse=True
        )
        
        if success and isinstance(parsed_data, dict) and 'sections' in parsed_data:
            # Add totalMarks to each section
            for section in parsed_data['sections']:
                total_marks = JSONParser._calculate_section_marks(section)
                section['totalMarks'] = total_marks
        
        return success, parsed_data, error
    
    @staticmethod
    def _calculate_section_marks(section: dict) -> int:
        """
        Calculate total marks for a section by summing marks from all questions
        
        Args:
            section: Section dictionary containing questions
            
        Returns:
            Total marks for the section
        """
        total = 0
        
        if 'questions' in section and isinstance(section['questions'], list):
            for question in section['questions']:
                # Handle regular questions with marks field
                if 'marks' in question:
                    total += question['marks']
                
                # Handle case-based questions with subQuestions
                if 'subQuestions' in question and isinstance(question['subQuestions'], list):
                    for sub_q in question['subQuestions']:
                        if 'marks' in sub_q:
                            total += sub_q['marks']
        
        return total
    
    @staticmethod
    def merge_dicts(dict1: dict, dict2: dict) -> dict:
        """
        Merge two dictionaries, with values from dict2 overwriting those in dict1
        """
        return {**dict1, **dict2}