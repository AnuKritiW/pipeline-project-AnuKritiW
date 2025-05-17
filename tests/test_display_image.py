import pytest

try:
    import scripts.display_image as display_image_module
except ImportError:
    pytest.skip("Skipping test: module not available in CI", allow_module_level=True)

import os
import sys
from unittest.mock import patch, MagicMock

# Ensure project root is on the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.mark.pi_only
@patch("scripts.display_image.Image.open")  # Avoid opening real image files
@patch("scripts.display_image.Inky")        # mock Inky display
def test_display_image(mock_inky_class, mock_image_open, mock_inky_display):
    # mock image object
    fake_image = MagicMock()
    mock_image_open.return_value = fake_image
    fake_image.resize.return_value = fake_image

    # shared mock display
    mock_inky_class.return_value = mock_inky_display

    # run function with dummy values
    display_image_module.display_image("dummy/path/image.jpg", saturation=0.75)

    # Assertions
    mock_image_open.assert_called_once_with("dummy/path/image.jpg")
    fake_image.resize.assert_called_once_with((mock_inky_display.WIDTH, mock_inky_display.HEIGHT))
    mock_inky_display.set_image.assert_called_once_with(fake_image, saturation=0.75)
    mock_inky_display.show.assert_called_once()

