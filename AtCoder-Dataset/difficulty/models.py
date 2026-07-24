from dataclasses import dataclass

@dataclass
class DifficultyResult:
    difficulty: str
    estimated_rating: int
    confidence: int
    reason: str
