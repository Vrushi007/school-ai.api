from flask import Blueprint, jsonify, request
from services.openai_service import OpenAIService
from utils.json_parser import JSONParser

lesson_plan_bp = Blueprint('lesson_plan', __name__)
openai_service = OpenAIService()

@lesson_plan_bp.route('/api/generate-lesson-plan', methods=['POST'])
def generate_lesson_plan():
    """
    Generate lesson plan endpoint
    """
    try:
        data = request.json
        
        # Extract required parameters
        subject_name = data.get("subjectName")
        class_name = data.get("className")
        chapter_title = data.get("chapterTitle")
        number_of_sessions = data.get("numberOfSessions")
        default_session_duration = data.get("defaultSessionDuration")
        
        # Validate required fields
        required_fields = {
            "subjectName": subject_name,
            "className": class_name,
            "chapterTitle": chapter_title,
            "numberOfSessions": number_of_sessions,
            "defaultSessionDuration": default_session_duration
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing_fields": missing_fields
            }), 400
        
        # Generate lesson plan using OpenAI service
        raw_response = openai_service.generate_lesson_plan(
            subject_name, 
            class_name, 
            chapter_title, 
            number_of_sessions, 
            default_session_duration
        )
        
        # Parse the response
        success, lesson_plan_data, error = JSONParser.parse_lesson_plan(raw_response)
        
        if success:
            return jsonify({"lesson_plan": lesson_plan_data})
        else:
            return jsonify({
                "error": "Failed to parse lesson plan JSON",
                "raw_content": lesson_plan_data,
                "json_error": error
            }), 500
            
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@lesson_plan_bp.route('/api/generate-detailed-content-for-session', methods=['POST'])
def generate_detailed_content_for_session():
    """
    Generate detailed content for a specific session endpoint
    """
    try:
        data = request.json
        
        # Extract required parameters
        session_data = data.get("sessionData")
        subject_name = data.get("subjectName")
        class_name = data.get("className")
        
        # Validate required fields
        if not session_data:
            return jsonify({
                "error": "Missing required field: sessionData"
            }), 400
            
        if not subject_name:
            return jsonify({
                "error": "Missing required field: subjectName"
            }), 400
            
        if not class_name:
            return jsonify({
                "error": "Missing required field: className"
            }), 400
        
        # Validate session data structure
        required_session_fields = ["title", "summary", "duration", "objectives"]
        missing_session_fields = [field for field in required_session_fields if field not in session_data or not session_data[field]]
        
        if missing_session_fields:
            return jsonify({
                "error": "Invalid session data structure",
                "missing_session_fields": missing_session_fields,
                "expected_fields": required_session_fields
            }), 400
        
        # Generate detailed session content using OpenAI service
        raw_response = openai_service.generate_detailed_session_content(
            session_data,
            subject_name,
            class_name
        )
        
        # Parse the response
        success, session_content_data, error = JSONParser.parse_detailed_session_content(raw_response)
        
        if success:
            return jsonify({"sessionContent": session_content_data})
        else:
            return jsonify({
                "error": "Failed to parse session content JSON",
                "raw_content": session_content_data,
                "json_error": error
            }), 500
            
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500