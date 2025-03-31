# -*- coding:utf-8 -*-

'''!
  @file Ninja_Gemini_Movement_Optimized.py
  @brief Control a 4-servo robot using text commands interpreted by Gemini,
         incorporating an ultrasonic sensor for obstacle avoidance and a buzzer for sound feedback.
  @note Requires DFRobot_RaspberryPi_Expansion_Board library, google-generativeai, RPi.GPIO.
        Ensure correct hardware connections and API key setup.
  @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license     The MIT License (MIT)
'''
# prompt example
# "Move servo 0 to 45 degrees with fast speed"
# "Set servo 1 to 135 degrees with jerky style"
# "All servos to center"
# "Servo 2 to 90, servo 3 to 180"
# "All the servos to zero" (Expect all the servo to be zero)
# "hello", "walk", "run", "turn left", "turn right", "rotate left", "rotate right", "step back", "run back", "stop", "rest"

import sys
import os
import time
import re
import threading
import RPi.GPIO as GPIO
import google.generativeai as genai

# --- DFRobot Library Import ---
# Ensure the DFRobot library is accessible (e.g., in the parent directory)
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
try:
    from DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_IIC as Board
    from DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_Servo as Servo
except ImportError:
    print("Error: DFRobot library not found. Make sure it's installed and accessible.")
    print("Try: cd DFRobot_RaspberryPi_Expansion_Board && sudo python setup.py install")
    sys.exit(1)

# --- Buzzer Import ---
# Ensure Ninja_Buzzer.py is in the same directory or accessible via sys.path
try:
    import Ninja_Buzzer as buzzer
except ImportError:
    print("Error: Ninja_Buzzer.py not found. Make sure it's in the same directory.")
    sys.exit(1)

# --- Constants ---
# Hardware Pins (VERIFY THESE GPIO NUMBERS FOR YOUR HAT/SETUP!)
TRIG_PIN = 21
ECHO_PIN = 22
BUZZER_PIN = buzzer.BUZZER_PIN # Use the pin defined in Ninja_Buzzer

# Servo Configuration
SERVO_PWM_PINS = [0, 1, 2, 3] # Corresponds to PWM0, PWM1, PWM2, PWM3 on the HAT
SERVO_RESET_ANGLES = {
    0: 105, # Servo 0 specific reset
    1: 90,
    2: 90,
    3: 90
}
SERVO_REST_ANGLES = {
    0: 15,
    1: 180,
    2: 90,
    3: 90
}

# Movement Parameters
SPEED_MAP = {
    'fast': 0.002,
    'slow': 0.015,
    'normal': 0.01
}
DEFAULT_SPEED = 'normal'
DISTANCE_THRESHOLD_CM = 5

# Sensor/Timing
SPEED_OF_SOUND = 34300 # cm/s

# --- Global Variables ---
stop_movement = False       # Flag to signal threads to stop continuous movements
board = None                # DFRobot board object
servo_controller = None     # DFRobot servo controller object
pwm_buzzer = None           # Buzzer PWM object
gemini_model = None         # Gemini model object

# --- Setup and Helper Functions ---

def initialize_hardware():
    """Initializes GPIO, Buzzer, DFRobot Board, and Servos."""
    global board, servo_controller, pwm_buzzer

    print("Initializing hardware...")
    try:
        # GPIO Setup (for Ultrasonic and potentially Buzzer if not handled by buzzer lib)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False) # Suppress GPIO warnings
        GPIO.setup(TRIG_PIN, GPIO.OUT)
        GPIO.setup(ECHO_PIN, GPIO.IN)

        # Buzzer Setup (delegated to buzzer module)
        buzzer.setup()
        pwm_buzzer = GPIO.PWM(BUZZER_PIN, 440) # Initial frequency
        pwm_buzzer.start(0) # Start silent

        # DFRobot Board Setup
        board = Board(1, 0x10) # I2C bus 1, address 0x10
        while board.begin() != board.STA_OK:
            print_board_status()
            print("DFRobot board begin failed, retrying...")
            time.sleep(2)
        print("DFRobot board begin success.")

        # DFRobot Servo Setup
        servo_controller = Servo(board)
        servo_controller.begin()
        print("Servo controller initialized.")

        reset_servos() # Start servos at reset position
        print("Hardware initialization complete.")
        buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_HAPPY) # Play startup sound

    except Exception as e:
        print(f"FATAL ERROR during hardware initialization: {e}")
        cleanup() # Attempt cleanup even on init failure
        sys.exit(1)

def initialize_gemini():
    """Configures and initializes the Google Gemini model."""
    global gemini_model
    print("Initializing Google Gemini...")
    try:
        # API Authentication
        GOOGLE_API_KEY = "Input your Google API key here!" # <-- PUT YOUR KEY HERE
        if len(GOOGLE_API_KEY) < 5 and "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
            print(
                "ERROR: Please provide your Google Gemini API key or set up Application Default Credentials."
            )
            quit()

        if len(GOOGLE_API_KEY) > 5:
            genai.configure(api_key=GOOGLE_API_KEY)
            print("Gemini configured using API Key.")
        else:
            # Make sure the path is correct if using ADC
            # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/your/service_account_key.json"
            genai.configure(transport='rest', location='us-central1')
            print("Gemini configured using Application Default Credentials.")

        # Select the Gemini model (ensure it's available)
        model_name = 'gemini-2.0-flash-lite' # <------- You can change to different model here, but I recommend 2.0 flash
        gemini_model = genai.GenerativeModel(model_name)
        print(f"Gemini model '{model_name}' loaded.")

    except Exception as e:
        print(f"FATAL ERROR during Gemini initialization: {e}")
        cleanup()
        sys.exit(1)

def print_board_status():
    """Prints the status of the DFRobot board operation."""
    if not board: return # Guard against calling before init
    status_map = {
        board.STA_OK: "everything ok",
        board.STA_ERR: "unexpected error",
        board.STA_ERR_DEVICE_NOT_DETECTED: "device not detected",
        board.STA_ERR_PARAMETER: "parameter error",
        board.STA_ERR_SOFT_VERSION: "unsupported board firmware version"
    }
    status_text = status_map.get(board.last_operate_status, "unknown status")
    print(f"Board status: {status_text}")

def get_sleep_time(speed_modifier=None):
    """Returns the appropriate sleep time based on the speed modifier."""
    return SPEED_MAP.get(speed_modifier, SPEED_MAP[DEFAULT_SPEED])

def measure_distance():
    """
    Measures the distance using the ultrasonic sensor.
    Returns distance in cm, or -1 if timeout/error.
    """
    try:
        # Ensure pins are set correctly each time (robustness)
        GPIO.setup(TRIG_PIN, GPIO.OUT)
        GPIO.setup(ECHO_PIN, GPIO.IN)

        # Send trigger pulse
        GPIO.output(TRIG_PIN, False)
        time.sleep(0.02) # Slightly longer pause before trigger
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(TRIG_PIN, False)

        # Measure echo pulse
        pulse_start = time.time()
        pulse_end = time.time()
        timeout = pulse_start + 0.1 # 100ms timeout

        # Wait for echo start
        while GPIO.input(ECHO_PIN) == 0 and pulse_start < timeout:
            pulse_start = time.time()

        # Wait for echo end
        while GPIO.input(ECHO_PIN) == 1 and pulse_end < timeout:
            pulse_end = time.time()

        if pulse_start >= timeout or pulse_end >= timeout:
             # print("Ultrasonic sensor timeout.") # Optional debug message
             return -1 # Timeout occurred

        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration * SPEED_OF_SOUND) / 2

        return distance
    except Exception as e:
        print(f"Error measuring distance: {e}")
        return -1

def get_gemini_command_details(text_command):
    """
    Uses Gemini Pro to extract servo angles and modifiers from a text command.
    Returns a dictionary with 'angles', 'speed', 'style', or None on error.
    """
    global gemini_model
    if not gemini_model:
        print("Error: Gemini model not initialized.")
        return None

    prompt = f"""
    You are controlling a robot with four servos (0, 1, 2, 3). Extract desired angles (0-180 degrees) for each servo and movement modifiers (speed, style) from the user's command.

    Return ONLY a JSON object enclosed in triple backticks (```).
    The JSON MUST contain keys: "servo0", "servo1", "servo2", "servo3", "speed", "style".
    - If an angle isn't specified, use 90.
    - For "speed", use "fast", "slow", or "normal". If unspecified, use null.
    - For "style", use "smooth", "jerky", or "curve". If unspecified, use null.

    Example Output:
    ```
    {{"servo0": 45, "servo1": 90, "servo2": 135, "servo3": 90, "speed": "fast", "style": "smooth"}}
    ```
    Another Example (no modifiers):
    ```
    {{"servo0": 0, "servo1": 0, "servo2": 0, "servo3": 0, "speed": null, "style": null}}
    ```

    User command: {text_command}
    """
    try:
        print(f"Sending prompt to Gemini...") # Debug
        response = gemini_model.generate_content(prompt)
        print(f"Raw Gemini Response: {response.text}") # Debug
        return extract_command_details_from_json(response.text)
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return None

def extract_command_details_from_json(json_string):
    """
    Extracts angles and modifiers from the JSON-like string.
    Returns a dictionary like {'angles': {...}, 'speed': '...', 'style': '...'}, or None on error.
    """
    if not json_string:
        print("Received empty JSON string from Gemini.")
        return None

    try:
        # Remove backticks and potentially leading/trailing whitespace or markdown
        json_content = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', json_string, re.DOTALL)
        if json_content:
            json_string = json_content.group(1).strip()
        else:
             json_string = json_string.replace('```', '').strip() # Fallback strip


        # Use regex to be more robust against minor formatting variations
        servo_matches = re.findall(r'"(servo\d)"\s*:\s*(\d+)', json_string)
        angles = {key: int(value) for key, value in servo_matches}

        # Ensure all servos have a default value if not found
        for i in range(len(SERVO_PWM_PINS)):
            key = f"servo{i}"
            if key not in angles:
                angles[key] = 90 # Default angle

        speed_match = re.search(r'"speed"\s*:\s*(?:null|"(\w+)")', json_string)
        speed = speed_match.group(1) if speed_match and speed_match.group(1) else None

        style_match = re.search(r'"style"\s*:\s*(?:null|"(\w+)")', json_string)
        style = style_match.group(1) if style_match and style_match.group(1) else None

        return {"angles": angles, "speed": speed, "style": style}

    except Exception as e:
        print(f"Error parsing JSON response: '{json_string}'. Error: {e}")
        return None

# --- Movement Functions ---

def reset_servos():
    """Resets all servos to their defined default standing positions."""
    print("Resetting servos to default positions...")
    try:
        for i, pwm_pin in enumerate(SERVO_PWM_PINS):
             angle = SERVO_RESET_ANGLES.get(i, 90) # Use specific reset or default 90
             servo_controller.move(pwm_pin, angle)
        time.sleep(0.5)
    except Exception as e:
        print(f"Error resetting servos: {e}")

def hello():
    """Performs the 'hello' wave movement."""
    global pwm_buzzer
    print("Performing 'hello' movement...")
    buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_HELLO)
    reset_servos()
    try:
        servo_controller.move(SERVO_PWM_PINS[0], 175) # Assuming servo 0 is used
        servo_controller.move(SERVO_PWM_PINS[1], 135) # Assuming servo 1 is used
        time.sleep(1)
        servo_controller.move(SERVO_PWM_PINS[0], SERVO_RESET_ANGLES.get(0, 90)) # Back to reset
        time.sleep(1)
        for _ in range(2): # Wave
            for angle in range(SERVO_RESET_ANGLES.get(0, 90), 74, -1):
                servo_controller.move(SERVO_PWM_PINS[0], angle)
                time.sleep(0.01)
            for angle in range(75, SERVO_RESET_ANGLES.get(0, 90) + 1):
                servo_controller.move(SERVO_PWM_PINS[0], angle)
                time.sleep(0.01)
        time.sleep(1)
    except Exception as e:
        print(f"Error during hello movement: {e}")
    finally:
        reset_servos()

def walk(speed=None, style=None):
    """
    Performs the continuous walking motion.
    Checks for obstacles and stops if detected within threshold.
    Uses speed modifier to adjust movement delay.
    """
    global stop_movement, pwm_buzzer
    print(f"Starting 'walk' movement (Speed: {speed or DEFAULT_SPEED})...")
    sleep_time = get_sleep_time(speed)

    while not stop_movement:
        distance = measure_distance()
        if distance != -1 and distance < DISTANCE_THRESHOLD_CM:
            print("Object detected! Playing danger sound and stopping walk!")
            buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_DANGER)
            stop()
            break

        try:
            # --- Step 1 ---
            servo_controller.move(SERVO_PWM_PINS[0], 70) # Right leg up/forward
            time.sleep(0.2)
            # Feet rotation for forward motion
            servo_controller.move(SERVO_PWM_PINS[2], 80) # Left foot rotate
            servo_controller.move(SERVO_PWM_PINS[3], 100) # Right foot rotate
            time.sleep(0.5)
            servo_controller.move(SERVO_PWM_PINS[2], 90) # Feet back to center
            servo_controller.move(SERVO_PWM_PINS[3], 90)
            servo_controller.move(SERVO_PWM_PINS[0], SERVO_RESET_ANGLES.get(0,90)) # Right leg down
            time.sleep(0.2)
            if stop_movement: break

            # --- Step 2 ---
            servo_controller.move(SERVO_PWM_PINS[1], 125) # Left leg up/forward
            time.sleep(0.2)
            # Feet rotation
            servo_controller.move(SERVO_PWM_PINS[2], 80)
            servo_controller.move(SERVO_PWM_PINS[3], 100)
            time.sleep(0.5)
            servo_controller.move(SERVO_PWM_PINS[2], 90)
            servo_controller.move(SERVO_PWM_PINS[3], 90)
            servo_controller.move(SERVO_PWM_PINS[1], SERVO_RESET_ANGLES.get(1,90)) # Left leg down
            time.sleep(0.2)
            if stop_movement: break

            time.sleep(sleep_time) # Control overall walk speed

        except Exception as e:
            print(f"Error during walk cycle: {e}")
            stop() # Stop on error
            break
    print("Walk movement finished.")

def turnleft(speed=None, style=None):
    """Performs a single turn left action."""
    global pwm_buzzer
    print(f"Performing 'turn left' action...")
    buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_TURN_LEFT)
    try:
        # Lift right leg
        servo_controller.move(SERVO_PWM_PINS[0], 70)
        time.sleep(0.3)
        # Rotate feet to turn left
        servo_controller.move(SERVO_PWM_PINS[2], 80)
        servo_controller.move(SERVO_PWM_PINS[3], 80) # Both rotate same way
        time.sleep(0.5)
        # Reset feet
        servo_controller.move(SERVO_PWM_PINS[2], 90)
        servo_controller.move(SERVO_PWM_PINS[3], 90)
        # Put right leg down
        servo_controller.move(SERVO_PWM_PINS[0], SERVO_RESET_ANGLES.get(0,90))
        time.sleep(0.3)
    except Exception as e:
         print(f"Error during turn left: {e}")
    finally:
        reset_servos()
        print("Turn left action finished.")

def turnright(speed=None, style=None):
    """Performs a single turn right action."""
    global pwm_buzzer
    print(f"Performing 'turn right' action...")
    buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_TURN_RIGHT)
    try:
        # Lift left leg
        servo_controller.move(SERVO_PWM_PINS[1], 125)
        time.sleep(0.3)
        # Rotate feet to turn right
        servo_controller.move(SERVO_PWM_PINS[2], 100) # Both rotate same way
        servo_controller.move(SERVO_PWM_PINS[3], 100)
        time.sleep(0.5)
        # Reset feet
        servo_controller.move(SERVO_PWM_PINS[2], 90)
        servo_controller.move(SERVO_PWM_PINS[3], 90)
        # Put left leg down
        servo_controller.move(SERVO_PWM_PINS[1], SERVO_RESET_ANGLES.get(1,90))
        time.sleep(0.3)
    except Exception as e:
        print(f"Error during turn right: {e}")
    finally:
        reset_servos()
        print("Turn right action finished.")

def run(speed=None, style=None):
    """
    Performs the continuous running motion (360 servos).
    Checks for obstacles. Uses speed modifier.
    """
    global stop_movement, pwm_buzzer
    print(f"Starting 'run' movement (Speed: {speed or DEFAULT_SPEED})...")
    buzzer.play_exciting_trill(pwm_buzzer) # Play exciting sound for run
    sleep_time = get_sleep_time(speed) # Use helper function

    # Set legs to running stance
    servo_controller.move(SERVO_PWM_PINS[0], 15)
    servo_controller.move(SERVO_PWM_PINS[1], 180)
    time.sleep(0.5)

    # Determine rotation angles for 360 servos based on speed
    # Closer to 90 is stop, further away is faster
    # Adjust these values based on your servo speed calibration
    if speed == 'fast':
        cw_angle = 0   # Max clockwise speed
        ccw_angle = 180 # Max counter-clockwise speed
    elif speed == 'slow':
        cw_angle = 80
        ccw_angle = 100
    else: # normal
        cw_angle = 70
        ccw_angle = 110

    # Note: Assuming servo 2 needs < 90 for CW, servo 3 needs > 90 for CW (adjust if reversed)
    run_cw_angle_s2 = cw_angle
    run_cw_angle_s3 = 180 - cw_angle # Opposite direction for other foot
    run_ccw_angle_s2 = ccw_angle
    run_ccw_angle_s3 = 180 - ccw_angle

    while not stop_movement:
        distance = measure_distance()
        if distance != -1 and distance < DISTANCE_THRESHOLD_CM:
            buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_DANGER)
            print("Object detected! Stopping run!")
            stop()
            break

        try:
            servo_controller.move(SERVO_PWM_PINS[2], run_cw_angle_s2) # Servo 2 Clockwise
            servo_controller.move(SERVO_PWM_PINS[3], run_cw_angle_s3) # Servo 3 Clockwise
            time.sleep(sleep_time) # Small delay to simulate speed

            if stop_movement: break

            # Optional: Add a brief pause or reverse slightly for a more "running" look?
            # servo_controller.move(SERVO_PWM_PINS[2], 90)
            # servo_controller.move(SERVO_PWM_PINS[3], 90)
            # time.sleep(sleep_time / 2)

        except Exception as e:
            print(f"Error during run cycle: {e}")
            stop()
            break

    print("Run movement finished.")
    # Ensure servos are stopped after loop ends (even if not by 'stop' command)
    servo_controller.move(SERVO_PWM_PINS[2], 90)
    servo_controller.move(SERVO_PWM_PINS[3], 90)
    reset_servos() # Back to standing

def rotateleft(speed=None, style=None):
    """Performs continuous counter-clockwise rotation using 360 servos."""
    global stop_movement, pwm_buzzer
    print(f"Starting 'rotate left' (Speed: {speed or DEFAULT_SPEED})...")
    buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_TURN_LEFT) # Play sound
    sleep_time = get_sleep_time(speed)

    # Determine rotation angles for 360 servos
    if speed == 'fast': rot_angle = 0
    elif speed == 'slow': rot_angle = 80
    else: rot_angle = 70

    # Both servos rotate same direction (e.g., < 90 for CCW on both, adjust if needed)
    rotate_angle_s2 = rot_angle
    rotate_angle_s3 = rot_angle

    while not stop_movement:
        distance = measure_distance()
        if distance != -1 and distance < DISTANCE_THRESHOLD_CM:
            buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_DANGER)
            print("Object detected! Stopping rotate left!")
            stop()
            break
        try:
            servo_controller.move(SERVO_PWM_PINS[2], rotate_angle_s2)
            servo_controller.move(SERVO_PWM_PINS[3], rotate_angle_s3)
            time.sleep(sleep_time) # Control rotation speed
            if stop_movement: break
        except Exception as e:
            print(f"Error during rotate left: {e}")
            stop()
            break

    print("Rotate left finished.")
    servo_controller.move(SERVO_PWM_PINS[2], 90) # Stop servos
    servo_controller.move(SERVO_PWM_PINS[3], 90)
    reset_servos()

def rotateright(speed=None, style=None):
    """Performs continuous clockwise rotation using 360 servos."""
    global stop_movement, pwm_buzzer
    print(f"Starting 'rotate right' (Speed: {speed or DEFAULT_SPEED})...")
    buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_TURN_RIGHT) # Play sound
    sleep_time = get_sleep_time(speed)

    # Determine rotation angles for 360 servos
    if speed == 'fast': rot_angle = 180
    elif speed == 'slow': rot_angle = 100
    else: rot_angle = 110

    # Both servos rotate same direction (e.g., > 90 for CW on both, adjust if needed)
    rotate_angle_s2 = rot_angle
    rotate_angle_s3 = rot_angle

    while not stop_movement:
        distance = measure_distance()
        if distance != -1 and distance < DISTANCE_THRESHOLD_CM:
            buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_DANGER)
            print("Object detected! Stopping rotate right!")
            stop()
            break
        try:
            servo_controller.move(SERVO_PWM_PINS[2], rotate_angle_s2)
            servo_controller.move(SERVO_PWM_PINS[3], rotate_angle_s3)
            time.sleep(sleep_time) # Control rotation speed
            if stop_movement: break
        except Exception as e:
            print(f"Error during rotate right: {e}")
            stop()
            break

    print("Rotate right finished.")
    servo_controller.move(SERVO_PWM_PINS[2], 90) # Stop servos
    servo_controller.move(SERVO_PWM_PINS[3], 90)
    reset_servos()

def stepback(speed=None, style=None, times=1):
    """Performs a 'step back' motion."""
    global stop_movement, pwm_buzzer
    print(f"Performing 'step back'...")
    buzzer.play_scared_sound(pwm_buzzer) # Play scared sound

    # Use default speed if not specified
    sleep_time_mod = get_sleep_time(speed) / 0.01 # Get ratio vs normal

    # Note: 'times' parameter isn't used effectively in the original logic for continuous
    #       We'll perform the sequence once as requested.
    try:
        for _ in range(int(times)): # Loop for specified times (default 1)
            if stop_movement: break

            # Distance check (optional here, but good practice)
            distance = measure_distance()
            if distance != -1 and distance < DISTANCE_THRESHOLD_CM:
                print("Object detected during step back!")
                buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_DANGER)
                stop()
                break

            # --- Step 1 (Left foot back) ---
            servo_controller.move(SERVO_PWM_PINS[1], 125) # Lift left leg
            time.sleep(0.2 * sleep_time_mod)
            # Feet rotate backward
            servo_controller.move(SERVO_PWM_PINS[2], 100)
            servo_controller.move(SERVO_PWM_PINS[3], 80)
            time.sleep(0.5 * sleep_time_mod)
            servo_controller.move(SERVO_PWM_PINS[2], 90)
            servo_controller.move(SERVO_PWM_PINS[3], 90)
            servo_controller.move(SERVO_PWM_PINS[1], SERVO_RESET_ANGLES.get(1,90)) # Put left leg down
            time.sleep(0.2 * sleep_time_mod)
            if stop_movement: break

            # --- Step 2 (Right foot back) ---
            servo_controller.move(SERVO_PWM_PINS[0], 70) # Lift right leg
            time.sleep(0.2 * sleep_time_mod)
            # Feet rotate backward
            servo_controller.move(SERVO_PWM_PINS[2], 100)
            servo_controller.move(SERVO_PWM_PINS[3], 80)
            time.sleep(0.5 * sleep_time_mod)
            servo_controller.move(SERVO_PWM_PINS[2], 90)
            servo_controller.move(SERVO_PWM_PINS[3], 90)
            servo_controller.move(SERVO_PWM_PINS[0], SERVO_RESET_ANGLES.get(0,90)) # Put right leg down
            time.sleep(0.2 * sleep_time_mod)
            if stop_movement: break

    except Exception as e:
        print(f"Error during step back: {e}")
    finally:
        # Don't reset immediately if it was a single step
        if not stop_movement: # Only reset if not stopped by another command
             time.sleep(0.5) # Pause before potential reset
        reset_servos() # Reset after the steps are done or if stopped
        print("Step back action finished.")


def runback(speed=None, style=None):
    """Performs the continuous running backward motion (360 servos)."""
    global stop_movement, pwm_buzzer
    print(f"Starting 'run back' (Speed: {speed or DEFAULT_SPEED})...")
    # Consider adding a specific sound for running back?
    sleep_time = get_sleep_time(speed)

    # Set legs to running stance (might need adjustment for backward)
    servo_controller.move(SERVO_PWM_PINS[0], 15)
    servo_controller.move(SERVO_PWM_PINS[1], 180)
    time.sleep(0.5)

    # Determine rotation angles for backward run
    if speed == 'fast':
        cw_angle = 180  # Max speed backward for servo 2
        ccw_angle = 0   # Max speed backward for servo 3
    elif speed == 'slow':
        cw_angle = 100
        ccw_angle = 80
    else: # normal
        cw_angle = 110
        ccw_angle = 70

    # Assuming servo 2 needs > 90 for CCW (backward), servo 3 needs < 90 for CCW (backward)
    run_back_angle_s2 = cw_angle
    run_back_angle_s3 = ccw_angle

    while not stop_movement:
        distance = measure_distance()
        # Note: Distance check might be less relevant when moving backward
        # if distance != -1 and distance < DISTANCE_THRESHOLD_CM:
        #     buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_DANGER)
        #     print("Object detected! Stopping run back!")
        #     stop()
        #     break

        try:
            servo_controller.move(SERVO_PWM_PINS[2], run_back_angle_s2) # Rotate backward
            servo_controller.move(SERVO_PWM_PINS[3], run_back_angle_s3) # Rotate backward
            time.sleep(sleep_time)
            if stop_movement: break

        except Exception as e:
            print(f"Error during run back cycle: {e}")
            stop()
            break

    print("Run back movement finished.")
    servo_controller.move(SERVO_PWM_PINS[2], 90) # Stop servos
    servo_controller.move(SERVO_PWM_PINS[3], 90)
    reset_servos()

def stop():
    """Stops ongoing continuous movements and resets servos."""
    global stop_movement
    if not stop_movement: # Only print and reset if not already stopped
        print("Stopping movement...")
        stop_movement = True
        # Give threads a moment to recognize the flag
        time.sleep(0.1)
        reset_servos()
        print("Movement stopped and servos reset.")
    # else:
    #     print("Already stopped.") # Optional debug

def rest():
    """Moves servos to a predefined 'rest' position."""
    print("Moving to 'rest' position...")
    reset_servos() # Start from known position
    try:
        for i, pwm_pin in enumerate(SERVO_PWM_PINS):
            angle = SERVO_REST_ANGLES.get(i, 90) # Use specific rest angles
            servo_controller.move(pwm_pin, angle)
        time.sleep(1)
        print("'Rest' position set.")
    except Exception as e:
        print(f"Error setting rest position: {e}")

def continuous_movement(movement_func, speed = None, style = None):
    """
    Starts a continuous movement function (like walk, run) in a separate thread.
    Ensures any previous continuous movement is stopped first.
    """
    global stop_movement
    if not stop_movement: # If a movement is already running, stop it first
        stop()
        time.sleep(0.6) # Allow time for servos to reset from previous stop

    stop_movement = False # Reset flag for the new movement
    print(f"Starting continuous movement: {movement_func.__name__}")
    thread = threading.Thread(target=movement_func, args=(speed, style,), daemon=True) # Use daemon thread
    thread.start()

def cleanup():
    """Cleans up GPIO resources and stops PWM."""
    global pwm_buzzer
    print("Cleaning up resources...")
    if pwm_buzzer:
        pwm_buzzer.stop()
    buzzer.cleanup() # Cleanup buzzer specific GPIO if needed
    GPIO.cleanup()   # Cleanup general GPIO
    print("Resources cleaned up.")

# --- Main Execution Logic ---
if __name__ == "__main__":
    try:
        initialize_hardware()
        initialize_gemini()

        # --- Define Command Map ---
        # Maps lowercase command keywords to functions
        COMMAND_MAP = {
            "hello": hello,
            "walk": lambda speed=None, style=None: continuous_movement(walk, speed, style),
            "run": lambda speed=None, style=None: continuous_movement(run, speed, style),
            "turn left": lambda speed=None, style=None: turnleft(speed, style),
            "turn right": lambda speed=None, style=None: turnright(speed, style),
            "rotate left": lambda speed=None, style=None: continuous_movement(rotateleft, speed, style),
            "rotate right": lambda speed=None, style=None: continuous_movement(rotateright, speed, style),
            "step back": lambda speed=None, style=None: stepback(speed, style),
            "run back": lambda speed=None, style=None: continuous_movement(runback, speed, style),
            "stop": stop,
            "rest": rest,
            # Add more commands here if needed
        }

        # --- Main Loop ---
        while True:
            # Obstacle check before getting input if a continuous movement might be active
            if not stop_movement:
               distance = measure_distance()
               if distance != -1 and distance < DISTANCE_THRESHOLD_CM:
                  print(f"Obstacle detected ({distance:.1f} cm)! Stopping.")
                  buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_DANGER)
                  stop()
                  time.sleep(1) # Pause after stopping due to obstacle
                  continue # Go back to start of loop, skipping input

            # Get user input
            user_command_raw = input("Enter command (or 'quit'): ")
            user_command = user_command_raw.lower().strip()

            if user_command in ["quit", "exit"]:
                break

            # Always stop previous continuous movement before processing new command
            stop()
            # Reset servos is now implicitly called by stop()

            # --- Command Processing ---
            matched_command_key = None
            extracted_speed = None
            extracted_style = None # Currently not used by movement funcs, but could be

            # 1. Check for exact or partial keyword matches
            for key in COMMAND_MAP:
                if key in user_command:
                    matched_command_key = key
                    # Simple speed extraction (can be enhanced)
                    if "fast" in user_command: extracted_speed = "fast"
                    elif "slow" in user_command: extracted_speed = "slow"
                    # Add style extraction if needed
                    break # Use the first match found

            # 2. Execute command from map or use Gemini
            if matched_command_key:
                command_func = COMMAND_MAP[matched_command_key]
                print(f"Executing command: {matched_command_key} (Speed: {extracted_speed or 'normal'})")
                # Call the function, passing extracted modifiers if relevant
                # Note: Only continuous_movement currently uses speed directly this way
                if matched_command_key in ["walk", "run", "rotate left", "rotate right", "run back"]:
                     command_func(speed=extracted_speed, style=extracted_style)
                elif matched_command_key in ["turn left", "turn right", "step back"]:
                     # These take one step, speed modifier affects step duration/pauses
                     command_func(speed=extracted_speed, style=extracted_style)
                else:
                    command_func() # Call functions like hello, stop, rest without args
            else:
                # 3. If no keyword match, try Gemini for specific angles
                print("Command not recognized directly, querying Gemini...")
                command_details = get_gemini_command_details(user_command_raw)

                if command_details and command_details["angles"]:
                    angles = command_details["angles"]
                    # Currently, we don't adjust speed/style for direct angle commands
                    # but you could add logic here if desired.
                    print(f"Setting specific angles from Gemini: {angles}")
                    try:
                        for i, pwm_pin in enumerate(SERVO_PWM_PINS):
                             angle = angles.get(f"servo{i}", 90) # Use default if missing
                             servo_controller.move(pwm_pin, angle)
                        print(f"Direct angle command sent!")
                    except Exception as e:
                        print(f"Error setting direct angles: {e}")
                else:
                    print("Invalid command or Gemini failed to parse.")

    except KeyboardInterrupt:
        print("\nProgram stopped by user (Ctrl+C).")
        # Play sleepy sound BEFORE final cleanup
        try:
             if pwm_buzzer:
                  buzzer.play_sequence(pwm_buzzer, buzzer.SOUND_SLEEPY)
                  time.sleep(1) # Allow sound to finish
        except Exception as e:
             print(f"Error playing exit sound: {e}")


    except Exception as e:
        # Catch other potential errors during main loop
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc() # Print detailed error information

    finally:
        # --- Final Cleanup ---
        # This block executes whether the program exits normally,
        # via KeyboardInterrupt, or due to an unhandled exception.
        print("\n--- Initiating Final Cleanup ---")
        stop() # Ensure all movement threads are signaled to stop & servos reset
        time.sleep(0.6) # Give threads a moment
        if pwm_buzzer:
            pwm_buzzer.stop()
        cleanup() # General GPIO cleanup
        print("---------------------------------")
        print("          Program Ended          ")
        print("---------------------------------")