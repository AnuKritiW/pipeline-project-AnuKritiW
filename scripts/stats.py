from PIL import Image, ImageDraw, ImageFont
import psutil

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

def get_system_stats():
    return {
        "CPU Usage": f"{psutil.cpu_percent()}%",
        "RAM Usage": f"{psutil.virtual_memory().percent}%",
        "Disk Usage": f"{psutil.disk_usage('/').percent}%"
    }

# Fetch system stats
stats = get_system_stats()
print(stats)

# Draw system stats
y_offset = 10
for key, value in stats.items():
    draw.text((10, y_offset), f"{key}: {value}", fill=color, font=font)
    y_offset += 20

if inky_display:
    # Only update E-Ink if the hardware is available
    inky_display.set_image(img)
    inky_display.show()
else:
    # Save the image as a file for preview
    img.save("eink_stats_output.png")
    print("Saved simulated output to eink_stats_output.png")
