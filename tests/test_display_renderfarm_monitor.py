import os
import sys
import builtins
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, mock_open, MagicMock

import scripts.display_renderfarm_monitor as monitor

# TODO: consider moving fixture into external file to share with test_app.py?
@pytest.fixture
def mock_render_data():
    # Sample job JSON and filters
    job_data = json.dumps([
        {
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

# run one cycle of logic in display_render_farm
# load the job and filter data; update the 'display', exit cleanly
# note that this does not interact with the actual hardware or files
@patch("scripts.display_renderfarm_monitor.time.sleep")  # Avoid real delay
@patch("scripts.display_renderfarm_monitor.ImageDraw")   # Avoid real image drawing logic
@patch("scripts.display_renderfarm_monitor.Image")       # Avoid real image creation
@patch("scripts.display_renderfarm_monitor.auto")        # mock inky screen
@patch("builtins.open", new_callable=mock_open)          # mock file reads
def test_display_render_once(mock_file, mock_auto, mock_image, mock_draw, mock_sleep, mock_render_data):
    job_data, filter_data = mock_render_data

    # mock file reads
    # first time open() is called, return the first item and so on. 
    mock_file.side_effect = [
        mock_open(read_data=job_data).return_value,     # return job_data
        mock_open(read_data=filter_data).return_value   # return filter_data
    ]

    # mock inky display object
    fake_display = MagicMock()
    fake_display.WHITE = 1
    fake_display.RED = 2
    fake_display.GREEN = 3
    fake_display.YELLOW = 4
    fake_display.BLACK = 5
    fake_display.ORANGE = 6
    fake_display.BLUE = 7
    fake_display.WIDTH = 250
    fake_display.HEIGHT = 122
    mock_auto.return_value = fake_display

    monitor.display_render_farm(run_once=True)

    # assertions to confirm that display was called
    fake_display.set_image.assert_called_once()
    fake_display.show.assert_called_once()
