# -*- coding:utf-8 -*-
# Filename: web_interface.py (Controller GUI + Speed + Sounds)

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
last_command_details = {"type": "N/A", "content": ""}
last_interpretation = {}
last_status_message = "System Initializing..."

# --- Sound Mapping ---
# Maps internal command names to sound keywords from Ninja_Buzzer.py
# Add more mappings as needed
COMMAND_TO_SOUND_MAP = {
    "run": "exciting",
    "runback": "scared", # Often uses same gait as stepback
    "walk": None, # No sound specified for normal walk? Add one if desired.
    "stepback": "scared",
    "rotateright": "right",
    "rotateleft": "left",
    "turnright_step": "right",
    "turnleft_step": "left",
    "hello": "hello",
    "rest": "thanks",
    "stop": "no", # Logical addition for stop
    # Add others? "reset_servos"?
}
# Sound delay in seconds (allows sound to play before movement starts)
SOUND_DELAY = 0.3

# --- Initialize Robot Core ---
print("--- Initializing Robot Core ---")
gemini_ok = ninja_core.initialize_gemini()
hardware_ok = ninja_core.initialize_hardware()
# ... (status checks remain the same) ...
print("--- Initialization Complete ---")

# --- Register Cleanup Function ---
atexit.register(ninja_core.cleanup_all)

# --- Helper Function to create action_data (Remains the same) ---
def create_action_data(command_name, speed="normal"):
    # ... (implementation remains the same) ...
    action_type = "move"
    action_data = {"action_type": action_type, "move_function": command_name, "speed": speed}
    if command_name in ['hello', 'stop', 'reset_servos', 'rest']:
         action_data.pop("speed", None)
    print(f"CONTROLLER_HELPER: Created action_data: {action_data}")
    return action_data

# --- Helper Function to process voice commands (Updated for Sound) ---
def process_voice_command(command_text):
    """Interprets voice command text via Gemini, plays sound, executes action."""
    global last_status_message, last_interpretation

    if not command_text:
        return "Error: Empty command received.", "error", {}

    print(f"PROCESS_VOICE: Processing text: '{command_text}'")
    last_status_message = f"Processing voice command: '{command_text}'..."
    last_interpretation = {}

    print("PROCESS_VOICE: Calling Gemini interpretation...")
    action_data = ninja_core.get_gemini_interpretation(command_text)
    last_interpretation = action_data if action_data else {}
    print(f"PROCESS_VOICE: Gemini Result: {action_data}")

    status_message = f"Failed to get interpretation for '{command_text}'."
    flash_category = "error"

    if action_data and action_data.get("action_type") != "unknown":
        # --- Play Sound Based on Interpretation ---
        sound_keyword = None
        action_type = action_data.get("action_type")
        move_func = action_data.get("move_function")
        sound_key_direct = action_data.get("sound_keyword") # From 'sound' or 'combo' types

        if action_type in ["sound", "combo"] and sound_key_direct:
            sound_keyword = sound_key_direct
        elif action_type in ["move", "combo"] and move_func:
            sound_keyword = COMMAND_TO_SOUND_MAP.get(move_func)

        if sound_keyword:
            print(f"PROCESS_VOICE: Playing sound '{sound_keyword}' for action.")
            ninja_core.play_robot_sound(sound_keyword)
            time.sleep(SOUND_DELAY) # Allow sound to play
        # --- End Sound Play ---

        status_message = f"Interpreted action: {action_data}. Attempting execution..."
        print(f"PROCESS_VOICE: Attempting execution of action: {action_data}")
        try:
            ninja_core.execute_action(action_data)
            time.sleep(0.1) # Small delay for action start
            status_message = f"Action likely initiated via voice: {action_data}"
            flash_category = "success"
        except Exception as e:
            # ... (error handling remains the same) ...
            status_message = f"Error executing voice action: {e}"; flash_category = "error"; print(f"ERROR: {e}")
            try: ninja_core.movements.stop()
            except Exception as stop_err: print(f"Emergency stop failed: {stop_err}")

    elif action_data: # Gemini returned unknown
        # ... (handling remains the same) ...
        error_msg = action_data.get("error", "Command not understood."); status_message = f"Voice command unclear: {error_msg}"; flash_category = "warning"; print(f"Unknown action: {error_msg}")
    else: # Gemini call failed
         print("PROCESS_VOICE: Failed to get interpretation."); flash_category = "error"

    last_status_message = status_message
    return status_message, flash_category, last_interpretation


# --- Flask Routes ---
@app.route('/', methods=['GET'])
def index():
    # ... (remains the same) ...
    try: interp_str = json.dumps(last_interpretation, indent=2)
    except TypeError: interp_str = "{}"
    return render_template('index.html', status=last_status_message, last_command_type=last_command_details["type"], last_command_content=last_command_details["content"], interpretation=interp_str, robot_state=ninja_core.get_robot_status())


# --- Route to handle commands from the CONTROLLER GUI (Updated for Sound) ---
@app.route('/controller_command', methods=['POST'])
def handle_controller_command():
    global last_status_message, last_command_details, last_interpretation

    print("\n--- HANDLE_CONTROLLER_COMMAND Route Called ---")
    if not request.is_json: return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.get_json()
    command_name = data.get('command', '').strip()
    speed = data.get('speed', 'normal').strip()
    print(f"CONTROLLER_CMD: Received JSON data: {data}")

    last_command_details = {"type": "Controller", "content": f"{command_name} ({speed})"}
    last_interpretation = {} # Reset interpretation for direct commands

    if not hardware_ok: # Check if core hardware init worked
         print("CONTROLLER_CMD: ERROR - Robot hardware not initialized.")
         return jsonify({"status": "error", "message": "Robot core not initialized."}), 500

    if not command_name:
        print("CONTROLLER_CMD: WARNING - Received empty command name.")
        last_status_message = "Received empty controller command."
        return jsonify({"status": "warning", "message": last_status_message}), 400

    # --- Play Sound Based on Command ---
    sound_keyword = COMMAND_TO_SOUND_MAP.get(command_name)
    if sound_keyword:
        print(f"CONTROLLER_CMD: Playing sound '{sound_keyword}' for '{command_name}'.")
        ninja_core.play_robot_sound(sound_keyword)
        time.sleep(SOUND_DELAY) # Allow sound to play
    # --- End Sound Play ---

    # Create the action data expected by execute_action
    action_data = create_action_data(command_name, speed)
    last_interpretation = action_data # Store direct action

    status_message = f"Executing controller command: {command_name}"
    flash_category = "info"
    print(f"CONTROLLER_CMD: Attempting execution: {action_data}")

    try:
        ninja_core.execute_action(action_data)
        time.sleep(0.1) # Give a moment
        status_message = f"Controller action '{command_name}' likely initiated."
        flash_category = "success"
    except Exception as e:
        # ... (error handling remains the same) ...
        status_message = f"Error executing controller command '{command_name}': {e}"; flash_category = "error"; print(f"ERROR: {e}")
        try: ninja_core.movements.stop()
        except Exception as stop_err: print(f"Emergency stop failed: {stop_err}")


    last_status_message = status_message

    return jsonify({
        "status": flash_category,
        "message": status_message,
        "interpretation": last_interpretation
        })

# --- Route to handle VOICE commands text (Uses process_voice_command now) ---
@app.route('/voice_command_text', methods=['POST'])
def handle_voice_command_text():
    global last_command_details, last_interpretation

    print("\n--- HANDLE_VOICE_COMMAND_TEXT Route Called ---")
    if not request.is_json: return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.get_json()
    command_text = data.get('command_text', '').strip()
    print(f"VOICE_CMD_TEXT: Received JSON data: {data}")

    last_command_details = {"type": "Voice", "content": command_text}

    if not hardware_ok: return jsonify({"status": "error", "message": "Robot core not initialized."}), 500
    if not command_text: return jsonify({"status": "warning", "message": "Received empty voice command text.", "interpretation": {}}), 200

    # Process the voice command using the helper (handles sound internally now)
    final_status, flash_category, interpretation = process_voice_command(command_text)

    print(f"VOICE_CMD_TEXT: Final status after processing: '{final_status}'")
    return jsonify({ "status": flash_category, "message": final_status, "interpretation": interpretation })


# --- Main Entry Point ---
if __name__ == '__main__':
    # ... (IP address determination and app.run() remain the same) ...
    app.run(host='0.0.0.0', port=5000, debug=True)
