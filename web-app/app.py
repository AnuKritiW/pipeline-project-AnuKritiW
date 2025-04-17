from flask import Flask, render_template, request, redirect
import subprocess

app = Flask(__name__, static_url_path='/static')

PROFILES = {
    "stats": {
        "name": "System Stats",
        "icon": "📊",
        "script": "stats-test.py"
    },
    "image1": {
        "name": "Image Display",
        "icon": "🖼️",
        "script": "display-image.py"
    }
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        profile = request.form["profile"]
        subprocess.Popen(["/home/pi/.virtualenvs/pimoroni/bin/python3", f"/home/pi/pipeline-project-AnuKritiW/scripts/{PROFILES[profile]['script']}"])
        with open("selected_profile.txt", "w") as f:
            f.write(profile)
        return redirect("/")
    return render_template("index.html", profiles=PROFILES)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

