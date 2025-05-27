# Build Your Own Voice-Controlled Ninja Robot (Raspberry Pi & Gemini)

![Robot Concept](https://via.placeholder.com/600x300.png?text=Ninja+Robot+Concept) <!-- Optional: Replace with an image of your robot -->

This tutorial guides you through building and programming a voice-controlled robot based on a Raspberry Pi Zero. It utilizes the DFRobot IO Expansion HAT, various sensors and actuators (servos, I2S microphone, ultrasonic sensor, buzzer), and Google's Gemini AI for natural language processing. The robot can be controlled via a web interface (controller buttons or browser microphone) or by speaking directly to its onboard microphone.

---

## Table of Contents

*   [Part 1: English Tutorial](#part-1-english-tutorial)
    *   [1. Introduction](#1-introduction)
    *   [2. Hardware Requirements](#2-hardware-requirements)
    *   [3. Hardware Assembly](#3-hardware-assembly)
    *   [4. Software Setup on Raspberry Pi](#4-software-setup-on-raspberry-pi)
    *   [5. Code Setup](#5-code-setup)
    *   [6. Configuration](#6-configuration)
    *   [7. Running the Application](#7-running-the-application)
    *   [8. Using the Interface](#8-using-the-interface)
    *   [9. Troubleshooting](#9-troubleshooting)
    *   [10. Stopping the Application](#10-stopping-the-application)
*   [Part 2: Japanese Tutorial (日本語チュートリアル)](#part-2-japanese-tutorial-日本語チュートリアル)
    *   [1. はじめに (Introduction)](#1-はじめに-introduction-jp)
    *   [2. 必要なハードウェア (Hardware Requirements)](#2-必要なハードウェア-hardware-requirements-jp)
    *   [3. ハードウェアの組み立て (Hardware Assembly)](#3-ハードウェアの組み立て-hardware-assembly-jp)
    *   [4. Raspberry Pi のソフトウェアセットアップ (Software Setup on Raspberry Pi)](#4-raspberry-pi-のソフトウェアセットアップ-software-setup-on-raspberry-pi-jp)
    *   [5. コードのセットアップ (Code Setup)](#5-コードのセットアップ-code-setup-jp)
    *   [6. 設定 (Configuration)](#6-設定-configuration-jp)
    *   [7. アプリケーションの実行 (Running the Application)](#7-アプリケーションの実行-running-the-application-jp)
    *   [8. インターフェースの使用方法 (Using the Interface)](#8-インターフェースの使用方法-using-the-interface-jp)
    *   [9. トラブルシューティング (Troubleshooting)](#9-トラブルシューティング-troubleshooting-jp)
    *   [10. アプリケーションの停止 (Stopping the Application)](#10-アプリケーションの停止-stopping-the-application-jp)

---

## Part 1: English Tutorial

### 1. Introduction

This project creates an interactive robot controllable via natural language commands. It integrates movement, sound feedback, basic obstacle detection, and AI-powered command interpretation using Google Gemini. You'll assemble the hardware, set up the Raspberry Pi environment, configure the code, and run a web server to interact with the robot.

### 2. Hardware Requirements

*   **Raspberry Pi Zero:** W or WH model recommended for built-in WiFi/Bluetooth.
*   **Micro SD Card:** 16GB+ recommended (due to swap usage during setup), Class 10, flashed with Raspberry Pi OS.
*   **Power Supply:** Stable 5V, >= 2.5A micro USB power supply. **Crucial for stability during compilation!**
*   **DFRobot IO Expansion HAT for raspberry pi zero:** Compatible with Raspberry Pi Zero GPIO layout.
*   **INMP441 I2S Microphone Module:** For onboard voice input.
*   **HC-SR04 Ultrasonic Distance Sensor:** For obstacle detection.
*   **Active Buzzer Module:** For audio feedback sounds.
*   **SG90 Servos (x4):** Standard hobby servos (or adjust code for different servos).
*   **Robot Chassis/Frame:** Suitable for mounting the components and allowing servo movement.
*   **Jumper Wires:** Assorted Female-to-Female (F/F) and Male-to-Female (M/F).
*   **Computer:** For initial setup and accessing the web UI.
*   **(Optional):** USB Keyboard, Mouse, HDMI Monitor/Adapter for non-headless setup.

### 3. Hardware Assembly

**⚠️ IMPORTANT: Always disconnect the power supply from the Raspberry Pi before connecting or disconnecting any components!**

1.  **Mount HAT:** Carefully align the DFRobot IO Expansion HAT onto the Raspberry Pi Zero's 40-pin GPIO header and press down firmly and evenly.
2.  **Connect Servos:**
    *   Connect the 4 servos to the dedicated servo ports on the Expansion HAT (usually marked S0-S3 or similar).
    *   Ensure correct polarity: Signal (usually Yellow/Orange), VCC/+ (Red), GND/- (Brown/Black).
    *   Note which physical servo corresponds to which port number (0-3). The default code assumes:
        *   Servo 0: Right Leg/Hip
        *   Servo 1: Left Leg/Hip
        *   Servo 2: Right Foot/Ankle
        *   Servo 3: Left Foot/Ankle
3.  **Connect I2S Microphone (INMP441):**
    *   Use jumper wires to connect the module to the HAT's GPIO breakout pins (refer to HAT documentation for pin mapping).
    *   `VDD` -> HAT `3.3V`
    *   `GND` -> HAT `GND`
    *   `SCK` -> HAT `GPIO 18` (I2S BCLK)
    *   `WS` -> HAT `GPIO 19` (I2S LRCLK/FS)
    *   `SD` -> HAT `GPIO 20` (I2S DIN / Data Out from Mic)
    *   `L/R` -> HAT `GND` (Selects Left channel for mono processing)
4.  **Connect Ultrasonic Sensor (HC-SR04):**
    *   Connect to the HAT's GPIO breakout pins.
    *   `VCC` -> HAT `5V` (Check sensor datasheet; some may work on 3.3V)
    *   `Trig` -> HAT `GPIO 21`
    *   `Echo` -> HAT `GPIO 22`
    *   `GND` -> HAT `GND`
5.  **Connect Buzzer:**
    *   Connect to the HAT's GPIO breakout pins.
    *   `Signal/IO` -> HAT `GPIO 23`
    *   `VCC/+` -> HAT `3.3V` (or `5V` depending on module)
    *   `GND/-` -> HAT `GND`
6.  **Assemble Robot:** Mount the Pi/HAT assembly, servos, sensor, and buzzer onto your robot chassis. Organize wiring to prevent snags during movement.

### 4. Software Setup on Raspberry Pi

This section involves steps that can take a **very long time** on a Raspberry Pi Zero, especially installing Rust and Python packages. Ensure a stable power supply and be patient.

1.  **Install OS:** Use Raspberry Pi Imager to flash Raspberry Pi OS (Lite or Desktop, **32-bit recommended** for Pi Zero compatibility and performance) onto the SD card. Use the advanced options (⚙️ icon) to pre-configure hostname, enable SSH, set user/password, and configure WiFi.
2.  **First Boot & Connect:** Insert SD card, connect power. Wait a few minutes for the first boot. Connect via SSH from your computer (`ssh your_username@your_pi_hostname.local` or `ssh your_username@<PI_IP_ADDRESS>`).
3.  **System Update & Essential Tools:** Bring the OS and packages up to date and install `curl` (needed for Rust):
    ```bash
    sudo apt update
    sudo apt full-upgrade -y
    sudo apt install -y curl git
    sudo reboot
    ```
    *(Reconnect via SSH after reboot)*
4.  **Enable I2S Interface:**
    *   Edit the boot configuration file:
        ```bash
        sudo nano /boot/firmware/config.txt # For newer Pi OS (Bookworm onwards)
        # If the above file doesn't exist, try:
        # sudo nano /boot/config.txt       # For older Pi OS (Bullseye or earlier)
        ```
    *   Add these lines at the very end:
        ```text
        # Enable I2S audio interface for Microphone
        dtparam=i2s=on
        dtoverlay=googlevoicehat-soundcard
        ```
    *   Save (`Ctrl+X`, `Y`, `Enter`) 
5.  **Enable I2C Interface:**
    *   Using “Raspi-config” on Command Line
        ```bash
        sudo raspi-config
        ```
        Interfacing Options > I2C > Yes > OK > Yes
    reboot: `sudo reboot`
    *(Reconnect via SSH after reboot)*

7.  **Install Core System Dependencies:** Install libraries needed for Python and audio processing:
    ```bash
    sudo apt install -y python3-dev python3-pip python3-venv build-essential libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg flac libatlas-base-dev
    ```

8.  **Install/Update Rust Compiler:**
    Some Python libraries (like `pydantic-core`, a dependency for `google-generativeai`) require a Rust compiler. We'll use `rustup` to install the latest version.
    **This step will take a considerable amount of time (30 mins to 1+ hour).**
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    ```
    *   When prompted, choose `1) Proceed with installation (default)`.
    *   After installation, configure your current shell:
        ```bash
        source "$HOME/.cargo/env"
        ```
    *   To make it permanent for future sessions, add it to your `.bashrc`:
        ```bash
        echo 'source "$HOME/.cargo/env"' >> ~/.bashrc
        ```
    *   Verify the installation (close and reopen terminal, or `source ~/.bashrc`):
        ```bash
        rustc --version
        cargo --version
        ```
        You should see version numbers (e.g., `rustc 1.7X.X ...`).

9.  **Configure Swap Space (Crucial for Pi Zero):**
    Compiling some Python packages (especially those with Rust components) is memory-intensive and can fail on the Pi Zero's limited RAM. We'll temporarily increase swap space.
    ```bash
    echo "CONF_SWAPSIZE=1024" | sudo tee /etc/dphys-swapfile # Sets swap to 1GB
    # For 2GB swap, use: echo "CONF_SWAPSIZE=2048" | sudo tee /etc/dphys-swapfile
    sudo dphys-swapfile setup
    sudo dphys-swapfile swapon
    ```
    *   Verify swap (look for total swap around 1G or 2G):
        ```bash
        free -h
        ```

10.  **Create Project Directory & Virtual Environment:**
    ```bash
    mkdir ~/NinjaRobot # Or your preferred project name
    cd ~/NinjaRobot
    python3 -m venv .venv # Create virtual environment named .venv
    source .venv/bin/activate # Activate the environment
    ```
    *(Your terminal prompt should now start with `(.venv)`)*

11.  **Install Python Libraries:**
    With Rust and swap configured, we can now install the Python packages. Install smbus for DFRobot IO Expansion board.
    **This step will also take a very long time (potentially 1-2+ hours) due to compilation on the Pi Zero.** Be patient.
    ```bash
    pip install --upgrade pip
    pip install RPi.GPIO google-generativeai SpeechRecognition gTTS pygame Flask google-cloud-speech
    pip install smbus
    ```
    *   **Note on PyAudio:** If `SpeechRecognition` or `google-cloud-speech` later complains about PyAudio, and the `apt` packages in step 4.5 didn't cover it, you might need to install it explicitly:
        `pip install pyaudio` (ensure system dependencies from 4.5 are installed first).

12. **Revert Swap Space (Optional but Recommended):**
    After the intensive compilation is done, you can revert swap to a smaller default to reduce SD card wear.
    ```bash
    echo "CONF_SWAPSIZE=100" | sudo tee /etc/dphys-swapfile # Sets swap back to 100MB (default)
    sudo dphys-swapfile setup
    sudo dphys-swapfile swapon
    # You might need to reboot for changes to fully apply or if errors occur.
    # sudo reboot
    ```

### 5. Code Setup

1.  **Download/Copy Code Files:** Ensure you are in your project directory (`~/NinjaRobot`). Place the following Python files into this directory:
    *   `Ninja_Movements_v1.py`
    *   `Ninja_Buzzer.py`
    *   `Ninja_Distance.py`
    *   `ninja_core.py`
    *   `Ninja_Voice_Control.py`
    *   `web_interface.py`
    *   `DFRobot_RaspberryPi_Expansion_Board.py` (If you are using the DFRobot RaspberryPi Expansion HAT for Zero, otherwise this might be specific to your HAT or handled by `RPi.GPIO` directly if using PCA9685-based HATs, which would require `adafruit-circuitpython-pca9685` and `adafruit-circuitpython-servokit` instead of direct `RPi.GPIO` for servos on HAT).
        *Assume for this tutorial, `DFRobot_RaspberryPi_Expansion_Board.py` is a custom library provided by DFRobot for their specific HAT to simplify servo/PWM control via RPi.GPIO.*

2.  **Create `templates` Directory:** Inside the project directory (`~/NinjaRobot`):
    ```bash
    mkdir templates
    ```
3.  **Create `index.html`:** Create the file `index.html` inside the `templates` directory. Paste the HTML/CSS/JavaScript code for the web interface into this file.

### 6. Configuration

1.  **Google Gemini API Key:**
    *   Activate your virtual environment if not already active:
        ```bash
        cd ~/NinjaRobot
        source .venv/bin/activate
        ```
    *   Edit the core logic file: `nano ninja_core.py`
    *   Locate the line: `GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"`
    *   Replace `"YOUR_GOOGLE_API_KEY"` with your actual key from Google AI Studio or Google Cloud.
    *   **IMPORTANT:** Keep your API key secure. Do not share it publicly. For production, consider environment variables.
    *   Save the file (`Ctrl+X`, `Y`, `Enter`).
2.  **(Optional) Robot Mic Sensitivity Tuning:**
    *   If the "Robot Mic" mode has trouble hearing you or triggers on noise, edit `Ninja_Voice_Control.py`.
    *   Find `recognizer.energy_threshold = 500`.
    *   Run the script once via the web UI ("Speak to Robot" button) and check the console output for the value printed after "Ambient noise adjustment complete".
    *   Stop the script (`Ctrl+C` in the *Flask server* terminal, then click Stop/Controller/Browser Mic button).
    *   Adjust the `500` value (higher if missing speech, lower if triggering on noise). You might also comment out the `recognizer.adjust_for_ambient_noise(...)` line if manual tuning works better. Save the file.

### 7. Running the Application

1.  **Activate Environment:** Navigate to your project directory and activate the virtual environment:
    ```bash
    cd ~/NinjaRobot
    source .venv/bin/activate
    ```
2.  **Find Pi's IP Address:**
    ```bash
    hostname -I | awk '{print $1}'
    ```
    *(Note the IP address shown, e.g., 192.168.1.XX)*
3.  **Start the Web Server:**
    ```bash
    python3 web_interface.py
    ```
    *(Look for lines indicating it's running on `http://0.0.0.0:5000`)*
4.  **Access Web Interface:** On another device (phone, computer) on the **same WiFi network**, open a web browser and go to:
    `http://<YOUR_PI_IP_ADDRESS>:5000`
    *(Replace `<YOUR_PI_IP_ADDRESS>` with the actual IP)*

### 8. Using the Interface

*   **Initial State:** The interface loads in "Controller" mode.
*   **Controller Mode:** Use the on-screen buttons (D-Pad, Actions △/□/○/×, Speed, Rest) to directly command the robot. This mode stops the "Robot Mic" background script if it was running.
*   **Browser Mic Mode:**
    1.  Click "Browser Mic" button to activate the mode.
    2.  Click "Browser Mic" again (now says "Listening...") to start recognition via your browser. Grant mic permission if needed.
    3.  Speak clearly.
    4.  The recognized text and robot response/action appear in the status area.
    5.  Clicking "Listening..." stops the current recognition.
*   **Robot Mic Mode:**
    1.  Click "Speak to Robot". The button should change to "Robot Mic (ON)". This starts the dedicated voice control script on the Pi.
    2.  The "Robot Mic Dialog" box will display the ongoing conversation log from the script.
    3.  Speak to the robot's physical INMP441 microphone. Use "ninja" as the wake word for commands (e.g., "ninja walk", "ninja tell me a joke"). Ask general questions without the wake word.
    4.  To stop this mode, click "Controller" or "Browser Mic".

### 9. Troubleshooting

*   **Python Errors (`NameError`, `ImportError`):** Ensure all libraries from step 4.9 are installed in the active virtual environment (`.venv`). Check file locations within `~/NinjaRobot`.
*   **`pydantic-core` build error / Rust related:** Ensure Rust was installed correctly (step 4.6) and that swap was active during `pip install` (step 4.7). If it persists, check `rustc --version`. You may need to clean pip's cache (`pip cache purge`) and try installing `pydantic-core` by itself (`pip install pydantic-core`) with more swap.
*   **Out of Memory / SIGKILL:** This is likely due to insufficient swap during compilation. Ensure step 4.7 (Configure Swap Space) was done correctly before `pip install`. Try with even more swap (e.g., 2GB if your SD card allows).
*   **Hardware/Core Init Failures:** Review hardware connections (Step 3). Check `web_interface.py` console output for errors during startup.
*   **"Robot Mic" Fails to Start:** Examine `web_interface.py` console output. Look for errors from `subprocess.Popen` or Python errors from `Ninja_Voice_Control.py` (often audio device issues like incorrect I2S setup). Verify I2S setup (Step 4.4). Use `arecord -l` and `aplay -l` to check if the soundcard is detected.
*   **Voice Recognition Issues:** Check mic connections. Tune sensitivity (Step 6.2 for Robot Mic). Ensure browser mic permission (Browser Mic). Check internet connection (both).
*   **Gemini Errors:** Verify API Key (Step 6.1). Check Google Cloud project status (API enabled?).
*   **Robot Movement Issues:** Verify servo connections (Step 3.2). Check angles in `Ninja_Movements_v1.py`. Ensure adequate power supply. If using a generic PCA9685 servo HAT, ensure the `DFRobot_RaspberryPi_Expansion_Board.py` is appropriate or replaced with Adafruit CircuitPython libraries.
*   **Web Interface Unresponsive:** Ensure Flask server (`web_interface.py`) is running on the Pi. Check Pi's IP address and network connection. Check browser console for JavaScript errors.

### 10. Stopping the Application

*   Go to the terminal running `web_interface.py`.
*   Press `Ctrl+C`.
*   The `atexit` cleanup function should automatically:
    *   Signal the background voice script (if running) to stop.
    *   Call `ninja_core.cleanup_all()` which plays the "thanks" sound, moves to rest, and releases GPIO resources.

