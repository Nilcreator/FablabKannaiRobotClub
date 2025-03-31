Ninja Gemini Robot Control

1. Overview
  This Python script (Ninja_Gemini_Movement_Optimized.py) controls a four-servo robot built using a Raspberry Pi Zero, a DFRobot IO Expansion HAT, an ultrasonic distance sensor, and a buzzer.
  The robot can perform various predefined movements (like walking, running, turning, waving hello) and can also move its servos to specific angles based on natural language text commands entered by the user. The Google Gemini Pro AI model is used to interpret these text commands.
  Additionally, the robot uses the ultrasonic sensor to detect nearby obstacles and automatically stops certain movements (like walking or running) if an object gets too close. Sound feedback is provided using the buzzer for various actions and events.

2. Key Features
  Text-Based Control: Accepts plain English commands to control the robot.
  Gemini AI Integration: Uses Google's Gemini Pro model to understand user commands and extract desired servo angles and movement modifiers (like speed).
  Predefined Movements: Includes functions for specific actions like walk, run, turn left, turn right, rotate left, rotate right, step back, run back, hello, rest, and stop.
  Speed Modification: Allows specifying "fast" or "slow" for continuous movements like walk and run.
  Ultrasonic Distance Sensing: Uses an HC-SR04 sensor to measure distances.
  Obstacle Avoidance: Automatically stops forward continuous movements (walk, run, etc.) if an object is detected within a predefined threshold (5 cm).
  Sound Feedback: Uses a buzzer (controlled by Ninja_Buzzer.py) to provide audible cues for startup, shutdown, specific movements (hello, turns), obstacle detection (danger), and other events (exciting run, scared step back).
  Servo Control: Manages four servos connected to the DFRobot HAT's PWM outputs. Includes functions to reset servos to a default position.
  Threading for Continuous Movements: Runs continuous actions like walk and run in separate threads so the main program can still accept commands like "stop".
  Robust Cleanup: Ensures GPIO resources are properly released when the program stops, even if an error occurs.

3. Hardware Requirements
  - Raspberry Pi Zero (or Zero W)
  - DFRobot IO Expansion HAT for Raspberry Pi Zero
  - 4 x Servos (Mix of 180-degree and 360-degree as specified in the code's movement logic)
  - HC-SR04 Ultrasonic Distance Sensor
  - Active Buzzer
  - External 5V Power Supply (Separate for servos is highly recommended)
  - Jumper Wires
  - MicroSD Card with Raspberry Pi OS

4. Software Setup
  - Python 3: The script is written for Python 3.
  - Required Libraries:
    google-generativeai: For interacting with the Gemini API.
    RPi.GPIO: For controlling the ultrasonic sensor and potentially the buzzer.
    DFRobot_RaspberryPi_Expansion_Board: The specific library for the DFRobot HAT (must be installed correctly and accessible).
    Ninja_Buzzer.py: The separate file containing the buzzer sound definitions and control functions (must be in the same directory or accessible via Python's path).
  - Google Cloud Setup:
    A Google Cloud project with the Vertex AI API enabled.
    Authentication configured: Either via an API Key set in the script OR using Application Default Credentials (ADC) by running gcloud auth application-default login on the Pi Zero.

5. How it Works (Core Logic)
  a. Initialization (if __name__ == "__main__":)
  b. Sets up GPIO mode.
  c. Calls initialize_hardware(): Sets up GPIO pins for the sensor, initializes the buzzer PWM, connects to the DFRobot HAT, initializes the servo controller, and resets servos to their starting positions. Plays a "happy" startup sound.
  d. Calls initialize_gemini(): Configures the connection to the Google Gemini API using your credentials and loads the specified AI model.
  e. Main Loop (while True:)
  f. Obstacle Check: Before asking for input, if a continuous movement might be running (not stop_movement), it checks the distance using measure_distance(). If an obstacle is too close (< 5 cm), it plays the "danger" sound, calls stop() to halt movement and reset servos, and skips to the next loop iteration.
  g. Get User Input: Prompts the user to enter a text command.
  h. Stop Previous Movement: Calls stop() to ensure any ongoing continuous movement (from a previous command) is halted and servos are reset before processing the new command.
  i. Command Processing:
    Keyword Matching: It first checks if the user's input contains keywords corresponding to predefined movements (like "walk", "run", "hello", "stop", etc.) defined in the COMMAND_MAP. It also looks for simple speed modifiers ("fast", "slow") if present with these keywords.
  j. Execute Mapped Command: If a keyword is found, it executes the corresponding function from the COMMAND_MAP. For continuous movements, it passes the extracted speed modifier.
  k. Gemini Interpretation: If no predefined command keyword is matched, the script assumes the user wants to set specific servo angles. It sends the user's raw command to Gemini via get_gemini_command_details().
  l. Parse Gemini Response: It attempts to parse the JSON-like response from Gemini using extract_command_details_from_json() to get individual servo angles (and potentially speed/style modifiers, although direct angle setting doesn't use speed/style in this version).
  m. Execute Direct Angle Command: If valid angles are extracted, it moves each servo to the specified position using servo_controller.move().
  n. Invalid Command: If no keyword is matched and Gemini parsing fails, it prints "Invalid command".
  o. Loop: The process repeats, waiting for the next user command.
  p. Cleanup (finally: block)
    This block always runs when the program exits (normally, via Ctrl+C, or due to an error).
    It ensures ongoing movements are stopped (stop()).
    It stops the buzzer PWM.
    It calls the cleanup functions for the buzzer module and RPi.GPIO to release all hardware resources properly.

6. Detailed Function Explanations
  - initialize_hardware() / initialize_gemini(): Set up the necessary connections and objects for hardware and the AI model. Crucial for the script to function.
  - print_board_status(): Provides feedback on the DFRobot HAT's status after operations.
  - get_sleep_time(speed): Calculates the delay used in loops based on the desired speed ("fast", "slow", "normal").
  - measure_distance(): Sends an ultrasonic pulse, listens for the echo, calculates the time difference, and converts it to distance in centimeters. Returns -1 if no echo is detected within the timeout.
  - get_gemini_command_details(text_command): Formats a detailed prompt for Gemini, sends the user's command, and returns Gemini's text response.
  - extract_command_details_from_json(json_string): Parses the JSON-like string from Gemini using regular expressions to reliably extract servo angles and speed/style modifiers, handling potential formatting issues and missing values.
  - reset_servos(): Moves all servos to their predefined starting angles (defined in SERVO_RESET_ANGLES).
  - Movement Functions (hello, walk, run, turnleft, turnright, rotateleft, rotateright, stepback, runback, rest): Each of these functions executes a specific sequence of servo_controller.move() commands and time.sleep() delays to create the desired robot action. Continuous movements (walk, run, etc.) run in loops that check the stop_movement flag and perform obstacle checks. They also incorporate sound effects.
  - stop(): Sets the stop_movement flag to True (signaling threads to exit their loops) and calls reset_servos().
  - continuous_movement(movement_func, speed, style): Starts a given movement function (like walk or run) in a background thread. This prevents the main program from freezing while the robot is moving continuously. It also stops any previously running continuous movement.
  - cleanup(): Releases GPIO resources to prevent conflicts or issues when the script finishes or if it crashes.

7. Command Examples
  hello - Robot performs the wave/hello sequence.
  walk - Robot starts walking forward at normal speed.
  walk fast - Robot starts walking forward at a faster speed.
  run slow - Robot starts running forward at a slower speed.
  turn left - Robot performs a single turn to the left.
  rotate right fast - Robot starts rotating clockwise quickly.
  step back - Robot performs a single step backward sequence and plays the "scared" sound.
  move servo 1 to 120 - Moves servo 1 (PWM1) to 120 degrees.
  set servo 0 to 30 degrees and servo 3 to 150 degrees - Moves servo 0 to 30 and servo 3 to 150, others default to 90.
  stop - Halts any ongoing continuous movement and resets servos.
  rest - Moves servos to the predefined rest positions.
  quit or exit - Stops the program.

8. Important Notes & Configuration
  - API Key: Ensure your GOOGLE_API_KEY is correctly set in the script, OR that you have properly configured Application Default Credentials (ADC). Keep your API key secure.
  Pin Numbers: CRITICAL: Double-check and modify the TRIG_PIN, ECHO_PIN, and BUZZER_PIN constants at the top of the script to match exactly where you have connected these components to your DFRobot HAT's GPIO pins. Incorrect pin numbers will cause parts of the script to fail.
  - Servo PWM Pins: The code assumes servos 0, 1, 2, and 3 are connected to the HAT's PWM outputs PWM0, PWM1, PWM2, and PWM3 respectively. The DFRobot library handles the mapping from these indices (0-3) to the actual GPIO pins used by the HAT for hardware PWM.
  - External Power: ESSENTIAL: Servos draw significant current. You must power the servos from a suitable external 5V power supply. Do NOT attempt to power them directly from the Raspberry Pi Zero's 5V pin, as this can damage the Pi. Ensure the ground of the external supply is connected to the Pi Zero's ground.
  - Library Paths: The sys.path.append(...) line assumes the DFRobot library directory is one level above the directory where you save this script. Adjust this path if your project structure is different. The Ninja_Buzzer.py file must be in the same directory as this script or in a location included in Python's search path.
  - Servo Calibration: The angle ranges and reset/rest positions might need fine-tuning depending on your specific servos and how they are mounted. Pay special attention to the 360-degree servos used in run, rotateleft, rotateright, and runback – the servo.move() values for these likely control speed/direction rather than a specific angle (90 is usually stop, values further from 90 are faster). You may need to experiment to find the best values for clockwise/counter-clockwise rotation at different speeds.
  - Resource Limits: Be mindful that the Raspberry Pi Zero has limited processing power and RAM. Complex movements or very fast loops might strain the system.
