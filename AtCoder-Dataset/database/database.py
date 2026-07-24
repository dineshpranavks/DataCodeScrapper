import sqlite3
import json
from pathlib import Path
from datetime import datetime
from .schema import CONTESTS_TABLE, PROBLEMS_TABLE, INDEXES
from models import Contest, Problem

class Database:
    def __init__(self, db_path="database/atcoder.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.create_tables()

    def create_tables(self):
        try:
            with self.conn:
                self.conn.execute(CONTESTS_TABLE)
                self.conn.execute(PROBLEMS_TABLE)
                for index in INDEXES:
                    self.conn.execute(index)
            print("Database created")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def insert_contest(self, contest: Contest):
        query = """
        INSERT INTO contests (contest_id, contest_name, contest_url, created_at)
        VALUES (?, ?, ?, ?)
        """
        try:
            with self.conn:
                self.conn.execute(query, (
                    contest.contest_id,
                    contest.name,
                    contest.url,
                    contest.created_at or datetime.now().isoformat()
                ))
            print(f"Inserted Contest {contest.contest_id}")
        except sqlite3.IntegrityError:
            print("Duplicate Contest skipped")
        except sqlite3.Error as e:
            print(f"Error inserting contest: {e}")
            raise

    def insert_problem(self, problem: Problem):
        query = """
        INSERT INTO problems (
            problem_id, contest_id, problem_url, title, statement,
            constraints, input_format, output_format, sample_inputs, sample_outputs,
            time_limit, memory_limit, topic, subtopic, difficulty, rating, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self.conn:
                self.conn.execute(query, (
                    problem.problem_id,
                    problem.contest_id,
                    problem.problem_url,
                    problem.title,
                    problem.statement,
                    problem.constraints,
                    problem.input_format,
                    problem.output_format,
                    json.dumps(problem.sample_inputs) if problem.sample_inputs else "[]",
                    json.dumps(problem.sample_outputs) if problem.sample_outputs else "[]",
                    problem.time_limit,
                    problem.memory_limit,
                    problem.topic,
                    problem.subtopic,
                    problem.difficulty,
                    problem.rating,
                    problem.created_at or datetime.now().isoformat()
                ))
            print(f"Inserted Problem {problem.problem_id}")
        except sqlite3.IntegrityError:
            print("Duplicate Problem skipped")
        except sqlite3.Error as e:
            print(f"Error inserting problem: {e}")
            raise

    def update_problem(self, problem: Problem):
        query = """
        UPDATE problems SET
            contest_id = ?, problem_url = ?, title = ?, statement = ?,
            constraints = ?, input_format = ?, output_format = ?, sample_inputs = ?, sample_outputs = ?,
            time_limit = ?, memory_limit = ?, topic = ?, subtopic = ?, difficulty = ?, rating = ?, created_at = ?
        WHERE problem_id = ?
        """
        try:
            with self.conn:
                cursor = self.conn.execute(query, (
                    problem.contest_id,
                    problem.problem_url,
                    problem.title,
                    problem.statement,
                    problem.constraints,
                    problem.input_format,
                    problem.output_format,
                    json.dumps(problem.sample_inputs) if problem.sample_inputs else "[]",
                    json.dumps(problem.sample_outputs) if problem.sample_outputs else "[]",
                    problem.time_limit,
                    problem.memory_limit,
                    problem.topic,
                    problem.subtopic,
                    problem.difficulty,
                    problem.rating,
                    problem.created_at,
                    problem.problem_id
                ))
                if cursor.rowcount > 0:
                    print(f"Updated Problem {problem.problem_id}")
                else:
                    print(f"Problem {problem.problem_id} not found for update")
        except sqlite3.Error as e:
            print(f"Error updating problem: {e}")
            raise

    def contest_exists(self, contest_id: str) -> bool:
        query = "SELECT 1 FROM contests WHERE contest_id = ?"
        cursor = self.conn.execute(query, (contest_id,))
        return cursor.fetchone() is not None

    def problem_exists(self, problem_id: str) -> bool:
        query = "SELECT 1 FROM problems WHERE problem_id = ?"
        cursor = self.conn.execute(query, (problem_id,))
        return cursor.fetchone() is not None

    def _row_to_problem(self, row) -> Problem:
        return Problem(
            problem_id=row[0],
            contest_id=row[1],
            problem_url=row[2],
            title=row[3],
            statement=row[4],
            constraints=row[5],
            input_format=row[6],
            output_format=row[7],
            sample_inputs=json.loads(row[8]) if row[8] else [],
            sample_outputs=json.loads(row[9]) if row[9] else [],
            time_limit=row[10],
            memory_limit=row[11],
            topic=row[12],
            subtopic=row[13],
            difficulty=row[14],
            rating=row[15],
            created_at=row[16]
        )

    def _row_to_contest(self, row) -> Contest:
        return Contest(
            contest_id=row[0],
            name=row[1],
            url=row[2],
            created_at=row[3]
        )

    def get_problem(self, problem_id: str) -> Problem:
        query = "SELECT * FROM problems WHERE problem_id = ?"
        cursor = self.conn.execute(query, (problem_id,))
        row = cursor.fetchone()
        if row:
            return self._row_to_problem(row)
        return None

    def get_all_problems(self) -> list[Problem]:
        query = "SELECT * FROM problems"
        cursor = self.conn.execute(query)
        return [self._row_to_problem(row) for row in cursor.fetchall()]

    def get_all_contests(self) -> list[Contest]:
        query = "SELECT * FROM contests"
        cursor = self.conn.execute(query)
        return [self._row_to_contest(row) for row in cursor.fetchall()]

    def delete_problem(self, problem_id: str):
        query = "DELETE FROM problems WHERE problem_id = ?"
        try:
            with self.conn:
                cursor = self.conn.execute(query, (problem_id,))
                if cursor.rowcount > 0:
                    print(f"Deleted Problem {problem_id}")
        except sqlite3.Error as e:
            print(f"Error deleting problem: {e}")
            raise

    def delete_contest(self, contest_id: str):
        query = "DELETE FROM contests WHERE contest_id = ?"
        try:
            with self.conn:
                cursor = self.conn.execute(query, (contest_id,))
                if cursor.rowcount > 0:
                    print(f"Deleted Contest {contest_id}")
        except sqlite3.Error as e:
            print(f"Error deleting contest: {e}")
            raise

    def count_contests(self) -> int:
        query = "SELECT COUNT(*) FROM contests"
        cursor = self.conn.execute(query)
        res = cursor.fetchone()
        return res[0] if res else 0

    def count_problems(self) -> int:
        query = "SELECT COUNT(*) FROM problems"
        cursor = self.conn.execute(query)
        res = cursor.fetchone()
        return res[0] if res else 0

    def search_by_topic(self, topic: str) -> list[Problem]:
        query = "SELECT * FROM problems WHERE topic = ?"
        cursor = self.conn.execute(query, (topic,))
        return [self._row_to_problem(row) for row in cursor.fetchall()]

    def search_by_difficulty(self, level: str) -> list[Problem]:
        query = "SELECT * FROM problems WHERE difficulty = ?"
        cursor = self.conn.execute(query, (level,))
        return [self._row_to_problem(row) for row in cursor.fetchall()]

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = Database()
    print(db.count_contests())
    print(db.count_problems())
    db.close()
