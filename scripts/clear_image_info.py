#!/usr/bin/env python3

import os

# Dynamically resolve path relative to the script location
def clear_current_image_file(path=None):
    if path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(script_dir, "..", "web_app")
        path = os.path.join(project_root, "current_image.txt")

    with open(path, 'w') as f:
        f.write('')

    print("current_image.txt cleared.")

if __name__ == "__main__":
    clear_current_image_file()
