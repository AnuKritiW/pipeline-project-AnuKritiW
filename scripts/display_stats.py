from PIL import Image, ImageDraw, ImageFont
import datetime
import json
import time
import os
import subprocess

# Try to import Inky library (only works on Raspberry Pi)
try:
    from inky.auto import auto
    inky_display = auto()  # auto library, creates an instance of the class called inky_display
except Exception as e:
    print(f"[ERROR] Failed to initialize Inky display: {e}", file=sys.stderr)
    sys.exit(1)

if inky_display is None:
    print("[ERROR] Could not find Inky display. Exiting.", file=sys.stderr)
    sys.exit(1)

font_sz_header = 40
font_sz_label = 32
font_sz_value = 32
spacer = 18

font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_sz_header)  # SYSTEM INFO
font_label  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_sz_label)  # "CPU Usage"
font_value  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_sz_value)  # "50.0%"

header_color = (255, 230, 0)     # Yellow
cpu_color    = (51, 153, 255)    # Light blue
ram_color    = (255, 153, 0)     # Orange
disk_color   = (0, 255, 255)     # Cyan
time_color   = (255, 255, 255)   # White
bar_bg       = (255, 255, 255)   # White background for bars
bg_color     = (0, 0, 0)         # Black canvas background

def get_pc_stats():
    try:
        with open("/home/pi/pipeline-project-AnuKritiW/out/pcstats.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"CPU Usage": "N/A", "RAM Usage": "N/A", "Disk Usage": "N/A"}

def draw_bar(draw, x, y, percent, width, height=font_sz_value, fill=(255,0,0), bg=bg_color):
    """Draws a horizontal bar with the given percentage (0–100)"""
    draw.rectangle([x, y, x + width, y + height], outline=bg, fill=bg)
    filled = int((percent / 100) * width)
    draw.rectangle([x, y, x + filled, y + height], fill=fill)

def display_stats(run_once=False):
    while True:
        if inky_display:
            img = Image.new("RGB", (inky_display.WIDTH, inky_display.HEIGHT))  # Use palette mode e ink display
            width, height = inky_display.WIDTH, inky_display.HEIGHT

        # Fetch system stats
        stats = get_pc_stats()

        draw = ImageDraw.Draw(img)

        # draw header
        center_x = width // 2
        y_offset = 30
        draw.text((center_x, y_offset), "SYSTEM INFO", font=font_header, fill=header_color, anchor="mm")
        y_offset += font_sz_header + spacer  # Space after header

        # Order of stats and their assigned colors
        stat_keys = ["CPU Usage", "RAM Usage", "Disk Usage"]
        stat_colors = [cpu_color, ram_color, disk_color]

        # Draw system stats
        for i, key in enumerate(stat_keys):
            value = stats.get(key, "N/A")
            try:
                percent = float(value.strip('%').strip())
            except:
                percent = 0

            stat_color = stat_colors[i]

            # Draw the label
            draw.text((10, y_offset), f"{key}:", fill=stat_color, font=font_label)
            y_offset += font_sz_label + spacer  # space after label

            # Draw the loading bar
            bar_x_offset = 10
            bar_width = width - 200
            draw_bar(draw, x=bar_x_offset, y=y_offset, percent=percent, width=bar_width, height=font_sz_value - 10, fill=stat_color, bg=bar_bg)

            value_x_offset = bar_x_offset + bar_width + 20
            draw.text((value_x_offset, y_offset - 2), f"{value}", fill=stat_color, font=font_value)
            y_offset += font_sz_value + spacer  # space after bar

        now = datetime.datetime.now().strftime("%H:%M:%S")
        draw.text((10, y_offset), f"Updated: {now}", fill=time_color, font=font_label)

        try:
            # Only update E-Ink if the hardware is available
            inky_display.set_image(img)
            inky_display.show()

            script_dir = os.path.dirname(os.path.abspath(__file__))
            clear_script = os.path.join(script_dir, 'clear_image_info.py')
            subprocess.run(['python3', clear_script])
        except Exception as e:
            print(f"[ERROR] Failed to update Inky display: {e}", file=sys.stderr)
            sys.exit(1)

        if run_once:
            break

        time.sleep(120)  # wait for a minute before updating again

if __name__ == "__main__":
    display_stats()

