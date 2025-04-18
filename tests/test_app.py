import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from app import app
from web_app.app import app

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"System Stats", response.data)

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

