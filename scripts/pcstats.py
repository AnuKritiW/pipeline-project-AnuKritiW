import psutil
import json
import time

def get_pc_stats():
    return {
        "CPU Usage": f"{psutil.cpu_percent()}%",
        "RAM Usage": f"{psutil.virtual_memory().percent}%",
        "Disk Usage": f"{psutil.disk_usage('/').percent}%"
    }

stats = get_pc_stats()
print(json.dumps(stats))  # Print the stats as JSON
