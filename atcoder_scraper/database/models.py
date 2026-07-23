from typing import TypedDict, List, Optional
from datetime import datetime

class Contest(TypedDict):
    contest_id: str
    contest_name: str
    contest_type: Optional[str]
    start_time: str
    duration: str
    rated_range: str
    url: str
    last_updated: datetime

class Problem(TypedDict):
    problem_id: str
    contest_id: str
    title: str
    difficulty: Optional[str]
    time_limit: Optional[str]
    memory_limit: Optional[str]
    statement_url: str
    tags: List[str]
    points: Optional[float]
    url: str
    scraped_at: datetime
