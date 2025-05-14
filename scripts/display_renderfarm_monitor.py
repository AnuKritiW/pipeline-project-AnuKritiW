from inky.auto import auto
from PIL import Image, ImageDraw, ImageFont
import os
import json

def display_render_farm():
    # setup display
    inky_display = auto()
    inky_display.set_border(inky_display.WHITE)
    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT), color=inky_display.WHITE)
    draw = ImageDraw.Draw(img)

    # Load fonts
    # TODO: Make fonts larger
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_data = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font_title = ImageFont.load_default()
        font_data = ImageFont.load_default()

    # get paths to renderfarm status and filter files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'web_app', 'data')
    jobs_file = os.path.join(data_dir, 'renderfarm_status.json')
    filter_file = os.path.join(data_dir, 'renderfarm_filter.json')

    # load jobs and filter
    with open(jobs_file) as jf:
        jobs = json.load(jf)

    with open(filter_file) as ff:
        filters = json.load(ff)

    filtered_jobs = []
    for job in jobs:
        match = True
        for key in ['user', 'project', 'status']:
            if filters.get(key) and job.get(key) != filters[key]:
                match = False
                break
        if match:
            filtered_jobs.append(job)

    # set up title and headers
    title = "Render Farm Status"
    draw.text((10, 10), title, inky_display.BLACK, font=font_title)

    y = 40
    spacing = 14
    headers = f"{'User':<6} {'Proj':<8} {'Shot':<6} {'Status':<10} {'%':<4}"
    draw.text((10, y), headers, inky_display.BLACK, font=font_data)
    y += spacing
    draw.text((10, y), "-" * 40, inky_display.BLACK, font=font_data)
    y += spacing

    # Display up to 4 jobs
    # TODO: adjust when font is being decided
    for job in filtered_jobs[:4]:
        row = f"{job['user'][:6]:<6} {job['project'][:8]:<8} {job['shot']:<6} {job['status']:<10} {job['progress']:>3}%"
        draw.text((10, y), row, inky_display.BLACK, font=font_data)
        y += spacing

    # TODO: test this logic
    if not filtered_jobs:
        draw.text((10, y), "No jobs match filter.", inky_display.BLACK, font=font_data)

    # Show image
    inky_display.set_image(img)
    inky_display.show()

display_render_farm()

