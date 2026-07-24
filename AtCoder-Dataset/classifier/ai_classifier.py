import os
import json
import time
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv
import openai
from openai import OpenAI, OpenAIError

# Ensure parent directory is in sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from models import Problem
from database.database import Database
from classifier.prompt_builder import build_prompt
from classifier.taxonomy import TOPICS, DIFFICULTY_LEVELS

# Load environment variables
load_dotenv()

@dataclass
class Classification:
    topic: str
    subtopic: str
    difficulty: str
    estimated_rating: int
    algorithm: str
    confidence: int

class AIClassifier:
    """
    AI Classification Engine for AtCoder Problems.
    """
    
    def __init__(self, model: str = None):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        )
        self.model = model or os.getenv("NVIDIA_MODEL", "meta/llama3-70b-instruct")
        self.db = Database()

    def validate_response(self, response_text: str) -> Optional[Classification]:
        """
        Validates the JSON response and returns a Classification object.
        """
        try:
            # Strip markdown if model incorrectly adds it
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            data = json.loads(clean_text)
            
            # Validate Topic
            if data.get("topic") not in TOPICS:
                return None
                
            # Validate Difficulty
            if data.get("difficulty") not in DIFFICULTY_LEVELS:
                return None
                
            # Validate Rating & Confidence
            rating = int(data.get("estimated_rating", 0))
            confidence = int(data.get("confidence", 0))
            if not (0 <= confidence <= 100):
                return None
                
            return Classification(
                topic=data["topic"],
                subtopic=data.get("subtopic", ""),
                difficulty=data["difficulty"],
                estimated_rating=rating,
                algorithm=data.get("algorithm", ""),
                confidence=confidence
            )
        except (json.JSONDecodeError, ValueError, KeyError):
            return None

    def classify(self, problem: Problem) -> Optional[Classification]:
        """
        Classifies a single problem using the OpenAI API.
        """
        prompt = build_prompt(problem.title, problem.statement, problem.constraints)
        
        for attempt in range(2):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a competitive programming assistant that strictly outputs JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                
                response_text = response.choices[0].message.content
                classification = self.validate_response(response_text)
                
                if classification:
                    return classification
                    
                print(f"Validation failed for {problem.problem_id}, retrying...")
            except OpenAIError as e:
                print(f"API Error on {problem.problem_id}: {e}")
                time.sleep(2)
        
        return None

    def classify_batch(self, problems: List[Problem], batch_size: int = 10) -> List[Classification]:
        """
        Process a batch of problems to reduce API overhead tracking.
        """
        results = []
        for problem in problems[:batch_size]:
            print(f"Classifying {problem.problem_id}")
            classification = self.classify(problem)
            if classification:
                results.append(classification)
                print(f"[OK] {classification.topic}")
                
                # Store even if confidence < 60, mark for review logic could be handled downstream
                problem.topic = classification.topic
                problem.subtopic = classification.subtopic
                problem.difficulty = classification.difficulty
                problem.rating = classification.estimated_rating
                
                self.db.update_problem(problem)
            else:
                print(f"[FAILED] Failed to classify {problem.problem_id}")
        return results

    def classify_all(self):
        """
        Classifies all unclassified problems in the database.
        """
        all_problems = self.db.get_all_problems()
        print(f"Loaded {len(all_problems)} problems")
        
        unclassified = [p for p in all_problems if not p.topic]
        classified_count = len(all_problems) - len(unclassified)
        
        print(f"Skipping {classified_count} classified")
        
        total_confidence = 0
        success_count = 0
        
        for problem in unclassified:
            print(f"Classifying {problem.problem_id}")
            classification = self.classify(problem)
            
            if classification:
                print(f"[OK] {classification.topic}")
                
                problem.topic = classification.topic
                problem.subtopic = classification.subtopic
                problem.difficulty = classification.difficulty
                problem.rating = classification.estimated_rating
                
                self.db.update_problem(problem)
                
                total_confidence += classification.confidence
                success_count += 1
            else:
                print(f"[FAILED] Failed to classify {problem.problem_id}")
                
        print("Completed")
        print(f"{success_count} problems classified")
        
        if success_count > 0:
            avg_confidence = total_confidence / success_count
            print(f"Average Confidence : {avg_confidence:.1f}%")

if __name__ == "__main__":
    classifier = AIClassifier()
    classifier.classify_all()
