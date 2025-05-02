from inky.auto import auto
from PIL import Image, ImageFont, ImageDraw
import os
import subprocess

def show_pipeline_splash():
    inky_display = auto()
    inky_display.set_border(inky_display.WHITE)

    # blank canvas
    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT), color=inky_display.WHITE)
    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_instruction = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_instruction = ImageFont.load_default()

    title = "PiPeline"
    instruction = "Go to http://pi.local:5000\nto run a profile"

    w_title, h_title = draw.textsize(title, font=font_title)
    w_instr, h_instr = draw.textsize(instruction, font=font_instruction)
    total_height = h_title + 10 + h_instr

    y_start = (inky_display.HEIGHT - total_height) / 2 - 20

    title_x = (inky_display.WIDTH - w_title) / 2
    instr_x = (inky_display.WIDTH - w_instr) / 2
    
    title_y = y_start #30
    instr_y = y_start + h_title + 10

    # Draw text
    draw.text((title_x, title_y), title, inky_display.BLACK, font=font_title)
    draw.multiline_text((instr_x, instr_y), instruction, inky_display.BLACK, font=font_instruction, align="center")

    # Display image
    inky_display.set_image(img)
    inky_display.show()

    # clear current_image.txt
    script_dir = os.path.dirname(os.path.abspath(__file__))
    clear_script = os.path.join(script_dir, 'clear_image_info.py')
    subprocess.run(['python3', clear_script])

show_pipeline_splash()
