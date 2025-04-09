# main.py

import subprocess
import os

# Define paths to each agent
agents = [
    "agents/agent1_jd_parser.py",
    "agents/agent2_resume_parser.py",
    "agents/agent3_matcher.py",
    "agents/agent4_shortlister.py",
    "agents/agent5_scheduler.py"
]

def run_agent(agent_path):
    print(f"🚀 Running {os.path.basename(agent_path)} ...")
    result = subprocess.run(["python", agent_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {os.path.basename(agent_path)} executed successfully.\n")
        print(result.stdout)
    else:
        print(f"❌ Error running {os.path.basename(agent_path)}:\n{result.stderr}")

if __name__ == "__main__":
    print("🧠 Starting AI-based Job Screening System...\n")
    for agent in agents:
        run_agent(agent)
    print("🎯 All agents completed.")
