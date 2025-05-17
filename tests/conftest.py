import sys
import os
import pytest
import json
from unittest.mock import MagicMock

# Make sure scripts and web_app are importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def mock_job_data():
    job_data = json.dumps([
        {
            "job_id": 1001,
            "user": "anu",
            "project": "cosmic-journey",
            "shot": "sh045",
            "frames": "200–215",
            "status": "rendering",
            "tool": "RenderMan",
            "progress": 45
        }
    ])
    filter_data = json.dumps({"user": "", "project": "", "status": "", "tool": ""})
    return job_data, filter_data

@pytest.fixture
def mock_inky_display():
    display = MagicMock()
    display.WHITE = 1
    display.RED = 2
    display.GREEN = 3
    display.YELLOW = 4
    display.BLACK = 5
    display.ORANGE = 6
    display.BLUE = 7
    display.WIDTH = 250
    display.HEIGHT = 122
    return display

