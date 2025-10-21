#!/usr/bin/env python3
"""
Test script to verify the School AI API functionality
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the API server is running.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_lesson_plan_generation():
    """Test lesson plan generation"""
    print("\n📚 Testing lesson plan generation...")
    
    payload = {
        "subject_name": "Mathematics",
        "class_name": "8th",
        "chapter_title": "Linear Equations in One Variable",
        "number_of_sessions": 3,
        "default_session_duration": "45 minutes"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/generate-lesson-plan", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            if result.get('success') and result.get('data'):
                lesson_plan = result['data']['lesson_plan']
                if isinstance(lesson_plan, list):
                    print(f"Generated {len(lesson_plan)} sessions")
                    return lesson_plan
                else:
                    print(f"Lesson plan type: {type(lesson_plan)}")
                    return lesson_plan
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_session_content_generation():
    """Test detailed session content generation"""
    print("\n📝 Testing session content generation...")
    
    payload = {
        "session_data": {
            "title": "Introduction to Linear Equations",
            "summary": "Students will learn the basic concepts of linear equations and practice solving simple equations with one variable.",
            "duration": "45 minutes",
            "objectives": [
                "Understand what a linear equation is",
                "Identify variables and constants in equations",
                "Solve simple linear equations using basic operations",
                "Apply linear equations to solve real-world problems"
            ]
        },
        "subject_name": "Mathematics",
        "class_name": "8th"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/session-content", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            if result.get('success') and result.get('data'):
                session_content = result['data']['session_content']
                print(f"Generated session: {session_content.get('sessionTitle', 'N/A')}")
                return True
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_question_generation():
    """Test question generation"""
    print("\n❓ Testing question generation...")
    
    payload = {
        "class_name": "8th",
        "subject_name": "Mathematics",
        "chapters": ["Linear Equations in One Variable", "Understanding Quadrilaterals"],
        "question_requirements": "Generate 10 questions with a mix of MCQ (4), Short Answer (3), and Long Answer (3) types. Include easy, medium, and hard difficulty levels."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/questions", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            if result.get('success') and result.get('data'):
                questions_data = result['data']['questions']
                if isinstance(questions_data, dict):
                    questions = questions_data.get('questions', [])
                    metadata = questions_data.get('metadata', {})
                    print(f"Generated {len(questions)} questions")
                    print(f"Total marks: {metadata.get('totalMarks', 'N/A')}")
                else:
                    print(f"Questions data type: {type(questions_data)}")
                return True
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting School AI API Tests")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("\n❌ Health check failed. Please ensure:")
        print("1. The API server is running (python main.py)")
        print("2. The server is accessible at http://localhost:8000")
        return
    
    print("✅ Health check passed!")
    
    # Test all endpoints
    test_results = []
    
    # Test lesson plan generation
    lesson_plan = test_lesson_plan_generation()
    test_results.append(("Lesson Plan Generation", lesson_plan is not None))
    
    # Test session content generation
    session_result = test_session_content_generation()
    test_results.append(("Session Content Generation", session_result))
    
    # Test question generation
    question_result = test_question_generation()
    test_results.append(("Question Generation", question_result))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
    
    passed_count = sum(1 for _, passed in test_results if passed)
    total_count = len(test_results)
    
    print(f"\nOverall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()