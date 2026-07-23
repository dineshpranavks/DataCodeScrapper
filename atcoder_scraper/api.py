from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
import os

from database.mongodb import db
from config import XML_DIR
from scraper.utils import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="AtCoder Data Collector API",
    description="REST API to retrieve scraped contests and problems from AtCoder.",
    version="1.0.0"
)

def serialize_doc(doc):
    """Helper to convert MongoDB ObjectId to string for JSON serialization."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

@app.get("/contests")
def get_contests(skip: int = 0, limit: int = 20):
    """Retrieve a list of contests with pagination."""
    contests = list(db.contests.find().skip(skip).limit(limit))
    return [serialize_doc(c) for c in contests]

@app.get("/contests/{contest_id}")
def get_contest(contest_id: str):
    """Retrieve a specific contest by its ID."""
    contest = db.contests.find_one({"contest_id": contest_id})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    return serialize_doc(contest)

@app.get("/problems")
def get_problems(skip: int = 0, limit: int = 20, contest_id: Optional[str] = None):
    """Retrieve a list of problems, optionally filtering by contest_id."""
    query = {}
    if contest_id:
        query["contest_id"] = contest_id
        
    problems = list(db.problems.find(query).skip(skip).limit(limit))
    return [serialize_doc(p) for p in problems]

@app.get("/problems/{problem_id}")
def get_problem(problem_id: str):
    """Retrieve a specific problem by its ID."""
    problem = db.problems.find_one({"problem_id": problem_id})
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return serialize_doc(problem)

@app.get("/search")
def search(keyword: str = Query(..., min_length=1)):
    """Search for contests or problems by keyword in their names/titles."""
    # Simple regex search (case-insensitive)
    regex_query = {"$regex": keyword, "$options": "i"}
    
    matched_contests = list(db.contests.find({"contest_name": regex_query}).limit(20))
    matched_problems = list(db.problems.find({"title": regex_query}).limit(20))
    
    return {
        "contests": [serialize_doc(c) for c in matched_contests],
        "problems": [serialize_doc(p) for p in matched_problems]
    }

@app.get("/difficulty/{level}")
def get_by_difficulty(level: str, skip: int = 0, limit: int = 20):
    """Retrieve problems by difficulty level."""
    # AtCoder doesn't always have simple 'level' like LeetCode, but we support the endpoint.
    problems = list(db.problems.find({"difficulty": level}).skip(skip).limit(limit))
    return [serialize_doc(p) for p in problems]

@app.get("/export/xml")
def export_xml(type: str = Query(..., description="Either 'contests' or 'problems'")):
    """Download the exported XML files."""
    filename = f"{type}.xml"
    file_path = os.path.join(XML_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"XML export for {type} not found. Ensure the scraper has run.")
        
    return FileResponse(path=file_path, filename=filename, media_type='application/xml')

# To run the API, use: uvicorn api:app --reload
