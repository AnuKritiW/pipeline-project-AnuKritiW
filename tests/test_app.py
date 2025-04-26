import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Ensure web_app is on sys.path

import pytest
from web_app.app import app

@pytest.fixture
def client():
    # create a mock HTTP client to make fake GET/POST requests
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get("/")          # GET request to the home page
    assert response.status_code == 200  # Check response status code is 200 (OK)
    assert b"PiPeline" in response.data # Check page contains text "PiPeline"

def test_invalid_profile(client):
    response = client.get("/profile/invalidkey")
    assert response.status_code == 404

def test_profile_stats_get(client):
    response = client.get("/profile/stats")
    assert response.status_code == 200
    assert b"System Stats" in response.data

def test_image_page_get(client):
    response = client.get("/profile/image")
    assert response.status_code == 200
    assert b"Image Display" in response.data

# to run `pytest tests/`
