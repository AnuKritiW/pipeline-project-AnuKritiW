"""
display_renderfarm_monitor.py

Displays the status of render jobs on an Inky Impression e-ink display.
It reads job and filter data from JSON files, formats them into a visual table,
and periodically refreshes the screen.

It also supports a `run_once` mode, which renders the display only once—
useful for testing or manual refreshes.

This script is intended to be run continuously in the background by the web app,
specifically when the "Renderfarm Monitor" profile is active.
"""

from inky.auto import auto
from PIL import Image, ImageDraw, ImageFont
import os
import json
import time
import subprocess

def display_render_farm(run_once=False):
    """
    Render the current status of the render farm on the Inky Impression display.

    Loads job data and filter criteria from JSON files, applies filters, and displays
    a formatted summary including user, project, tool, frame count, status, and progress.

    Args:
        run_once (bool): If True, renders the display once and exits.
                         If False (default), continues refreshing every 2 minutes.
    """
    # setup display
    inky_display = auto()
    inky_display.set_border(inky_display.WHITE)

    WIDTH, HEIGHT = inky_display.WIDTH, inky_display.HEIGHT

    # Load fonts
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_data_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_data = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_data_header = ImageFont.load_default()
        font_data = ImageFont.load_default()

    # get paths to renderfarm status and filter files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'web_app', 'data')
    jobs_file = os.path.join(data_dir, 'renderfarm_status.json')
    filter_file = os.path.join(data_dir, 'renderfarm_filter.json')

    # Colors
    RED = inky_display.RED
    GREEN = inky_display.GREEN
    YELLOW = inky_display.YELLOW
    BLACK = inky_display.BLACK
    WHITE = inky_display.WHITE
    ORANGE = inky_display.ORANGE
    BLUE = inky_display.BLUE

    status_colors = {
        "failed": RED,
        "done": GREEN,
        "rendering": YELLOW,
        "waiting": ORANGE
    }

    clear_script = os.path.join(script_dir, 'clear_image_info.py')
    subprocess.run(['python3', clear_script])

    while True:
        print("LOOP")
        img = Image.new("P", (WIDTH, HEIGHT), color=WHITE)
        draw = ImageDraw.Draw(img)

        # load jobs and filter
        try:
            with open(jobs_file) as jf:
                jobs = json.load(jf)
        except:
            jobs = []

        try:
            with open(filter_file) as ff:
                filters = json.load(ff)
        except:
            filters = {}

        FILTER_KEYS = ['user', 'project', 'tool', 'status']
        filtered_jobs = [
            job for job in jobs
            if all(
                not filters.get(k, "").strip() or
                str(job.get(k, "")).strip().lower() == filters[k].strip().lower()
                for k in FILTER_KEYS
            )
        ]

        # set up title and headers
        draw.text((10, 10), "Render Farm Status", BLACK, font=font_title)
        y = 40
        row_height = 28
        spacing = row_height + 4

        col_user = 10
        col_proj = col_user + 70
        col_tool = col_proj + 115
        col_frames = col_tool+ 95
        col_status = col_frames + 85
        col_bar = col_status + 100
        bar_width = 110
        bar_height = 14

        # header row
        draw.text((col_user, y), "User", BLACK, font=font_data_header)
        draw.text((col_proj, y), "Project", BLACK, font=font_data_header)
        draw.text((col_tool, y), "Tool", BLACK, font=font_data_header)
        draw.text((col_frames, y), "Frames", BLACK, font=font_data_header)
        draw.text((col_status, y), "Status", BLACK, font=font_data_header)
        draw.text((col_bar, y), "Progress", BLACK, font=font_data_header)
        y += spacing  # move below the header

        max_rows = (HEIGHT - y - 10) // spacing

        for job in filtered_jobs[:max_rows]:
            draw.text((col_user, y), job["user"][:8], BLACK, font=font_data)
            draw.text((col_proj, y), job["project"][:14], BLACK, font=font_data)
            draw.text((col_tool, y), job.get("tool", "")[:10], BLACK, font=font_data)
            draw.text((col_frames, y), job.get("frames", "")[:10], BLACK, font=font_data)

            status = job.get("status", "unknown")
            color = status_colors.get(status, BLACK)

            # Fill status cell background
            status_text = status.capitalize()
            bbox = draw.textbbox((0, 0), status_text, font=font_data)
            status_w = bbox[2] - bbox[0]
            status_h = bbox[3] - bbox[1]
            padding = 4
            status_box = [
                col_status - padding,
                y - 2,
                col_status + status_w + padding,
                y + status_h + 2
            ]
            draw.rectangle(status_box, fill=color)
            draw.text((col_status, y), status_text, BLACK, font=font_data)


            progress = job.get("progress", 0)
            fill_width = int(bar_width * progress / 100)
            bar_color = GREEN if progress == 100 else BLUE

            bar_x = col_bar
            bar_y = y + 2
            draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], outline=BLACK, fill=WHITE)
            draw.rectangle([bar_x, bar_y, bar_x + fill_width, bar_y + bar_height], fill=bar_color)

            percent_text = f"{progress}%"
            bbox = draw.textbbox((0, 0), percent_text, font=font_data)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            text_x = bar_x + (bar_width - w) // 2
            text_y = bar_y + (bar_height - h) // 2
            draw.text((text_x, text_y), percent_text, fill=WHITE if progress > 60 else BLACK, font=font_data)

            y += spacing

        if not filtered_jobs:
            draw.text((10, y), "No jobs match filter.", BLACK, font=font_data)

        # Show image
        inky_display.set_image(img)
        inky_display.show()

        if run_once:
            break

        time.sleep(120) # refresh every 2 min

def simulate_render_jobs():
    """
    Launch the render job simulator script in the background.

    This is useful for testing or demonstration. The simulator
    generates mock job data to populate the display.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sim_script_path = os.path.join(script_dir, "simulate_render_jobs.py")
    subprocess.Popen(["python3", sim_script_path])

if __name__ == "__main__":
    simulate_render_jobs()
    display_render_farm()

