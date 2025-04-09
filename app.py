from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import subprocess
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a random secret key

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database/job_screening.db')  # Replace with your actual database path
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/')
def index():
    conn = get_db_connection()
    
    # Get counts for dashboard
    job_count = conn.execute('SELECT COUNT(*) FROM job_descriptions').fetchone()[0]
    resume_count = conn.execute('SELECT COUNT(*) FROM candidates').fetchone()[0]
    shortlisted_count = conn.execute('SELECT COUNT(*) FROM shortlisted_candidates').fetchone()[0]
    interview_count = conn.execute('SELECT COUNT(*) FROM interview_schedule').fetchone()[0]
    
    # Get recent job descriptions
    recent_jobs = conn.execute('SELECT * FROM job_descriptions ORDER BY id DESC LIMIT 5').fetchall()
    
    # Get upcoming interviews
    upcoming_interviews = conn.execute('''
    SELECT 
        i.*, 
        c.name AS candidate_name
    FROM interview_schedule i
    JOIN candidates c ON i.candidate_id = c.id
    WHERE date(i.scheduled_date) >= date('now')
    ORDER BY date(i.scheduled_date)
    LIMIT 5
''').fetchall()

    
    conn.close()
    
    return render_template('index.html', 
                          job_count=job_count,
                          resume_count=resume_count,
                          shortlisted_count=shortlisted_count,
                          interview_count=interview_count,
                          recent_jobs=recent_jobs,
                          upcoming_interviews=upcoming_interviews)

@app.route('/jobs')
def jobs():
    conn = get_db_connection()
    jobs = conn.execute('SELECT * FROM job_descriptions ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('jobs.html', jobs=jobs)

@app.route('/candidates')
def candidates():
    conn = get_db_connection()
    candidates = conn.execute('SELECT * FROM candidates ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('candidates.html', candidates=candidates)

@app.route('/matching')
def matching():
    conn = get_db_connection()
    scores = conn.execute('''
        SELECT s.*, j.title as job_title, c.name as candidate_name 
        FROM candidate_scores s
        JOIN job_descriptions j ON s.job_id = j.id
        JOIN candidates c ON s.candidate_id = c.id
        ORDER BY s.job_id, s.score DESC
    ''').fetchall()
    conn.close()
    return render_template('matching.html', scores=scores)

@app.route('/shortlisted')
def shortlisted():
    conn = get_db_connection()
    shortlisted = conn.execute('''
        SELECT s.*, j.title as job_title, c.name as candidate_name 
        FROM shortlisted_candidates s
        JOIN job_descriptions j ON s.job_id = j.id
        JOIN candidates c ON s.candidate_id = c.id
        ORDER BY s.job_id
    ''').fetchall()
    conn.close()
    return render_template('shortlisted.html', shortlisted=shortlisted)

@app.route('/interviews')
def interviews():
    conn = get_db_connection()
    interviews = conn.execute('''
    SELECT 
        i.*, 
        c.name AS candidate_name
    FROM interview_schedule i
    JOIN candidates c ON i.candidate_id = c.id
    ORDER BY date(i.scheduled_date)
''').fetchall()
    print(interviews[0])
    conn.close()
    return render_template('interviews.html', interviews=interviews)

@app.route('/run-agent/<agent_name>', methods=['POST'])
def run_agent(agent_name):
    # Map agent names to script paths
    agent_scripts = {
        'job_processor': 'agents/agent1_jd_parser.py',
        'resume_parser': 'agents/agent2_resume_parser.py',
        'candidate_matcher': 'agents/agent3_matcher.py',
        'shortlister': 'agents/agent4_shortlister.py',
        'interview_scheduler': 'agents/agent5_scheduler.py'
    }
    
    if agent_name in agent_scripts:
        try:
            # Run the agent script
            result = subprocess.run(['python', agent_scripts[agent_name]], capture_output=True, text=True)
            
            if result.returncode == 0:
                flash(f"Successfully ran {agent_name}", "success")
            else:
                flash(f"Error running {agent_name}: {result.stderr}", "error")
        except Exception as e:
            flash(f"Error running {agent_name}: {str(e)}", "error")
    else:
        flash(f"Unknown agent: {agent_name}", "error")
    
    return redirect(request.referrer or url_for('index'))

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    file = request.files['resume']
    if file and file.filename.endswith('.pdf'):
        upload_path = os.path.join('data/resumes', file.filename)
        file.save(upload_path)

        # After saving, run all agents (or only needed ones)
        agent_scripts = [
            'agents/agent2_resume_parser.py',
            'agents/agent3_matcher.py',
            'agents/agent4_shortlister.py',
            'agents/agent5_scheduler.py'
        ]

        errors = []
        for script in agent_scripts:
            try:
                result = subprocess.run(['python', script], capture_output=True, text=True)
                if result.returncode != 0:
                    errors.append(f"Error in {os.path.basename(script)}: {result.stderr}")
            except Exception as e:
                errors.append(f"Error in {os.path.basename(script)}: {str(e)}")

        if errors:
            for error in errors:
                flash(error, "error")
            flash("Resume uploaded, but some steps failed.", "error")
        else:
            flash("Resume uploaded and processed successfully!", "success")
    else:
        flash("Please upload a valid PDF file.", "error")

    return redirect(url_for('candidates'))


@app.route('/run-all-agents', methods=['POST'])
def run_all_agents():
    # List of all agent scripts in order
    agent_scripts = [
        'agents/agent1_jd_parser.py',
        'agents/agent2_resume_parser.py',
        'agents/agent3_matcher.py',
        'agents/agent4_shortlister.py',
        'agents/agent5_scheduler.py'
    ]
    
    errors = []
    
    for script in agent_scripts:
        try:
            result = subprocess.run(['python', script], capture_output=True, text=True)
            if result.returncode != 0:
                errors.append(f"Error in {os.path.basename(script)}: {result.stderr}")
        except Exception as e:
            errors.append(f"Error in {os.path.basename(script)}: {str(e)}")
    
    if errors:
        for error in errors:
            flash(error, "error")
        flash("Some agents failed to run", "error")
    else:
        flash("All agents ran successfully", "success")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)