# -*- coding:utf-8 -*-
# Filename: web_interface.py

import os
import subprocess
import time
import sys # <-------------------- ADD THIS LINE
from flask import Flask, render_template, jsonify, request, Response

# --- Configuration ---
VOICE_SCRIPT_NAME = "Ninja_Voice_Control.py"
LOG_FILE_NAME = "conversation.log"
STOP_FLAG_FILE = "stop_voice.flag" # Must match the one in Ninja_Voice_Control.py
MAX_LOG_LINES_TO_SHOW = 30 # How many recent lines to display
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__)) # Directory of this script

# --- Global Variable for Process ---
voice_process = None

# --- Flask App Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # Change this for security if needed

# --- Helper Functions ---

def is_voice_script_running():
    """Checks if the voice control process is running."""
    global voice_process
    if voice_process and voice_process.poll() is None:
        return True
    # Check if flag exists but process handle is lost (e.g. Flask restarted)
    stop_flag_path = os.path.join(SCRIPT_DIR, STOP_FLAG_FILE)
    if not os.path.exists(stop_flag_path):
         # If the flag *doesn't* exist, the script *might* be running orphan.
         # This is harder to detect reliably without PID checking.
         # For simplicity, we'll mainly rely on the process handle.
         pass
    return False


def read_log_file():
    """Reads the last N lines from the log file."""
    log_path = os.path.join(SCRIPT_DIR, LOG_FILE_NAME)
    lines = []
    try:
        if os.path.exists(log_path):
            with open(log_path, "r", encoding='utf-8') as f:
                # Read all lines then take the tail
                all_lines = f.readlines()
                lines = all_lines[-MAX_LOG_LINES_TO_SHOW:]
    except Exception as e:
        lines = [f"Error reading log file: {e}"]
    # Join lines into a single string for display
    return "".join(lines)

# --- Flask Routes ---

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/start_voice', methods=['POST'])
def start_voice():
    """Starts the Ninja_Voice_Control.py script."""
    global voice_process
    if is_voice_script_running():
        return jsonify({"status": "error", "message": "Voice control is already running."}), 400

    # Clear any previous stop flag
    stop_flag_path = os.path.join(SCRIPT_DIR, STOP_FLAG_FILE)
    if os.path.exists(stop_flag_path):
        try:
            os.remove(stop_flag_path)
        except OSError as e:
            print(f"Warning: Could not remove existing stop flag: {e}")

    # Clear the log file before starting
    log_path = os.path.join(SCRIPT_DIR, LOG_FILE_NAME)
    try:
        open(log_path, 'w').close() # Create or truncate the file
    except Exception as e:
         print(f"Warning: Could not clear log file: {e}")


    script_path = os.path.join(SCRIPT_DIR, VOICE_SCRIPT_NAME)
    if not os.path.exists(script_path):
         return jsonify({"status": "error", "message": f"{VOICE_SCRIPT_NAME} not found."}), 500

    try:
        print(f"Starting {VOICE_SCRIPT_NAME}...")
        # Run the script using the python interpreter in the virtual env if applicable
        # Modify python executable path if needed e.g. /home/pi/my_venv/bin/python3
        python_executable = sys.executable # <--- This line needs 'import sys'
        # Start the process without capturing stdout/stderr directly here
        # Let it run in the background and write to its own console/log
        voice_process = subprocess.Popen([python_executable, script_path], cwd=SCRIPT_DIR)
        time.sleep(2) # Give script time to initialize
        if voice_process.poll() is not None: # Check if it exited immediately
             process_return_code = voice_process.returncode
             print(f"Script exited immediately with code: {process_return_code}")
             # You could try reading stderr/stdout here if needed for debugging
             # stdout, stderr = voice_process.communicate()
             # print("Script stdout:", stdout)
             # print("Script stderr:", stderr)
             return jsonify({"status": "error", "message": f"Script failed to start or exited quickly (code: {process_return_code}). Check console."}), 500
        print(f"Script started with PID: {voice_process.pid}")
        return jsonify({"status": "success", "message": "Voice control started."})
    except Exception as e:
        print(f"Error starting voice script: {e}")
        return jsonify({"status": "error", "message": f"Failed to start script: {e}"}), 500

@app.route('/stop_voice', methods=['POST'])
def stop_voice():
    """Signals the Ninja_Voice_Control.py script to stop by creating a flag file."""
    global voice_process
    # Check process handle *first* before resorting to just flag creation
    if not is_voice_script_running():
         print("Stop signal requested, but process not tracked or already stopped.")
         # Still try creating the flag file in case the script is orphaned
         # but maybe return a different status?
         # return jsonify({"status": "warning", "message": "Voice control appears stopped, but sent signal anyway."})


    stop_flag_path = os.path.join(SCRIPT_DIR, STOP_FLAG_FILE)
    try:
        print(f"Creating stop flag: {stop_flag_path}")
        with open(stop_flag_path, 'w') as f:
            f.write('stop') # Write something to the file
        # Don't clear voice_process here yet, let the script terminate.
        # The is_voice_script_running() check will eventually return false.
        return jsonify({"status": "success", "message": "Stop signal sent. Please wait for cleanup."})
    except Exception as e:
        print(f"Error creating stop flag: {e}")
        return jsonify({"status": "error", "message": f"Failed to send stop signal: {e}"}), 500

@app.route('/status')
def status():
    """Provides the current log content and running status."""
    log_content = read_log_file()
    running = is_voice_script_running()
    return jsonify({
        "running": running,
        "log_content": log_content
    })

# --- Main Execution ---
if __name__ == '__main__':
    # Make Flask accessible on the local network
    # Use port 5000 by default (http://<pi_ip_address>:5000)
    # Use threaded=True to handle multiple requests (like status polling) better
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
