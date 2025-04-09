import sqlite3

# Connect to DB
conn = sqlite3.connect("database/job_screening.db")
cursor = conn.cursor()

# Step 1: Clear old scores
cursor.execute("DELETE FROM candidate_scores")
conn.commit()
print(" Old entries deleted from candidate_scores.")

# Step 2: Fetch job and candidate data
cursor.execute("SELECT id, required_skills, min_experience, qualifications FROM job_descriptions")
jobs = cursor.fetchall()

cursor.execute("SELECT id, skills, experience, education FROM candidates")
candidates = cursor.fetchall()

def extract_years(exp_str):
    # Try to extract numeric value from experience like '2 years' or '0 years'
    try:
        return int(''.join([c for c in exp_str if c.isdigit()]))
    except:
        return 0

def match_score(job, candidate):
    job_skills = [s.strip().lower() for s in job[1].split(',')] if job[1] else []
    candidate_skills = [s.strip().lower() for s in candidate[1].split(',')] if candidate[1] else []

    skill_score = sum([1 for s in job_skills if s in candidate_skills])

    # Experience score
    job_exp = extract_years(job[2]) if job[2] else 0
    cand_exp = extract_years(candidate[2]) if candidate[2] else 0
    exp_score = 1 if cand_exp >= job_exp else 0

    # Qualification score
    qual_score = 1 if job[3] and candidate[3] and job[3].lower() in candidate[3].lower() else 0

    return skill_score + exp_score + qual_score

# Step 3: Score and insert fresh records
count = 0
for job in jobs:
    for candidate in candidates:
        score = match_score(job, candidate)

        cursor.execute("""
            INSERT INTO candidate_scores (job_id, candidate_id, score)
            VALUES (?, ?, ?)
        """, (job[0], candidate[0], score))
        count += 1

conn.commit()
conn.close()

print(f" {count} new candidate scores inserted.")
