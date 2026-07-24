CONTESTS_TABLE = """
CREATE TABLE IF NOT EXISTS contests (
    contest_id TEXT PRIMARY KEY,
    contest_name TEXT NOT NULL,
    contest_url TEXT NOT NULL,
    created_at TIMESTAMP
);
"""

PROBLEMS_TABLE = """
CREATE TABLE IF NOT EXISTS problems (
    problem_id TEXT PRIMARY KEY,
    contest_id TEXT NOT NULL,
    problem_url TEXT NOT NULL,
    title TEXT,
    statement TEXT,
    constraints TEXT,
    input_format TEXT,
    output_format TEXT,
    sample_inputs TEXT,
    sample_outputs TEXT,
    time_limit TEXT,
    memory_limit TEXT,
    topic TEXT,
    subtopic TEXT,
    difficulty TEXT,
    rating INTEGER,
    created_at TIMESTAMP,
    FOREIGN KEY(contest_id) REFERENCES contests(contest_id)
);
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_contest_id ON problems (contest_id);",
    "CREATE INDEX IF NOT EXISTS idx_difficulty ON problems (difficulty);",
    "CREATE INDEX IF NOT EXISTS idx_topic ON problems (topic);"
]
