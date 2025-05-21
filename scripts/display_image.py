"""
display_image.py

Displays an image on the Inky Impression e-ink display.

The script takes an image file path as input, resizes it to match the
resolution of the Inky display, and renders it using the appropriate
driver with configurable saturation.

Usage:
    python display_image.py <image-path>
"""

import sys
from PIL import Image
from inky.inky_uc8159 import Inky  # explicitly use the Impression display

def display_image(image_path, saturation=0.5):
    """
    Display an image on the Inky Impression display.

    The image is resized to the native resolution of the display and
    rendered with the specified color saturation.

    Args:
        image_path (str): Path to the image file to display.
        saturation (float): Saturation level for the display (default: 0.5).
    """
    inky = Inky()

    # Load image
    image = Image.open(image_path)

    # Resize to display resolution
    image = image.resize((inky.WIDTH, inky.HEIGHT))

    # Let Inky handle the conversion + display
    inky.set_image(image, saturation=saturation)
    inky.show()

if __name__ == "__main__":
    # Get image path from command line
    if len(sys.argv) < 2:
        print("Usage: python display-image.py <image-path>")
        sys.exit(1)

    image_path = sys.argv[1]
    display_image(image_path)

