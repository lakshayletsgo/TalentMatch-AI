# database/setup_db.py

import sqlite3

# Connect to database (creates it if it doesn't exist)
conn = sqlite3.connect("database/job_screening.db")
cursor = conn.cursor()

# --- Table 1: Job Descriptions ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS job_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    summary TEXT,
    required_skills TEXT,
    min_experience TEXT,
    qualifications TEXT
)
""")

# --- Table 2: Candidates / Resumes ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    education TEXT,
    experience TEXT,
    skills TEXT,
    certifications TEXT
)
""")

# --- Table 3: Match Scores ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS match_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    candidate_id INTEGER,
    score REAL,
    passed_threshold BOOLEAN,
    FOREIGN KEY (job_id) REFERENCES job_descriptions(id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
)
""")

# --- Table 4: Interview Scheduler ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS interview_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER,
    scheduled_date TEXT,
    email_message TEXT,
    status TEXT,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS candidate_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    candidate_id INTEGER,
    score INTEGER,
    FOREIGN KEY(job_id) REFERENCES job_descriptions(id),
    FOREIGN KEY(candidate_id) REFERENCES candidates(id)
)
""")


conn.commit()
conn.close()

print("✅ SQLite database and tables created successfully.")
