import sqlite3
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect("database/job_screening.db")
cursor = conn.cursor()

# Fetch shortlisted candidates
cursor.execute("""
    SELECT candidate_id FROM shortlisted_candidates
""")
shortlisted = cursor.fetchall()

# Set start date for scheduling
start_date = datetime.today() + timedelta(days=1)

# Clear old interview schedule (optional, for dev/testing)
cursor.execute("DELETE FROM interview_schedule")

# Schedule interviews
for idx, (candidate_id,) in enumerate(shortlisted):
    scheduled_date = start_date + timedelta(days=idx)
    date_str = scheduled_date.strftime("%Y-%m-%d %H:%M")

    # Generate email message
    email_message = f"""
    Dear Candidate,

    Congratulations! You have been shortlisted for the next round of interviews.
    Your interview is scheduled on {date_str}.

    Please be available and check your email for the meeting link.

    Regards,
    HR Team
    """

    # Insert into interview_schedule table
    cursor.execute("""
        INSERT INTO interview_schedule (candidate_id, scheduled_date, email_message, status)
        VALUES (?, ?, ?, ?)
    """, (candidate_id, date_str, email_message.strip(), "Scheduled"))

conn.commit()
conn.close()

print(" Interviews scheduled successfully for all shortlisted candidates.")
