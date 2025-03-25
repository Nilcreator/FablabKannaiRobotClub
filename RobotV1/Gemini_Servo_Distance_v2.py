# -*- coding:utf-8 -*-

'''!
  @file demo_servo.py
  @brief Connect servo to one of pwm channels. All or part servos will sweep from 0 to 180 degrees.
  @n Test Servo: https://www.dfrobot.com/product-255.html
  @note Warning: Servos must connect to pwm channel, otherwise may destory Pi IO
  @n
  @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license     The MIT License (MIT)
  @author      Frank(jiehan.guo@dfrobot.com)
  @version     V1.0
  @date        2019-3-28
  @url https://github.com/DFRobot/DFRobot_RaspberryPi_Expansion_Board
'''
# prompt example
# "Move servo 0 to 45 degrees with fast speed"
# "Set servo 1 to 135 degrees with jerky style"
# "All servos to center"
# "Servo 2 to 90, servo 3 to 180"
# "All the servos to zero" (Expect all the servo to be zero)

import sys
import os
import time
import re  # Import regular expression module
import threading
import RPi.GPIO as GPIO   # Ultrasonic codes require this!

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_IIC as Board
from DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_Servo as Servo

import google.generativeai as genai  # Import Gemini library

board = Board(1, 0x10)  # Select i2c bus 1, set address to 0x10
servo = Servo(board)

# Global flag to stop continuous movements
stop_movement = False

def print_board_status():
    if board.last_operate_status == board.STA_OK:
        print("board status: everything ok")
    elif board.last_operate_status == board.STA_ERR:
        print("board status: unexpected error")
    elif board.last_operate_status == board.STA_ERR_DEVICE_NOT_DETECTED:
        print("board status: device not detected")
    elif board.last_operate_status == board.STA_ERR_PARAMETER:
        print("board status: parameter error")
    elif board.last_operate_status == board.STA_ERR_SOFT_VERSION:
        print("board status: unsupport board framware version")

# Gemini Setup
# API Authentication
# Insert your API key here, else comment it out to use Google application default credentials (ADC)
GOOGLE_API_KEY = "Input your Google API key here!"
if len(GOOGLE_API_KEY) < 5 and "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    print(
        f"Please add your Google Gemini API key in the program, set up Application Default Credentials, or set it as environment variable. \n "
    )
    quit()

# set Google Gemini API key as a system environment variable or add it here
if len(GOOGLE_API_KEY) > 5:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    os.environ[
        "GOOGLE_APPLICATION_CREDENTIALS"
    ] = "/path/to/your/service_account_key.json"  # Comment this if ADC is setup
    genai.configure(transport='rest', location='us-central1')  # Explicitly set region

model = genai.GenerativeModel('gemini-2.0-flash-lite')  # Can change model.

def get_servo_angles(text_command):
    """Uses Gemini Pro to extract servo angles and modifiers from a text command."""
    prompt = f"""
    You are controlling a robot arm with four servos (0, 1, 2, 3). Extract both the desired angle (0-180 degrees) for each servo from the user's text command.

    Return ONLY a JSON-like string object that includes the following:
        - The desired angles for each servo (Keys: servo0, servo1, servo2, servo3). If an angle isn't specified, default to 90.
        - A "speed" modifier (Keys will be fast, slow, normal).
        - A "style" modifier (Keys will be smooth, jerkly, curve).

    Enclose the JSON object with triple backticks.
     *   If the user doesn't specify one of the three modifier, then it will just be a null value.
        It will be defined as:
            "servo0":90,
            "servo1":90,
            "servo2":90,
            "servo3":90,
            "speed":null,
            "style":null

    Example input
    {{"servo0": 45, "servo1": 90, "servo2": 135, "servo3": 90,"speed":fast, "style":smooth}}

    User command: {text_command}
    """
    response = model.generate_content(prompt)
    return response.text

def extract_angles_from_json(json_string):
    """Extracts angles and modifiers from the JSON-like string. Returns a dictionary."""
    try:
        # Remove triple backticks and whitespace
        json_string = json_string.replace('```', '').strip()

        # Use regular expression to find key-value pairs for servos
        servo_matches = re.findall(r'"(servo\d)":\s*(\d+)', json_string)
        angles = {key: int(value) for key, value in servo_matches}

        # Extract speed and style (handle null values)
        speed_match = re.search(r'"speed":\s*"(\w+)"', json_string)
        speed = speed_match.group(1) if speed_match else None

        style_match = re.search(r'"style":\s*"(\w+)"', json_string)
        style = style_match.group(1) if style_match else None

        return {"angles": angles, "speed": speed, "style": style}

    except Exception as e:
        print(f"Error parsing JSON response: {json_string}: {e}")
        return None

def reset_servos():
    """Resets all servos to 90 degrees."""
    servo.move(0, 90)
    servo.move(1, 90)
    servo.move(2, 90)
    servo.move(3, 90)
    time.sleep(0.5)  # Short delay for the servos to reach the position

def shake_hands():
    """Shakes hands by swiping servo 0 from 135 to 180 degrees for 2 times."""
    reset_servos()
    for _ in range(2):
        for angle in range(135, 181):
            servo.move(0, angle)
            time.sleep(0.01)
        for angle in range(180, 134, -1):
            servo.move(0, angle)
            time.sleep(0.01)
    servo.move(0, 90)  # Reset servo 0 to 90 degrees

def walk(speed=None, style=None):
    """Continuously swipes servo 0 and 3 from 115 to 75 and servo 1 and 2 from 75 to 115 degrees until stop."""
    global stop_movement

    # Adjust speed and style based on input modifiers (add more sophisticated logic)
    if speed == 'fast':
        sleep_time = 0.002  # Significantly faster
    elif speed == 'slow':
        sleep_time = 0.015
    else:
        sleep_time = 0.01

    # Further implement other style modifiers or specific ranges from JSON input
    while not stop_movement:
        #Distance check
        distance = measure_distance()
        if distance != -1 and distance < 5:
            print("Object detected! Stopping walk!")
            stop()  # Stop all
            break

        for angle in range(75, 116):
            servo.move(0, 115-angle+75)  # Servo 0: 115 to 75
            servo.move(2, 115-angle+75)  # Servo 3: 115 to 75
            servo.move(1, angle)  # Servo 1: 75 to 115
            servo.move(3, angle)  # Servo 2: 75 to 115
            time.sleep(sleep_time)
            if stop_movement:
                break
        if stop_movement:
            break
        for angle in range(115, 74, -1):
            servo.move(0, 115-angle+75)  # Servo 0: 75 to 115
            servo.move(2, 115-angle+75)  # Servo 3: 75 to 115
            servo.move(1, angle)  # Servo 1: 115 to 75
            servo.move(3, angle)  # Servo 2: 75 to 115
            time.sleep(sleep_time)
            if stop_movement:
                break

def run(speed=None, style=None):
    """Continuously swipes servo 0 and 3 from 135 to 45 and servo 1 and 2 from 45 to 135 degrees until stop.
    Checks for obstacle and stops at the range of 5cm!
    """
    global stop_movement
    #Adjust speed and style based on input modifiers (add more sophisticated logic)
    if speed == 'fast':
        sleep_time = 0.002 #Significantly faster
    elif speed == 'slow':
        sleep_time = 0.015
    else:
        sleep_time = 0.01

    while not stop_movement:
    #Distance check
        distance = measure_distance()
        if distance != -1 and distance < 5:
            print("Object detected! Stopping run!")
            stop()  # Stop all
            break

        for angle in range(45, 136):
            servo.move(0, 135-angle+45)  # Servo 0: 135 to 45
            servo.move(2, 135-angle+45)  # Servo 3: 135 to 45
            servo.move(1, angle)  # Servo 1: 45 to 135
            servo.move(3, angle)  # Servo 2: 45 to 135
            time.sleep(sleep_time)
            if stop_movement:
                break
        if stop_movement:
            break
        for angle in range(135, 44, -1):
            servo.move(0, 135-angle+45)  # Servo 0: 45 to 135
            servo.move(2, 135-angle+45)  # Servo 3: 45 to 135
            servo.move(1, angle)  # Servo 1: 135 to 45
            servo.move(3, angle)  # Servo 2: 45 to 135
            time.sleep(sleep_time)
            if stop_movement:
                break

def backward(speed=None, style=None):
    """Continuously swipes servo 0 and 3 from 75 to 115 and servo 1 and 2 from 115 to 75 degrees until stop."""
    global stop_movement

    # Adjust speed and style based on input modifiers (add more sophisticated logic)
    if speed == 'fast':
        sleep_time = 0.002  #Significantly faster
    elif speed == 'slow':
        sleep_time = 0.015
    else:
        sleep_time = 0.01

    # Further implement other style modifiers or specific ranges from JSON input
    while not stop_movement:
        #Distance check
        distance = measure_distance()
        if distance != -1 and distance < 5:
            print("Object detected! Stopping backward!")
            stop()  # Stop all
            break

        for angle in range(115, 74, -1): #Change range to start 115
            servo.move(0, 115-angle+75)  # Servo 0: 75 to 115
            servo.move(2, 115-angle+75)  # Servo 3: 75 to 115
            servo.move(1, angle)  # Servo 1: 115 to 75
            servo.move(3, angle)  # Servo 2: 115 to 75
            time.sleep(sleep_time)
            if stop_movement:
                break
        if stop_movement:
            break
        for angle in range(75, 116): #Change range to start 75
            servo.move(0, 115-angle+75)  # Servo 0: 75 to 115
            servo.move(2, 115-angle+75)  # Servo 3: 75 to 115
            servo.move(1, angle)  # Servo 1: 115 to 75
            servo.move(3, angle)  # Servo 2: 75 to 115
            time.sleep(sleep_time)
            if stop_movement:
                break

def stop():
    """Stops all movements and resets all servos to 90 degrees."""
    global stop_movement
    stop_movement = True
    reset_servos()

def rest():
    """Moves servo0 and servo3 to 0 degrees, servo1 and servo2 to 180 degrees."""
    reset_servos()
    servo.move(0, 0)
    servo.move(3, 0)
    servo.move(1, 180)
    servo.move(2, 180)
    time.sleep(1)

def continuous_movement(movement_func, speed = None, style = None):
    """Starts a movement function in a separate thread."""
    global stop_movement
    stop_movement = False
    thread = threading.Thread(target=movement_func, args=(speed, style,))
    thread.start()

# Ultrasonic sensor functions
TRIG_PIN = 21  # GPIO pin connected to Trig
ECHO_PIN = 22  # GPIO pin connected to Echo

# Speed of sound in cm/s (at room temperature)
SPEED_OF_SOUND = 34300

def measure_distance():
    """Measures the distance using the ultrasonic sensor."""
    # Set TRIG_PIN as output
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    # Set ECHO_PIN as input
    GPIO.setup(ECHO_PIN, GPIO.IN)

    # Ensure TRIG_PIN is low
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.1)

    # Send a 10us pulse to trigger
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    pulse_start = time.time()
    pulse_end = time.time()

    # Measure echo pulse duration
    maxTime = time.time() + 0.05
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
        if time.time() > maxTime:
            return -1 #No object found

    maxTime = time.time() + 0.05
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
        if time.time() > maxTime:
            return -1 #No object found

    # Calculate distance
    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration * SPEED_OF_SOUND) / 2

    return distance

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering

    while board.begin() != board.STA_OK:  # Board begin and check board status
        print_board_status()
        print("board begin faild")
        time.sleep(2)
    print("board begin success")

    servo.begin()  # servo control begin
    reset_servos()  # Reset all servos to 90 at the beginning

    try:
        while True:
            #Check distance in while loop
            if stop_movement == False:
               distance = measure_distance()
               if distance != -1 and distance < 5:
                  print("Object detected! Stopping all actions! in the check.")
                  stop() #Run stop function and clean-up
                  continue #Skip and loop again, instead of checking input

            user_command = input(
                "Enter servo command (e.g., 'move servo 0 to 45 degrees with fast speed', 'shake hands', 'walk with fast speed', 'move back with slow speed', 'stop', 'rest'): "
            )
            user_command = user_command.lower()

            # Reset servos before each movement command
            stop()
            reset_servos()

            if "shake hands" in user_command:
                shake_hands()
            elif "walk" in user_command:
                if "fast" in user_command:
                    continuous_movement(walk, "fast", 0) #continuous_movement(walk, angles_data["speed"], angles_data["style"])
                elif "slow" in user_command:
                    continuous_movement(walk, "slow", 0)  # continuous_movement(walk, angles_data["speed"], angles_data["style"])
                else:
                    continuous_movement(walk, 0, 0) #Normal speed
            elif "run" in user_command:
                if "fast" in user_command:
                    continuous_movement(run, "fast", 0) #continuous_movement(run,  angles_data["speed"], angles_data["style"])
                elif  "slow" in user_command:
                    continuous_movement(run, "slow", 0)  # continuous_movement(walk, angles_data["speed"], angles_data["style"])
                else:
                    continuous_movement(run,  0, 0) #continuous_movement(run,  angles_data["speed"], angles_data["style"])
            elif "move back" in user_command:
                continuous_movement(backward, 0, 0) #continuous_movement(backward, angles_data["speed"], angles_data["style"])
            elif "stop" in user_command:
                stop()
            elif "rest" in user_command:
                rest()
            else:
                # Get the servo from the text command, using Gemini model
                json_response = get_servo_angles(user_command)

                # Parse the JSON, getting the desired angle for each servo
                angles_data = extract_angles_from_json(json_response)

                if angles_data:
                    angles = angles_data["angles"]
                    # Move each servo to the desired angle, or do nothing if failed.
                    try:
                        servo.move(0, angles.get("servo0", 90))  # pwm0
                        servo.move(1, angles.get("servo1", 90))  # pwm1
                        servo.move(2, angles.get("servo2", 90))  # pwm2
                        servo.move(3, angles.get("servo3", 90))  # pwm3
                        print(f"Command sent! {angles}")
                    except Exception as e:
                        print("Command failed")
                else:
                    print("Invalid command")

    except KeyboardInterrupt:
        print("Program stopped")
        GPIO.cleanup()
        stop()  # Ensure servos are stopped on program exit
        #rest()
