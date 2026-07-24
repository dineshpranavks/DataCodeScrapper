import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

DB_PATH = Path("database/atcoder.db")

def get_connection() -> sqlite3.Connection:
    """Returns a read-only database connection."""
    if not DB_PATH.exists():
        logging.warning(f"Database not found at {DB_PATH}")
    # Using uri=True and mode=ro for read-only connection
    conn = sqlite3.connect(f"file:{DB_PATH.resolve()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn

def get_statistics() -> Dict[str, Any]:
    """Fetch high-level statistics for the dashboard."""
    stats = {
        "total_contests": 0,
        "total_problems": 0,
        "classified_problems": 0,
        "topics_count": 0,
        "average_rating": 0,
        "problems_per_topic": [],
        "problems_per_difficulty": [],
        "highest_rated_problem": None,
        "lowest_rated_problem": None,
    }
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM contests")
            row = cursor.fetchone()
            if row: stats["total_contests"] = row["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM problems")
            row = cursor.fetchone()
            if row: stats["total_problems"] = row["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM problems WHERE topic IS NOT NULL")
            row = cursor.fetchone()
            if row: stats["classified_problems"] = row["count"]
            
            cursor.execute("SELECT COUNT(DISTINCT topic) as count FROM problems WHERE topic IS NOT NULL")
            row = cursor.fetchone()
            if row: stats["topics_count"] = row["count"]
            
            cursor.execute("SELECT AVG(rating) as avg_rating FROM problems WHERE rating IS NOT NULL")
            row = cursor.fetchone()
            if row and row["avg_rating"] is not None:
                stats["average_rating"] = round(row["avg_rating"], 2)
            
            # Additional stats for charts
            cursor.execute("SELECT topic, COUNT(*) as count FROM problems WHERE topic IS NOT NULL GROUP BY topic ORDER BY count DESC")
            stats["problems_per_topic"] = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT difficulty, COUNT(*) as count FROM problems WHERE difficulty IS NOT NULL GROUP BY difficulty")
            stats["problems_per_difficulty"] = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT title, rating, problem_id FROM problems WHERE rating IS NOT NULL ORDER BY rating DESC LIMIT 1")
            highest = cursor.fetchone()
            stats["highest_rated_problem"] = dict(highest) if highest else None
            
            cursor.execute("SELECT title, rating, problem_id FROM problems WHERE rating IS NOT NULL ORDER BY rating ASC LIMIT 1")
            lowest = cursor.fetchone()
            stats["lowest_rated_problem"] = dict(lowest) if lowest else None
            
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    return stats

def get_problems(limit: int = 25, offset: int = 0, search: str = "", topic: str = "", difficulty: str = "", contest_id: str = "", sort_by: str = "problem_id", sort_order: str = "ASC") -> Dict[str, Any]:
    """Fetch problems with filtering, pagination, and sorting."""
    problems = []
    total_count = 0
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            query = "FROM problems WHERE 1=1"
            params = []
            
            if search:
                query += " AND (problem_id LIKE ? OR contest_id LIKE ? OR title LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
                
            if topic:
                query += " AND topic = ?"
                params.append(topic)
                
            if difficulty:
                query += " AND difficulty = ?"
                params.append(difficulty)
                
            if contest_id:
                query += " AND contest_id = ?"
                params.append(contest_id)
                
            # Get total count
            cursor.execute(f"SELECT COUNT(*) as count {query}", params)
            row = cursor.fetchone()
            if row: total_count = row["count"]
            
            # Safe sorting
            valid_sort_columns = ["problem_id", "contest_id", "title", "difficulty", "rating"]
            if sort_by not in valid_sort_columns:
                sort_by = "problem_id"
            if sort_order.upper() not in ["ASC", "DESC"]:
                sort_order = "ASC"
                
            query = f"SELECT problem_id, contest_id, title, topic, subtopic, difficulty, rating {query} ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            problems = [dict(row) for row in cursor.fetchall()]
            
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        
    return {"data": problems, "total": total_count}

def get_problem(problem_id: str) -> Optional[Dict[str, Any]]:
    """Fetch details of a single problem."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM problems WHERE problem_id = ?", (problem_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    return None

def get_distinct_values(column: str) -> List[str]:
    """Fetch distinct values for a given column (e.g. topic, difficulty)."""
    valid_columns = ["topic", "difficulty", "contest_id"]
    if column not in valid_columns:
        return []
        
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT DISTINCT {column} FROM problems WHERE {column} IS NOT NULL ORDER BY {column}")
            return [row[column] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    return []
