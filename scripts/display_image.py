import sys
from PIL import Image
from inky.inky_uc8159 import Inky  # explicitly use the Impression display

def display_image(image_path, saturation=0.5):
    inky = Inky()

    # Load image
    image = Image.open(image_path)

    # Resize to display resolution
    # TODO: add paramter on web app
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

