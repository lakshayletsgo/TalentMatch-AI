# agents/agent1_jd_parser.py

import pandas as pd
import sqlite3

# Load job descriptions from CSV
df = pd.read_csv("data/job_description.csv", encoding='cp1252')



# --- Placeholder JD parser function (you'll upgrade this later using LLM/NLP) ---
def parse_jd(description):
    summary = description[:200]  # First 200 characters
    skills = "Python, SQL, ML" if "data" in description.lower() else "JavaScript, Node.js"
    experience = "2+ years" if "experience" in description.lower() else "0+ years"
    qualifications = "Bachelor's Degree"
    return summary, skills, experience, qualifications

# Connect to the database
conn = sqlite3.connect("database/job_screening.db")
cursor = conn.cursor()

# Insert parsed JD into DB
for _, row in df.iterrows():
    title = row['Job Title']
    jd = row['Job Description']
    
    summary, skills, exp, qual = parse_jd(jd)

    cursor.execute("""
        INSERT INTO job_descriptions (title, summary, required_skills, min_experience, qualifications)
        VALUES (?, ?, ?, ?, ?)
    """, (title, summary, skills, exp, qual))

conn.commit()
conn.close()

print("All job descriptions inserted into the database.")
