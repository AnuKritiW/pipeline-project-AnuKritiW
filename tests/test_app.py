import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Ensure web_app is on sys.path

import pytest
from unittest.mock import patch, mock_open
import io
from web_app.app import app, stop_current_profile, PROFILES
import subprocess
import json

"""Fixtures for the test suite"""
@pytest.fixture
def client():
    # create a mock HTTP client to make fake GET/POST requests
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_opens():
    # temporarily replace/mock subprocess.Popen
    # temporarily replace/mock open
    with patch('web_app.app.subprocess.Popen') as mock_popen, \
         patch('builtins.open', new_callable=mock_open) as mock_open_file:
        yield mock_open_file, mock_popen

@pytest.fixture
def mock_uploads():
    with patch('web_app.app.os.makedirs'), \
         patch('web_app.app.os.path.exists', return_value=True), \
         patch('builtins.open', new_callable=mock_open) as mock_open_file:
        yield mock_open_file

"""General Routes"""
# Test home route
def test_home_page(client):
    response = client.get("/")          # GET request to the home page
    assert response.status_code == 200  # Check response status code is 200 (OK)
    assert b"PiPeline" in response.data # Check page contains text "PiPeline"

# Test invalid profile route
def test_invalid_profile(client):
    response = client.get("/profile/invalidkey")
    assert response.status_code == 404

"""Stats Routes"""
# Tests GET for /profile/stats
def test_profile_stats_get(client):
    response = client.get("/profile/stats")
    assert response.status_code == 200
    assert b"System Stats" in response.data

# test POST /profile/stats with "run" action
def test_profile_run_post(mock_opens, client):
    mock_open_file, mock_popen = mock_opens
    response = client.post("/profile/stats", data={"action": "run"}) # simulate submitting a POST request -- clicking 'Run'
    assert response.status_code == 302                               # Should redirect
    mock_popen.assert_called_once()
    assert mock_open_file.called

# test POST /profile/stats with "stop" action
# "Stop" button correctly calls pkill and clears the profile
def test_profile_stop_post(mock_opens, client):
    mock_open_file, mock_popen = mock_opens
    response = client.post("/profile/stats", data={"action": "stop"})
    assert response.status_code == 302  # Should redirect
    mock_popen.assert_called_once()
    assert mock_open_file.called

"""Image Routes"""
# Test GET /profile/image
def test_image_page_get(client):
    response = client.get("/profile/image")
    assert response.status_code == 200
    assert b"Image Display" in response.data

# test POST /profile/image to upload an image
def test_image_upload_valid(mock_uploads, client):
    with patch('web_app.app.os.listdir', return_value=["test.jpg"]):
        data = {
            "action": "upload",
            "image": (io.BytesIO(b"fake image data"), "test.jpg")
        }
        response = client.post("/profile/image", data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert b"Uploaded" in response.data

# test POST /profile/image to upload an invalid file
def test_image_upload_invalid_filetype(mock_uploads, client):
    with patch('web_app.app.os.listdir', return_value=["test.txt"]):
        data = {
            "action": "upload",
            "image": (io.BytesIO(b"fake file data"), "test.txt")
        }
        response = client.post("/profile/image", data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert b"Invalid file type" in response.data

# test POST /profile/image to display an image
@patch('builtins.open', new_callable=mock_open)
@patch('web_app.app.subprocess.run')
def test_image_display(mock_run, mock_open_file, mock_uploads, client):
    with patch('web_app.app.os.listdir', return_value=["test.jpg"]):
        data = {
            "action": "display",
            "selected_image": "test.jpg"
        }
        response = client.post("/profile/image", data=data)
        assert response.status_code == 200
        assert b"Now displaying" in response.data
        mock_run.assert_called_once()
        assert mock_open_file.call_count == 3

# test deleting an image
@patch('builtins.open', new_callable=mock_open)
@patch('web_app.app.os.remove')
def test_image_delete(mock_remove, mock_open_file, mock_uploads, client):
    with patch('web_app.app.os.listdir', return_value=["test.jpg"]):
        data = {
            "action": "delete",
            "delete_image": "test.jpg"
        }
        response = client.post("/profile/image", data=data)
        assert response.status_code == 200
        assert b"Deleted" in response.data
        mock_remove.assert_called_once()
        assert mock_open_file.call_count == 2

# test except CalledProcessError block if subprocess.run fails
@patch('builtins.open', new_callable=mock_open)
@patch('web_app.app.subprocess.run', side_effect=subprocess.CalledProcessError(1, ['fake']))
def test_display_image_subprocess_failure(mock_run, mock_open_file, mock_uploads, client):
    with patch('web_app.app.os.listdir', return_value=["test.jpg"]):
        data = {"action": "display", "selected_image": "test.jpg"}
        response = client.post("/profile/image", data=data)
        assert response.status_code == 200
        assert b"Failed to display image" in response.data

# Tests missing file during upload
def test_upload_missing_file(mock_uploads, client):
    # No file included
    response = client.post("/profile/image", data={"action": "upload"}, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"Invalid file type" in response.data  # Should trigger the invalid type branch

# TODO: Test repeat file upload

"""Global Stop"""
# test app correctly kills the script when users want to stop everything
@patch("web_app.app.subprocess.Popen")
@patch("builtins.open", new_callable=mock_open, read_data="renderfarm")
@patch("web_app.app.os.path.exists", return_value=True)
def test_stop_current_profile(mock_exists, mock_open_file, mock_popen):
    stopped_profile = stop_current_profile()

    # Should return the stopped profile name
    assert stopped_profile == "renderfarm"

    # Should call pkill for the main script
    monitor_script = PROFILES["renderfarm"]["script"]
    mock_popen.assert_any_call(["pkill", "-f", monitor_script])

    # Should also call pkill for the simulate script
    mock_popen.assert_any_call(["pkill", "-f", "simulate_render_jobs.py"])

    # Should clear the profile file
    assert mock_open_file.call_count >= 2  # read + write

# to run `pytest tests/``
