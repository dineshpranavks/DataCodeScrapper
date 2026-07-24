from classifier.taxonomy import TOPICS, DIFFICULTY_LEVELS

def build_prompt(title: str, statement: str, constraints: str) -> str:
    """
    Builds the prompt for the AI to classify a problem.
    """
    topics_str = ", ".join(TOPICS)
    difficulty_str = ", ".join(DIFFICULTY_LEVELS)
    
    return f"""You are an expert competitive programmer.

Analyze the following AtCoder problem.

Determine:
1. Main DSA Topic
2. Subtopic
3. Difficulty Level
4. Estimated AtCoder Rating
5. Primary Algorithm
6. Confidence Score (0-100)

Use ONLY the allowed taxonomy.
Allowed Topics: {topics_str}
Allowed Difficulties: {difficulty_str}

Return ONLY valid JSON.
No markdown. No explanations. Only JSON.

Expected JSON format:
{{
    "topic": "Dynamic Programming",
    "subtopic": "Knapsack DP",
    "difficulty": "Medium Hard",
    "estimated_rating": 1400,
    "algorithm": "0/1 Knapsack",
    "confidence": 96
}}

Problem Title:
{title}

Statement:
{statement}

Constraints:
{constraints}
"""
