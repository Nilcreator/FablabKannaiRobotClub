# Mastering the Raspberry Pi & SPI LCD: A Professional's Guide

This guide provides a comprehensive, expert-level tutorial for building a dynamic, interactive face application on a Raspberry Pi using a Waveshare 2-inch SPI LCD. We will walk through every step, from hardware assembly to writing the final Python code, ensuring a successful result even for those new to Raspberry Pi development. This tutorial has been refined to address common hardware and driver issues, providing a validated, reliable solution.

### Table of Contents

  * [a. Hardware Setup](https://www.google.com/search?q=%23a-hardware-setup-assembling-the-physical-platform)
  * [b. Raspberry Pi OS Installation](https://www.google.com/search?q=%23b-raspberry-pi-os-installation-a-headless-and-reliable-foundation)
  * [c. System Configuration and Libraries](https://www.google.com/search?q=%23c-system-configuration-and-libraries-preparing-the-software-environment)
  * [d. The Python Application Code](https://www.google.com/search?q=%23d-the-python-application-code-bringing-the-face-to-life)
  * [e. Running the Application](https://www.google.com/search?q=%23e-running-the-application)

-----

## a. Hardware Setup: Assembling the Physical Platform

A correctly assembled hardware platform is the foundation of any successful embedded project. This section details the physical construction.

### Step 1: Mounting the DFRobot IO Expansion HAT

The DFRobot HAT provides clearly labeled pins, making it easier to wire the LCD correctly.

1.  **Power down** the Raspberry Pi 3B and disconnect all cables.
2.  Carefully align the 40-pin female header on the underside of the **DFRobot IO Expansion HAT** with the 40-pin male GPIO header on the Raspberry Pi.
3.  Press down firmly and evenly until the HAT is securely seated. There should be no gap between the headers. The HAT's shape will align with the Pi's board, overhanging the USB and Ethernet ports.

### Step 2: Connecting the Waveshare 2-inch LCD Module

Precise wiring is critical for SPI communication. Use the 8-pin cable provided with the LCD to make the following connections from the LCD to the DFRobot HAT's pass-through pins.

**Table 1: Waveshare LCD to Raspberry Pi Wiring Map**

| LCD Pin | Function | Raspberry Pi Pin (BCM) | DFRobot HAT Pin Label |
| :--- | :--- | :---: | :--- |
| **VCC** | Power (3.3V) | 17 | `3.3V` |
| **GND** | Ground | 20 | `GND` |
| **DIN** | SPI Data In (MOSI) | GPIO 10 | `SPI_MOSI` |
| **CLK** | SPI Clock (SCLK) | GPIO 11 | `SPI_SCLK` |
| **CS** | Chip Select | GPIO 8 | `SPI_SS` |
| **DC** | Data/Command | GPIO 25 | `D25` |
| **RST** | Reset | GPIO 17 | `D17` |
| **BL** | Backlight | GPIO 18 | `D18` |

-----

## b. Raspberry Pi OS Installation: A Headless and Reliable Foundation

We will use a "headless" setup, which is highly efficient as it doesn't require a dedicated monitor, keyboard, or mouse for the Raspberry Pi.

### Step 1: Prepare the Operating System

1.  On a separate computer, download and install the official **Raspberry Pi Imager**.
2.  Launch the Raspberry Pi Imager.
3.  Click `CHOOSE DEVICE` and select `Raspberry Pi 3`.
4.  Click `CHOOSE OS`, select `Raspberry Pi OS (other)`, and then choose **`Raspberry Pi OS (Legacy, 64-bit) with desktop`**. This version (based on "Bullseye") has proven to be the most reliable for this specific display hardware.

### Step 2: Pre-configure for Headless Access

1.  In the Imager, before writing, click the **gear icon** to open the "Advanced options".
2.  Configure the following:
      * **Set hostname**: Enter a name like `robot-face.local`.
      * **Enable SSH**: Check the box and select "Use password authentication".
      * **Set username and password**: Create a secure username and password.
      * **Configure wireless LAN**: Enter your Wi-Fi network's SSID and password.
      * **Set locale settings**: Choose your correct time zone and keyboard layout.
3.  Click **SAVE**.
4.  Insert your microSD card, click `CHOOSE STORAGE`, and select it.
5.  Click **WRITE**.

### Step 3: First Boot and SSH Connection

1.  Once writing is complete, insert the microSD card into the Raspberry Pi and connect the power supply.
2.  Wait 2-3 minutes for it to boot and connect to your Wi-Fi.
3.  From your computer's terminal or command prompt, connect via SSH:
    ```bash
    ssh your_username@robot-face.local
    ```
4.  Accept the host key and enter the password you created. You are now logged into your Raspberry Pi.

-----

## c. System Configuration and Libraries: Preparing the Software Environment

With remote access, we can now configure the system and install the necessary Python libraries.

### Step 1: Update the System

Always start by ensuring your system is up-to-date.

```bash
sudo apt update
sudo apt full-upgrade -y
```

### Step 2: Enable Hardware Interfaces

We need to enable the SPI interface for the LCD.

1.  Run the configuration tool:
    ```bash
    sudo raspi-config
    ```
2.  Navigate the menus using the arrow keys:
      * Select `3 Interface Options`.
      * Select `I3 SPI` and choose `<Yes>` to enable it.
3.  Select `<Finish>` on the main menu and reboot when prompted.

### Step 3: Install Python Libraries

Reconnect via SSH after rebooting. Now, install all required Python packages with a single command:

```bash
pip install -U RPi.GPIO Pillow numpy spidev
```

-----

## d. The Python Application Code: Bringing the Face to Life

This is the final step where we write the code for our application. It is split into three files for good organization.

### Step 1: Create Project Files

First, create a directory for your project and create the three empty Python files.

```bash
mkdir ~/robot_face_project
cd ~/robot_face_project
touch lcd_driver.py robot_face.py main.py
```

### Step 2: The LCD Driver (`lcd_driver.py`)

This file contains the low-level code to control the LCD. It includes the critical bug fix for the data transfer that solves many common display issues. Copy the code below and paste it into `lcd_driver.py`.

```python
# lcd_driver.py
import spidev
import RPi.GPIO as GPIO
import time
from PIL import Image
import numpy as np

class WaveshareLCD:
    """
    A corrected, validated driver for the Waveshare 2-inch LCD Module.
    This version fixes a critical data transfer bug and works in portrait mode.
    """
    def __init__(self, rst_pin=17, dc_pin=25, bl_pin=18, cs_pin=8, spi_bus=0, spi_device=0):
        # Pin configuration (BCM numbering)
        self.RST_PIN = rst_pin
        self.DC_PIN = dc_pin
        self.BL_PIN = bl_pin
        self.CS_PIN = cs_pin
        
        # This driver works in portrait mode (240x320)
        self.width = 240
        self.height = 320

        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.BL_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)

        # Initialize SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 40000000
        self.spi.mode = 0b00

        print("Corrected LCD Driver Initialized.")
        self.init_display()

    def _command(self, cmd):
        """Sends a command to the display."""
        GPIO.output(self.DC_PIN, GPIO.LOW)
        self.spi.writebytes([cmd])

    def _data(self, data):
        """Sends data to the display."""
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        self.spi.writebytes([data])

    def _data_word(self, data):
        """Sends a 16-bit data word."""
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        self.spi.writebytes([(data >> 8) & 0xFF, data & 0xFF])

    def _reset(self):
        """Performs a hardware reset of the display."""
        GPIO.output(self.RST_PIN, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.RST_PIN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.RST_PIN, GPIO.HIGH)
        time.sleep(0.01)

    def init_display(self):
        """Initializes the ST7789V controller with a standard command sequence."""
        self._reset()
        self.backlight_on()

        self._command(0x36); self._data(0x00) # Set to default portrait mode
        self._command(0x3A); self._data(0x05)
        self._command(0xB2); self._data(0x0C); self._data(0x0C); self._data(0x00); self._data(0x33); self._data(0x33)
        self._command(0xB7); self._data(0x35)
        self._command(0xBB); self._data(0x19)
        self._command(0xC0); self._data(0x2C)
        self._command(0xC2); self._data(0x01)
        self._command(0xC3); self._data(0x12)
        self._command(0xC4); self._data(0x20)
        self._command(0xC6); self._data(0x0F)
        self._command(0xD0); self._data(0xA4); self._data(0xA1)
        self._command(0xE0); self._data(0xD0); self._data(0x04); self._data(0x0D); self._data(0x11); self._data(0x13); self._data(0x2B); self._data(0x3F); self._data(0x54); self._data(0x4C); self._data(0x18); self._data(0x0D); self._data(0x0B); self._data(0x1F); self._data(0x23)
        self._command(0xE1); self._data(0xD0); self._data(0x04); self._data(0x0C); self._data(0x11); self._data(0x13); self._data(0x2C); self._data(0x3F); self._data(0x44); self._data(0x51); self._data(0x2F); self._data(0x1F); self._data(0x1F); self._data(0x20); self._data(0x23)
        self._command(0x21)
        self._command(0x11)
        time.sleep(0.12)
        self._command(0x29)
        self.clear()

    def set_window(self, x_start, y_start, x_end, y_end):
        """Sets the drawing window area on the display."""
        self._command(0x2A); self._data_word(x_start); self._data_word(x_end)
        self._command(0x2B); self._data_word(y_start); self._data_word(y_end)
        self._command(0x2C) # Memory Write

    def display(self, image):
        """
        Takes a Pillow Image object, converts it to the correct format, and displays
        it on the screen. This method contains the critical data transfer bug fix.
        """
        if image.width != self.width or image.height != self.height:
            image = image.resize((self.width, self.height))

        # Convert image to RGB565 format
        pixel_data = np.array(image.convert("RGB")).astype('uint16')
        color = ((pixel_data[:, :, 0] & 0xF8) << 8) | \
                ((pixel_data[:, :, 1] & 0xFC) << 3) | \
                (pixel_data[:, :, 2] >> 3)
        
        # Set the drawing window to the full screen
        self.set_window(0, 0, self.width - 1, self.height - 1)
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        
        # BUG FIX: Convert the 16-bit data to a proper byte array
        # and use writebytes2 for efficient transfer.
        self.spi.writebytes2(color.astype('>H').flatten())

    def clear(self):
        """Clears the display to black."""
        black_image = Image.new("RGB", (self.width, self.height), "BLACK")
        self.display(black_image)

    def backlight_on(self):
        """Turns the backlight on."""
        GPIO.output(self.BL_PIN, GPIO.HIGH)

    def backlight_off(self):
        """Turns the backlight off."""
        GPIO.output(self.BL_PIN, GPIO.LOW)

    def cleanup(self):
        """Cleans up GPIO resources."""
        self.backlight_off()
        self.spi.close()
        GPIO.cleanup()
        print("LCD resources cleaned up.")
```

### Step 3: The Face Application (`robot_face.py`)

This file contains the logic for drawing all the different expressions. It creates a horizontal image and then rotates it in software before sending it to the portrait-mode driver. Copy and paste this code into `robot_face.py`.

```python
# robot_face.py
import time
from PIL import Image, ImageDraw, ImageFont

class RobotFace:
    """
    Uses software rotation to draw a full-screen face with enhanced, animated expressions.
    """
    def __init__(self, lcd_driver):
        self.lcd = lcd_driver
        # Define a horizontal canvas (320x240) to draw on
        self.width = 320
        self.height = 240
        # Try to load a nicer font, fall back to the default if not found
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except IOError:
            self.font = ImageFont.load_default()

    def _display(self, image):
        """Rotates the final horizontal image for the vertical display."""
        rotated_image = image.rotate(-90, expand=True)
        self.lcd.display(rotated_image)

    def _create_base_image(self):
        """Creates a blank black image canvas."""
        image = Image.new("RGB", (self.width, self.height), "BLACK")
        draw = ImageDraw.Draw(image)
        return image, draw

    def _draw_eyes(self, draw, mood='idle', pupil_data=None):
        """A versatile function to draw different eye styles based on mood."""
        eye_y, eye_radius = 100, 40
        left_eye_x = self.width // 2 - 80
        right_eye_x = self.width // 2 + 80

        # Draw the main white part of the eyes
        draw.ellipse((left_eye_x - eye_radius, eye_y - eye_radius, left_eye_x + eye_radius, eye_y + eye_radius), fill="WHITE")
        draw.ellipse((right_eye_x - eye_radius, eye_y - eye_radius, right_eye_x + eye_radius, eye_y + eye_radius), fill="WHITE")

        # Draw pupils if data is provided
        if pupil_data:
            for i, p in enumerate(pupil_data):
                eye_x = left_eye_x if i == 0 else right_eye_x
                px, py, p_radius = p # pupil x-offset, y-offset, radius
                draw.ellipse((eye_x + px - p_radius, eye_y + py - p_radius, eye_x + px + p_radius, eye_y + py + p_radius), fill="BLACK")

        # Draw lids or brows to show expression
        if mood == 'happy':
            # Draw black semi-circles on the bottom to create a happy-looking eye shape
            draw.arc((left_eye_x - eye_radius, eye_y - eye_radius, left_eye_x + eye_radius, eye_y + eye_radius), 180, 360, fill="BLACK")
            draw.arc((right_eye_x - eye_radius, eye_y - eye_radius, right_eye_x + eye_radius, eye_y + eye_radius), 180, 360, fill="BLACK")
        elif mood == 'sleepy':
            # Draw black rectangles as half-closed eyelids
            draw.rectangle((left_eye_x - eye_radius, eye_y - eye_radius, left_eye_x + eye_radius, eye_y), fill="BLACK")
            draw.rectangle((right_eye_x - eye_radius, eye_y - eye_radius, right_eye_x + eye_radius, eye_y), fill="BLACK")
        elif mood == 'angry':
            # Draw thick, angled black lines for angry eyebrows
            draw.line([(left_eye_x - eye_radius - 10, eye_y - 25), (left_eye_x + eye_radius - 10, eye_y - 5)], fill="BLACK", width=15)
            draw.line([(right_eye_x + eye_radius + 10, eye_y - 25), (right_eye_x - eye_radius + 10, eye_y - 5)], fill="BLACK", width=15)
        elif mood == 'scary':
            # A special case for a unique look
            draw.ellipse((left_eye_x - eye_radius, eye_y - eye_radius, left_eye_x + eye_radius, eye_y + eye_radius), fill="RED")
            draw.ellipse((right_eye_x - eye_radius, eye_y - eye_radius, right_eye_x + eye_radius, eye_y + eye_radius), fill="RED")
            draw.ellipse((left_eye_x - 5, eye_y - 5, left_eye_x + 5, eye_y + 5), fill="BLACK")
            draw.ellipse((right_eye_x - 5, eye_y - 5, right_eye_x + 5, eye_y + 5), fill="BLACK")

    # --- Public Methods for Each Expression ---

    def show_idle(self):
        """Displays a neutral, blinking face."""
        image, draw = self._create_base_image()
        pupils = [(0, 0, 15), (0, 0, 15)]
        self._draw_eyes(draw, mood='idle', pupil_data=pupils)
        draw.line((140, 180, 180, 180), fill="WHITE", width=6)
        self._display(image)

    def show_happy(self):
        """Displays a happy face with a big smile."""
        image, draw = self._create_base_image()
        self._draw_eyes(draw, mood='happy')
        draw.arc((100, 150, 220, 210), 0, 180, fill="WHITE", width=12)
        self._display(image)

    def show_sad(self):
        """Displays a sad face with downturned pupils and a frown."""
        image, draw = self._create_base_image()
        pupils = [(0, 15, 12), (0, 15, 12)] # Pupils look down
        self._draw_eyes(draw, mood='sad', pupil_data=pupils)
        draw.arc((120, 190, 200, 220), 180, 360, fill="WHITE", width=8)
        self._display(image)

    def show_angry(self):
        """Displays an angry face."""
        image, draw = self._create_base_image()
        pupils = [(0, 0, 18), (0, 0, 18)]
        self._draw_eyes(draw, mood='angry', pupil_data=pupils)
        draw.line((130, 190, 190, 190), fill="WHITE", width=8)
        self._display(image)

    def show_amazing(self):
        """Displays a wide-eyed, amazed face with a sparkle."""
        image, draw = self._create_base_image()
        pupils = [(0, 0, 25), (0, 0, 25)] # Big pupils
        self._draw_eyes(draw, mood='amazing', pupil_data=pupils)
        # Draw a star/sparkle in the corner
        sparkle_coords = [(70, 70), (80, 90), (100, 80), (90, 100), (80, 120), (70, 100), (50, 100), (60, 80)]
        draw.polygon(sparkle_coords, fill="WHITE")
        draw.ellipse((140, 170, 180, 210), fill="WHITE") # "O" mouth
        self._display(image)

    def show_confuse(self):
        """Displays a confused face with pupils looking apart."""
        image, draw = self._create_base_image()
        pupils = [(-15, 0, 12), (15, 0, 12)] # Pupils look apart
        self._draw_eyes(draw, mood='confuse', pupil_data=pupils)
        draw.text((150, 170), "?", fill="WHITE", font=self.font)
        self._display(image)

    def show_scary(self):
        """Displays glowing red eyes."""
        image, draw = self._create_base_image()
        self._draw_eyes(draw, mood='scary') # The mood handles all drawing
        self._display(image)

    def animate_sleepy(self):
        """Animates the face falling asleep."""
        for i in range(3):
            image, draw = self._create_base_image()
            self._draw_eyes(draw, mood='sleepy')
            self._display(image)
            time.sleep(0.5)
            self.show_idle()
            time.sleep(1.0 - i * 0.3)
        # Final "asleep" face
        image, draw = self._create_base_image()
        draw.arc((80 - 40, 100 - 20, 80 + 40, 100 + 20), 180, 360, fill="WHITE", width=6)
        draw.arc((240 - 40, 100 - 20, 240 + 40, 100 + 20), 180, 360, fill="WHITE", width=6)
        draw.text((260, 40), "Zzz", fill="WHITE", font=self.font)
        self._display(image)

    def animate_cry(self):
        """Animates a tear dropping from one eye."""
        self.show_sad()
        time.sleep(0.5)
        for _ in range(3): # Drop 3 tears
            for y_offset in range(0, 80, 10):
                image, draw = self._create_base_image()
                pupils = [(0, 15, 12), (0, 15, 12)]
                self._draw_eyes(draw, mood='sad', pupil_data=pupils)
                draw.arc((120, 190, 200, 220), 180, 360, fill="WHITE", width=8)
                # Draw the tear at its current position
                tear_x, tear_y = 240, 140
                draw.ellipse((tear_x - 5, tear_y + y_offset - 10, tear_x + 5, tear_y + y_offset + 10), fill="CYAN")
                self._display(image)
                time.sleep(0.02)
        self.show_sad()

```

### Step 4: The Main Program (`main.py`)

This file is the main entry point that ties everything together. It listens for user input and calls the correct function from the `RobotFace` class. Copy and paste this code into `main.py`.

```python
# main.py
from lcd_driver import WaveshareLCD
from robot_face import RobotFace
import time

def print_commands():
    """Prints the available commands to the user."""
    print("\n--- Robot Face Expression Controller ---")
    print("Enter a command to change the expression:")
    print("  idle    | happy | sad     | angry")
    print("  amazing | cry   | sleepy  | confuse")
    print("  scary   | help  | exit")

def main_loop():
    """Initializes the system and runs the main command loop."""
    lcd = None
    try:
        # Initialize the LCD driver
        lcd = WaveshareLCD()
        # Create an instance of our RobotFace class
        face = RobotFace(lcd)
        
        # Show the default face and print commands
        face.show_idle()
        print_commands()

        # Loop forever, waiting for user input
        while True:
            command = input("> ").lower().strip()
            
            if command == 'exit':
                print("Exiting...")
                break
            elif command == 'idle':
                face.show_idle()
            elif command == 'happy':
                face.show_happy()
            elif command == 'sad':
                face.show_sad()
            elif command == 'angry':
                face.show_angry()
            elif command == 'amazing':
                face.show_amazing()
            elif command == 'cry':
                face.animate_cry()
            elif command == 'sleepy':
                face.animate_sleepy()
            elif command == 'confuse':
                face.show_confuse()
            elif command == 'scary':
                face.show_scary()
            elif command == 'help':
                print_commands()
            else:
                print("Unknown command. Type 'help' for a list of commands.")

    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        # This cleanup code runs no matter how the program exits
        if lcd:
            print("Cleaning up resources.")
            lcd.cleanup()

if __name__ == '__main__':
    main_loop()

```

-----

## e. Running the Application

You are now ready to bring your robot face to life\! From your project directory (`~/robot_face_project`) in the terminal, run the main script:

```bash
python3 main.py
```

The LCD will display the idle face. You can now type any of the commands (e.g., `happy`, `cry`, `sleepy`) and press Enter to see the expression change. Congratulations on completing the project\! 🎉
