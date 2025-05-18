"""
simulate_render_jobs.py

Simulates a render farm job queue and updates a JSON file with dummy job entries.
This is used for testing the render farm monitoring UI without needing a real backend.

The script creates, updates, and removes jobs based on probabilistic logic to mimic
real-world render queue dynamics. It is designed to be run continuously in the background.
"""

import json
import os
import time
import random

# set paths
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, '..', 'web_app', 'data')
status_file = os.path.join(data_dir, 'renderfarm_status.json')

# dummy data
USERS = ["anu", "marie", "li", "sasha", "james", "alex", "mike", "chris", "kim", "sam", "drew"]
PROJECTS = ["cosmic-journey", "deep-sea", "void-echo", "desert-dust", "forest-whisper", "city-lights"]
TOOLS = ["RenderMan", "Redshift", "Arnold", "Cycles", "V-Ray", "Octane", "Mantra", "Clarisse", "Nuke", "Fusion"]
STATUS = ["waiting", "rendering"]

# Job ID counter with default 1001 starting point
next_id = 1001

def generate_job():
    """
    Generate a new fake render job with randomized attributes.

    Returns:
        dict: A new job entry with fields like user, project, shot, tool,
              frame range, progress (0), and status ('waiting' or 'rendering').
    """
    global next_id
    job = {
        "job_id": next_id,
        "user": random.choice(USERS),
        "project": random.choice(PROJECTS),
        "shot": f"sh{random.randint(1, 999):03}",
        "frames": f"{random.randint(100, 500)}-{random.randint(501, 700)}",
        "status": random.choice(STATUS),
        "tool": random.choice(TOOLS),
        "progress": 0
    }
    next_id += 1
    return job

def simulate_render_jobs(run_once=False):
    """
    Simulate a render farm by managing a list of active jobs and saving to JSON.

    Jobs can:
      - Transition from 'waiting' → 'rendering'
      - Progress from 0 to 100% while rendering
      - Randomly fail
      - Randomly be removed after completion/failure

    A new job is added periodically to maintain activity.

    Args:
        run_once (bool): If True, only run the simulation once; otherwise loop forever.
    """
    while True:
        if not os.path.exists(status_file):
            jobs = []
        else:
            with open(status_file) as f:
                jobs = json.load(f)

        # get the next job ID if there are existing jobs
        if jobs:
            global next_id
            next_id = max(job["job_id"] for job in jobs) + 1

        updated_jobs = []

        # Update existing jobs
        for job in jobs:
            if job["status"] == "waiting" or job["status"] == "rendering":
                if random.random() < 0.05:  # 5% chance to fail
                    job["status"] = "failed"

                if job["status"] == "waiting":
                    # 30% chance to change status to rendering
                    if random.random() < 0.3:
                        job["status"] = "rendering"
                        job["progress"] = random.randint(0, 5)

                if job["status"] == "rendering":
                    # simulate progress
                    job["progress"] += random.randint(1, 9)
                    # cap progress at 100 and update status accordingly
                    if job["progress"] >= 100:
                        job["progress"] = 100
                        job["status"] = "done"
            updated_jobs.append(job)

        # randomly remove some completed/failed jobs
        updated_jobs = [
            job for job in updated_jobs
            if not (
                (job["status"] == "done" and random.random() < 0.1) or
                (job["status"] == "failed" and random.random() < 0.05)
            )
        ]

        # add a new job 30% of the time or if there are less than 2 jobs
        if random.random() < 0.3 or len(updated_jobs) < 2:
            new_job = generate_job()
            print(f"Added job {new_job['job_id']}")
            updated_jobs.append(new_job)

        # Save to file
        with open(status_file, "w") as f:
            json.dump(updated_jobs, f, indent=2)

        print(f"Updated {len(updated_jobs)} jobs at {time.strftime('%H:%M:%S')}")

        if run_once:
            break

        time.sleep(90) # update every 90 seconds

if __name__ == "__main__":
    simulate_render_jobs()
