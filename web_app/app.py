from flask import Flask, render_template, request, redirect
import subprocess
import os
import json
import time

# ==================== CONFIGURATION ====================
app = Flask(__name__, static_url_path='/static')

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'scripts'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_UPLOADS = os.path.join(BASE_DIR, 'static', 'uploads')
SELECTED_PROFILE_FILE = os.path.join(BASE_DIR, 'selected_profile.txt')
CURRENT_IMAGE_FILE = os.path.join(BASE_DIR, 'current_image.txt')

VENV_PYTHON = "/home/pi/.virtualenvs/pimoroni/bin/python3"
SPLASH_SCRIPT = "splash_screen.py"
CLEAR_IMAGE_SCRIPT = "clear_image_info.py"

# Script filenames
PROFILES = {
    "stats": {
        "name": "System Stats",
        "icon": "📊",
        "script": "display_stats.py"
    },
    "image": {
        "name": "Image Display",
        "icon": "🖼️",
        "script": "display_image.py"
    },
    "renderfarm": {
        "name": "Renderfarm Monitor",
        "icon": "🎞️",
        "script": "display_renderfarm_monitor.py",
        "simulate": "simulate_render_jobs.py"
    },
}

# ==================== HELPERS ====================

def get_current_profile():
    """
    Return the currently selected profile key.

    Reads the selected_profile.txt file to determine which profile
    is currently active. Returns an empty string if no profile is selected.
    """
    if os.path.exists(SELECTED_PROFILE_FILE):
        with open(SELECTED_PROFILE_FILE) as f:
            return f.read().strip()
    return ""

def can_start_new_profile(requested_profile):
    """
    Check if the requested profile can be started.

    Prevents starting a new profile if another one is already running.
    Returns a tuple (can_start: bool, message: Optional[str]).
    """
    current = get_current_profile()
    if current and current != requested_profile:
        requested_name = PROFILES.get(requested_profile, {}).get("name", requested_profile)
        current_name = PROFILES.get(current, {}).get("name", current)
        return False, f"Cannot start {requested_name}. '{current_name}' is currently running."
    return True, None

def kill_script(script_name):
    """
    Kill any running process matching the script name.

    Uses `pkill -f` to terminate all processes that match the provided script name.
    """
    subprocess.Popen(["pkill", "-f", script_name])

def clear_image_state():
    """
    Clear the currently displayed image state.

    Executes the clear_image_info.py script to reset the image-related state.
    """
    clear_script = os.path.join(SCRIPT_DIR, CLEAR_IMAGE_SCRIPT)
    subprocess.run(['python3', clear_script])

def launch_script(profile_key):
    """
    Launch the script associated with a given profile.

    Clears image state if the profile isn't 'image',
    then writes the selected profile key to file.
    """
    script = os.path.join(SCRIPT_DIR, PROFILES[profile_key]["script"])
    if profile_key != "image":
        clear_image_state()
    subprocess.Popen([VENV_PYTHON, script])
    with open(SELECTED_PROFILE_FILE, "w") as f:
        f.write(profile_key)

def stop_current_profile():
    """
    Stop the currently running profile, if any.

    Kills associated scripts and clears the selected profile file.
    Returns the profile that was stopped.
    """
    current_profile = get_current_profile()

    if current_profile and current_profile in PROFILES:
        kill_script(PROFILES[current_profile]["script"])

        if current_profile == "renderfarm":
            kill_script(PROFILES["renderfarm"]["simulate"])

    open(SELECTED_PROFILE_FILE, "w").close()
    return current_profile

# clear files when script is interrupted
def clear_session_files():
    """
    Clear all temporary session files.

    Empties selected_profile.txt, current_image.txt,
    and resets the renderfarm_filter.json file.
    """
    try:
        open(SELECTED_PROFILE_FILE, "w").close()
    except Exception as e:
        print(f"Error clearing selected_profile.txt: {e}")
    try:
        open(CURRENT_IMAGE_FILE, "w").close()
    except Exception as e:
        print(f"Error clearing current_image.txt: {e}")
    try:
        filter_path = os.path.join(DATA_DIR, "renderfarm_filter.json")
        with open(filter_path, "w") as f:
            json.dump({"user": "", "project": "", "status": "", "tool": ""}, f, indent=2)
    except Exception as e:
        print(f"Error resetting renderfarm_filter.json: {e}")

    print("Session files cleared.")

# ==================== ROUTES ====================

# Route: Home
# renders the home page using index.html
@app.route("/", methods=["GET", "POST"])
def index():
    """
    Render the home page.

    Handles the global "Stop" action via POST and renders the index template
    with the list of profiles and current profile state.
    """
    current_profile = get_current_profile()
    current_profile_name = PROFILES.get(current_profile, {}).get("name", current_profile)

    if request.method == "POST" and request.form.get("stop_global"):
        stop_current_profile()
        return redirect(request.path)

    return render_template(
        "index.html",
        profiles=PROFILES,
        current_profile=current_profile,
        current_profile_name=current_profile_name
    )

# Route: Stats
# creates a generic profile page if no special profile has been created for it
# GET checks if the profile exists, then redirects to the right profile
# a file 'selected_profile.txt' is created that describes what profile is currently running, if any
# POST handles the buttons ('Run'/'Stop')
# lastly, display-generic.html is rendered
@app.route("/profile/stats", methods=["GET", "POST"])
def profile_stats():
    """
    Handle the System Stats profile route.

    Starts/stops the stats display script on POST, and renders
    a generic display template with status and controls.
    """
    profile_key = "stats"
    name = PROFILES[profile_key]["name"]
    current_profile = get_current_profile()
    message = ""
    running = (current_profile == profile_key)

    if request.method == "POST":
        if request.form.get("stop_global"):
            stop_current_profile()
            return redirect(request.path)

        action = request.form.get("action")
        if action == "run":
            can_start, message = can_start_new_profile(profile_key)
            if can_start:
                launch_script(profile_key)
                running = True
                message = f"{name} started."
                return redirect(f"/profile/{profile_key}")
        elif action == "stop":
            kill_script(PROFILES[profile_key]["script"])
            open(SELECTED_PROFILE_FILE, "w").close()
            running = False
            message = f"{name} stopped."
            return redirect(f"/profile/{profile_key}")

    current_profile_name = PROFILES.get(current_profile, {}).get("name", current_profile)

    return render_template(
        "display-generic.html",
        profile_name=name,
        profile_key=profile_key,
        running=running,
        message=message,
        current_profile=current_profile,
        current_profile_name=current_profile_name,
        profiles=PROFILES
    )

# Route: Image Profile
# specialised image profile page
# GET loads current image name (if set) and lists all uploaded images
# POST either uploads, displays or deletes.
# Note that only .png and .jpg/.jpeg are supported for uploads
# lastly, renders display_image.html
@app.route("/profile/image", methods=["GET", "POST"])
def profile_image():
    """
    Handle the Image Display profile route.

    On GET, lists uploaded images and displays the current image.
    On POST, supports uploading, displaying, and deleting images.
    """
    message = ""
    current_image = ""

    # Load current image name if set
    if os.path.exists(CURRENT_IMAGE_FILE):
        with open(CURRENT_IMAGE_FILE) as f:
            current_image = f.read().strip()

    # Handle form actions
    if request.method == "POST":
        action = request.form.get("action")

        # Upload image
        if action == "upload":
            uploaded_file = request.files.get("image")
            if uploaded_file and uploaded_file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                filepath = os.path.join(STATIC_UPLOADS, uploaded_file.filename)
                if os.path.exists(filepath):
                    message = f"{uploaded_file.filename} already exists."
                else:
                    uploaded_file.save(filepath)
                    message = f"Uploaded {uploaded_file.filename}"
            else:
                message = "Invalid file type. Use .png, .jpg, or .jpeg."

        # Display selected image
        elif action == "display":
            can_start, message = can_start_new_profile("image")
            if can_start:
                filename = request.form.get("selected_image")
                image_path = os.path.join(STATIC_UPLOADS, filename)

                try:
                    subprocess.run([
                        VENV_PYTHON,
                        os.path.join(SCRIPT_DIR, PROFILES["image"]["script"]),
                        image_path
                    ], check=True)  # check=True will raise CalledProcessError if fails
                    with open(CURRENT_IMAGE_FILE, "w") as f:
                        f.write(filename)
                    current_image = filename
                    message = f"Now displaying {filename}"
                except subprocess.CalledProcessError as e:
                    message = "Failed to display image. The display might be busy or another script is running."

        # Delete selected image
        elif action == "delete":
            filename = request.form.get("delete_image")
            try:
                os.remove(os.path.join(STATIC_UPLOADS, filename))
                if filename == current_image:
                    current_image = ""
                    open(CURRENT_IMAGE_FILE, "w").close()
                message = f"Deleted {filename}"
            except Exception as e:
                message = f"Error deleting {filename}: {e}"

    # Make sure the uploads folder exists
    if not os.path.exists(STATIC_UPLOADS):
        os.makedirs(STATIC_UPLOADS)

    # List available images
    images = os.listdir(STATIC_UPLOADS)
    current_profile = get_current_profile()

    # Global stop handler (from status card)
    if request.method == "POST" and request.form.get("stop_global"):
        stop_current_profile()
        return redirect(request.path)

    current_profile_name = PROFILES.get(current_profile, {}).get("name", current_profile)

    return render_template(
        "display_image.html",
        images=images,
        current_image=current_image,
        message=message,
        current_profile=current_profile,
        current_profile_name=current_profile_name
    )

# Route: Renderfarm profile
@app.route("/profile/renderfarm", methods=["GET", "POST"])
def profile_renderfarm():
    """
    Handle the Renderfarm Monitor profile route.

    Manages script launching, stopping, and dynamic filtering
    of jobs. Supports POST requests to update job filters.
    """
    profile_key = "renderfarm"
    name = PROFILES[profile_key]["name"]
    message = ""
    current_profile = get_current_profile()
    running = (current_profile == profile_key)
    monitor_script = PROFILES[profile_key]["script"]
    sim_script = PROFILES[profile_key]["simulate"]
    monitor_path = os.path.join(SCRIPT_DIR, monitor_script)

    if request.method == "POST":
        if request.form.get("action") == "run":
            can_start, message = can_start_new_profile("renderfarm")
            if can_start:
                launch_script(profile_key)
                running = True
                message = f"{name} started."
                return redirect("/profile/renderfarm")

        elif request.form.get("action") == "stop":
            kill_script(monitor_script)
            time.sleep(1)
            kill_script(sim_script)
            open(SELECTED_PROFILE_FILE, "w").close()
            running = False
            message = f"{name} stopped."
            return redirect("/profile/renderfarm")

        elif request.form.get("action") == "update_filter":
            filter_data = {
                "user": request.form.get("filter_user", "").strip(),
                "project": request.form.get("filter_project", "").strip(),
                "status": request.form.get("filter_status", "").strip(),
                "tool": request.form.get("filter_tool", "").strip()
            }

            filter_path = os.path.join(DATA_DIR, 'renderfarm_filter.json')
            with open(filter_path, "w") as f:
                json.dump(filter_data, f, indent=2)

            if running:
                # restart the display script so it refreshes immediately
                kill_script(monitor_script)
                time.sleep(1)
                subprocess.Popen([
                    VENV_PYTHON,
                    monitor_path
                ])

            message = "Filter updated."
            return redirect("/profile/renderfarm")

    jobs = []
    status_path = os.path.join(DATA_DIR, "renderfarm_status.json")
    if os.path.exists(status_path):
        try:
            with open(status_path) as f:
                jobs = json.load(f)
        except json.JSONDecodeError:
            jobs = []

    users = sorted(set(job['user'] for job in jobs))
    projects = sorted(set(job['project'] for job in jobs))
    tools = sorted(set(job['tool'] for job in jobs))

    if request.method == "POST" and request.form.get("stop_global"):
        stop_current_profile()
        return redirect(request.path)

    # Always define filter_data, from file if not set in POST
    if 'filter_data' not in locals():
        filter_path = os.path.join(DATA_DIR, 'renderfarm_filter.json')
        try:
            with open(filter_path) as f:
                filter_data = json.load(f)
        except json.JSONDecodeError:
            filter_data = {}

    current_filter = {
        "user": filter_data.get("user", ""),
        "project": filter_data.get("project", ""),
        "tool": filter_data.get("tool", ""),
        "status": filter_data.get("status", "")
    }

    current_profile_name = PROFILES.get(current_profile, {}).get("name", current_profile)

    return render_template(
        "display-renderfarm.html",
        profile_name=name,
        profile_key=profile_key,
        running=running,
        message=message,
        current_profile=current_profile,
        users=users,
        projects=projects,
        tools=tools,
        current_filter=current_filter,
        current_profile_name=current_profile_name
    )

# ==================== MAIN ====================

if __name__ == "__main__":
    """
    Entry point for running the Flask app.

    Starts the splash screen script and runs the web server.
    On shutdown, clears session-related files.
    """
    try:
        subprocess.Popen([
            VENV_PYTHON,
            os.path.join(SCRIPT_DIR, SPLASH_SCRIPT)
        ])
        app.run(host="0.0.0.0", port=5000)
    finally:
        clear_session_files()
