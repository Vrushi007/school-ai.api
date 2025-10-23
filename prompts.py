"""
Prompt templates for OpenAI API interactions
"""

from typing import List, Dict, Any


class PromptTemplates:
    """Class containing all prompt templates for the School AI API"""
    
    # System messages for different functionalities
    LESSON_PLAN_SYSTEM = """You are an expert educational content creator specializing in curriculum design for Indian school standards (CBSE syllabus) with NCERT books. Always respond with valid JSON only."""
    
    SESSION_CONTENT_SYSTEM = """You are an expert educational content creator specializing in detailed lesson planning for Indian school standards (CBSE syllabus) with NCERT books. Create comprehensive, engaging lesson content that is age-appropriate and follows pedagogical best practices. Always respond with valid JSON only."""
    
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
        return f"""Create a detailed session plan for a teacher teaching {subject_name} to {class_name} standard students.

Chapter: {chapter_title}
Number of Sessions: {number_of_sessions}

For each session, provide:
1. A clear, engaging session title
2. A comprehensive summary (2-3 sentences) of what will be covered
3. Estimated duration (typically {default_session_duration} per session)
4. 3-4 specific learning objectives

The sessions should:
- Build progressively from basic to advanced concepts
- Be age-appropriate for {class_name} standard students
- Include practical examples and applications
- Cover the complete chapter content across all {number_of_sessions} sessions

Please respond with a JSON array containing exactly {number_of_sessions} session objects, each with the following structure:
{{
  "sessionNumber": number,
  "title": "string",
  "summary": "string", 
  "duration": "string",
  "objectives": ["objective1", "objective2", "objective3", "objective4"]
}}"""
    
    @staticmethod
    def get_session_content_prompt(session_data: Dict[str, Any], subject_name: str, class_name: str) -> str:
        """Generate detailed session content prompt"""
        objectives_text = chr(10).join([f"- {obj}" for obj in session_data.get('objectives', [])])
        
        return f"""Create detailed lesson content for the following session:

Session Title: {session_data.get('title')}
Subject: {subject_name}
Class: {class_name} standard
Duration: {session_data.get('duration')}
Summary: {session_data.get('summary')}

Learning Objectives:
{objectives_text}

Please provide a comprehensive lesson plan with the following sections:

1. **Introduction** (5-10 minutes)
   - Hook/attention grabber
   - Brief overview of what will be covered
   - Connection to previous learning

2. **Main Content** (detailed breakdown)
   - Key concepts explanation
   - Step-by-step teaching sequence
   - Important formulas/definitions
   - Real-world examples and applications

3. **Activities & Practice**
   - Interactive activities for student engagement
   - Practice problems with solutions
   - Group work suggestions
   - Hands-on experiments (if applicable)

4. **Assessment & Evaluation**
   - Quick assessment questions
   - Exit ticket suggestions
   - Homework assignments

5. **Resources & Materials**
   - Required materials/equipment
   - Reference materials
   - Additional reading suggestions

6. **Differentiation Strategies**
   - Support for struggling learners
   - Extensions for advanced students
   - Multiple learning styles accommodation

Please respond with valid JSON only in the following structure:
{{
  "sessionTitle": "string",
  "duration": "string",
  "introduction": {{
    "hook": "string",
    "overview": "string",
    "previousConnection": "string"
  }},
  "mainContent": {{
    "keyConcepts": ["concept1", "concept2", "concept3"],
    "teachingSequence": ["step1", "step2", "step3"],
    "formulas": ["formula1", "formula2"],
    "examples": ["example1", "example2"]
  }},
  "activities": {{
    "interactive": ["activity1", "activity2"],
    "practiceProblems": ["problem1", "problem2"],
    "groupWork": "string",
    "experiments": ["experiment1", "experiment2"]
  }},
  "assessment": {{
    "quickQuestions": ["question1", "question2", "question3"],
    "exitTicket": "string",
    "homework": "string"
  }},
  "resources": {{
    "materials": ["material1", "material2"],
    "references": ["ref1", "ref2"],
    "additionalReading": ["reading1", "reading2"]
  }},
  "differentiation": {{
    "strugglingLearners": "string",
    "advancedStudents": "string",
    "multipleStyles": "string"
  }}
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