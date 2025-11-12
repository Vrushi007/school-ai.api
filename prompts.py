"""
Prompt templates for OpenAI API interactions
"""

from typing import List, Dict, Any
from pathlib import Path
import json


class PromptTemplates:
    """Class containing all prompt templates for the School AI API"""
    
    # System messages for different functionalities
    LESSON_PLAN_SYSTEM = """Expert CBSE/NCERT educator. Output exactly 5 JSON session objects in an array. No text, only JSON."""
    
    SESSION_CONTENT_SYSTEM = """Expert CBSE/NCERT lesson planner. Always output one JSON object exactly following the provided field names. No explanations, no text outside JSON. Keep age-appropriate, teacher-friendly tone."""
    
    QUESTIONS_SYSTEM = """You are an expert educator and question paper creator specializing in Indian school standards (CBSE syllabus) with NCERT books. Create high-quality, curriculum-aligned questions that test various cognitive levels according to Bloom's taxonomy. Always respond with valid JSON only."""
    
    STUDENT_TUTOR_SYSTEM = """You are an expert tutor for Indian school students (CBSE/NCERT curriculum). 
Your role is to provide detailed, educational answers to student questions.

Guidelines:
- Provide clear, detailed explanations with step-by-step reasoning
- Include practical examples and real-world applications
- Use age-appropriate language for the student's level
- Break down complex concepts into simpler parts
- Encourage learning and curiosity
- If the question is outside academic scope, politely redirect to educational topics

{subject_context}
{class_context}

Always be encouraging, patient, and thorough in your explanations."""
    
    @staticmethod
    def get_lesson_plan_prompt(subject_name: str, class_name: str, chapter_title: str, 
                              number_of_sessions: int, default_session_duration: str) -> str:
        """Generate lesson plan prompt"""
        return f"""Generate {number_of_sessions} sequential sessions for {subject_name} Class {class_name}, Chapter: "{chapter_title}"

Each session includes: 
- title (clear),
- summary (1-2 sentences),
- duration ("{default_session_duration}"),
- 3-4 objectives.

Format:
[{{"sessionNumber": 1, "title": "", "summary": "", "duration": "{default_session_duration}", "objectives": []}}]"""
    
    @staticmethod
    def get_session_content_prompt(session_data: Dict[str, Any], subject_name: str, class_name: str) -> str:
        """Generate detailed session content prompt"""
        objectives_text = chr(10).join([f"- {obj}" for obj in session_data.get('objectives', [])])
        
        return f"""Generate a detailed lesson plan for:

Session Title: {session_data.get('title')}
Subject: {subject_name}
Class: {class_name} standard
Duration: {session_data.get('duration')}
Summary: {session_data.get('summary')}

Learning Objectives:
{objectives_text}

Output JSON keys (fill with relevant content, no placeholders):

{{
  "sessionTitle": "",
  "subject": "",
  "class": "",
  "duration": "",
  "summary": "",
  "objectives": [],
  "teachingScript": {{ "overview": "", "stepByStep": [{{ "time": "", "teacherLines": "", "studentActivity": "" }}], "transitions": "" }},
  "boardWorkPlan": {{ "definitions": [], "lawsOrRules": [{{ "name": "", "statement": "", "notation": "" }}], "diagramsToDraw": [{{ "label": "", "instructions": "", "placeholderTag": "" }}], "keywords": [] }},
  "detailedExplanations": {{ "subtopics": [{{ "title": "", "explanation": "", "example": "", "diagram": "", "comparisonTable": {{ "useIfRelevant": false, "headers": [], "rows": [] }}, "classroomTips": "" }}], "formulasAndDerivations": [] }},
  "activities": {{ "warmUpHook": "", "interactive": [{{ "name": "", "type": "", "steps": [], "time": "", "materials": [], "expectedOutcome": "" }}], "practiceProblems": [{{ "problem": "", "difficulty": "", "answer": "" }}], "groupWork": {{ "task": "", "roles": [], "successCriteria": "" }}, "experiments": [] }},
  "wrapUp": {{ "summary": [], "engagementQuestions": [], "closureActivity": "" }},
  "quickAssessment": {{ "fiveQandA": [{{ "q": "", "a": "" }}], "formatHints": "" }},
  "assessment": {{ "exitTicket": "", "homework": "", "rubricOrMarkingHints": "" }},
  "resources": {{ "materials": [], "references": [], "additionalReadingOrMedia": [], "youtubeSearchKeywords": [] }},
  "differentiation": {{ "strugglingLearners": "", "advancedStudents": "", "multipleLearningStyles": "" }}
}}"""
    
    @staticmethod
    def get_questions_prompt(class_name: str, subject_name: str, chapters: List[str], 
                           question_requirements: str) -> str:
        """Generate questions creation prompt"""
        chapters_text = ", ".join(chapters)
        
        return f"""Create a comprehensive set of questions for {class_name} standard {subject_name} students.

Chapters to cover: {chapters_text}

Question Requirements: {question_requirements}

Please generate a diverse set of questions that:
- Cover all specified chapters proportionally
- Are age-appropriate for {class_name} standard students
- Follow CBSE/NCERT curriculum standards
- Include various difficulty levels (easy, medium, hard)
- Cover different question types (MCQ, short answer, long answer, application-based)
- Test conceptual understanding, not just memorization

For each question, provide:
1. Question text
2. Question type (MCQ, Short Answer, Long Answer, Application)
3. Difficulty level (Easy, Medium, Hard)
4. Chapter reference
5. Marks/Points
6. Expected answer/solution (for non-MCQ)
7. Options (for MCQ only)
8. Correct answer (for MCQ only)

Please respond with a JSON object containing an array of question objects with the following structure:
{{
  "questions": [
    {{
      "id": number,
      "questionText": "string",
      "questionType": "MCQ|Short Answer|Long Answer|Application",
      "difficultyLevel": "Easy|Medium|Hard",
      "chapterReference": "string",
      "marks": number,
      "options": ["option1", "option2", "option3", "option4"], // only for MCQ
      "correctAnswer": "string", // for MCQ: option letter/number, for others: detailed answer
      "explanation": "string" // brief explanation of the answer
    }}
  ],
  "metadata": {{
    "totalQuestions": number,
    "questionTypeBreakdown": {{
      "MCQ": number,
      "Short Answer": number,
      "Long Answer": number,
      "Application": number
    }},
    "difficultyBreakdown": {{
      "Easy": number,
      "Medium": number,
      "Hard": number
    }},
    "chapterBreakdown": {{
      "chapter1": number,
      "chapter2": number
    }},
    "totalMarks": number
  }}
}}"""
    
    @staticmethod
    def get_student_tutor_system_prompt(subject_name: str = None, class_name: str = None) -> str:
        """Generate student tutor system prompt with context"""
        subject_context = f"Subject context: {subject_name}" if subject_name else ""
        class_context = f"Class/Grade: {class_name}" if class_name else ""
        
        return PromptTemplates.STUDENT_TUTOR_SYSTEM.format(
            subject_context=subject_context,
            class_context=class_context
        )
