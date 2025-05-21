#!/bin/bash

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate the virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

while true; do
    echo "[INFO] Running pcstats.py..."
    STATS=$(python3 "$SCRIPT_DIR/pcstats.py")

    if [[ -z "$STATS" ]]; then
        echo "[ERROR] No stats received!"
    else
        echo "Captured stats: $STATS"
        echo "$STATS" | ssh pi@pi.local "mkdir -p ~/pipeline-project-AnuKritiW/out &&
                            cat > ~/pipeline-project-AnuKritiW/out/pcstats.json"
    fi

    sleep 120
done
