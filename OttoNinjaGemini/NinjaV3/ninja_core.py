# -*- coding:utf-8 -*-

'''!
  @file ninja_core.py
  @brief Core logic for controlling the Ninja Robot using Google Gemini API,
         integrating movement, sound, and distance sensing. Now handles
         natural language questions and prefixed commands.
  @copyright Copyright (c) 2024 Your Name/Assistant
  @license The MIT License (MIT)
  @author Your Name/Assistant
  @version V1.4 (Natural Language Update)
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

# Gemini Setup
GOOGLE_API_KEY = "Input your Gemini API key here!"  # <----------- input your API key here ***** IMPORTANT *****
# GEMINI_MODEL_NAME = "gemini-1.0-pro" # Or a model known to be good at following instructions & potential search
GEMINI_MODEL_NAME = "gemini-2.0-flash-lite" # Use a recent, capable flash model

# Robot Hardware Configuration
DISTANCE_THRESHOLD_CM = 5.0 # Stop distance in cm
WAKE_WORD = "ninja" # Used internally to check if it's a command

# --- Import Robot Modules ---
try:
    import Ninja_Movements_v1 as movements
    import Ninja_Buzzer as buzzer
    import Ninja_Distance as distance
except ImportError as e:
    print(f"Error importing robot modules: {e}")
    print("Ensure Ninja_Movements_v1.py, Ninja_Buzzer.py, Ninja_Distance.py are in the same directory.")
    sys.exit(1)

# --- Global Variables ---
model = None
movement_thread = None
distance_check_thread = None
is_continuous_moving = False
buzzer_pwm = None
keep_distance_checking = False
hardware_initialized = False

# --- Initialization Functions ---

def initialize_gemini():
    """Initializes the Gemini model."""
    global model
    if model:
        print("Gemini already initialized.")
        return True

    print(f"Initializing Gemini model: {GEMINI_MODEL_NAME}...")
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY":
        print("Error: GOOGLE_API_KEY is not set in ninja_core.py. Please add your key.")
        return False
    try:
        print("Configuring Gemini using API Key.")
        genai.configure(api_key=GOOGLE_API_KEY)
        # Configure safety settings to be less restrictive for general conversation
        # Adjust as needed based on Gemini behavior
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        model = genai.GenerativeModel(GEMINI_MODEL_NAME, safety_settings=safety_settings)
        # Optional: Test generation to confirm connection
        # test_response = model.generate_content("Test prompt")
        # print("Gemini test response received.")
        print("Gemini model loaded successfully.")
        return True
    except Exception as e:
        print(f"Error configuring or loading Gemini model: {e}")
        model = None
        return False

def initialize_hardware():
    """Initializes Servos, Buzzer, Distance Sensor and performs startup sequence."""
    global buzzer_pwm, hardware_initialized
    if hardware_initialized:
        print("Hardware already initialized.")
        return True

    print("Initializing hardware components...")
    try:
        movements.init_board_and_servo()
        buzzer.setup()
        buzzer_pwm = GPIO.PWM(buzzer.BUZZER_PIN, 440)
        buzzer_pwm.start(0)
        distance.setup_sensor()

        hardware_initialized = True # Set flag AFTER successful component init
        print("Hardware components initialized.")

        # --- Startup Sequence (Requirement 5) ---
        print("Performing startup sequence...")
        play_robot_sound('hello') # Play sound first
        time.sleep(0.2) # Small delay
        movements.hello() # Perform hello movement
        # movements.reset_servos() # Ensure it returns to stand after hello
        print("Startup sequence complete.")
        # --- End Startup Sequence ---

        time.sleep(0.5) # Allow servos to settle fully

        return True

    except Exception as e:
        print(f"An error occurred during hardware initialization: {e}")
        try: GPIO.cleanup()
        except Exception: pass
        hardware_initialized = False
        return False

# --- Cleanup Function ---

def cleanup_all():
    """Stops all actions, performs shutdown sequence, and cleans up resources."""
    global keep_distance_checking, movement_thread, distance_check_thread, is_continuous_moving, hardware_initialized, buzzer_pwm

    print("\n--- Initiating Cleanup ---")

    # --- Shutdown Sequence (Requirement 6) ---
    if hardware_initialized:
        print("Performing shutdown sequence...")
        try:
            # Stop any active movement first
            if is_continuous_moving:
                movements.stop() # This should also set stop_movement = True
                time.sleep(0.2) # Give threads time to see flag

            play_robot_sound('thanks') # Play sound
            time.sleep(0.5) # Let sound play
            if movements.servo:
                movements.rest() # Move to rest position
                time.sleep(1.0) # Wait for rest movement
            else:
                 print("Warning: Servo object not available, cannot move to rest.")

        except Exception as shutdown_e:
             print(f"Error during shutdown sequence: {shutdown_e}")
        print("Shutdown sequence finished.")
    else:
        print("Skipping shutdown sequence as hardware was not initialized.")
    # --- End Shutdown Sequence ---

    # 1. Stop Distance Checking Thread
    print("Stopping distance checker...")
    keep_distance_checking = False
    if distance_check_thread and distance_check_thread.is_alive():
        distance_check_thread.join(timeout=1.0)
    distance_check_thread = None

    # 2. Ensure Movement Thread is stopped (stop() inside shutdown sequence should handle this)
    print("Ensuring movement thread is stopped...")
    if movement_thread and movement_thread.is_alive():
        print("Waiting for movement thread final check...")
        movement_thread.join(timeout=1.0) # Wait again just in case
    movement_thread = None
    is_continuous_moving = False


    if hardware_initialized:
        # 3. Stop Buzzer
        if buzzer_pwm:
            print("Stopping buzzer PWM...")
            try: buzzer_pwm.stop()
            except Exception: pass
        else: print("Buzzer PWM object not found or not initialized.")

        # 4. Cleanup GPIO
        print("Cleaning up GPIO...")
        try: GPIO.cleanup()
        except Exception: pass
        print("GPIO cleanup attempt complete.")
    else:
        print("Skipping hardware resource cleanup.")

    # Reset flags
    hardware_initialized = False
    buzzer_pwm = None

# --- Gemini Interaction (Modified) ---

def get_gemini_interpretation(user_input, is_command):
    """
    Sends the input to Gemini, choosing a prompt based on whether it's a command or question.
    Returns a dictionary:
        {"type": "answer", "text": "..."} for questions
        {"type": "action", "data": {...}} for commands (using the previous JSON format)
        {"type": "error", "text": "..."} on failure
    """
    global model
    if not model:
        print("Error: Gemini model not initialized.")
        return {"type": "error", "text": "Gemini model not ready."}

    if is_command:
        # --- COMMAND PROMPT ---
        prompt = f"""
Analyze the following robot command and determine the intended action(s).
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

Available Sound Keywords (map to these keywords for the 'sound_keyword' field):
- 'hello', 'thanks', 'thank you', 'no', 'yes', 'danger', 'exciting', 'happy', 'right', 'left', 'scared', 'stop'

Output Format:
Return ONLY a valid JSON object describing the action. Do NOT include ```json ... ``` markers or any other text. Use the following keys:
- "action_type": "move", "sound", "combo" (move and sound), "servo", or "unknown".
- "move_function": (string) Name of the movement function (e.g., "walk", "hello"). Required if action_type is "move" or "combo".
- "speed": (string) "fast", "slow", or "normal". Optional.
- "sound_keyword": (string) The keyword for the sound (e.g., "hello", "danger"). Required if action_type is "sound" or "combo". Gemini should infer appropriate sounds (like 'yes' for confirmation, 'danger' for urgent commands, 'no' for unknown) if not explicit.
- "servo_id": (int) Servo ID (0-3). Required if action_type is "servo".
- "servo_angle": (int) Servo angle (0-180). Required if action_type is "servo".
- "error": (string) Description if the command is unclear or cannot be mapped. Set action_type to "unknown".

Examples:
Command: "can you walk" -> {{"action_type": "combo", "move_function": "walk", "speed": "normal", "sound_keyword": "yes"}}
Command: "run for your life" -> {{"action_type": "combo", "move_function": "run", "speed": "fast", "sound_keyword": "danger"}}
Command: "make a happy sound" -> {{"action_type": "sound", "sound_keyword": "happy"}}
Command: "stop everything" -> {{"action_type": "move", "move_function": "stop"}}
Command: "turn left slowly" -> {{"action_type": "combo", "move_function": "turnleft_step", "speed": "slow", "sound_keyword": "left"}}
Command: "servo 0 to 45" -> {{"action_type": "servo", "servo_id": 0, "servo_angle": 45}}
Command: "go stand over there" -> {{"action_type": "unknown", "error": "Cannot navigate to locations."}}

Robot Command: "{user_input}"

Analyze the command and provide ONLY the JSON output:
"""
        expected_type = "action"

    else:
        # --- QUESTION PROMPT ---
        prompt = f"""
You are a helpful assistant integrated into a small robot. Answer the user's question concisely based on your knowledge. You can access and process information from the real-time internet.

User Question: "{user_input}"

Provide a brief, conversational answer:
"""
        expected_type = "answer"

    print(f"Sending to Gemini ({expected_type} mode): '{user_input}'")
    try:
        generation_config = genai.types.GenerationConfig(
            temperature=0.7 if expected_type == "answer" else 0.2, # Higher temp for answers
            max_output_tokens=1024
        )
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        response_text = response.text.strip()

        if expected_type == "answer":
            print(f"Gemini Answer: {response_text}")
            return {"type": "answer", "text": response_text}
        else: # Expected type is "action" (JSON)
            try:
                # Try direct parsing first
                action_data = json.loads(response_text)
                print(f"Gemini Action JSON: {action_data}")
                return {"type": "action", "data": action_data}
            except json.JSONDecodeError:
                # If direct parse fails, try extracting from markdown
                print("Direct JSON parsing failed. Trying markdown extraction...")
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL | re.IGNORECASE)
                if json_match:
                    json_str = json_match.group(1)
                    try:
                        action_data = json.loads(json_str)
                        print(f"Gemini Action JSON (extracted): {action_data}")
                        return {"type": "action", "data": action_data}
                    except json.JSONDecodeError as e_inner:
                        print(f"Error: Extracted text was not valid JSON: {e_inner}")
                        print(f"Extracted: {json_str}")
                        return {"type": "error", "text": "Invalid JSON action response from AI."}
                else:
                    print("Error: Could not find or parse JSON object in Gemini response.")
                    print(f"Received: {response_text}")
                    return {"type": "error", "text": "Could not parse AI action response."}

    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        # Check for specific safety blocks which might happen with open questions
        if "response was blocked" in str(e).lower():
             return {"type": "error", "text": "My safety filters blocked the response. Please ask differently."}
        return {"type": "error", "text": f"API communication error: {e}"}


# --- Sound Playing Helper ---

def play_robot_sound(sound_keyword):
    """Plays a sound based on the keyword using the buzzer module."""
    if not hardware_initialized or not buzzer_pwm:
        print("Warning: Hardware/Buzzer not initialized. Cannot play sound.")
        return

    print(f"Playing sound for keyword: '{sound_keyword}'")
    sound_action = buzzer.SOUND_MAP.get(str(sound_keyword).lower()) # Ensure keyword is string and lowercase

    if sound_action is None:
        print(f"Warning: No sound defined for keyword '{sound_keyword}' in Ninja_Buzzer.")
        return

    try:
        if sound_action == buzzer.SOUND_SCARED_IDENTIFIER:
            buzzer.play_scared_sound(buzzer_pwm)
        elif sound_action == buzzer.SOUND_EXCITING_IDENTIFIER:
            buzzer.play_exciting_trill(buzzer_pwm)
        elif isinstance(sound_action, list):
            buzzer.play_sequence(buzzer_pwm, sound_action)
        else:
             # Should not happen if SOUND_MAP check passed, but as fallback:
             print(f"Warning: Unknown sound action type for '{sound_keyword}'.")

    except Exception as e:
        print(f"Error during sound playback for '{sound_keyword}': {e}")


# --- Distance Checking Thread (Modified) ---

def distance_checker():
    """Thread function to periodically check distance and stop if obstacle detected."""
    global keep_distance_checking, is_continuous_moving
    print("Distance checker thread started.")
    last_warning_time = 0
    warning_interval = 3.0 # Time between danger sounds if obstacle persists

    while keep_distance_checking:
        if not is_continuous_moving or movements.stop_movement:
            if movements.stop_movement: print("Distance checker noticed movement stop flag.")
            keep_distance_checking = False
            break

        if not hardware_initialized:
            print("Distance checker: Hardware no longer initialized. Stopping check.")
            keep_distance_checking = False
            break

        try: dist = distance.measure_distance()
        except Exception as e:
            print(f"Error in distance_checker during measurement: {e}")
            dist = -2

        if dist == -2:
            print("Distance sensor GPIO error. Stopping checker.")
            keep_distance_checking = False
            break # Stop checking if sensor fails
        elif 0 <= dist < DISTANCE_THRESHOLD_CM: # Check if distance is valid and below threshold
            print(f"!!! OBSTACLE DETECTED at {dist:.1f} cm !!!")

            # --- Stop Robot and Play Sound (Requirement 4) ---
            print("Stopping movement due to obstacle.")
            play_robot_sound('stop') # Play the stop sound
            # It's crucial to call movements.stop() which sets the flag and stops servos
            if is_continuous_moving: # Check flag before calling stop again
                movements.stop() # This sets the internal flag and stops servos
            is_continuous_moving = False # Update core state flag
            keep_distance_checking = False # Signal this thread to stop
            # --- End Obstacle Handling ---
            break # Exit the loop immediately

        # --- Optional: Warning sound if getting close? ---
        # elif DISTANCE_THRESHOLD_CM <= dist < (DISTANCE_THRESHOLD_CM + 10):
        #     current_time = time.time()
        #     if current_time - last_warning_time > warning_interval:
        #         play_robot_sound('danger') # Warning sound
        #         last_warning_time = current_time

        if keep_distance_checking:
            time.sleep(0.15) # Check distance fairly often

    print("Distance checker thread finished.")


# --- Action Execution (Modified) ---

def execute_action(action_data):
    """Executes the robot action based on the parsed 'action' data from Gemini."""
    global movement_thread, distance_check_thread, is_continuous_moving, keep_distance_checking

    if not hardware_initialized:
        print("Error: Hardware not initialized. Cannot execute action.")
        # play_robot_sound('no') # Maybe avoid sound if hardware failed
        return

    action_type = action_data.get("action_type", "unknown")
    move_func_name = action_data.get("move_function")
    sound_keyword = action_data.get("sound_keyword")
    speed = action_data.get("speed", "normal")

    is_new_continuous = action_type in ["move", "combo"] and move_func_name in [
        "walk", "stepback", "run", "runback", "rotateleft", "rotateright"
    ]
    is_new_finite_move = action_type in ["move", "combo", "servo"] and not is_new_continuous and move_func_name != "stop"

    # Stop previous continuous movement if a new move/servo command arrives
    if (is_new_continuous or is_new_finite_move) and is_continuous_moving:
        print("Stopping previous continuous movement before starting new action.")
        keep_distance_checking = False
        if distance_check_thread and distance_check_thread.is_alive():
             distance_check_thread.join(timeout=0.5) # Wait briefly
        distance_check_thread = None
        movements.stop() # This sets the flag and stops servos
        if movement_thread and movement_thread.is_alive():
             movement_thread.join(timeout=1.0) # Wait for thread to finish
        movement_thread = None
        is_continuous_moving = False
        time.sleep(0.2) # Pause before starting new action

    try:
        # --- Play sound specified by Gemini FIRST (if combo/sound type) ---
        if action_type in ["sound", "combo"] and sound_keyword:
            play_robot_sound(sound_keyword)
            # Add delay only if there's also a move to follow
            if action_type == "combo" and move_func_name:
                 time.sleep(0.3)
        # --- End Sound Play ---

        # --- Execute Movement / Servo / Stop ---
        if action_type in ["move", "combo"] and move_func_name:
            target_func = getattr(movements, move_func_name, None)
            if target_func:
                print(f"Executing movement: {move_func_name} (Speed: {speed})")
                if move_func_name in ["walk", "stepback", "run", "runback", "rotateleft", "rotateright"]:
                    # Start continuous movement in a new thread
                    if not is_continuous_moving: # Ensure not already moving
                        is_continuous_moving = True
                        movements.stop_movement = False # Reset the library's stop flag
                        movement_thread = threading.Thread(target=target_func, args=(speed, None), daemon=True)
                        movement_thread.start()
                        # Start distance checker only for forward movements
                        if move_func_name in ["walk", "run"]:
                             keep_distance_checking = True
                             distance_check_thread = threading.Thread(target=distance_checker, daemon=True)
                             distance_check_thread.start()
                        else:
                             keep_distance_checking = False # No distance check for backward/rotate
                    else: print("Warning: Tried to start continuous move while flag indicates already moving.")

                elif move_func_name == "stop":
                    # Explicit stop command
                    print("Executing stop command.")
                    keep_distance_checking = False # Stop distance check first
                    if distance_check_thread and distance_check_thread.is_alive(): distance_check_thread.join(timeout=0.5)
                    movements.stop() # Tell movement library to stop
                    if movement_thread and movement_thread.is_alive(): movement_thread.join(timeout=1.0) # Wait for thread
                    is_continuous_moving = False # Update core state flag
                else:
                    # Finite movements (hello, turn steps, reset, rest)
                    if not is_continuous_moving:
                        target_func() if move_func_name in ["hello", "reset_servos", "rest"] else target_func(speed, None)
                    else:
                        # This case should ideally be prevented by the check at the start
                        print(f"Warning: Cannot perform '{move_func_name}' while continuous movement active. Stop first.")
                        play_robot_sound('no')
            else:
                print(f"Error: Movement function '{move_func_name}' not found in movements module.")
                play_robot_sound('no')

        elif action_type == "servo":
            # Set individual servo angle
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
            play_robot_sound('no') # Play 'no' sound for unknown commands

        # Implicit else: action_type was 'sound', already handled above.

    except Exception as e:
        print(f"An unexpected error occurred during action execution: {e}")
        try: # Attempt emergency stop
            movements.stop()
            is_continuous_moving = False
            keep_distance_checking = False
        except Exception as stop_e: print(f"Error during emergency stop: {stop_e}")
        import traceback
        traceback.print_exc()


# --- NEW Main Processing Function ---

def process_user_input(user_input_text):
    """
    Determines if input is a command or question, gets Gemini interpretation,
    and returns the result structure for the caller to handle.
    """
    if not isinstance(user_input_text, str):
         print("Error: process_user_input received non-string input.")
         return {"type": "error", "text": "Internal processing error."}

    user_input_lower = user_input_text.lower().strip()
    is_command = user_input_lower.startswith(WAKE_WORD)

    text_for_gemini = user_input_text # Send original case for questions
    if is_command:
        # Remove wake word for command processing
        text_for_gemini = user_input_lower.split(WAKE_WORD, 1)[1].strip()
        # Handle case where only wake word was said
        if not text_for_gemini:
             print("Only wake word detected.")
             # Decide action: maybe ask "Yes?" or return a specific "prompt" type?
             # For now, treat as error/do nothing specific for core.
             return {"type": "action", "data": {"action_type": "sound", "sound_keyword": "yes"}} # Simple 'yes' sound


    result = get_gemini_interpretation(text_for_gemini, is_command=is_command)
    return result # Return the dictionary {"type": "answer/action/error", ...}


# --- Helper function to get current status (Unchanged) ---
def get_robot_status():
    """Returns a simple string indicating the robot's movement state."""
    if not hardware_initialized: return "Hardware Not Initialized"
    if is_continuous_moving:
        if movement_thread and movement_thread.is_alive():
            # Check if distance checker is active (only for fwd moves)
            status = "Executing continuous movement"
            if keep_distance_checking and distance_check_thread and distance_check_thread.is_alive():
                 status += " (distance check active)"
            else:
                 status += " (no distance check)"
            return status
        else: return "Movement thread stopped unexpectedly."
    else: return "Idle / Standing"

# --- END OF FILE ninja_core.py ---
