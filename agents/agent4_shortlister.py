import sqlite3

# Connect to the database
conn = sqlite3.connect("database/job_screening.db")
cursor = conn.cursor()

# Create the shortlisted_candidates table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS shortlisted_candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        candidate_id INTEGER,
        score INTEGER
    )
""")

# Clear previous shortlisting data
cursor.execute("DELETE FROM shortlisted_candidates")

# Fetch distinct job IDs from the candidate_scores table
cursor.execute("SELECT DISTINCT job_id FROM candidate_scores")
job_ids = [row[0] for row in cursor.fetchall()]

# Number of top candidates to shortlist per job
TOP_N = 5

# Loop through each job and shortlist top N candidates
for job_id in job_ids:
    cursor.execute("""
        SELECT candidate_id, score
        FROM candidate_scores
        WHERE job_id = ?
        ORDER BY score DESC, candidate_id ASC
        LIMIT ?
    """, (job_id, TOP_N))
    
    top_candidates = cursor.fetchall()

    for candidate_id, score in top_candidates:
        cursor.execute("""
            INSERT INTO shortlisted_candidates (job_id, candidate_id, score)
            VALUES (?, ?, ?)
        """, (job_id, candidate_id, score))

# Commit changes and close connection
conn.commit()
conn.close()

print("Top candidates shortlisted for each job.")
