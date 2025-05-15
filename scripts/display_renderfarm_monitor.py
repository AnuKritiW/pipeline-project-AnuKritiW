from inky.auto import auto
from PIL import Image, ImageDraw, ImageFont
import os
import json
import time

def display_render_farm():
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

    status_colors = {
        "failed": RED,
        "done": GREEN,
        "rendering": YELLOW,
        "waiting": ORANGE
    }

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

        filtered_jobs = [
            job for job in jobs
            if all(not filters.get(k) or job.get(k) == filters[k] for k in ['user', 'project', 'status'])
        ]

        # set up title and headers
        draw.text((10, 10), "Render Farm Status", BLACK, font=font_title)
        y = 40
        row_height = 28
        spacing = row_height + 4

        col_user = 10
        col_proj = col_user + 80
        col_status = col_proj + 130
        col_bar = col_status + 110
        bar_width = 130
        bar_height = 14

        # header row
        draw.text((col_user, y), "User", BLACK, font=font_data_header)
        draw.text((col_proj, y), "Project", BLACK, font=font_data_header)
        draw.text((col_status, y), "Status", BLACK, font=font_data_header)
        draw.text((col_bar, y), "Progress", BLACK, font=font_data_header)
        y += spacing  # move below the header

        max_rows = (HEIGHT - y - 10) // spacing

        for job in filtered_jobs[:max_rows]:
            draw.text((col_user, y), job["user"][:8], BLACK, font=font_data)
            draw.text((col_proj, y), job["project"][:14], BLACK, font=font_data)

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
            bar_color = GREEN if progress == 100 else BLACK

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

        time.sleep(120) # refresh every 2 min

display_render_farm()

