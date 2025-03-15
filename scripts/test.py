from PIL import Image, ImageFont, ImageDraw

# https://learn.pimoroni.com/article/getting-started-with-inky-phat#building-your-own-code

# Try to import Inky library (only works on Raspberry Pi)
try:
    from inky.auto import auto
    inky_display = auto() # auto library, creates an instance of the class called inky_display
except ImportError:
    print("[WARNING] Inky display not found. Running in simulation mode.")
    inky_display = None

if inky_display:
    img = Image.new("P", inky_display.resolution)  # Use palette mode e ink display
    color = inky_display.RED
    width, height = inky_display.width, inky_display.height
else:
    img = Image.new("RGB", (600, 448), "white") # Use full color mode in simulation
    color = (255, 0, 0)
    width, height = (600, 448)

draw = ImageDraw.Draw(img)
font = ImageFont.load_default()

message = "Hello, World!"
_, _, w, h = font.getbbox(message)
x = (width / 2) - (w / 2)
y = (height / 2) - (h / 2)

draw.text((x, y), message, color, font)

if inky_display:
    # Only update E-Ink if the hardware is available
    inky_display.set_image(img)
    inky_display.show()
else:
    # Save the image as a file for preview
    img.save("eink_test_output.png")
    print("Saved simulated output to eink_test_output.png")