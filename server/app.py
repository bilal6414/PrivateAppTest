from flask import Flask, request, jsonify, send_from_directory, abort
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), "static")
VERSION_FILE = os.path.join(os.getcwd(), "version.txt")
# Use an environment variable for the API key; default value provided for testing.
API_KEY = os.environ.get("DEPLOY_API_KEY", "Bilal1416179")
#sdfgw
# Ensure the static folder exists.
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_latest_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    return "0.0.0"

def update_version(new_version):
    with open(VERSION_FILE, "w") as f:
        f.write(new_version)

@app.route("/api/latest_version", methods=["GET"])
def latest_version():
    version = get_latest_version()
    # Build the download URL assuming the file is served under /static/
    download_url = request.host_url + "static/SimpleAppAutoUpdate.exe"
    return jsonify({"version": version, "download_url": download_url})

@app.route("/api/upload", methods=["POST"])
def upload():
    # Verify API key.
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer ") or auth_header.split(" ")[1] != API_KEY:
        abort(401, description="Unauthorized")

    if "file" not in request.files:
        abort(400, description="No file part in the request")
    file = request.files["file"]
    if file.filename == "":
        abort(400, description="No selected file")

    # Get the new version from the form data.
    new_version = request.form.get("version", None)
    if new_version is None:
        abort(400, description="Missing version information")

    # Save the uploaded file.
    file_path = os.path.join(UPLOAD_FOLDER, "SimpleAppAutoUpdate.exe")
    file.save(file_path)

    # Update the version.
    update_version(new_version)

    return jsonify({"message": "File uploaded and version updated", "version": new_version})

# Serve static files.
@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
