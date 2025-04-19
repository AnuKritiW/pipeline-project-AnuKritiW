from PIL import Image, ImageDraw, ImageFont
import datetime
import json
import time

# Try to import Inky library (only works on Raspberry Pi)
try:
    from inky.auto import auto
    inky_display = auto()  # auto library, creates an instance of the class called inky_display
except ImportError:
    print("[WARNING] Inky display not found. Running in simulation mode.")
    inky_display = None

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)

cpu_color   = (180, 255, 60)     # Lime green
ram_color   = (255, 165, 0)      # Orange
disk_color  = (0, 255, 255)      # Cyan
time_color  = (120, 255, 120)    # Light green
bar_bg      = (30, 30, 30)       # Dark grey background for bars
bg_color    = (0, 0, 0)          # Black canvas background

def get_pc_stats():
    try:
        with open("/home/pi/pipeline-project-AnuKritiW/out/pcstats.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"CPU Usage": "N/A", "RAM Usage": "N/A", "Disk Usage": "N/A"}

def draw_bar(draw, x, y, percent, width=100, height=10, fill=(255,0,0), bg=bg_color):
    """Draws a horizontal bar with the given percentage (0–100)"""
    print(percent)
    draw.rectangle([x, y, x + width, y + height], outline=bg, fill=bg)
    filled = int((percent / 100) * width)
    draw.rectangle([x, y, x + filled, y + height], fill=fill)

while True:
    if inky_display:
        img = Image.new("RGB", inky_display.resolution)  # Use palette mode e ink display
        color = inky_display.RED
        width, height = inky_display.width, inky_display.height
    else:
        img = Image.new("RGB", (600, 448), bg_color) # Use full color mode in simulation
        color = (255, 0, 0)
        width, height = (600, 448)

    # Fetch system stats
    stats = get_pc_stats()
    print(stats)

    draw = ImageDraw.Draw(img)

    # Order of stats and their assigned colors
    stat_keys = ["CPU Usage", "RAM Usage", "Disk Usage"]
    stat_colors = [cpu_color, ram_color, disk_color]

    # Draw system stats
    y_offset = 10

    for i, key in enumerate(stat_keys):
        value = stats.get(key, "N/A")
        try:
            percent = float(value.strip('%').strip())
        except:
            percent = 0

        stat_color = stat_colors[i]

        # Draw the label
        # draw.text((10, y_offset), f"{key}: {value}", fill=color, font=font)
        draw.text((10, y_offset), f"{key}:", fill=stat_color, font=font)
        y_offset += 18  # space after label

        # Draw the loading bar
        # bar_fill = inky_display.RED if inky_display else (255, 0, 0)
        # bar_bg = inky_display.WHITE if inky_display else "white"
        draw_bar(draw, x=10, y=y_offset, percent=percent, width=120, height=10, fill=stat_color, bg=bar_bg)

        draw.text((140, y_offset - 2), f"{value}", fill=stat_color, font=font)
        y_offset += 30  # space after bar

    now = datetime.datetime.now().strftime("%H:%M:%S")
    draw.text((10, y_offset), f"Updated: {now}", fill=time_color, font=font)

    if inky_display:
        # Only update E-Ink if the hardware is available
        inky_display.set_image(img)
        inky_display.show()
    else:
        # Save the image as a file for preview
        img.save("eink_stats_output.png")
        print("Saved simulated output to eink_stats_output.png")

    time.sleep(120)  # wait for a minute before updating again

