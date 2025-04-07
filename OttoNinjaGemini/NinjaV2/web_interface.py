# -*- coding:utf-8 -*-
# Filename: web_interface.py (Combined Text and Voice Input)

import time
import atexit
import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Import the core robot logic
import ninja_core

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Global Status Variables ---
last_status = "System Initializing..."
last_command_type = "N/A"
last_command_content = ""
last_interpretation = {}

# --- Initialize Robot Core (Gemini and Hardware) ---
print("--- Initializing Robot Core ---")
gemini_ok = ninja_core.initialize_gemini()
hardware_ok = ninja_core.initialize_hardware()

if not gemini_ok:
    last_status = "CRITICAL ERROR: Failed to initialize Gemini AI."
elif not hardware_ok:
    last_status = "CRITICAL ERROR: Failed to initialize Robot Hardware."
else:
    last_status = "Robot Initialized and Ready."
print("--- Initialization Complete ---")

# --- Register Cleanup Function ---
atexit.register(ninja_core.cleanup_all)

# --- Helper Function to Process Command (Remains the same) ---
def process_and_execute(command_text):
    """Interprets text command via Gemini and executes action."""
    global last_status, last_interpretation
    # ... (implementation remains the same as previous version with logging) ...
    if not command_text:
        print("PROCESS_AND_EXECUTE: Received empty command text.")
        return "Error: Empty command received."

    print(f"PROCESS_AND_EXECUTE: Processing text: '{command_text}'")
    last_status = f"Processing command: '{command_text}'..."
    last_interpretation = {} # Clear previous

    print("PROCESS_AND_EXECUTE: Calling Gemini interpretation...")
    action_data = ninja_core.get_gemini_interpretation(command_text)
    last_interpretation = action_data if action_data else {} # Store result
    print(f"PROCESS_AND_EXECUTE: Gemini Result: {action_data}")

    status_message = f"Failed to get interpretation for '{command_text}'."
    flash_category = "error"

    if action_data:
        action_type = action_data.get("action_type", "unknown")
        if action_type != "unknown":
            status_message = f"Interpreted action: {action_data}. Attempting execution..."
            print(f"PROCESS_AND_EXECUTE: Attempting execution of action: {action_data}")
            try:
                ninja_core.execute_action(action_data)
                time.sleep(0.1) # Small delay
                status_message = f"Action likely initiated: {action_data}"
                print(f"PROCESS_AND_EXECUTE: execute_action call finished.")
                flash_category = "success"
                # Don't flash here, let the calling route handle it
                # flash(f"Executed: {action_data}", flash_category)
            except Exception as e:
                status_message = f"Error executing action for '{command_text}': {e}"
                print(f"PROCESS_AND_EXECUTE: ERROR during execute_action: {e}")
                flash_category = "error"
                # Don't flash here
                # flash(f"Runtime error during execution: {e}", flash_category)
                try:
                    print("PROCESS_AND_EXECUTE: Attempting emergency stop due to error...")
                    ninja_core.movements.stop()
                except Exception as stop_err:
                    print(f"PROCESS_AND_EXECUTE: Error during emergency stop: {stop_err}")
        else:
            error_msg = action_data.get("error", "Command not understood.")
            status_message = f"Command unclear: '{command_text}'. Reason: {error_msg}"
            print(f"PROCESS_AND_EXECUTE: Gemini returned unknown action: {error_msg}")
            flash_category = "warning"
            # Don't flash here
            # flash(f"Command not understood: {error_msg}", flash_category)
    else:
         print("PROCESS_AND_EXECUTE: Failed to get any interpretation from Gemini.")
         flash_category = "error"
         # Don't flash here
         # flash("Error communicating with AI.", "error")

    last_status = status_message # Update global status
    # Return both status and category for context
    return status_message, flash_category

# --- Flask Routes ---
@app.route('/', methods=['GET'])
def index():
    """Renders the main control page."""
    try: interp_str = json.dumps(last_interpretation, indent=2)
    except TypeError: interp_str = "{}"

    return render_template('index.html', # Point to the NEW combined index.html
                           status=last_status,
                           last_command_type=last_command_type,
                           last_command_content=last_command_content,
                           interpretation=interp_str,
                           robot_state=ninja_core.get_robot_status())

# --- Route to handle TEXT commands from HTML form ---
@app.route('/text_command', methods=['POST'])
def handle_text_command():
    global last_command_type, last_command_content

    print("\n--- HANDLE_TEXT_COMMAND Route Called ---")

    command = request.form.get('command_input', '').strip()
    print(f"HANDLE_TEXT_COMMAND: Received form data: '{command}'")

    last_command_type = "Text"
    last_command_content = command

    if not gemini_ok or not hardware_ok:
         print("HANDLE_TEXT_COMMAND: ERROR - Robot core not initialized.")
         flash("Error: Robot core not initialized.", "error")
         return redirect(url_for('index'))

    if not command:
        print("HANDLE_TEXT_COMMAND: WARNING - Empty command submitted.")
        flash("Please enter a command.", "warning")
        return redirect(url_for('index'))

    # Process the command text using the helper
    final_status, flash_category = process_and_execute(command)
    print(f"HANDLE_TEXT_COMMAND: Final status after processing: '{final_status}'")

    # Flash the result message
    flash(final_status, flash_category)

    # Redirect back to the main page to show updates
    return redirect(url_for('index'))


# --- Route to handle VOICE commands (Transcribed Text) from JS fetch ---
@app.route('/voice_command', methods=['POST']) # Renamed from /command
def handle_voice_command():
    global last_command_type, last_command_content

    print("\n--- HANDLE_VOICE_COMMAND Route Called ---")

    if not request.is_json:
        print("HANDLE_VOICE_COMMAND: ERROR - Request is not JSON")
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.get_json()
    print(f"HANDLE_VOICE_COMMAND: Received JSON data: {data}")
    command = data.get('command', '').strip()

    last_command_type = "Voice (Transcribed)"
    last_command_content = command
    print(f"HANDLE_VOICE_COMMAND: Extracted Command: '{command}'")

    if not gemini_ok or not hardware_ok:
         print("HANDLE_VOICE_COMMAND: ERROR - Robot core not initialized.")
         return jsonify({"status": "error", "message": "Robot core not initialized."}), 500

    if not command:
        print("HANDLE_VOICE_COMMAND: WARNING - Received empty command transcript.")
        # Return success to JS, but indicate empty command
        return jsonify({
            "status": "success", # Request succeeded, but command was empty
            "message": "Received empty command transcript.",
            "interpretation": {},
            "flash_category": "warning" # Add category for JS flashing
            }), 200

    # Process the command text using the helper
    final_status, flash_category = process_and_execute(command)

    print(f"HANDLE_VOICE_COMMAND: Final status after processing: '{final_status}'")
    print(f"HANDLE_VOICE_COMMAND: Returning interpretation: {last_interpretation}")

    # Return detailed status back to the JavaScript fetch call
    return jsonify({
        "status": "success", # Indicate the HTTP part worked
        "message": final_status,
        "interpretation": last_interpretation,
        "flash_category": flash_category # Send flash category back to JS
        })


# Route for explicit stop (Remains the same)
@app.route('/stop', methods=['POST'])
def handle_stop():
    global last_status, last_command_type, last_command_content, last_interpretation
    print("\n--- HANDLE_STOP Route Called ---")
    last_command_type = "Button"
    last_command_content = "STOP"
    last_interpretation = {"action_type": "move", "move_function": "stop"}
    try:
        ninja_core.execute_action(last_interpretation)
        last_status = "STOP command executed."
        flash("STOP command sent.", "info")
        print("HANDLE_STOP: Stop action executed.")
    except Exception as e:
        last_status = f"Error executing STOP: {e}"
        flash(f"Error during STOP: {e}", "error")
        print(f"HANDLE_STOP: ERROR during stop execution: {e}")

    return redirect(url_for('index'))


# --- Main Entry Point ---
if __name__ == '__main__':
    print("--- Starting Flask Web Server ---")
    # ... (IP address determination code remains the same) ...
    print(f"*** Open http://<YOUR_PI_IP_ADDRESS>:5000 in your browser ***")
    app.run(host='0.0.0.0', port=5000, debug=True)
