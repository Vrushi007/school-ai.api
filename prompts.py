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
        
        return f"""Create detailed lesson content for the following session:

Session Title: {session_data.get('title')}
Subject: {subject_name}
Class: {class_name} standard
Duration: {session_data.get('duration')}
Summary: {session_data.get('summary')}

Learning Objectives:
{objectives_text}

Please provide a comprehensive lesson plan following this EXACT JSON structure:

{{
    "sessionTitle": "{session_data.get('title')}",
    "subject": "{subject_name}",
    "class": "{class_name}",
    "duration": "{session_data.get('duration')}",
    "summary": "{session_data.get('summary')}",
    "objectives": {session_data.get('objectives', [])},
    "teachingScript": {{
        "overview": "A short paragraph that the teacher can read to introduce the lesson (2-4 sentences).",
        "stepByStep": [
            {{
                "time": "e.g. 0-5 mins",
                "teacherLines": "What the teacher says (dialogue-style) — simple, classroom friendly language.",
                "studentActivity": "What students should do/respond during this step."
            }}
        ],
        "transitions": "Short phrases to move between segments (e.g. 'Now that we have seen X, let's try Y')."
    }},
    "boardWorkPlan": {{
        "definitions": [
            "Term — concise definition (one line)."
        ],
        "lawsOrRules": [
            {{
                "name": "Law name",
                "statement": "One-line statement of the law",
                "notation": "Any formula or symbol (if applicable)"
            }}
        ],
        "diagramsToDraw": [
            {{
                "label": "Diagram name",
                "instructions": "Step-by-step for drawing on board",
                "placeholderTag": "[Diagram Placeholder: Diagram name]"
            }}
        ],
        "keywords": [
            "keyword1", "keyword2", "keyword3"
        ]
    }},
    "detailedExplanations": {{
        "subtopics": [
            {{
                "title": "Subtopic title",
                "explanation": "Teacher friendly expanded explanation of the subtopic with examples.",
                "example": "Short worked example or scenario.",
                "diagram": "[Diagram Placeholder: short descriptor]",
                "comparisonTable": {{
                    "useIfRelevant": true,
                    "headers": ["Feature", "Item A", "Item B"],
                    "rows": [["Property 1", "A value/description", "B value/description"]]
                }},
                "classroomTips": "Reminders for teacher (misconceptions, demonstration notes)."
            }}
        ],
        "formulasAndDerivations": [
            {{
                "formula": "e.g. c = λν",
                "meaning": "Explain symbols and units",
                "derivationOrUse": "Brief derivation or how to use the formula in class problems"
            }}
        ]
    }},
    "activities": {{
        "warmUpHook": "One-sentence activity to grab attention (e.g. quick thought experiment).",
        "interactive": [
            {{
                "name": "Activity name",
                "type": "class discussion / demo / video / interactive experiment",
                "steps": ["Step 1", "Step 2"],
                "time": "minutes",
                "materials": ["material1", "material2"],
                "expectedOutcome": "What students will observe or learn from the activity"
            }}
        ],
        "practiceProblems": [
            {{
                "problem": "Short problem statement",
                "difficulty": "easy / medium / hard",
                "answer": "expected short answer or calculation outline"
            }}
        ],
        "groupWork": {{
            "task": "One-sentence group task (e.g. make a poster, build a model)",
            "roles": ["researcher", "recorder", "presenter"],
            "successCriteria": "What a good group output looks like"
        }},
        "experiments": [
            {{
                "title": "Experiment name",
                "objective": "What it demonstrates",
                "materials": ["list materials"],
                "procedure": ["Step 1", "Step 2"],
                "safetyNotes": "Any safety precautions",
                "observationPoints": "What students should record/notice"
            }}
        ]
    }},
    "wrapUp": {{
        "summary": "3-5 concise bullet sentences that restate the lesson's key takeaways.",
        "engagementQuestions": [
            "Open-ended question 1 to provoke thinking",
            "Open-ended question 2",
            "Application question 3",
            "Reflective question 4 (optional)"
        ],
        "closureActivity": "One-line activity to finish class (e.g. quick exit ticket prompt)."
    }},
    "quickAssessment": {{
        "fiveQandA": [
            {{
                "q": "Question 1 (clear, classroom-level)",
                "a": "Expected short answer"
            }},
            {{
                "q": "Question 2",
                "a": "Expected short answer"
            }},
            {{
                "q": "Question 3",
                "a": "Expected short answer"
            }},
            {{
                "q": "Question 4",
                "a": "Expected short answer"
            }},
            {{
                "q": "Question 5",
                "a": "Expected short answer"
            }}
        ],
        "formatHints": "Specify whether Qs are MCQ / short answer / calculation and marks for each (e.g. 1 mark each)."
    }},
    "assessment": {{
        "exitTicket": "One-sentence prompt for students to complete before leaving (e.g. 'Write one new thing you learned and one question you still have').",
        "homework": "Short homework assignment aligned with objectives (what to research or practice).",
        "rubricOrMarkingHints": "Short descriptors for quick marking (e.g. full / partial / no credit criteria)."
    }},
    "resources": {{
        "materials": [
            "material1 (e.g. prism)",
            "material2 (e.g. torch/flashlight)",
            "whiteboard, markers"
        ],
        "references": [
            "Main textbook reference (chapter and page)",
            "Lab manual or teacher guide"
        ],
        "additionalReadingOrMedia": [
            "Short article or video title with brief note on use (no external links)"
        ],
        "youtubeSearchKeywords": [
            "Search term 1 related to the lesson (e.g. 'Structure of Human Eye Class 10 Science')",
            "Search term 2 (e.g. 'Vision Defects Myopia Hypermetropia explained')"
        ]
    }},
    "differentiation": {{
        "strugglingLearners": "Concrete scaffolds, sentence starters, simplified diagrams, pairing with peers.",
        "advancedStudents": "Extension tasks, deeper problem solving or mini-research prompts.",
        "multipleLearningStyles": "How to present (visual / kinesthetic / auditory) — e.g. diagrams, hands-on demo, spoken summary."
    }},
    "formattingGuidelinesForOutput": {{
        "languageTone": "Simple, teacher-friendly, conversational (avoid overly technical jargon).",
        "diagramPlaceholders": "Include [Diagram Placeholder: short descriptor] exactly where teacher should draw or project diagrams.",
        "tables": "Use small comparison tables (max 4-5 rows) for quick board writing.",
        "lengthHints": {{
            "teachingScript": "Approx 200-350 words",
            "eachSubtopic": "Approx 80-150 words",
            "assessmentQ": "Short and precise — one line per Q"
        }},
        "jsonValidationNotes": "All text fields must be strings; lists must be arrays. Replace placeholder strings with actual content when generating session output."
    }}
}}

IMPORTANT INSTRUCTIONS:
1. Replace ALL placeholder text with actual, relevant content for the session
2. Ensure all arrays have at least one real item (no empty arrays)
3. Make sure all text is appropriate for {class_name} standard students
4. Include subject-specific terminology and examples relevant to {subject_name}
5. Respond with ONLY valid JSON - no additional text or explanations
6. All content should be practical and implementable in a real classroom
7. Use simple, teacher-friendly language throughout"""
    
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