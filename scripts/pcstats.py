"""
pcstats.py

Collects system statistics (CPU, RAM, and Disk usage) using the `psutil` library
and writes them as a JSON object to a file. This file is typically consumed by
the PiPipeline's display modules, such as the system stats E-Ink display.

Intended to be run periodically (e.g., via cron or systemd timer).
"""

import psutil
import json
import time

def get_pc_stats():
    """
    Collect system resource usage statistics.

    Returns:
        dict: A dictionary containing human-readable usage percentages for:
            - "CPU Usage"
            - "RAM Usage"
            - "Disk Usage"
    """
    return {
        "CPU Usage": f"{psutil.cpu_percent()}%",
        "RAM Usage": f"{psutil.virtual_memory().percent}%",
        "Disk Usage": f"{psutil.disk_usage('/').percent}%"
    }

stats = get_pc_stats()
print(json.dumps(stats))  # Print the stats as JSON
