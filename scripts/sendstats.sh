#!/bin/bash
while true; do
    python3 ~/pipeline-project-AnuKritiW/scripts/pcstats.py | ssh pi@192.168.181.44 "cat > ~/pipeline-project-AnuKritiW/out/pcstats.json"
    # | (pipe) passes the JSON stats from pcstats.py to the next command
    sleep 120  # Update every two minutes
done
