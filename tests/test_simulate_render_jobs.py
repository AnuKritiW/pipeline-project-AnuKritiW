import os
import sys
import builtins
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, mock_open, MagicMock

import scripts.simulate_render_jobs as sim

# TODO: consider moving fixture to external file
@pytest.fixture
def mock_job_data():
    job_data = json.dumps([
        {
            "job_id": 1001,
            "user": "anu",
            "project": "cosmic-journey",
            "shot": "sh045",
            "frames": "200–215",
            "status": "waiting",
            "tool": "RenderMan",
            "progress": 0
        }
    ])
    return job_data

# run one simulation cycle
# mocks file IO and random to ensure predictable behavior
@patch("scripts.simulate_render_jobs.time.sleep")       # avoid real sleep
@patch("scripts.simulate_render_jobs.random.random")    # mock random.random
@patch("scripts.simulate_render_jobs.random.randint")   # mock random.randint
@patch("builtins.open", new_callable=mock_open)         # mock file read/write
@patch("scripts.simulate_render_jobs.os.path.exists", return_value=True)  # simulate that file exists
def test_simulate_render_once(mock_exists, mock_file, mock_randint, mock_random, mock_sleep, mock_job_data):
    # return low values from random.random to ensure status changes occur
    mock_random.side_effect = [0.1] * 10
    mock_randint.return_value = 10

    # simulate reading from the job file
    mock_file.return_value.__enter__.return_value.read.return_value = mock_job_data

    sim.simulate_render_jobs(run_once=True)

    assert mock_file.call_count >= 2 # read and write

    # confirm that updated jobs were written
    handle = mock_file()
    handle.write.assert_called()

