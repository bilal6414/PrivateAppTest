import tkinter as tk
from tkinter import messagebox
import cv2
import os
import sys
import requests
import threading

# URL to your update API endpoint (adjust to your server URL)
UPDATE_API_URL = "http://yourserver.com/api/latest_version"

def get_local_version():
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def fetch_remote_version():
    """Call the update API and return a dict with 'version' and 'download_url'."""
    try:
        response = requests.get(UPDATE_API_URL, timeout=5)
        if response.status_code == 200:
            return response.json()  # e.g., {"version": "2.0.0", "download_url": "http://..."}
    except Exception as e:
        print("Error fetching update info:", e)
    return None

def download_new_exe(download_url, target_path):
    """Download the new executable from the provided URL."""
    try:
        r = requests.get(download_url, stream=True)
        r.raise_for_status()
        with open(target_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print("Download failed:", e)
        return False

def perform_update(new_version, download_url):
    """Download the new executable and restart the application."""
    # Download the new executable to a temporary file.
    temp_exe = "SimpleAppAutoUpdate_new.exe"
    success = download_new_exe(download_url, temp_exe)
    if success:
        # Update version.txt locally.
        with open("version.txt", "w") as f:
            f.write(new_version)
        messagebox.showinfo("Update", f"Updated to version {new_version}. The application will now restart.")
        # Launch the new executable.
        os.startfile(temp_exe)
        # Exit current instance.
        sys.exit(0)
    else:
        messagebox.showerror("Update Failed", "Failed to download the update. Please try again later.")

def check_for_updates_async(current_version):
    """Run the update check in a separate thread to avoid freezing the UI."""
    def _check():
        update_info = fetch_remote_version()
        if update_info:
            remote_version = update_info.get("version", current_version)
            download_url = update_info.get("download_url", "")
            # For simplicity, a direct string comparison is used.
            if current_version != remote_version and download_url:
                # Ask the user for permission to update.
                if messagebox.askyesno("Update Available",
                                       f"A new version ({remote_version}) is available. Update now?"):
                    perform_update(remote_version, download_url)
            else:
                messagebox.showinfo("No Update", "You are using the latest version.")
        else:
            messagebox.showwarning("Update Check", "Could not check for updates.")
    threading.Thread(target=_check).start()

def main():
    current_version = get_local_version()
    root = tk.Tk()
    root.title(f"SimpleApp - v{current_version}")

    label = tk.Label(root, text=f"Welcome to SimpleApp! Version: {current_version}", padx=20, pady=20)
    label.pack()

    # Display OpenCV version.
    cv_label = tk.Label(root, text=f"OpenCV Version: {cv2.__version__}")
    cv_label.pack()

    # Button to trigger update check.
    update_btn = tk.Button(root, text="Check for Updates",
                           command=lambda: check_for_updates_async(current_version))
    update_btn.pack(pady=10)

    # Optionally, check for updates automatically at startup:
    # check_for_updates_async(current_version)

    root.mainloop()

if __name__ == "__main__":
    main()
