# -*- coding:utf-8 -*-

'''!
  @file ninja_core.py
  @brief Core logic for controlling the Ninja Robot using Google Gemini API,
         integrating movement, sound, and distance sensing.
         Designed to be imported by other scripts (like a web interface).
  @copyright Copyright (c) 2024 Your Name/Assistant
  @license The MIT License (MIT)
  @author Your Name/Assistant
  @version V1.3 (Fixed initialization order)
  @date 2024-05-23
'''

import sys
import os
import time
import re
import threading
import json
import RPi.GPIO as GPIO
import google.generativeai as genai

# --- Configuration ---

# Gemini Setup using google-generativeai
GOOGLE_API_KEY = "Input  your Gemini API key here!"  # <----------- input your API key
GEMINI_MODEL_NAME = "gemini-2.0-flash-lite" # Use a known valid model

# Robot Hardware Configuration
DISTANCE_THRESHOLD_CM = 5.0 # Stop distance in cm

# --- Import Robot Modules ---
try:
    import Ninja_Movements_v1 as movements
    import Ninja_Buzzer as buzzer
    import Ninja_Distance as distance
except ImportError as e:
    print(f"Error importing robot modules: {e}")
    print("Ensure Ninja_Movements_v1.py, Ninja_Buzzer.py, Ninja_Distance.py are in the same directory.")
    sys.exit(1) # Exit if core components are missing

# --- Global Variables ---
model = None # Initialize model to None
movement_thread = None
distance_check_thread = None
is_continuous_moving = False
buzzer_pwm = None
keep_distance_checking = False
hardware_initialized = False # Flag to track initialization

# --- Initialization Functions ---

def initialize_gemini():
    """Initializes the Gemini model."""
    global model # Declare intent to modify the global variable
    if model:
        print("Gemini already initialized.")
        return True # Already initialized

    print(f"Initializing Gemini model: {GEMINI_MODEL_NAME}...")
    try:
        if GOOGLE_API_KEY and len(GOOGLE_API_KEY) > 5:
            print("Configuring Gemini using API Key.")
            genai.configure(api_key=GOOGLE_API_KEY)
        else:
            print("API Key not provided or short. Attempting Application Default Credentials (ADC).")
            pass

        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        print("Gemini model loaded successfully.")
        return True
    except Exception as e:
        print(f"Error configuring or loading Gemini model: {e}")
        model = None
        return False

# !! THIS FUNCTION IS CORRECTED !!
def initialize_hardware():
    """Initializes Servos, Buzzer, and Distance Sensor."""
    global buzzer_pwm, hardware_initialized # Ensure hardware_initialized is global
    if hardware_initialized:
        print("Hardware already initialized.")
        return True # Already initialized

    print("Initializing hardware components...")
    try:
        # Servos
        movements.init_board_and_servo()
        # Buzzer
        buzzer.setup()
        buzzer_pwm = GPIO.PWM(buzzer.BUZZER_PIN, 440)
        buzzer_pwm.start(0)
        # Distance Sensor
        distance.setup_sensor()

        # --- Set Flag AFTER successful component init ---
        print("Hardware components initialized.")
        hardware_initialized = True # <-- SET FLAG HERE (MOVED)

        # --- Perform final setup actions ---
        print("Resetting servos to initial position.")
        movements.reset_servos() # Now safe to call

        print("Playing startup sound.")
        play_robot_sound('hello') # Now safe to call

        time.sleep(1) # Allow servos to settle

        print("Hardware initialization and setup complete.")
        return True # Return success

    except Exception as e:
        print(f"An error occurred during hardware initialization: {e}")
        try:
            GPIO.cleanup() # Attempt cleanup
        except Exception as cleanup_e:
            print(f"Error during cleanup after init failure: {cleanup_e}")
        hardware_initialized = False # Ensure flag is False on error
        return False # Return failure

# --- Cleanup Function ---

def cleanup_all():
    """Stops all actions and cleans up resources."""
    global keep_distance_checking, movement_thread, distance_check_thread, is_continuous_moving, hardware_initialized
    print("\n--- Initiating Cleanup ---")

    # 1. Stop Distance Checking Thread
    print("Stopping distance checker...")
    keep_distance_checking = False
    if distance_check_thread and distance_check_thread.is_alive():
        distance_check_thread.join(timeout=1.0)
    if distance_check_thread and distance_check_thread.is_alive():
        print("Warning: Distance check thread did not terminate gracefully.")
    distance_check_thread = None

    # 2. Stop Movement
    print("Stopping movement...")
    if is_continuous_moving:
         movements.stop()
         time.sleep(0.1)
    if movement_thread and movement_thread.is_alive():
         print("Waiting for movement thread to finish...")
         movement_thread.join(timeout=1.0)
    if movement_thread and movement_thread.is_alive():
         print("Warning: Movement thread did not terminate gracefully.")
    movement_thread = None
    is_continuous_moving = False

    if hardware_initialized:
        print("Putting robot to rest...")
        try:
            if movements.servo:
                movements.rest()
            else:
                print("Warning: Servo object not available, cannot move to rest.")
        except Exception as rest_e:
            print(f"Error during rest movement: {rest_e}")

        if buzzer_pwm:
            print("Stopping buzzer...")
            try:
                buzzer_pwm.stop()
            except Exception as buzz_e:
                print(f"Error stopping buzzer: {buzz_e}")
            buzzer_pwm = None

        print("Cleaning up GPIO...")
        try:
             GPIO.cleanup()
             print("GPIO cleanup successful.")
        except Exception as gpio_e:
             print(f"Error during GPIO cleanup: {gpio_e}")
    else:
        print("Skipping hardware cleanup as initialization failed.")

    hardware_initialized = False


# --- Gemini Interaction ---

def get_gemini_interpretation(user_command):
    """Sends the command to Gemini and parses the JSON response."""
    global model
    if not model:
        print("Error: Gemini model not initialized.")
        return {"action_type": "unknown", "error": "Gemini model not ready."}

    prompt = f"""
Analyze the following user command directed at a robot and determine the intended action(s).
The robot has functions for movement and making sounds.

Available Movement Functions:
- 'hello': A specific wave/wiggle sequence.
- 'walk': Continuous forward walking. Speed options: 'normal', 'fast', 'slow'.
- 'stepback': Continuous backward walking. Speed options: 'normal', 'fast', 'slow'.
- 'run': Continuous forward running (tire mode). Speed options: 'normal', 'fast', 'slow'.
- 'runback': Continuous backward running (tire mode). Speed options: 'normal', 'fast', 'slow'.
- 'turnleft_step': Perform ONE step turning left.
- 'turnright_step': Perform ONE step turning right.
- 'rotateleft': Continuous counter-clockwise rotation (tire mode). Speed options: 'normal', 'fast', 'slow'.
- 'rotateright': Continuous clockwise rotation (tire mode). Speed options: 'normal', 'fast', 'slow'.
- 'stop': Stop any ongoing continuous movement.
- 'reset_servos': Return to standard standing position.
- 'rest': Go to lowered resting position.
- 'set_servo_angle': Set a specific servo (0-3) to an angle (0-180). (Parse ID and Angle if possible)

Available Sound Keywords (map to these keywords):
- 'hello'
- 'thanks' (or 'thank you')
- 'no'
- 'yes'
- 'danger'
- 'exciting'
- 'happy'
- 'right' (for turn sound)
- 'left' (for turn sound)
- 'scared'
- (Add others from Ninja_Buzzer SOUND_MAP if needed)

Output Format:
Return ONLY a valid JSON object describing the action. Do NOT include ```json ... ``` markers or any other text. Use the following keys:
- "action_type": "move", "sound", "combo" (move and sound), "servo", or "unknown".
- "move_function": (string) Name of the movement function to call (e.g., "walk", "hello"). Required if action_type is "move" or "combo".
- "speed": (string) "fast", "slow", or "normal". Optional, defaults to "normal" for continuous movements.
- "sound_keyword": (string) The keyword for the sound to play (e.g., "hello", "danger"). Required if action_type is "sound" or "combo".
- "servo_id": (int) Servo ID (0-3). Required if action_type is "servo".
- "servo_angle": (int) Servo angle (0-180). Required if action_type is "servo".
- "error": (string) Description if the command is unclear or cannot be mapped. Set action_type to "unknown".

Examples:
User: "Say hello" -> {{"action_type": "combo", "move_function": "hello", "sound_keyword": "hello"}}
User: "Walk forward quickly" -> {{"action_type": "move", "move_function": "walk", "speed": "fast"}}
User: "Make a happy sound" -> {{"action_type": "sound", "sound_keyword": "happy"}}
User: "Stop moving" -> {{"action_type": "move", "move_function": "stop"}}
User: "Turn left" -> {{"action_type": "combo", "move_function": "turnleft_step", "sound_keyword": "left"}}
User: "Set servo 1 to 90 degrees" -> {{"action_type": "servo", "servo_id": 1, "servo_angle": 90}}
User: "What time is it?" -> {{"action_type": "unknown", "error": "Cannot determine time."}}

User Command: "{user_command}"

Analyze the command and provide ONLY the JSON output:
"""

    print(f"Sending to Gemini: '{user_command}'")
    try:
        generation_config = genai.types.GenerationConfig(
            temperature=0.2,
            max_output_tokens=1024
        )
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        response_text = response.text.strip()

        try:
            action_data = json.loads(response_text)
            print(f"Gemini Interpretation: {action_data}")
            return action_data
        except json.JSONDecodeError as e:
            print(f"Direct JSON parsing failed: {e}. Trying to extract from markdown.")
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL | re.IGNORECASE)
            if json_match:
                 json_str = json_match.group(1)
                 try:
                      action_data = json.loads(json_str)
                      print(f"Gemini Interpretation (extracted): {action_data}")
                      return action_data
                 except json.JSONDecodeError as e_inner:
                      print(f"Error: Extracted text was not valid JSON: {e_inner}")
                      print(f"Extracted: {json_str}")
                      return {"action_type": "unknown", "error": "Invalid JSON response from AI."}
            else:
                 print("Error: Could not find or parse JSON object in Gemini response.")
                 print(f"Received: {response_text}")
                 return {"action_type": "unknown", "error": "Could not parse AI response."}

    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        return {"action_type": "unknown", "error": f"API communication error: {e}"}


# --- Sound Playing Helper ---

def play_robot_sound(sound_keyword):
    """Plays a sound based on the keyword using the buzzer module."""
    if not hardware_initialized or not buzzer_pwm:
        # Print the error but don't exit, maybe other parts can still work
        print("Error: Hardware/Buzzer not initialized. Cannot play sound.")
        return # Exit this function

    print(f"Playing sound for keyword: '{sound_keyword}'")
    sound_action = buzzer.SOUND_MAP.get(sound_keyword)

    try:
        if sound_action == buzzer.SOUND_SCARED_IDENTIFIER:
            buzzer.play_scared_sound(buzzer_pwm)
        elif sound_action == buzzer.SOUND_EXCITING_IDENTIFIER:
             buzzer.play_exciting_trill(buzzer_pwm)
        elif isinstance(sound_action, list):
            buzzer.play_sequence(buzzer_pwm, sound_action)
        else:
            print(f"Warning: No sound defined for keyword '{sound_keyword}' in Ninja_Buzzer.")
            if 'no' in buzzer.SOUND_MAP:
                play_robot_sound('no')
            else:
                print("Warning: Default 'no' sound not found either.")
    except Exception as e:
        print(f"Error during sound playback for '{sound_keyword}': {e}")


# --- Distance Checking Thread ---

def distance_checker():
    """Thread function to periodically check distance during movement."""
    global keep_distance_checking, is_continuous_moving
    print("Distance checker thread started.")
    last_warning_time = 0
    warning_interval = 2.0

    while keep_distance_checking:
        if not is_continuous_moving or movements.stop_movement:
            if movements.stop_movement: print("Distance checker noticed movement stop flag.")
            keep_distance_checking = False
            break

        if not hardware_initialized:
            print("Distance checker: Hardware no longer initialized. Stopping check.")
            keep_distance_checking = False
            break

        try:
            dist = distance.measure_distance()
        except Exception as e:
            print(f"Error during distance measurement: {e}")
            dist = -2

        if dist == -2:
             print("Distance sensor GPIO error. Stopping checker.")
             keep_distance_checking = False
             break
        elif dist == -1:
             pass
        elif 0 <= dist < DISTANCE_THRESHOLD_CM:
            print(f"!!! OBSTACLE DETECTED at {dist:.1f} cm !!!")
            current_time = time.time()
            if current_time - last_warning_time > warning_interval:
                 play_robot_sound('danger')
                 last_warning_time = current_time

            print("Stopping movement due to obstacle.")
            if is_continuous_moving:
                movements.stop()
                is_continuous_moving = False
            keep_distance_checking = False
            break

        if keep_distance_checking:
            time.sleep(0.15)

    print("Distance checker thread finished.")


# --- Action Execution ---

def execute_action(action_data):
    """Executes the robot action based on the parsed data from Gemini."""
    global movement_thread, distance_check_thread, is_continuous_moving, keep_distance_checking

    if not hardware_initialized:
        print("Error: Hardware not initialized. Cannot execute action.")
        # Try playing sound even if hardware init failed (might partially work if buzzer is ok)
        if 'no' in buzzer.SOUND_MAP: play_robot_sound('no')
        return

    action_type = action_data.get("action_type", "unknown")
    move_func_name = action_data.get("move_function")
    sound_keyword = action_data.get("sound_keyword")
    speed = action_data.get("speed", "normal")

    is_new_continuous = action_type in ["move", "combo"] and move_func_name in [
        "walk", "stepback", "run", "runback", "rotateleft", "rotateright"
    ]
    is_new_finite_move = action_type in ["move", "combo", "servo"] and not is_new_continuous and move_func_name != "stop"

    if (is_new_continuous or is_new_finite_move) and is_continuous_moving:
        print("Stopping previous continuous movement before starting new action.")
        keep_distance_checking = False
        if distance_check_thread and distance_check_thread.is_alive():
             print("Waiting for distance thread...")
             distance_check_thread.join(timeout=0.5)
        distance_check_thread = None
        movements.stop()
        if movement_thread and movement_thread.is_alive():
             print("Waiting for movement thread...")
             movement_thread.join(timeout=1.0)
        movement_thread = None
        is_continuous_moving = False
        time.sleep(0.2)

    try:
        if action_type in ["sound", "combo"] and sound_keyword:
            play_robot_sound(sound_keyword)
            if action_type == "combo": time.sleep(0.2)

        if action_type in ["move", "combo"] and move_func_name:
            target_func = getattr(movements, move_func_name, None)
            if target_func:
                print(f"Executing movement: {move_func_name} (Speed: {speed})")
                if move_func_name in ["walk", "stepback", "run", "runback", "rotateleft", "rotateright"]:
                    if not is_continuous_moving:
                        is_continuous_moving = True
                        movements.stop_movement = False
                        movement_thread = threading.Thread(target=target_func, args=(speed, None), daemon=True)
                        movement_thread.start()
                        keep_distance_checking = True
                        distance_check_thread = threading.Thread(target=distance_checker, daemon=True)
                        distance_check_thread.start()
                    else: print("Warning: Tried to start continuous move while already moving.")
                elif move_func_name == "stop":
                    print("Executing stop command.")
                    keep_distance_checking = False
                    if distance_check_thread and distance_check_thread.is_alive(): distance_check_thread.join(timeout=0.5)
                    movements.stop()
                    if movement_thread and movement_thread.is_alive(): movement_thread.join(timeout=1.0)
                    is_continuous_moving = False
                elif move_func_name in ["turnleft_step", "turnright_step"]:
                    if not is_continuous_moving: target_func(speed, None)
                    else:
                        print("Warning: Cannot perform turn step while continuous movement active. Stop first.")
                        play_robot_sound('no')
                else:
                    if not is_continuous_moving: target_func()
                    else:
                        print(f"Warning: Cannot perform '{move_func_name}' while continuous movement active. Stop first.")
                        play_robot_sound('no')
            else:
                print(f"Error: Movement function '{move_func_name}' not found.")
                play_robot_sound('no')
        elif action_type == "servo":
             if not is_continuous_moving:
                servo_id_raw = action_data.get("servo_id")
                servo_angle_raw = action_data.get("servo_angle")
                if servo_id_raw is not None and servo_angle_raw is not None:
                    try:
                        servo_id = int(servo_id_raw)
                        servo_angle = int(servo_angle_raw)
                        if 0 <= servo_id <= 3 and 0 <= servo_angle <= 180:
                             print(f"Setting servo {servo_id} to {servo_angle} degrees.")
                             movements.set_servo_angle(servo_id, servo_angle)
                        else:
                             print(f"Error: Servo ID ({servo_id}) or Angle ({servo_angle}) out of range.")
                             play_robot_sound('no')
                    except (ValueError, TypeError):
                        print("Error: Invalid servo ID or angle format received from AI.")
                        play_robot_sound('no')
                else:
                    print("Error: Missing servo_id or servo_angle for servo action.")
                    play_robot_sound('no')
             else:
                 print("Warning: Cannot set individual servo while continuous movement active. Stop first.")
                 play_robot_sound('no')
        elif action_type == "unknown":
            error_msg = action_data.get("error", "Command not understood.")
            print(f"AI Error/Unknown Command: {error_msg}")
            play_robot_sound('no')
        else:
            # Only print warning if action_type is not 'sound' (already handled)
            if action_type != "sound":
                print(f"Warning: Unhandled action_type '{action_type}'.")
                play_robot_sound('no')

    except Exception as e:
        print(f"An unexpected error occurred during action execution: {e}")
        try:
            movements.stop()
            is_continuous_moving = False
            keep_distance_checking = False
        except Exception as stop_e:
            print(f"Error during emergency stop: {stop_e}")
        import traceback
        traceback.print_exc()

# --- Helper function to get current status ---
def get_robot_status():
    """Returns a simple string indicating the robot's movement state."""
    if not hardware_initialized:
        return "Hardware Not Initialized"
    if is_continuous_moving:
        if movement_thread and movement_thread.is_alive():
            return "Executing continuous movement..."
        else:
             # Potentially reset state if thread died unexpectedly
             # is_continuous_moving = False # Consider implications
             return "Movement thread stopped unexpectedly."
    else:
        return "Idle / Standing"
