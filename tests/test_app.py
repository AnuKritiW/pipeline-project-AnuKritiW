import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Ensure web_app is on sys.path

import unittest
from web_app.app import app

class FlaskAppTestCase(unittest.TestCase):

    # Set up the test client
    # automatically run before every test method
    def setUp(self):
        # create a mock HTTP client to make fake GET/POST requests
        self.client = app.test_client()
        self.client.testing = True

    def test_home_page(self):
        response = self.client.get("/")             # GET request to the home page
        self.assertEqual(response.status_code, 200) # Check response status code is 200 (OK)
        self.assertIn(b"PiPeline", response.data)   # Check page contains text "PiPeline"

    def test_invalid_profile(self):
        response = self.client.get("/profile/invalidkey")
        self.assertEqual(response.status_code, 404)

    def test_profile_stats_get(self):
        response = self.client.get("/profile/stats")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"System Stats", response.data)

    def test_image_page_get(self):
        response = self.client.get("/profile/image")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Image Display", response.data)

if __name__ == "__main__":
    unittest.main()
