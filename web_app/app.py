from flask import Flask, render_template, request, redirect
import subprocess
import os
import json
import time

app = Flask(__name__, static_url_path='/static')

PROFILES = {
    "stats": {
        "name": "System Stats",
        "icon": "📊",
        "script": "stats-test.py"
    },
    "image": {
        "name": "Image Display",
        "icon": "🖼️",
        "script": "display-image.py"
    },
    "renderfarm": {
        "name": "Renderfarm Monitor",
        "icon": "🧮",
        "script": "display_renderfarm_monitor.py"
    },
}

def stop_current_profile():
    current_profile = ""
    if os.path.exists("selected_profile.txt"):
        with open("selected_profile.txt") as f:
            current_profile = f.read().strip()

    if current_profile and current_profile in PROFILES:
        script_name = PROFILES[current_profile]["script"]
        subprocess.Popen(["pkill", "-f", script_name])

        if current_profile == "renderfarm":
            subprocess.Popen(["pkill", "-f", "simulate_render_jobs.py"])

        open("selected_profile.txt", "w").close()

    return current_profile

# renders the home page using index.html
@app.route("/", methods=["GET", "POST"])
def index():
    current_profile = ""
    if os.path.exists("selected_profile.txt"):
        with open("selected_profile.txt") as f:
            current_profile = f.read().strip()

    if request.method == "POST" and request.form.get("stop_global"):
        stop_current_profile()
        return redirect(request.path)

    return render_template("index.html", profiles=PROFILES, current_profile=current_profile)

# creates a generic profile page if no special profile has been created for it
# GET checks if the profile exists, then redirects to the right profile
# a file 'selected_profile.txt' is created that describes what profile is currently running, if any
# POST handles the buttons ('Run'/'Stop')
# lastly, display-generic.html is rendered
@app.route("/profile/<profile_key>", methods=["GET", "POST"])
def profile_page(profile_key):
    if profile_key not in PROFILES:
        return "Invalid profile", 404

    if profile_key == "image":
        return redirect("/profile/image")
    elif profile_key == "renderfarm":
        return redirect("/profile/renderfarm")

    script = PROFILES[profile_key]["script"]
    name = PROFILES[profile_key]["name"]
    message = ""
    running = False

    current_profile = ""
    if os.path.exists("selected_profile.txt"):
        with open("selected_profile.txt") as f:
            current_profile = f.read().strip()
            running = (current_profile == profile_key)
            # running = (f.read().strip() == profile_key)

    if request.method == "POST":

        if request.method == "POST" and request.form.get("stop_global"):
            stop_current_profile()
            return redirect(request.path)

        action = request.form.get("action")
        if action == "run":
            subprocess.Popen([
                "/home/pi/.virtualenvs/pimoroni/bin/python3",
                f"/home/pi/pipeline-project-AnuKritiW/scripts/{script}"
            ])
            with open("selected_profile.txt", "w") as f:
                f.write(profile_key)
            running = True
            message = f"{name} started."
        elif action == "stop":
            subprocess.Popen(["pkill", "-f", script])
            open("selected_profile.txt", "w").close()
            running = False
            message = f"{name} stopped."
        return redirect(f"/profile/{profile_key}")

    return render_template("display-generic.html", profile_name=name, profile_key=profile_key, running=running, message=message, current_profile=current_profile)

# specialised image profile page
# GET loads current image name (if set) and lists all uploaded images
# POST either uploads, displays or deletes.
# Note that only .png and .jpg/.jpeg are supported for uploads
# lastly, renders display-image.html
@app.route("/profile/image", methods=["GET", "POST"])
def profile_image():
    # TODO: make all paths relative
    # UPLOAD_FOLDER = "/home/pi/pipeline-project-AnuKritiW/uploads"
    UPLOAD_FOLDER = os.path.join(app.root_path, "static/uploads")
    CURRENT_IMAGE_FILE = "/home/pi/pipeline-project-AnuKritiW/web_app/current_image.txt"
    DISPLAY_SCRIPT = "/home/pi/pipeline-project-AnuKritiW/scripts/display-image.py"

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
                filepath = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
                uploaded_file.save(filepath)
                message = f"Uploaded {uploaded_file.filename}"
            else:
                message = "Invalid file type. Use .png, .jpg, or .jpeg."

        # Display selected image
        elif action == "display":
            filename = request.form.get("selected_image")
            image_path = os.path.join(UPLOAD_FOLDER, filename)

            try:
                subprocess.run([
                    "/home/pi/.virtualenvs/pimoroni/bin/python3",
                    DISPLAY_SCRIPT,
                    image_path
                ], check=True)  # check=True will raise CalledProcessError if fails
                with open(CURRENT_IMAGE_FILE, "w") as f:
                    f.write(filename)
                current_image = filename
                message = f"Now displaying {filename}"
            except subprocess.CalledProcessError as e:
                message = "Failed to display image. The display might be busy or another script is running."
                # message = f"Failed to display image: {e}"

        # Delete selected image
        elif action == "delete":
            filename = request.form.get("delete_image")
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, filename))
                if filename == current_image:
                    current_image = ""
                    open(CURRENT_IMAGE_FILE, "w").close()
                message = f"Deleted {filename}"
            except Exception as e:
                message = f"Error deleting {filename}: {e}"

    # Make sure the uploads folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # List available images
    images = os.listdir(UPLOAD_FOLDER)

    current_profile = ""
    if os.path.exists("selected_profile.txt"):
        with open("selected_profile.txt") as f:
            current_profile = f.read().strip()

    # Global stop handler (from status card)
    if request.method == "POST" and request.form.get("stop_global"):
        stop_current_profile()
        return redirect(request.path)

    return render_template(
        "display-image.html",
        images=images,
        current_image=current_image,
        message=message,
        current_profile=current_profile
    )

@app.route("/profile/renderfarm", methods=["GET", "POST"])
def profile_renderfarm():
    name = PROFILES["renderfarm"]["name"]
    message = ""
    running = False
    data_dir = os.path.join(app.root_path, "data")

    # Load current profile
    current_profile = ""
    if os.path.exists("selected_profile.txt"):
        with open("selected_profile.txt") as f:
            current_profile = f.read().strip()
            running = (current_profile == "renderfarm")

    if request.method == "POST":
        monitor_script = PROFILES["renderfarm"]["script"]
        monitor_path = f"/home/pi/pipeline-project-AnuKritiW/scripts/{monitor_script}"

        sim_script = "simulate_render_jobs.py"
        sim_path = f"/home/pi/pipeline-project-AnuKritiW/scripts/{sim_script}"

        if request.form.get("action") == "run":
            subprocess.Popen([
                "/home/pi/.virtualenvs/pimoroni/bin/python3",
                monitor_path
            ])
            with open("selected_profile.txt", "w") as f:
                f.write("renderfarm")
            running = True
            message = f"{name} started."
            return redirect("/profile/renderfarm")

        elif request.form.get("action") == "stop":
            subprocess.Popen(["pkill", "-f", monitor_script])
            time.sleep(1)
            subprocess.Popen(["pkill", "-f", sim_script])
            open("selected_profile.txt", "w").close()
            running = False
            message = f"{name} stopped."
            return redirect("/profile/renderfarm")

        elif request.form.get("action") == "update_filter":
            user = request.form.get("filter_user", "").strip()
            project = request.form.get("filter_project", "").strip()
            status = request.form.get("filter_status", "").strip()
            tool = request.form.get("filter_tool", "").strip()

            filter_data = {
                "user": user,
                "project": project,
                "tool": tool,
                "status": status
            }

            filter_path = os.path.join(data_dir, 'renderfarm_filter.json')
            with open(filter_path, "w") as f:
                json.dump(filter_data, f, indent=2)

            if running:
                # restart the display script so it refreshes immediately
                subprocess.Popen(["pkill", "-f", monitor_script])
                time.sleep(1)
                subprocess.Popen([
                    "/home/pi/.virtualenvs/pimoroni/bin/python3",
                    monitor_path
                ])

            message = "Filter updated."
            return redirect("/profile/renderfarm")

    with open(os.path.join(data_dir, 'renderfarm_status.json')) as f:
        jobs = json.load(f)

    users = sorted(set(job['user'] for job in jobs))
    projects = sorted(set(job['project'] for job in jobs))
    tools = sorted(set(job['tool'] for job in jobs))

    if request.method == "POST" and request.form.get("stop_global"):
        stop_current_profile()
        return redirect(request.path)

    # Always define filter_data, from file if not set in POST
    if 'filter_data' not in locals():
        filter_path = os.path.join(data_dir, 'renderfarm_filter.json')
        if os.path.exists(filter_path):
            try:
                with open(filter_path) as f:
                    filter_data = json.load(f)
            except json.JSONDecodeError:
                filter_data = {}
        else:
            filter_data = {}

    current_filter = {
        "user": filter_data.get("user", ""),
        "project": filter_data.get("project", ""),
        "tool": filter_data.get("tool", ""),
        "status": filter_data.get("status", "")
    }

    return render_template(
        "display-renderfarm.html",
        profile_name=name,
        profile_key="renderfarm",
        running=running,
        message=message,
        current_profile=current_profile,
        users=users,
        projects=projects,
        tools=tools,
        current_filter=current_filter
    )

# clear files when script is interrupted
def clear_session_files():
    try:
        open("selected_profile.txt", "w").close()
    except Exception as e:
        print(f"Error clearing selected_profile.txt: {e}")
    try:
        open("/home/pi/pipeline-project-AnuKritiW/web_app/current_image.txt", "w").close()
    except Exception as e:
        print(f"Error clearing current_image.txt: {e}")
    try:
        filter_path = os.path.join(app.root_path, "data", "renderfarm_filter.json")
        with open(filter_path, "w") as f:
            json.dump({"user": "", "project": "", "status": "", "tool": ""}, f, indent=2)
    except Exception as e:
        print(f"Error resetting renderfarm_filter.json: {e}")

    print("Session files cleared.")

if __name__ == "__main__":
    try:
        subprocess.Popen([
            "/home/pi/.virtualenvs/pimoroni/bin/python3",
            "/home/pi/pipeline-project-AnuKritiW/scripts/splash_screen.py"
        ])
        app.run(host="0.0.0.0", port=5000)
    finally:
        clear_session_files()
