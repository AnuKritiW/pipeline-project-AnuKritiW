import sys
from PIL import Image
from inky.inky_uc8159 import Inky  # explicitly use the Impression display

inky = Inky()
# TODO: add parameter on web app
saturation = 0.5  # default

# Get image path from command line
if len(sys.argv) < 2:
    print("Usage: python display-image.py <image-path>")
    sys.exit(1)

image_path = sys.argv[1]

# Load image
image = Image.open(image_path)

# Resize to display resolution
# TODO: add paramter on web app
image = image.resize(inky.resolution)

# Let Inky handle the conversion + display
inky.set_image(image, saturation=saturation)
inky.show()
