import pytest

try:
    import scripts.display_stats as stats
except ImportError:
    pytest.skip("Skipping test: module not available in CI", allow_module_level=True)

from unittest.mock import patch, mock_open, MagicMock

@pytest.mark.pi_only
@patch("scripts.display_stats.subprocess.run")  # avoid clearing script
@patch("scripts.display_stats.ImageDraw")       # avoid real image drawing logic
@patch("scripts.display_stats.Image")           # avoid real image creation
@patch("scripts.display_stats.get_pc_stats")    # mock system stats
def test_display_stats_once(mock_get_stats, mock_image, mock_draw, mock_run, mock_inky_display):
    # dummy system stats
    mock_get_stats.return_value = {
        "CPU Usage": "50%",
        "RAM Usage": "75%",
        "Disk Usage": "90%"
    }

    # Assign mock image size and resolution
    fake_img = MagicMock()
    mock_image.new.return_value = fake_img
    mock_draw.Draw.return_value.text.return_value = None

    stats.inky_display = mock_inky_display

    stats.display_stats(run_once=True)

    stats.inky_display.set_image.assert_called_once()
    stats.inky_display.show.assert_called_once()
    mock_run.assert_called_once()

