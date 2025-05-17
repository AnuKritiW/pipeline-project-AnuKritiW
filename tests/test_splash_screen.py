import pytest

try:
    import scripts.splash_screen as splash
except ImportError:
    pytest.skip("Skipping test: module not available in CI", allow_module_level=True)

from unittest.mock import patch, mock_open, MagicMock

@pytest.mark.pi_only
# run the splash screen logic once with all dependencies mocked
# ensures text is drawn and image is displayed without triggering hardware or subprocess
@patch("scripts.splash_screen.subprocess.run")           # avoid running clear_image_info.py
@patch("scripts.splash_screen.ImageDraw")                # avoid real image drawing logic
@patch("scripts.splash_screen.Image")                    # avoid real image creation
@patch("scripts.splash_screen.auto")                     # mock inky screen
def test_show_pipeline_splash(mock_auto, mock_image, mock_draw, mock_run, mock_inky_display):
    # mock inky display object
    mock_auto.return_value = mock_inky_display

    # mock dimensions returned by draw.textsize
    mock_draw.Draw.return_value.textsize.return_value = (100, 30)

    splash.show_pipeline_splash()

    # assert the image was shown
    mock_inky_display.set_image.assert_called_once()
    mock_inky_display.show.assert_called_once()

    # assert the subprocess was called to clear image info
    mock_run.assert_called_once()

