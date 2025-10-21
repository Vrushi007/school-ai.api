import json
import re

class JSONParser:
    @staticmethod
    def extract_json_from_response(raw_content):
        """
        Extract JSON content from OpenAI response, handling markdown code blocks
        """
        # Remove markdown code blocks if present
        # Look for ```json ... ``` or ``` ... ``` patterns
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_content, re.DOTALL)
        if json_match:
            json_content = json_match.group(1).strip()
        else:
            # If no code blocks found, use the raw content
            json_content = raw_content.strip()
        
        return json_content
    
    @staticmethod
    def parse_lesson_plan(raw_content):
        """
        Parse lesson plan from OpenAI response
        Returns: (success: bool, data: dict/str, error: str/None)
        """
        try:
            json_content = JSONParser.extract_json_from_response(raw_content)
            lesson_plan_data = json.loads(json_content)
            return True, lesson_plan_data, None
        except json.JSONDecodeError as e:
            return False, raw_content, str(e)
    
    @staticmethod
    def parse_detailed_session_content(raw_content):
        """
        Parse detailed session content from OpenAI response
        Returns: (success: bool, data: dict/str, error: str/None)
        """
        try:
            json_content = JSONParser.extract_json_from_response(raw_content)
            session_content_data = json.loads(json_content)
            return True, session_content_data, None
        except json.JSONDecodeError as e:
            return False, raw_content, str(e)
    
    @staticmethod
    def parse_questions(raw_content):
        """
        Parse questions from OpenAI response
        Returns: (success: bool, data: dict/str, error: str/None)
        """
        try:
            json_content = JSONParser.extract_json_from_response(raw_content)
            questions_data = json.loads(json_content)
            return True, questions_data, None
        except json.JSONDecodeError as e:
            return False, raw_content, str(e)