def build_prompt(title: str, statement: str, constraints: str) -> str:
    """
    Builds the prompt for the AI to estimate the difficulty of a problem.
    """
    return f"""You are an experienced AtCoder problem setter.

Estimate the difficulty of this programming problem.

Use:
- statement
- constraints
- required algorithms
- implementation complexity
- mathematical reasoning
- edge cases

Return ONLY JSON.
No markdown. No explanations. Only JSON.

Expected JSON format:
{{
    "difficulty": "Medium Hard",
    "estimated_rating": 1400,
    "confidence": 95,
    "reason": "Requires dynamic programming with state optimization."
}}

Allowed difficulties: Very Easy, Easy, Medium, Medium Hard, Hard, Very Hard, Expert
Rating scale: 0-4000

Problem Title

{title}

Statement

{statement}

Constraints

{constraints}
"""
