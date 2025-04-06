
## Configuration

1.  **Google Gemini API Key:**
    *   Open the `ninja_core.py` file.
    *   Find the line `GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"`
    *   Replace `"YOUR_GOOGLE_API_KEY"` with your actual API key obtained from Google AI Studio.
    *   *(Alternatively, you can remove the key and set up Google Cloud Application Default Credentials (ADC) on your Pi, but using the API key is simpler for this project).*

2.  **Hardware Pins & Parameters (Optional):**
    *   **Distance Sensor Pins:** Defined in `Ninja_Distance.py` (`TRIG_PIN = 21`, `ECHO_PIN = 22`). Change if you use different GPIO pins.
    *   **Buzzer Pin:** Defined in `Ninja_Buzzer.py` (`BUZZER_PIN = 23`). Change if you use a different GPIO pin.
    *   **Obstacle Threshold:** Defined in `ninja_core.py` (`DISTANCE_THRESHOLD_CM = 5.0`). Adjust the distance (in cm) at which the robot stops.
    *   **I2C Address/Bus:** The HAT address (`0x10`) and I2C bus (`1`) are set in `Ninja_Movements_v1.py` within `init_board_and_servo()`. Change only if your HAT is configured differently.

## Hardware Connections (Example)

*   **HAT:** Mount the DFRobot Expansion HAT securely onto the Raspberry Pi's GPIO header.
*   **Servos:** Connect the 4 servos to the PWM channels labeled `PWM0` through `PWM3` on the HAT. Ensure correct polarity (+, -, Signal).
*   **Ultrasonic Sensor (HC-SR04):**
    *   `VCC` -> HAT `5V` pin
    *   `GND` -> HAT `GND` pin
    *   `Trig` -> HAT GPIO pin corresponding to BCM `21` (Check HAT pinout diagram)
    *   `Echo` -> HAT GPIO pin corresponding to BCM `22` (Check HAT pinout diagram)
*   **Active Buzzer:**
    *   `VCC` or `+` -> HAT `3.3V` or `5V` pin (check buzzer requirements)
    *   `GND` or `-` -> HAT `GND` pin
    *   `I/O` or `Signal` -> HAT GPIO pin corresponding to BCM `23` (Check HAT pinout diagram)

*   **Refer to the DFRobot Expansion HAT documentation for the exact pin mapping between HAT labels and BCM numbers.**

## Running the Robot

1.  **Connect to Pi:** Ensure your Raspberry Pi is powered on and connected to your local Wi-Fi network. Connect via SSH or use a terminal directly on the Pi.
2.  **Navigate to Code Directory:** Open a terminal and change to the directory where you saved all the project files.
    ```bash
    cd /path/to/your/robot/code
    ```
3.  **Run the Web Interface:** Execute the Flask application script:
    ```bash
    python web_interface.py
    ```
4.  **Note the IP Address:** The script will attempt to print the Pi's IP address. Look for lines like:
    ```
    *** Your Pi's Likely IP Address: 192.168.1.XXX ***
    *** Open http://192.168.1.XXX:5000 in your browser ***
    ```
    If it fails to detect, use `hostname -I` in another terminal window to find the IP address manually.

## Using the Web Interface

1.  **Open Browser:** On another device (computer, tablet, phone) connected to the *same Wi-Fi network* as the Raspberry Pi.
2.  **Navigate:** Open a web browser (Chrome or Edge recommended for best Web Speech API support) and go to `http://<YOUR_PI_IP_ADDRESS>:5000` (replace `<YOUR_PI_IP_ADDRESS>` with the address noted in the previous step).
3.  **Interface:**
    *   **Text Command:** Type a command (e.g., "walk forward", "say hello", "turn right", "stop") into the text box and click "Send Text".
    *   **Voice Command:**
        *   Click the "Record Command" button. Your browser may ask for microphone permission the first time – allow it.
        *   Speak your command clearly.
        *   Click the button again ("Listening...") to stop recording.
        *   The browser will transcribe the audio (using Web Speech API) and send the text to the robot.
    *   **STOP Button:** Click the red "STOP ROBOT" button for an immediate stop command.
    *   **Status Area:** Observe the status messages, last command, and AI interpretation displayed on the page.

## Customization

*   **Servo Angles:** Adjust the default angles for standing (`reset_servos`) and resting (`rest`) in `ninja_core.py` to match your robot's build. Fine-tune angles within movement functions (`walk`, `run`, etc.) in `Ninja_Movements_v1.py`.
*   **Sounds:** Modify or add sound sequences in `Ninja_Buzzer.py`. Define new note frequencies or change the `SOUND_MAP`. Remember to update the Gemini prompt in `ninja_core.py` if you add new sound keywords.
*   **Gemini Prompt:** Edit the `prompt` string within the `get_gemini_interpretation` function in `ninja_core.py` to change how Gemini interprets commands or add information about new capabilities.
*   **Movement Logic:** Modify the step sequences and timings in `Ninja_Movements_v1.py` to change how the robot walks, turns, or runs.

## Troubleshooting / Important Notes

*   **Microphone Access (HTTPS):** Browsers often require a secure connection (HTTPS) to allow microphone access when accessing a site via an IP address (not `localhost`). If voice input doesn't work:
    *   Try accessing via `http://<PI_HOSTNAME>.local:5000` if your network supports mDNS/Bonjour.
    *   *For testing only:* Use browser flags to allow insecure origins (e.g., `chrome://flags/#unsafely-treat-insecure-origin-as-secure` in Chrome – **this is insecure**).
    *   The proper solution involves setting up HTTPS on Flask, which is more complex (e.g., using `ssl_context` in `app.run` with certificates or using a reverse proxy like Nginx).
*   **Network:** Ensure the Pi and the controlling device are on the *same* Wi-Fi network. Firewalls could potentially block access to port 5000.
*   **Performance:** The Raspberry Pi Zero is not very powerful. Complex Gemini interactions or rapid commands might be slow.
*   **API Costs:** While Google Gemini has a generous free tier, be mindful of potential costs if usage becomes very high. Check Google's pricing.
*   **Debugging:** Check the output in the Flask terminal window on the Raspberry Pi for detailed logs and error messages. Use your browser's developer console (F12) to check for JavaScript errors or network issues related to the Web Speech API or `fetch` calls.
*   **Power:** Ensure your power supply can handle the Pi, HAT, and **all four servos moving simultaneously**, especially during complex actions or startup. Insufficient power can cause instability or reboots.

