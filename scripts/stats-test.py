from PIL import Image, ImageDraw, ImageFont
# import psutil
import json
import time

# Try to import Inky library (only works on Raspberry Pi)
try:
    from inky.auto import auto
    inky_display = auto()  # auto library, creates an instance of the class called inky_display
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

def get_pc_stats():
    try:
        with open("/home/pi/pipeline-project-AnuKritiW/out/pcstats.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"CPU Usage": "N/A", "RAM Usage": "N/A", "Disk Usage": "N/A"}

def draw_bar(draw, x, y, percent, width=100, height=10, fill=color, bg=0):
    """Draws a horizontal bar with the given percentage (0–100)"""
    print(percent)
    draw.rectangle([x, y, x + width, y + height], outline=bg, fill=bg)
    filled = int((percent / 100) * width)
    draw.rectangle([x, y, x + filled, y + height], fill=fill)

while True:
    # Fetch system stats
    stats = get_pc_stats()
    print(stats)

    # Draw system stats
    y_offset = 10
    for key, value in stats.items():
        try:
            percent = float(value.strip('%').strip())
        except:
            percent = 0

        # Draw the label
        # draw.text((10, y_offset), f"{key}: {value}", fill=color, font=font)
        draw.text((10, y_offset), f"{key}:", fill=color, font=font)
        y_offset += 12  # space after label

        # Draw the loading bar
        bar_fill = inky_display.RED if inky_display else (255, 0, 0)
        bar_bg = inky_display.WHITE if inky_display else "white"
        draw_bar(draw, x=10, y=y_offset, percent=percent, width=120, height=10, fill=bar_fill, bg=bar_bg)

        draw.text((140, y_offset - 2), f"{value}", fill=color, font=font)
        y_offset += 20  # space after bar

    if inky_display:
        # Only update E-Ink if the hardware is available
        inky_display.set_image(img)
        inky_display.show()
    else:
        # Save the image as a file for preview
        img.save("eink_stats_output.png")
        print("Saved simulated output to eink_stats_output.png")

    time.sleep(120)  # wait for a minute before updating again

