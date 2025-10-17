from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_lesson_plan(self, subject_name, class_name, chapter_title, number_of_sessions, default_session_duration):
        """
        Generate a lesson plan using OpenAI API
        """
        user_message = f"""Create a detailed session plan for a teacher teaching {subject_name} to {class_name} standard students.

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

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational content creator specializing in curriculum design for Indian school standards (CBSE syllabus) with NCERT books. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        return response.choices[0].message.content
    
    def generate_detailed_session_content(self, session_data, subject_name, class_name):
        """
        Generate detailed content for a specific session using OpenAI API
        """
        user_message = f"""Create detailed lesson content for the following session:

Session Title: {session_data.get('title')}
Subject: {subject_name}
Class: {class_name} standard
Duration: {session_data.get('duration')}
Summary: {session_data.get('summary')}

Learning Objectives:
{chr(10).join([f"- {obj}" for obj in session_data.get('objectives', [])])}

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

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational content creator specializing in detailed lesson planning for Indian school standards (CBSE syllabus) with NCERT books. Create comprehensive, engaging lesson content that is age-appropriate and follows pedagogical best practices. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        return response.choices[0].message.content