import os
import json
import time
import sys
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Ensure parent directory is in sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from models import Problem
from database.database import Database
from difficulty.models import DifficultyResult
from difficulty.prompt import build_prompt

# Load environment variables
load_dotenv()

DIFFICULTY_LEVELS = [
    "Very Easy", "Easy", "Medium", "Medium Hard", "Hard", "Very Hard", "Expert"
]

class DifficultyEstimator:
    """
    Difficulty Estimation Module for AtCoder Problems.
    """
    
    def __init__(self, model: str = None):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        )
        self.model = model or os.getenv("NVIDIA_MODEL", "meta/llama3-70b-instruct")
        self.db = Database()

    def _validate_response(self, response_text: str) -> Optional[DifficultyResult]:
        """
        Validates the JSON response and returns a DifficultyResult object.
        """
        try:
            # Strip markdown if model incorrectly adds it
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
                
            data = json.loads(clean_text)
            
            # Validate Difficulty
            difficulty = data.get("difficulty")
            if difficulty not in DIFFICULTY_LEVELS:
                return None
                
            # Validate Rating
            rating = int(data.get("estimated_rating", -1))
            if not (0 <= rating <= 4000):
                return None
                
            # Validate Confidence
            confidence = int(data.get("confidence", -1))
            if not (0 <= confidence <= 100):
                return None
                
            reason = data.get("reason", "")
            
            return DifficultyResult(
                difficulty=difficulty,
                estimated_rating=rating,
                confidence=confidence,
                reason=reason
            )
        except (json.JSONDecodeError, ValueError, KeyError):
            return None

    def estimate(self, problem: Problem) -> Optional[DifficultyResult]:
        """
        Estimates the difficulty of a single problem using OpenAI API.
        """
        prompt = build_prompt(problem.title, problem.statement, problem.constraints)
        
        for attempt in range(2):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a difficulty estimator that strictly outputs JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                
                response_text = response.choices[0].message.content
                result = self._validate_response(response_text)
                
                if result:
                    return result
                    
                print(f"Validation failed for {problem.problem_id}, retrying...")
            except OpenAIError as e:
                print(f"API Error on {problem.problem_id}: {e}")
                time.sleep(2)
                
        return None

    def estimate_batch(self, problems: List[Problem], batch_size: int = 20, force: bool = False) -> List[DifficultyResult]:
        """
        Estimates a batch of problems to manage API load.
        """
        results = []
        for problem in problems[:batch_size]:
            # Skip if already rated and not forcing
            if not force and problem.difficulty and problem.rating is not None:
                continue
                
            print(f"Estimating {problem.problem_id}")
            result = self.estimate(problem)
            
            if result:
                print(f"[OK] {result.difficulty} ({result.estimated_rating})")
                
                problem.difficulty = result.difficulty
                problem.rating = result.estimated_rating
                
                self.db.update_problem(problem)
                results.append(result)
            else:
                print(f"[FAILED] Failed to estimate {problem.problem_id}")
                
        return results

    def estimate_all(self, force: bool = False):
        """
        Estimates difficulty for all unrated problems in the database.
        """
        all_problems = self.db.get_all_problems()
        print(f"Loaded {len(all_problems)} problems")
        
        if not force:
            unrated = [p for p in all_problems if not p.difficulty or p.rating is None]
            rated_count = len(all_problems) - len(unrated)
            print(f"Skipping {rated_count} already rated")
        else:
            unrated = all_problems
            
        success_count = 0
        total_rating = 0
        
        for problem in unrated:
            print(f"Estimating {problem.problem_id}")
            result = self.estimate(problem)
            
            if result:
                print(f"[OK] {result.difficulty} ({result.estimated_rating})")
                
                # Database update
                problem.difficulty = result.difficulty
                problem.rating = result.estimated_rating
                self.db.update_problem(problem)
                
                success_count += 1
                total_rating += result.estimated_rating
            else:
                print(f"[FAILED] Failed to estimate {problem.problem_id}")
                
        print("Completed")
        print(f"{success_count} problems updated")
        
        if success_count > 0:
            avg_rating = total_rating // success_count
            print(f"Average estimated rating: {avg_rating}")

if __name__ == "__main__":
    estimator = DifficultyEstimator()
    estimator.estimate_all()
