import os
import re
import fitz  # PyMuPDF
import sqlite3
import datetime

def extract_text_from_pdf(path):
    text = ""
    doc = fitz.open(path)
    for page in doc:
        text += page.get_text()
    return text

def extract_candidate_info(text):
    # Extract name and email
    name_match = re.search(r"Name[:\-]?\s*(.*)", text, re.IGNORECASE)
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)

    # Education detection
    edu_keywords = ["B.Tech", "M.Tech", "Bachelor", "Master", "B.Sc", "BCA", "MCA", "Ph.D", "Diploma"]
    education = ", ".join([word for word in edu_keywords if word.lower() in text.lower()])

    # Skills detection
    skills_match = re.findall(r"(Python|Java|SQL|ML|AI|C\+\+|HTML|CSS|React|Kafka|AWS|Azure|Spring Boot)", text, re.IGNORECASE)
    skills = ", ".join(set(s.lower() for s in skills_match)) if skills_match else "Not listed"

    # Experience from year ranges like 2018–2022
    year_ranges = re.findall(r"(\d{4})\s*[-–]\s*(\d{4})", text)
    total_exp = 0
    for start, end in year_ranges:
        try:
            start_year = int(start)
            end_year = int(end)
            if end_year >= start_year:
                total_exp += end_year - start_year
        except:
            pass
    experience = f"{total_exp} years" if total_exp > 0 else "0 years"

    # Certifications (optional)
    cert_match = re.findall(r"(Certified[^,\n]*)", text)
    certifications = ", ".join(cert_match).strip() if cert_match else "NA"

    return {
        "name": name_match.group(1).strip() if name_match else "Unknown",
        "email": email_match.group(0) if email_match else "Not found",
        "education": education if education else "Not listed",
        "skills": skills,
        "experience": experience,
        "certifications": certifications
    }

# Connect to database
conn = sqlite3.connect("database/job_screening.db")
cursor = conn.cursor()

# Resume folder
resume_folder = "data/resumes"
for filename in os.listdir(resume_folder):
    if filename.endswith(".pdf"):
        path = os.path.join(resume_folder, filename)
        raw_text = extract_text_from_pdf(path)
        info = extract_candidate_info(raw_text)

        cursor.execute("""
            INSERT INTO candidates (name, email, education, experience, skills, certifications)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            info['name'], info['email'], info['education'], info['experience'],
            info['skills'], info['certifications']
        ))

conn.commit()
conn.close()

