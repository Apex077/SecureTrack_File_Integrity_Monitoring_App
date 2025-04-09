import threading
import os
import time
import logging
import csv
import io
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from file_monitor import start_monitoring, stop_monitoring

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

LOG_FILE = "./logs/file_monitor.log"
monitoring_thread = None
is_monitoring = False
monitor_lock = threading.Lock()
selected_directory = None

# ✅ Disable Flask's built-in logging to avoid polluting file_monitor.log
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)  # Suppress request logs in console

def parse_logs():
    """Reads the log file and extracts only file monitoring logs."""
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as file:
                for line in file.readlines():
                    if "ADDED" in line or "MODIFIED" in line or "DELETED" in line or "RENAMED" in line:
                        parts = line.strip().split(" - ")
                        if len(parts) >= 3:
                            timestamp, level, message = parts[:3]
                            logs.append({
                                "timestamp": timestamp,
                                "level": level,
                                "message": message
                            })
        except Exception as e:
            print(f"Error reading log file: {e}")
    return logs

@app.route("/download_logs", methods=["GET"])
def download_logs():
    """Allows the user to download logs as a CSV file."""
    logs = parse_logs()

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["timestamp", "level", "message"])
    writer.writeheader()
    writer.writerows(logs)

    csv_content = output.getvalue()
    output.close()

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=logs.csv"}
    )

@app.route("/validate_directory", methods=["POST"])
def validate_directory():
    """Validates if the directory exists."""
    data = request.get_json()
    directory = data.get("directory")

    if not directory or not os.path.isdir(directory):
        return jsonify({"status": "invalid"}), 400  # Directory doesn't exist
    return jsonify({"status": "valid"})  # Directory is valid

@app.route("/logs", methods=["GET"])
def get_logs():
    """API to fetch logs."""
    return jsonify(parse_logs())

@app.route("/start", methods=["POST"])
def start():
    """Starts the file monitoring process with the selected directory."""
    global monitoring_thread, is_monitoring, selected_directory
    data = request.get_json()
    directory = data.get("directory")
    
    # Ensure directory is valid
    if not directory or not os.path.isdir(directory):
        return jsonify({"error": "Invalid directory path"}), 400
    
    selected_directory = directory
    
    with monitor_lock:
        if is_monitoring:
            return jsonify({"status": "already running"}), 400

        if not selected_directory:  # Ensure a directory is selected before starting
            return jsonify({"error": "No directory selected for monitoring"}), 400

        try:
            monitoring_thread = threading.Thread(target=start_monitoring, args=(selected_directory,), daemon=True)
            monitoring_thread.start()
            is_monitoring = True
            time.sleep(1)  # Allow time for the thread to start
            return jsonify({"status": f"Monitoring Started in {selected_directory}"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/stop", methods=["POST"])
def stop():
    """Stops the file monitoring process."""
    global is_monitoring

    with monitor_lock:
        if not is_monitoring:
            return jsonify({"status": "Monitoring Already Stopped!"}), 400

        try:
            stop_monitoring()
            is_monitoring = False
            return jsonify({"status": "Monitoring Stopped!"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/clear_logs", methods=["POST"])
def clear_logs():
    """Clears the log file."""
    try:
        open(LOG_FILE, "w").close()  # Truncate the file
        return jsonify({"status": "Logs cleared!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
