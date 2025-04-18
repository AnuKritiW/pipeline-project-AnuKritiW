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
@app.route("/")
def index():
    return render_template("index.html", profiles=PROFILES)

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

    if os.path.exists("selected_profile.txt"):
        with open("selected_profile.txt") as f:
            running = (f.read().strip() == profile_key)

    if request.method == "POST":
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

    return render_template("display-generic.html", profile_name=name, profile_key=profile_key, running=running, message=message)

# specialised image profile page
# GET loads current image name (if set) and lists all uploaded images
# POST either uploads, displays or deletes.
# Note that only .png and .jpg/.jpeg are supported for uploads
# lastly, renders display-image.html
@app.route("/profile/image", methods=["GET", "POST"])
def profile_image():
    # TODO: make all paths relative
    UPLOAD_FOLDER = "/home/pi/pipeline-project-AnuKritiW/uploads"
    CURRENT_IMAGE_FILE = "/home/pi/pipeline-project-AnuKritiW/web-app/current_image.txt"
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
            subprocess.Popen([
                "/home/pi/.virtualenvs/pimoroni/bin/python3",
                DISPLAY_SCRIPT,
                image_path
            ])
            with open(CURRENT_IMAGE_FILE, "w") as f:
                f.write(filename)
            current_image = filename
            message = f"Now displaying {filename}"

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

    return render_template(
        "display-image.html",
        images=images,
        current_image=current_image,
        message=message
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

