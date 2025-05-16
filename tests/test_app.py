import os
import sys
import io
import json
import builtins
import subprocess

# Ensure web_app is on sys.path for imports to work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, mock_open
from web_app.app import app, clear_session_files, stop_current_profile, PROFILES


# Fixtures
@pytest.fixture
def client():
    # create a mock HTTP client to make fake GET/POST requests
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_open_and_popen():
    # temporarily replace/mock subprocess.Popen
    # temporarily replace/mock open
    with patch('web_app.app.subprocess.Popen') as mock_popen, \
         patch('builtins.open', new_callable=mock_open) as mock_open_file:
        yield mock_open_file, mock_popen

"""General Routes"""
class TestGeneralRoutes:
    # Test home route
    def test_home_page(self, client):
        response = client.get("/")          # GET request to the home page
        assert response.status_code == 200  # Check response status code is 200 (OK)
        assert b"PiPeline" in response.data # Check page contains text "PiPeline"

    # Test invalid profile route
    def test_invalid_profile(self, client):
        response = client.get("/profile/invalidkey")
        assert response.status_code == 404

    def test_index_post_stop_global(self, client):
        with patch("web_app.app.os.path.exists", return_value=True), \
            patch("web_app.app.open", mock_open(read_data="stats")), \
            patch("web_app.app.subprocess.Popen"):
            response = client.post("/", data={"stop_global": "1"})
            assert response.status_code == 302

"""Stats Routes"""
class TestStatsRoutes:
    # Tests GET for /profile/stats
    def test_profile_stats_get(self, client):
        response = client.get("/profile/stats")
        assert response.status_code == 200
        assert b"System Stats" in response.data

    # test POST /profile/stats with "run" action
    def test_profile_run_post(self, mock_open_and_popen, client):
        mock_open_file, mock_popen = mock_open_and_popen
        response = client.post("/profile/stats", data={"action": "run"}) # simulate submitting a POST request -- clicking 'Run'
        assert response.status_code == 302                               # Should redirect
        mock_popen.assert_called_once()
        assert mock_open_file.called

    # test POST /profile/stats with "stop" action
    # "Stop" button correctly calls pkill and clears the profile
    def test_profile_stop_post(self, mock_open_and_popen, client):
        mock_open_file, mock_popen = mock_open_and_popen
        response = client.post("/profile/stats", data={"action": "stop"})
        assert response.status_code == 302  # Should redirect
        mock_popen.assert_called_once()
        assert mock_open_file.called

"""Image Routes"""
# Fixtures
@pytest.fixture
def mock_uploads():
    with patch('web_app.app.os.makedirs'), \
         patch('web_app.app.os.path.exists', return_value=True), \
         patch('builtins.open', new_callable=mock_open) as mock_open_file:
        yield mock_open_file

class TestImageRoutes:
    # Test GET /profile/image
    def test_image_page_get(self, client):
        response = client.get("/profile/image")
        assert response.status_code == 200
        assert b"Image Display" in response.data

    @pytest.mark.parametrize("filename, content, expected_text", [
        ("test.jpg", b"fake image data", b"Uploaded"),          # test POST /profile/image to upload an image
        ("test.txt", b"fake file data", b"Invalid file type"),  # test POST /profile/image to upload an invalid file
    ])
    def test_image_upload_variants(mock_uploads, client, filename, content, expected_text):
        with patch('web_app.app.os.listdir', return_value=[filename]):
            data = {"action": "upload", "image": (io.BytesIO(content), filename)}
            response = client.post("/profile/image", data=data, content_type='multipart/form-data')
            assert expected_text in response.data

    # test POST /profile/image to display an image
    @patch('builtins.open', new_callable=mock_open)
    @patch('web_app.app.subprocess.run')
    def test_image_display(self, mock_run, mock_open_file, mock_uploads, client):
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
    def test_image_delete(self, mock_remove, mock_open_file, mock_uploads, client):
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

    # test error on deleting an image
    @patch("web_app.app.os.remove", side_effect=Exception("disk full"))
    def test_image_delete_failure(mock_remove, mock_uploads, client):
        with patch("web_app.app.os.listdir", return_value=["test.jpg"]):
            data = {"action": "delete", "delete_image": "test.jpg"}
            response = client.post("/profile/image", data=data)
            assert b"Error deleting" in response.data

    # test except CalledProcessError block if subprocess.run fails
    @patch('builtins.open', new_callable=mock_open)
    @patch('web_app.app.subprocess.run', side_effect=subprocess.CalledProcessError(1, ['fake']))
    def test_display_image_subprocess_failure(self, mock_run, mock_open_file, mock_uploads, client):
        with patch('web_app.app.os.listdir', return_value=["test.jpg"]):
            data = {"action": "display", "selected_image": "test.jpg"}
            response = client.post("/profile/image", data=data)
            assert response.status_code == 200
            assert b"Failed to display image" in response.data

    @pytest.mark.parametrize("filename, content, expected_text", [
        ("test.jpg", b"fake image data", b"Uploaded"),
        ("test.txt", b"fake file data", b"Invalid file type"),
        ("test.gif", b"not allowed", b"Invalid file type"),
        (None, None, b"Invalid file type"),  # No file uploaded at all
    ])
    def test_image_upload_variants(mock_uploads, client, filename, content, expected_text):
        with patch("web_app.app.os.listdir", return_value=[]):
            if filename is not None:
                data = {"action": "upload", "image": (io.BytesIO(content), filename)}
            else:
                data = {"action": "upload"}  # No file key

            response = client.post("/profile/image", data=data, content_type='multipart/form-data')
            assert expected_text in response.data

    def test_repeat_file_upload(self, mock_uploads, client):
        with patch("web_app.app.os.listdir", return_value=["test.jpg"]), \
            patch("web_app.app.os.path.exists", return_value=True):
            data = {
                "action": "upload",
                "image": (io.BytesIO(b"duplicate data"), "test.jpg")
            }
            response = client.post("/profile/image", data=data, content_type="multipart/form-data")
            assert response.status_code == 200
            assert b"already exists" in response.data

    def test_unknown_post_action_image(self, mock_uploads, client):
        data = {"action": "foobar"}
        response = client.post("/profile/image", data=data)
        assert response.status_code == 200
        assert b"Invalid file type" not in response.data
        assert b"Now displaying" not in response.data
        assert b"Deleted" not in response.data

"""Renderfarm Routes"""
#Fixtures

# Save the original open() function
real_open = builtins.open

# Custom open handler
@pytest.fixture
def renderfarm_mocked_open():
    def _mocked_open(filepath, *args, **kwargs):
        if filepath.endswith("selected_profile.txt"):
            return mock_open(read_data="renderfarm")()

        elif filepath.endswith("renderfarm_status.json"):
            return io.StringIO("""[
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
            ]""")

        elif filepath.endswith("renderfarm_filter.json"):
            return io.StringIO("""{
                "user": "",
                "project": "",
                "tool": "",
                "status": ""
            }""")

        # Allow Flask to load templates normally
        return real_open(filepath, *args, **kwargs)

    return _mocked_open

@pytest.fixture
def patch_renderfarm_context(renderfarm_mocked_open):
    # Start both patches
    open_patch = patch("builtins.open", new=renderfarm_mocked_open)
    exists_patch = patch("web_app.app.os.path.exists", return_value=True)

    open_mock = open_patch.start()
    exists_mock = exists_patch.start()

    yield open_mock, exists_mock  # yield in case you want to assert on them later

    # Stop both patches
    open_patch.stop()
    exists_patch.stop()

@pytest.fixture
def mock_popen():
    with patch("web_app.app.subprocess.Popen") as mock:
        yield mock

class TestRenderfarmRoutes:
    # Test GET /profile/renderfarm
    def test_renderfarm_page_get(self, client, patch_renderfarm_context):
        response = client.get("/profile/renderfarm")
        assert response.status_code == 200
        assert b"Render Farm Monitor" in response.data

    # test POST /profile/renderfarm with "run" action
    def test_renderfarm_run(self, mock_popen, client, patch_renderfarm_context):
        response = client.post("/profile/renderfarm", data={"action": "run"})
        assert response.status_code == 302  # Redirect
        assert mock_popen.call_count == 1   # simulate + monitor scripts

    # Tests POST /profile/renderfarm stop
    def test_renderfarm_stop(self, mock_popen, client, patch_renderfarm_context):
        response = client.post("/profile/renderfarm", data={"action": "stop"})
        assert response.status_code == 302
        assert mock_popen.call_count == 2
        mock_popen.assert_any_call(["pkill", "-f", "display_renderfarm_monitor.py"])
        mock_popen.assert_any_call(["pkill", "-f", "simulate_render_jobs.py"])

    # Tests POST /profile/renderfarm update filter
    @pytest.mark.parametrize("filter_data", [
        {"filter_user": "anu", "filter_project": "cosmic-journey", "filter_status": "rendering", "filter_tool": "RenderMan"},
        {"filter_user": "", "filter_project": "deep-sea", "filter_status": "waiting", "filter_tool": "Redshift"},
        {"filter_user": "marie", "filter_project": "", "filter_status": "", "filter_tool": ""},
        {"filter_user": "", "filter_project": "", "filter_status": "", "filter_tool": ""},
    ])
    @patch('web_app.app.json.dump')
    def test_renderfarm_update_filter(self, mock_json_dump, mock_popen, client, patch_renderfarm_context, filter_data):
        data = {"action": "update_filter", **filter_data}
        response = client.post("/profile/renderfarm", data=data)
        assert response.status_code == 302
        assert mock_json_dump.called

    # test fallback json handling
    @patch("web_app.app.open", new_callable=mock_open, read_data="{ invalid json }")
    @patch("web_app.app.os.path.exists", return_value=True)
    @patch("web_app.app.subprocess.Popen")
    def test_renderfarm_corrupted_filter_file(self, mock_popen, mock_exists, mock_open_file, client):
        response = client.get("/profile/renderfarm")
        assert response.status_code == 200

"""Global Stop"""
# test app correctly kills the script when users want to stop everything
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

def test_stop_current_profile_file_missing():
    with patch("web_app.app.os.path.exists", return_value=False), \
         patch("web_app.app.subprocess.Popen") as mock_popen:
        stopped_profile = stop_current_profile()
        assert stopped_profile is None
        mock_popen.assert_not_called()

@patch("web_app.app.open", new_callable=mock_open)
@patch("web_app.app.os.path.join", side_effect=lambda *args: "/mocked/path/renderfarm_filter.json")
def test_clear_session_files_success(mock_join, mock_open_file):
    clear_session_files()

    # Should attempt to open three files total
    assert mock_open_file.call_count == 3

    opened_files = [call[0][0] for call in mock_open_file.call_args_list]
    assert "selected_profile.txt" in opened_files[0]
    assert "current_image.txt" in opened_files[1]
    assert "renderfarm_filter.json" in opened_files[2]

@patch("web_app.app.open", side_effect=Exception("disk error"))
def test_clear_session_files_error(mock_open_file):

    # Should not crash, just print errors
    clear_session_files()

# to run `pytest tests/``
