#!/usr/bin/env python3

CURRENT_IMAGE_FILE = "/home/pi/pipeline-project-AnuKritiW/web_app/current_image.txt"

with open(CURRENT_IMAGE_FILE, 'w') as f:
    f.write('')

print("current_image.txt cleared.")

