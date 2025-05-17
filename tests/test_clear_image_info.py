import os
from unittest.mock import patch, mock_open
from scripts.clear_image_info import clear_current_image_file

def test_clear_image_info_file_write():
    fake_path = "/mocked/path/current_image.txt"
    with patch("builtins.open", mock_open()) as mock_file:
        clear_current_image_file(path=fake_path)
        mock_file.assert_called_once_with(fake_path, "w")
        mock_file().write.assert_called_once_with('')

