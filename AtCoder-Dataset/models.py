from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Contest:
    contest_id: str
    name: str
    url: str
    created_at: Optional[str] = None

@dataclass
class Problem:
    problem_id: str
    contest_id: str
    problem_url: str
    title: str
    statement: str
    constraints: str
    input_format: str
    output_format: str
    sample_inputs: List[str]
    sample_outputs: List[str]
    time_limit: str
    memory_limit: str
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    difficulty: Optional[str] = None
    rating: Optional[int] = None
    created_at: Optional[str] = None
