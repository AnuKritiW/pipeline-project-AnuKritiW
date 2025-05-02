from flask import Flask, render_template, request, redirect
import subprocess
import os

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
    }
}

# renders the home page using index.html
@app.route("/", methods=["GET", "POST"])
def index():
    current_profile = ""
    if os.path.exists("selected_profile.txt"):
        with open("selected_profile.txt") as f:
            current_profile = f.read().strip()

    if request.method == "POST" and request.form.get("stop_global"):
        if current_profile and current_profile in PROFILES:
            script_name = PROFILES[current_profile]["script"]
            subprocess.Popen(["pkill", "-f", script_name])
            open("selected_profile.txt", "w").close()
            current_profile = ""
        return redirect("/") 
    
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
        if request.form.get("stop_global"):
            if current_profile and current_profile in PROFILES:
                script_name = PROFILES[current_profile]["script"]
                subprocess.Popen(["pkill", "-f", script_name])
                open("selected_profile.txt", "w").close()
                current_profile = ""
            return redirect(f"/profile/{profile_key}")

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
        if current_profile and current_profile in PROFILES:
            script_name = PROFILES[current_profile]["script"]
            subprocess.Popen(["pkill", "-f", script_name])
            open("selected_profile.txt", "w").close()
            current_profile = ""
            message = "Stopped current display."

    return render_template(
        "display-image.html",
        images=images,
        current_image=current_image,
        message=message,
        current_profile=current_profile
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
