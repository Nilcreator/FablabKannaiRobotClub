# Ninja Gemini Robot Control System

## 1. Overview

This Python script (`Ninja_Gemini_Movement_Optimized.py`) controls a four-servo robot built using a Raspberry Pi Zero, a DFRobot IO Expansion HAT, an ultrasonic distance sensor, and a buzzer.

The robot can perform various predefined movements (like walking, running, turning, waving hello) and can also move its servos to specific angles based on natural language text commands entered by the user. The Google Gemini Pro AI model is used to interpret these text commands.

Additionally, the robot uses the ultrasonic sensor to detect nearby obstacles and automatically stops certain movements (like walking or running) if an object gets too close (within 5 cm). Sound feedback is provided using the buzzer for various actions and events.

## 2. Key Features

-   Text-Based Control: Accepts plain English commands.
-   Gemini AI Integration: Uses Google's Gemini Pro model to understand commands, extract servo angles, and movement modifiers (speed).
-   Predefined Movements: Includes functions for `walk`, `run`, `turn left`, `turn right`, `rotate left`, `rotate right`, `step back`, `run back`, `hello`, `rest`, and `stop`.
-   Speed Modification: Allows "fast" or "slow" commands for continuous movements.
-   Ultrasonic Distance Sensing: Measures distances using an HC-SR04 sensor.
-   Obstacle Avoidance: Automatically stops forward continuous movements if an object is detected within 5 cm and plays a "danger" sound.
-   Sound Feedback: Uses a buzzer (`Ninja_Buzzer.py`) for startup, shutdown, movements, obstacle detection, etc.
-   Servo Control: Manages four servos connected via the DFRobot HAT.
-   Threading: Runs continuous movements in background threads to keep the command input responsive.
-   Robust Cleanup: Ensures GPIO resources are released properly on exit.

## 3. Hardware Requirements

-   Raspberry Pi Zero (or Zero W recommended)
-   DFRobot IO Expansion HAT for Raspberry Pi Zero
-   4 x Servos (Mix of 180/360-degree as needed for movement functions)
-   HC-SR04 Ultrasonic Distance Sensor
-   Active Buzzer
-   External 5V Power Supply: ESSENTIAL for servos (separate supply recommended). Ensure grounds are connected.
-   Jumper Wires
-   MicroSD Card (8GB+) with Raspberry Pi OS (Lite recommended)

## 4. Software Setup

-   Python 3
-   Required Libraries:
    -   `google-generativeai`: Install via `pip install google-generativeai`
    -   `RPi.GPIO`: Install via `pip install RPi.GPIO` (May require `sudo apt install python3-rpi.gpio`)
    -   `DFRobot_RaspberryPi_Expansion_Board`: Install according to DFRobot's instructions (often involves running `sudo python setup.py install` within their library directory). Ensure it's accessible from your script's location.
    -   `Ninja_Buzzer.py`: Must be in the same directory as `Ninja_Gemini_Movement_Optimized.py`.
-   Google Cloud Setup:
    -   Google Cloud project with Vertex AI API enabled.
    -   Authentication: Configure either:
        -   API Key: Set the `GOOGLE_API_KEY` variable within the script. (Keep your key secure!)
        -   ADC (Recommended): Run `gcloud auth application-default login` on the Pi Zero and ensure the correct project is selected. (You might need to install `gcloud` first).

## 5. How it Works (Core Logic)

1.  Initialization (`if __name__ == "__main__":`):
    -   Sets the GPIO mode (`GPIO.BCM`).
    -   Calls `initialize_hardware()`:
        -   Sets up GPIO pins for Ultrasonic sensor & Buzzer.
        -   Initializes the Buzzer PWM object.
        -   Initializes the DFRobot Board connection (I2C).
        -   Initializes the DFRobot Servo controller.
        -   Resets servos to starting positions.
        -   Plays the "happy" startup sound.
    -   Calls `initialize_gemini()`:
        -   Configures authentication with Google Cloud.
        -   Loads the specified Gemini AI model (`gemini-pro`).
2.  Main Loop (`while True:`):
    -   Obstacle Check: If a continuous movement -might- be running (`not stop_movement`), check distance with `measure_distance()`. If `< 5cm`, play "danger" sound, call `stop()`, and `continue` to the next loop iteration (skipping user input).
    -   Get User Input: Prompt the user for a text command (e.g., "walk fast", "hello", "move servo 0 to 45").
    -   Handle Exit: Check for "quit" or "exit".
    -   Stop Previous Movement: Call `stop()` unconditionally to halt any previous continuous action and reset servos before processing the new command.
    -   Command Processing:
        -   Keyword Matching: Check if the input command contains known keywords (from `COMMAND_MAP`). Extract simple speed modifiers ("fast", "slow").
        -   Execute Mapped Command: If a keyword matches, call the corresponding function (e.g., `hello()`, `continuous_movement(walk, "fast")`).
        -   Gemini Interpretation (Fallback): If no keyword matches, send the raw command to Gemini via `get_gemini_command_details()`.
        -   Parse Gemini Response: Use `extract_command_details_from_json()` to get angles and potentially speed/style from Gemini's JSON-like output.
        -   Execute Direct Angle Command: If valid angles are parsed, move servos directly using `servo_controller.move()`.
        -   Invalid Command: If no keyword matched and Gemini parsing failed, print an error.
    -   Loop: Repeat the cycle.
3.  Cleanup (`finally:` block):
    -   This block always executes when the script ends (normal exit, Ctrl+C, or error).
    -   Calls `stop()` to halt movements and reset servos.
    -   Stops the buzzer PWM.
    -   Calls `buzzer.cleanup()` and `GPIO.cleanup()` to release all hardware resources.
    -   Plays a final sound (currently "thanks", could be changed to a dedicated "sleepy" sound).

## 6. Detailed Function Explanations

-   `initialize_hardware() / initialize_gemini()`: Handles essential setup for hardware components and the AI model.
-   `print_board_status()`: Reports the status of the DFRobot HAT communication.
-   `get_sleep_time(speed)`: Returns a `time.sleep()` duration based on speed modifiers.
-   `measure_distance()`: Calculates distance using the ultrasonic sensor.
-   `get_gemini_command_details(text_command)`: Sends the user's command to Gemini and gets the AI's interpretation.
-   `extract_command_details_from_json(json_string)`: Parses Gemini's JSON-like response for angles and modifiers.
-   `reset_servos()`: Moves servos to predefined default standing angles.
-   Movement Functions (`hello`, `walk`, `run`, etc.): Contain the logic for specific robot actions, including servo movements, delays, sound triggers, and obstacle checks (for continuous movements).
-   `stop()`: Halts continuous movements and calls `reset_servos()`.
-   `continuous_movement(movement_func, speed, style)`: Starts long-running actions like `walk` or `run` in a separate thread.
-   `cleanup()`: Releases GPIO resources safely.

## 7. Command Examples

-   `hello` - Performs the wave/hello sequence + sound.
-   `walk` - Starts walking forward (normal speed).
-   `walk fast` - Starts walking forward quickly.
-   `run slow` - Starts running forward slowly + exciting sound.
-   `turn left` - Performs a single left turn + sound.
-   `rotate right fast` - Starts rotating clockwise quickly + sound.
-   `step back` - Performs a single step backward sequence + scared sound.
-   `move servo 1 to 120` - Moves servo 1 (PWM1) to 120 degrees.
-   `set servo 0 to 30 degrees and servo 3 to 150 degrees` - Moves specific servos.
-   `stop` - Halts continuous movement and resets servos.
-   `rest` - Moves servos to predefined rest positions.
-   `quit` or `exit` - Stops the program + final sound.

## 8. Important Notes & Configuration

-   API Key: SECURE YOUR KEY. Set `GOOGLE_API_KEY` or use ADC.
-   Pin Numbers: CRITICAL: Verify `TRIG_PIN`, `ECHO_PIN`, `BUZZER_PIN` match your physical wiring to the HAT's GPIOs.
-   Servo PWM Pins: Assumes servos 0-3 map to HAT PWM outputs 0-3.
-   External Power: ESSENTIAL: Use a separate 5V supply for servos. Connect grounds!
-   Library Paths: Ensure `DFRobot_...` library is installed correctly and `Ninja_Buzzer.py` is in the same directory.
-   Servo Calibration: Fine-tune angles, reset/rest positions, and especially the speed control values for 360-degree servos in the movement functions. `servo.move(90)` is typically stop for 360 servos.
-   Resource Limits: The Pi Zero is limited. Expect potential slowness.

## 9. Basic Troubleshooting

-   No Movement: Check wiring (power, ground, signal), code pin numbers, external servo power, DFRobot board status (`i2cdetect -y 1`). Check GPIO permissions if using `RPi.GPIO` directly was needed previously (less likely with DFRobot lib).
-   Buzzer Not Working: Check wiring, `BUZZER_PIN`, `Ninja_Buzzer.py`.
-   Ultrasonic Issues: Check wiring, `TRIG_PIN`/`ECHO_PIN`. Ensure clear line of sight.
-   Gemini Errors: Check API Key/ADC, internet, Vertex AI API enabled status. Read Gemini error messages.
-   `ImportError`: Check DFRobot library installation and `Ninja_Buzzer.py` location.
-   General Errors: Read Python error messages. Add `print()` statements to debug.