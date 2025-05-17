import pytest

try:
    import scripts.display_renderfarm_monitor as monitor
except ImportError:
    pytest.skip("Skipping test: module not available in CI", allow_module_level=True)

from unittest.mock import patch, mock_open, MagicMock

@pytest.mark.pi_only
# run one cycle of logic in display_render_farm
# load the job and filter data; update the 'display', exit cleanly
# note that this does not interact with the actual hardware or files
@patch("scripts.display_renderfarm_monitor.time.sleep")  # Avoid real delay
@patch("scripts.display_renderfarm_monitor.ImageDraw")   # Avoid real image drawing logic
@patch("scripts.display_renderfarm_monitor.Image")       # Avoid real image creation
@patch("scripts.display_renderfarm_monitor.auto")        # mock inky screen
@patch("builtins.open", new_callable=mock_open)          # mock file reads
def test_display_render_once(mock_file, mock_auto, mock_image, mock_draw, mock_sleep, mock_job_data, mock_inky_display):
    job_data, filter_data = mock_job_data

    # mock file reads
    # first time open() is called, return the first item and so on. 
    mock_file.side_effect = [
        mock_open(read_data=job_data).return_value,     # return job_data
        mock_open(read_data=filter_data).return_value   # return filter_data
    ]

    mock_auto.return_value = mock_inky_display

    monitor.display_render_farm(run_once=True)

    # assertions to confirm that display was called
    mock_inky_display.set_image.assert_called_once()
    mock_inky_display.show.assert_called_once()
