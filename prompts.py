"""
Prompt templates for OpenAI API interactions
"""

from typing import List, Dict, Any



class PromptTemplates:
    """Class containing all prompt templates for the School AI API"""
    
    # System messages for different functionalities
    LESSON_PLAN_SYSTEM = """Expert CBSE/NCERT educator. Respond only in JSON."""
    
    SESSION_CONTENT_SYSTEM = """Expert CBSE/NCERT lesson planner. Always output one JSON object exactly following the provided field names. No explanations, no text outside JSON. Keep age-appropriate, teacher-friendly tone."""
    
    QUESTIONS_SYSTEM = """You create CBSE/NCERT-aligned question papers. 
Always output ONLY valid JSON that matches the user-given structure and counts. 
Never add or remove questions. 
Never modify marks per question."""
    
    KNOWLEDGE_POINTS_SYSTEM = """You are an expert curriculum architect and assessment scientist.
You specialize in CBSE/NCERT syllabus decomposition, competency-based education,
Bloom's Taxonomy alignment, and Item Response Theory (IRT).

Your task is to decompose curriculum content into atomic, teachable,
and assessable Knowledge Points (KPs).

Follow these rules strictly:
- Each KP must represent ONE clear cognitive skill.
- KPs must be atomic (no compound learning outcomes).
- KPs must be ordered by prerequisite dependency.
- Use NCERT terminology only.
- Bloom level must match the action verb used.
- IRT difficulty must increase with abstraction and integration.

MANDATORY OUTPUT FORMAT:
Return ONLY valid JSON in the EXACT structure provided by the user.
Do NOT add, remove, or rename any fields.
Do NOT add explanations, comments, or markdown.

CONSTRAINT RULES:
1. Foundational KPs must have an empty prerequisite_kps array.
2. A KP must NOT depend on a KP from a later section.
3. assessment_examples must be EXACTLY 2 per KP.
4. misconception_tags must be concept-specific, not generic.
5. difficulty_label must align with irt_difficulty:
   - Very Easy: -3.0 to -2.0
   - Easy: -2.0 to -1.0
   - Medium: -1.0 to +1.0
   - Hard: +1.0 to +2.0
   - Very Hard: +2.0 to +3.0
6. kp_id must be stable and deterministic."""
    
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
    def get_questions_prompt(class_name: str, subject_name: str, chapters: List[str], total_marks: int, allocation: Dict[str, Any]) -> str:
        """Generate questions creation prompt"""
        chapters_text = ", ".join(chapters)
        
        countA = allocation["A"]
        countB = allocation["B"]
        countC = allocation["C"]
        countD = allocation["D"]
        countE = allocation["E"]

        prompt = f"""
Create a Class {class_name} {subject_name} question paper from these chapters:
{chapters_text}

Total marks: {total_marks}

Use EXACTLY this many questions (computed by backend):

A: {countA} MCQ (1 mark each)
B: {countB} VSA (2 marks each)
C: {countC} SA (3 marks each)
D: {countD} LA (5 marks each)
E: {countE} CASE (4 marks each, each CASE must contain 3 sub-questions: 1m, 1m, 2m)

Rules:
- Maintain difficulty split: Easy 40%, Medium 40%, Hard 20%.
- All questions must be NCERT-based and conceptually correct.
- Do NOT change counts/marks.
- Output ONLY JSON in this structure:

{{
  "sections": [
    {{
      "sectionName": "A",
      "description": "Multiple Choice Questions",
      "questions": [
        {{ "qNo": 1, "questionText": "", "marks": 1, "difficulty": "", "type": "MCQ", "options": ["", "", "", ""], "correctAnswer": "" }}
      ]
    }},
    {{
      "sectionName": "B",
      "description": "Very Short Answer Questions",
      "questions": [
        {{ "qNo": 1, "questionText": "", "marks": 2, "difficulty": "", "type": "VSA", "answerHints": "" }}
      ]
    }},
    {{
      "sectionName": "C",
      "description": "Short Answer Questions",
      "questions": [
        {{ "qNo": 1, "questionText": "", "marks": 3, "difficulty": "", "type": "SA", "answerHints": "" }}
      ]
    }},
    {{
      "sectionName": "D",
      "description": "Long Answer Questions",
      "questions": [
        {{ "qNo": 1, "questionText": "", "marks": 5, "difficulty": "", "type": "LA", "answerHints": "" }}
      ]
    }},
    {{
      "sectionName": "E",
      "description": "Case-Based / Source-Based Questions",
      "questions": [
        {{ 
          "qNo": 1, 
          "caseText": "",
          "type": "CASE",
          "subQuestions": [
            {{ "subQNo": "a", "questionText": "", "marks": 1, "answerHints": "" }},
            {{ "subQNo": "b", "questionText": "", "marks": 1, "answerHints": "" }},
            {{ "subQNo": "c", "questionText": "", "marks": 2, "answerHints": "" }}
          ]
        }}
      ]
    }}
  ],
  "instructions": [
    "All questions are compulsory.",
    "Answer the questions in sequence.",
    "Use diagrams wherever necessary.",
    "No overall choice, but internal choices may be given."
  ]
}}"""
        return prompt
    
    @staticmethod
    def get_student_tutor_system_prompt(subject_name: str = None, class_name: str = None) -> str:
        """Generate student tutor system prompt with context"""
        subject_context = f"Subject context: {subject_name}" if subject_name else ""
        class_context = f"Class/Grade: {class_name}" if class_name else ""
        
        return PromptTemplates.STUDENT_TUTOR_SYSTEM.format(
            subject_context=subject_context,
            class_context=class_context
        )

    @staticmethod
    def get_knowledge_points_prompt(board: str, grade: int, subject: str, chapter: str, section: str = None) -> str:
        """Generate knowledge points decomposition prompt"""
        section_spec = f"Section: {section}" if section else "Sections: All in chapter"
        
        return f"""CURRICULUM INPUT:

Board: {board} (NCERT-aligned)
Grade: {grade}
Subject: {subject}
Chapter: {chapter}
{section_spec}

MANDATORY OUTPUT FORMAT:

Return ONLY valid JSON in the EXACT structure below.
Do NOT add, remove, or rename any fields.
Do NOT add explanations, comments, or markdown.

{{
  "syllabus": {{
    "board": "{board}",
    "grade": {grade},
    "subject": "{subject}",
    "chapter": "{chapter}",
    "sections": [
      {{
        "section_title": "<string>",
        "knowledge_points": [
          {{
            "kp_id": "<{board.lower()}{grade}_{subject.lower().replace(' ', '_')}_{chapter.lower().replace(' ', '_')}_kpXX>",
            "kp_title": "<concise action-oriented title>",
            "kp_description": "<what the student must demonstrably do>",
            "bloom_level": "Remember | Understand | Apply | Analyze | Evaluate | Create",
            "irt_difficulty": <float between -3.0 and +3.0>,
            "difficulty_label": "Very Easy | Easy | Medium | Hard | Very Hard",
            "prerequisite_kps": ["<kp_id>", "..."],
            "misconception_tags": ["<snake_case_code>", "..."],
            "assessment_examples": [
              "<short observable example 1>",
              "<short observable example 2>"
            ]
          }}
        ]
      }}
    ]
  }}
}}"""
