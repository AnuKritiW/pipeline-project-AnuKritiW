#!/bin/bash

source ~/Desktop/CAVE/pipeline-project-AnuKritiW/venv/bin/activate
while true; do
    echo "[INFO] Running pcstats.py..."
    STATS=$(python3 ~/Desktop/CAVE/pipeline-project-AnuKritiW/scripts/pcstats.py)
    echo "TEST"

    if [[ -z "$STATS" ]]; then
        echo "[ERROR] No stats received!"
    else
        echo "Captured stats: $STATS"
        echo "$STATS" | ssh pi@pi.local "mkdir -p ~/pipeline-project-AnuKritiW/out &&
                            cat > ~/pipeline-project-AnuKritiW/out/pcstats.json"
    fi

    sleep 120
done
