import sqlite3

# Path to your database file
db_path = "database/job_screening.db"

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List of tables to clear
tables_to_clear = [
    "job_descriptions",
    "candidates",
    "candidate_scores",
    "shortlisted_candidates",
    "interview_schedule",
    "match_scores"
]

# Delete all records and reset AUTOINCREMENT counters
for table in tables_to_clear:
    cursor.execute(f"DELETE FROM {table}")
    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")  # Resets ID counter

# Commit and close
conn.commit()
conn.close()

print(" All tables cleared and ID counters reset.")
