import os
import sys
import builtins
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, mock_open, MagicMock

import scripts.splash_screen as splash

# run the splash screen logic once with all dependencies mocked
# ensures text is drawn and image is displayed without triggering hardware or subprocess
@patch("scripts.splash_screen.subprocess.run")           # avoid running clear_image_info.py
@patch("scripts.splash_screen.ImageDraw")                # avoid real image drawing logic
@patch("scripts.splash_screen.Image")                    # avoid real image creation
@patch("scripts.splash_screen.auto")                     # mock inky screen
def test_show_pipeline_splash(mock_auto, mock_image, mock_draw, mock_run):
    # mock inky display object
    fake_display = MagicMock()
    fake_display.WHITE = 1
    fake_display.BLACK = 2
    fake_display.WIDTH = 250
    fake_display.HEIGHT = 122
    mock_auto.return_value = fake_display

    # mock dimensions returned by draw.textsize
    mock_draw.Draw.return_value.textsize.return_value = (100, 30)

    splash.show_pipeline_splash()

    # assert the image was shown
    fake_display.set_image.assert_called_once()
    fake_display.show.assert_called_once()

    # assert the subprocess was called to clear image info
    mock_run.assert_called_once()

