class OpenAIHelper:
    @staticmethod
    def extract_output_text(response):
        for item in response.output:
            if hasattr(item, "content") and item.content:
                for c in item.content:
                    if hasattr(c, "text") and c.text:
                        return c.text
        raise ValueError("No valid text content found in response")
    
    @staticmethod
    def allocate_marks_and_generate_blueprint(total_marks: int):
        MARKS_PER_QUESTION = {"MCQ": 1, "VSA": 2, "SA": 3, "LA": 5, "CASE": 4}
        SECTION_MAP = {"A": "MCQ", "B": "VSA", "C": "SA", "D": "LA", "E": "CASE"}

        SECTION_DISTRIBUTION = {
            "A": 0.15, "B": 0.15, "C": 0.25, "D": 0.25, "E": 0.20
        }

        allocated_marks = {
            sec: round(total_marks * pct)
            for sec, pct in SECTION_DISTRIBUTION.items()
        }

        questions_per_section = {
            sec: max(1, allocated_marks[sec] // MARKS_PER_QUESTION[SECTION_MAP[sec]])
            for sec in SECTION_MAP
        }

        # Adjust marks mismatch
        actual_marks = sum(
            questions_per_section[sec] * MARKS_PER_QUESTION[SECTION_MAP[sec]]
            for sec in SECTION_MAP
        )
        diff = total_marks - actual_marks
        if diff != 0:
            questions_per_section["A"] += diff  # Adjust MCQs

        # --- BUILD BLUEPRINT HERE ---
        blueprint_marks = {
            SECTION_MAP[sec]: questions_per_section[sec] * MARKS_PER_QUESTION[SECTION_MAP[sec]]
            for sec in SECTION_MAP
        }

        final = {
            "total_marks": total_marks,
            "questions_per_section": questions_per_section,
            "blueprint": {
                "marksDistribution": blueprint_marks,
                "difficultySplit": {"Easy": "40%", "Medium": "40%", "Hard": "20%"},
                "skillsCovered": []
            }
        }

        return final

