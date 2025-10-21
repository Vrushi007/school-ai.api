#!/usr/bin/env python3
"""
Test script to verify the JSON parser integration
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_json_parsing():
    """Test that JSON parsing works correctly for all endpoints"""
    print("🧪 Testing JSON Parser Integration")
    print("=" * 50)
    
    # Test 1: Lesson Plan Generation
    print("\n📚 Testing Lesson Plan JSON Parsing...")
    lesson_plan_payload = {
        "subject_name": "Mathematics",
        "class_name": "8th",
        "chapter_title": "Linear Equations in One Variable",
        "number_of_sessions": 2,
        "default_session_duration": "45 minutes"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/generate-lesson-plan", json=lesson_plan_payload)
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        
        if result['success']:
            lesson_plan = result['data']['lesson_plan']
            print(f"✅ Lesson Plan Parsed Successfully")
            print(f"   - Type: {type(lesson_plan)}")
            if isinstance(lesson_plan, list):
                print(f"   - Sessions: {len(lesson_plan)}")
                if lesson_plan:
                    print(f"   - First Session: {lesson_plan[0].get('title', 'N/A')}")
            elif isinstance(lesson_plan, dict):
                print(f"   - Keys: {list(lesson_plan.keys())}")
        else:
            print(f"❌ Lesson Plan Failed: {result.get('error', 'Unknown error')}")
            if 'raw_response' in result.get('data', {}):
                print(f"   Raw Response Preview: {result['data']['raw_response'][:200]}...")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the API server is running.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Session Content Generation
    print("\n📝 Testing Session Content JSON Parsing...")
    session_content_payload = {
        "session_data": {
            "title": "Introduction to Linear Equations",
            "summary": "Basic concepts of linear equations",
            "duration": "45 minutes",
            "objectives": [
                "Understand linear equations",
                "Solve simple equations"
            ]
        },
        "subject_name": "Mathematics",
        "class_name": "8th"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/session-content", json=session_content_payload)
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        
        if result['success']:
            session_content = result['data']['session_content']
            print(f"✅ Session Content Parsed Successfully")
            print(f"   - Type: {type(session_content)}")
            if isinstance(session_content, dict):
                print(f"   - Keys: {list(session_content.keys())}")
                print(f"   - Session Title: {session_content.get('sessionTitle', 'N/A')}")
        else:
            print(f"❌ Session Content Failed: {result.get('error', 'Unknown error')}")
            if 'raw_response' in result.get('data', {}):
                print(f"   Raw Response Preview: {result['data']['raw_response'][:200]}...")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Questions Generation
    print("\n❓ Testing Questions JSON Parsing...")
    questions_payload = {
        "class_name": "8th",
        "subject_name": "Mathematics",
        "chapters": ["Linear Equations in One Variable"],
        "question_requirements": "Generate 3 questions with mix of MCQ and short answer types"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/questions", json=questions_payload)
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        
        if result['success']:
            questions_data = result['data']['questions']
            print(f"✅ Questions Parsed Successfully")
            print(f"   - Type: {type(questions_data)}")
            if isinstance(questions_data, dict):
                questions = questions_data.get('questions', [])
                metadata = questions_data.get('metadata', {})
                print(f"   - Questions Count: {len(questions)}")
                print(f"   - Total Questions (metadata): {metadata.get('totalQuestions', 'N/A')}")
                print(f"   - Total Marks: {metadata.get('totalMarks', 'N/A')}")
        else:
            print(f"❌ Questions Failed: {result.get('error', 'Unknown error')}")
            if 'raw_response' in result.get('data', {}):
                print(f"   Raw Response Preview: {result['data']['raw_response'][:200]}...")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 JSON Parser Integration Test Complete")
    print("Check the results above to ensure all endpoints parse JSON correctly.")

if __name__ == "__main__":
    test_json_parsing()