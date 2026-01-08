"""
Prompt templates for OpenAI API interactions
"""

from typing import List, Dict, Any



class PromptTemplates:
    """Class containing all prompt templates for the School AI API"""
    
    # System messages for different functionalities
    LESSON_PLAN_SYSTEM = """You are an expert CBSE/NCERT lesson planner and classroom pedagogy designer.

You generate lesson plans STRICTLY based on provided Knowledge Points (KPs).
You must NOT introduce new concepts, objectives, terminology, or examples
that are not derivable from the given KPs.

Always follow NCERT terminology and Class-appropriate pedagogy.

Output ONE JSON object exactly matching the provided output schema.
Do NOT add explanations, comments, or text outside JSON."""
    
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
    
    SESSION_SUMMARY_SYSTEM = """You are an experienced school teacher preparing a lesson plan for another teacher.

Your task is to create a concise instructional overview for a teaching session.

Guidelines for the summary:
- Write strictly for teachers, not for students.
- Describe the teaching focus and scope of this session.
- Limit the summary to 2–4 sentences.
- Do NOT include activities, assessments, or student engagement language.
- Do NOT mention knowledge point codes or IDs.

Guidelines for the objectives:
- Provide 2–4 objectives.
- Each objective should describe what the teacher intends to cover or emphasise.
- Use clear instructional verbs (e.g., introduce, explain, distinguish, demonstrate).
- Keep objectives aligned strictly to the given knowledge points.
- Avoid student-facing phrasing such as "students will enjoy".

Output Rules:
- Return ONLY valid JSON.
- Do NOT include any explanatory text outside JSON.
- Do NOT include session title, duration, or numbering.
- The JSON must contain exactly two top-level properties: "summary" and "objectives".

Expected JSON format:

{
  "summary": "",
  "objectives": []
}"""
    
    @staticmethod
    def get_kp_grouping_system_prompt(board: str = "CBSE") -> str:
        """Generate KP grouping system prompt with board context"""
        board_context = f"{board}/NCERT" if board == "CBSE" else board
        return f"""You are an expert school curriculum planner specializing in {board_context} curriculum.

Group the given knowledge points into the specified number of teaching sessions.
Each session represents one classroom period of ~40 minutes.

Rules:
- Respect prerequisite order between knowledge points.
- Each session should cover a coherent concept flow.
- A session may include multiple knowledge points.
- Do NOT split a single knowledge point across sessions.
- Ensure earlier sessions are easier and later sessions progress in difficulty.
- Follow {board_context} pedagogical standards and terminology.

Return ONLY valid JSON in the following format:

{{
  "sessions": [
    {{
      "session_number": 1,
      "session_title": "...",
      "kp_ids": ["kp01", "kp02"]
    }}
  ]
}}"""
    
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
    def get_session_content_prompt(title: str, subject_name: str, class_name: str, duration: str, summary: str, objectives: List[str], kp_list_with_description: str) -> str:
        """Generate detailed session content prompt"""
        return f"""Generate a detailed lesson plan for:
Session Title: {title}
Subject: {subject_name}
Class: {class_name} standard
Duration: {duration}
Instructional Summary:
{summary}
Learning Objectives:
{objectives}
Knowledge Points to be covered in this session:
{kp_list_with_description}
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
    def get_knowledge_points_prompt(grade: int, subject: str, chapter: str, section: str = None) -> str:
        """Generate knowledge points decomposition prompt - simplified to AI-only KP generation"""
        section_spec = f"Section: {section}" if section else "All sections in chapter"
        
        return f"""Decompose the curriculum into atomic, teachable Knowledge Points (KPs).

CURRICULUM INPUT:
- Grade: {grade}
- Subject: {subject}
- Chapter: {chapter}
- Scope: {section_spec}

RETURN ONLY this JSON structure (no syllabus wrapper):

{{
  "knowledge_points": [
    {{
      "section_title": "<section name>",
      "kp_title": "<concise action-oriented title>",
      "kp_description": "<what the student must demonstrably do>",
      "bloom_level": "Remember | Understand | Apply | Analyze | Evaluate | Create",
      "irt_difficulty": <float -3.0 to +3.0>,
      "difficulty_label": "Very Easy | Easy | Medium | Hard | Very Hard",
      "prerequisite_kps": ["<prerequisite_id_1>", "..."] or [],
      "misconception_tags": ["<tag>", "..."],
      "assessment_examples": ["<example 1>", "<example 2>"],
      "detailed_explanation": "<100-150 word explanation>",
      "auto_grading_components": {{
        "conceptual_triples": [{{"triple": "<subject, predicate, object>"}}],
        "key_terms_and_synonyms": [
          {{"term": "<key term>", "synonyms": ["<synonym 1>", "<synonym 2>"]}}
        ],
        "assessment_criteria": [
          {{"criterion": "<criterion>", "weightage": <int 0-100>}}
        ]
      }},
      "tags": ["<tag1>", "<tag2>", "<tag3>"],
      "real_world_applications": ["<application 1>", "<application 2>"]
    }}
  ]
}}

GUIDELINES:
1. Each KP = ONE clear cognitive skill (atomic)
2. Ordered by prerequisite dependency
3. Bloom level must match action verbs
4. IRT difficulty increases with abstraction
5. Assessment examples = exactly 2
6. Assessment criteria weightages sum to 100%
7. Use NCERT terminology for {subject} Grade {grade}
8. Prerequisite KPs reference placeholder IDs (server will generate final IDs)
"""

    @staticmethod
    def get_kp_grouping_prompt(board: str, chapter: str, class_name: str, subject: str, 
                              number_of_sessions: int, session_duration: str,
                              knowledge_points: List[Dict[str, Any]]) -> str:
        """Generate KP grouping into sessions prompt"""
        kps_formatted = "\n".join([
            f"  - {kp['kp_id']}: {kp['title']} (Difficulty: {kp['difficulty']}, "
            f"Cognitive: {kp['cognitive_level']}, Prerequisites: {kp['prerequisites']})"
            for kp in knowledge_points
        ])
        
        board_context = f"{board}/NCERT" if board == "CBSE" else board
        
        return f"""Group the following knowledge points into {number_of_sessions} teaching sessions.

Board: {board_context}
Chapter: {chapter}
Class: {class_name}
Subject: {subject}
Session Duration: {session_duration}

Knowledge Points:
{kps_formatted}

Provide {number_of_sessions} sessions with coherent grouping that respects:
1. Prerequisite dependencies (prerequisites must come in earlier sessions)
2. Cognitive progression (easier → harder)
3. Conceptual coherence within each session
4. Balanced distribution across sessions
5. {board_context} curriculum standards and terminology

Return ONLY JSON in this exact format:
{{
  "sessions": [
    {{
      "session_number": 1,
      "session_title": "...",
      "kp_ids": ["1", "2", "3"]
    }}
  ]
}}"""

    @staticmethod
    def get_session_summary_prompt(board: str, chapter: str, class_name: str, subject: str,
                                   session_title: str, knowledge_points: List[Dict[str, Any]]) -> str:
        """Generate session summary prompt"""
        board_context = f"{board}/NCERT" if board == "CBSE" else board
        
        kps_formatted = "\n".join([
            f"  - {kp['title']} (Cognitive Level: {kp['cognitive_level']}, Difficulty: {kp['difficulty']})"
            for kp in knowledge_points
        ])
        
        return f"""Context:
- Board: {board_context}
- Chapter: {chapter}
- Class: {class_name}
- Subject: {subject}
- Session Title: {session_title}

Knowledge Points included in this session:
{kps_formatted}

Task:
Create a concise instructional overview for this session consisting of:
1. A short session summary (2-4 sentences)
2. A list of instructional objectives (2-4 objectives)

Return ONLY JSON in this exact format:
{{
  "summary": "",
  "objectives": []
}}"""
