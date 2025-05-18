#!/usr/bin/env python3

"""
clear_image_info.py

Clears the contents of current_image.txt, which stores the name of the image currently displayed
in the image profile of the PiPipeline web app. This script can be run independently or imported
as a utility function.
"""

import os

# Dynamically resolve path relative to the script location
def clear_current_image_file(path=None):
    """
    Clear the contents of current_image.txt.

    If a path is not provided, the function will resolve the path to current_image.txt
    relative to the script location, assuming the default project directory layout.

    Args:
        path (str, optional): Full path to the file to clear. Defaults to None.
    """
    if path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(script_dir, "..", "web_app")
        path = os.path.join(project_root, "current_image.txt")

    with open(path, 'w') as f:
        f.write('')

    print("current_image.txt cleared.")

if __name__ == "__main__":
    clear_current_image_file()
