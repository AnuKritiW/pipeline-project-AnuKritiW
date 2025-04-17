import sys
from PIL import Image
from inky.inky_uc8159 import Inky  # explicitly use the Impression display

inky = Inky()
# TODO: add parameter on web app
saturation = 0.5  # default

# Load image
# image_path = "/home/pi/pipeline-project-AnuKritiW/assets/comicref-1.jpg"
image_path = "/home/pi/pipeline-project-AnuKritiW/assets/grogu-ref.jpg"
image = Image.open(image_path)

# Resize to display resolution
# TODO: add paramter on web app
image = image.resize(inky.resolution)

# Let Inky handle the conversion + display
inky.set_image(image, saturation=saturation)
inky.show()
