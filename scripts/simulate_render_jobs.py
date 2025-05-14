import json
import os
import time
import random

# set paths
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, '..', 'web_app', 'data')
status_file = os.path.join(data_dir, 'renderfarm_status.json')

# dummy data
USERS = ["anu", "marie", "li", "sasha" "james", "alex", "mike", "chris", "kim", "sam", "drew"]
PROJECTS = ["cosmic-journey", "deep-sea", "void-echo", "desert-dust", "forest-whisper", "city-lights"]
TOOLS = ["RenderMan", "Redshift", "Arnold", "Cycles", "V-Ray", "Octane", "Mantra", "Clarisse", "Nuke", "Fusion"]
STATUS = ["waiting", "rendering"]

# Job ID counter with default 1001 starting point
next_id = 1001

def generate_job():
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

while True:
    if not os.path.exists(status_file):
        jobs = []
    else:
        with open(status_file) as f:
            jobs = json.load(f)

    # get the next job ID if there are existing jobs
    if jobs:
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

    time.sleep(90) # update every 30 seconds
