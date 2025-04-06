# -*- coding:utf-8 -*-
# Filename: web_interface.py

import time
import atexit # To handle cleanup on exit
import os     # <--- ADD THIS IMPORT
import json   # <--- ADD THIS IMPORT (needed for json.dumps later)
from flask import Flask, render_template, request, redirect, url_for, flash

# Import the core robot logic
import ninja_core

# --- Flask App Setup ---
app = Flask(__name__)
# Required for flash messages (optional but good for feedback)
app.secret_key = os.urandom(24) # Generates a random secret key (Now 'os' is defined)

# --- Global Status Variable (Simple way to pass status to template) ---
# Note: This is not thread-safe for production servers, but fine for Flask dev server
last_status = "System Initializing..."
last_command = ""
last_interpretation = {}

# --- Initialize Robot Core ---
# Do this once when the app starts
print("Initializing Robot Core...")
gemini_ok = ninja_core.initialize_gemini()
hardware_ok = ninja_core.initialize_hardware()

if not gemini_ok:
    last_status = "CRITICAL ERROR: Failed to initialize Gemini AI."
elif not hardware_ok:
    last_status = "CRITICAL ERROR: Failed to initialize Robot Hardware."
else:
    last_status = "Robot Initialized and Ready."

# --- Register Cleanup Function ---
# Ensures cleanup runs when the Flask app (Python script) exits
atexit.register(ninja_core.cleanup_all)

# --- Flask Routes ---
@app.route('/', methods=['GET'])
def index():
    """Renders the main control page."""
    # Pass the last known status and command info to the template
    # Ensure last_interpretation is valid JSON before passing
    try:
        interp_str = json.dumps(last_interpretation, indent=2)
    except TypeError:
        interp_str = "{}" # Default to empty JSON if serialization fails

    return render_template('index.html',
                           status=last_status,
                           last_command=last_command,
                           interpretation=interp_str, # Pass the JSON string
                           robot_state=ninja_core.get_robot_status())

@app.route('/command', methods=['POST'])
def handle_command():
    """Handles commands submitted from the web form."""
    global last_status, last_command, last_interpretation

    # Ensure hardware/AI are initialized
    if not gemini_ok or not hardware_ok:
         flash("Error: Robot core not initialized properly. Cannot process command.", "error")
         return redirect(url_for('index'))

    command = request.form.get('command_input', '').strip()
    last_command = command # Store for display

    if not command:
        flash("Please enter a command.", "warning")
        last_status = "No command entered."
        last_interpretation = {}
        return redirect(url_for('index'))

    print(f"Received command from web: '{command}'")
    last_status = f"Processing command: '{command}'..."
    last_interpretation = {} # Clear previous interpretation

    # Get interpretation from Gemini (via ninja_core)
    action_data = ninja_core.get_gemini_interpretation(command)
    last_interpretation = action_data if action_data else {} # Store for display, ensure it's a dict

    if action_data:
        print(f"Action data: {action_data}")
        action_type = action_data.get("action_type", "unknown")

        if action_type != "unknown":
             last_status = f"Executing action: {action_data}"
             try:
                 # Execute the action (via ninja_core)
                 # This function now handles sounds, movements, threads etc.
                 ninja_core.execute_action(action_data)
                 # Give a moment for actions to potentially start/finish if not threaded
                 time.sleep(0.1)
                 # Update status based on execution (execute_action could potentially return status)
                 last_status = f"Action '{action_type}' for '{command}' likely initiated."
                 flash(f"Executed: {action_data}", "success")
             except Exception as e:
                 last_status = f"Error executing action for '{command}': {e}"
                 print(f"Error during execute_action: {e}")
                 flash(f"Runtime error during execution: {e}", "error")
                 # Attempt to stop things if an error occurred mid-action
                 try:
                    ninja_core.movements.stop() # Safely stop movement if possible
                 except Exception as stop_err:
                    print(f"Error during emergency stop: {stop_err}") # Log error during stop itself
        else:
             error_msg = action_data.get("error", "Command not understood.")
             last_status = f"Command unclear or invalid: '{command}'. Reason: {error_msg}"
             flash(f"Command not understood: {error_msg}", "warning")
    else:
        last_status = f"Failed to get interpretation for '{command}'."
        flash("Error communicating with AI.", "error")

    # Redirect back to the main page to show the updated status
    # Using redirect prevents form re-submission on refresh
    return redirect(url_for('index'))

# --- Route for explicit stop (Good Practice) ---
@app.route('/stop', methods=['POST'])
def handle_stop():
    """Handles an explicit stop button press."""
    global last_status, last_command, last_interpretation
    print("Received STOP command from web.")
    last_command = "STOP"
    last_interpretation = {"action_type": "move", "move_function": "stop"}
    try:
        ninja_core.execute_action(last_interpretation)
        last_status = "STOP command executed. Robot should be stopping/stopped."
        flash("STOP command sent.", "info")
    except Exception as e:
        last_status = f"Error executing STOP: {e}"
        flash(f"Error during STOP: {e}", "error")

    return redirect(url_for('index'))


# --- Main Entry Point ---
if __name__ == '__main__':
    # IMPORTANT: host='0.0.0.0' makes the server accessible
    # from other devices on your local network.
    # Use debug=False for production-like environments if needed,
    # but debug=True is useful during development (enables auto-reloading).
    print("Starting Flask web server...")
    # Determine the IP address for user convenience
    try:
        import socket
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print(f"*** Your Pi's Hostname: {hostname} ***")
        print(f"*** Your Pi's IP Address: {ip_address} ***")
        print(f"*** Open http://{ip_address}:5000 in your browser ***")
    except Exception as e:
        print(f"Could not determine local IP address: {e}")
        print(f"Open http://<YOUR_PI_IP_ADDRESS>:5000 in your browser.")

    app.run(host='0.0.0.0', port=5000, debug=True)
    # Note: The debug server is not recommended for production.
    # For better performance/stability, consider Gunicorn or Waitress later.
