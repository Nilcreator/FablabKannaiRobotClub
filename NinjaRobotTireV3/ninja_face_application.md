Of course. Here is the content optimized for readability in downloadable markdown format.

````markdown
# Building an Advanced SPI LCD Application for Raspberry Pi Zero 2 W

## pi0disp User Guide (Enhanced)

This repository provides Python drivers and example applications for various small displays on the Raspberry Pi Zero 2 W and other Raspberry Pi models. This guide covers hardware setup, software installation, and usage instructions.

---

## Supported Hardware

* **Waveshare 2inch LCD Module:** A 240x320 pixel color LCD based on the ST7789V controller.
* **Generic 2.2inch SPI TFT LCD:** A 176x220 pixel color LCD based on the ILI9225 controller.

---

## Hardware Wiring

Connect your display to the Raspberry Pi's 40-pin GPIO header as shown in the tables below. Both displays operate on 3.3V logic, so no logic level shifters are required.

### Waveshare ST7789V (2") Wiring

| LCD pin | Function              | Raspberry Pin       | DFRobot HAT Pin Label | Ninja HAT Pin Label |
| :------ | :-------------------- | :------------------ | :-------------------- | :------------------ |
| **VCC** | 3.3V Power            | Pin 1 (3.3V)        | 3V3                   | 3V3                 |
| **GND** | Ground                | Pin 6 (GND)         | GND                   | GND                 |
| **DIN** | SPI Data In (MOSI)    | Pin 19 (SPI0\_MOSI) | D10                   | D10                 |
| **CLK** | SPI Clock (SCLK)      | Pin 23 (SPI0\_SCLK) | D11                   | D11                 |
| **CS** | SPI Chip Select       | Pin 24 (SPI0\_CE0\_N) | D8                    | D8                  |
| **DC** | Data/Command Select   | Pin 22 (GPIO 25)    | D25                   | D25                 |
| **RST** | Reset                 | Pin 18 (GPIO 24)    | D24                   | D24                 |
| **BL** | Backlight Control     | Pin 12 (GPIO 18)    | D18                   | D18                 |

### Generic ILI9225 (2.2") Wiring

**Note:** The following pinout matches the control pins (RST, RS/DC, LED/BL) of the ST7789V driver for software compatibility.

| LCD pin | Function            | Raspberry Pin       | DFRobot HAT Pin Label | Ninja HAT Pin Label |
| :------ | :------------------ | :------------------ | :-------------------- | :------------------ |
| **VCC** | 3.3V Power          | Pin 1 (3.3V)        | N/A                   | N/A                 |
| **GND** | Ground              | Pin 9 (GND)         | N/A                   | N/A                 |
| **NC** | Not Connected       | -                   | N/A                   | N/A                 |
| **LED** | Backlight Control   | Pin 38 (GPIO 20)    | N/A                   | N/A                 |
| **CLK** | SPI Clock (SCLK)    | Pin 23 (SPI0\_SCLK) | N/A                   | N/A                 |
| **SDI** | SPI Data In (MOSI)  | Pin 19 (SPI0\_MOSI) | N/A                   | N/A                 |
| **RS** | Register Select (D/C) | Pin 12 (GPIO 18)    | N/A                   | N/A                 |
| **RST** | Reset               | Pin 35 (GPIO 19)    | N/A                   | N/A                 |
| **CS** | SPI Chip Select     | Pin 24 (SPI0\_CE0\_N) | N/A                   | N/A                 |

---

## Software Setup

This guide provides a linear set of instructions that a user can follow to replicate the project on their own Raspberry Pi Zero 2 W. All commands are designed to be copied and pasted directly into the terminal.

### 1. System Prerequisites

It is assumed you are starting with a fresh installation of Raspberry Pi OS (Bookworm, 64-bit Lite is recommended) on your SD card.

* **Update System Packages:**
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```
* **Enable SPI Interface:** The SPI hardware interface is disabled by default. Enable it using the `raspi-config` utility.
    ```bash
    sudo raspi-config
    ```
    Navigate to **3 Interface Options -> I3 SPI**. Select **<Yes>** to enable the SPI interface and reboot when prompted.

### 2. Software Installation

Install `git` and `uv`. `uv` is a modern, fast Python package manager that simplifies project setup.

```bash
sudo apt install git -y
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
source $HOME/.cargo/env
````

**Explanation:** This installs `git` for cloning the repository and `uv` for managing the Python project.

### 3\. Project Setup

  * **Clone the Repository:**
    ```bash
    git clone [https://github.com/ytani01/pi0disp.git](https://github.com/ytani01/pi0disp.git)
    cd pi0disp
    ```
  * **Install Python Dependencies:** Use `uv` to create the virtual environment and install the required packages from the `pyproject.toml` file.
    ```bash
    uv sync
    ```
    **Explanation:** `uv sync` reads the `pyproject.toml` and `uv.lock` files, creates a `.venv` directory, and installs the exact versions of the dependencies, ensuring a reproducible environment.

-----

## Running the Applications

All scripts should be run from the root of the `pi0disp` directory using the `uv run` command.

### test\_text.py

A simple utility to display a line of text. Useful for initial hardware verification.

  * **Usage:**
    `uv run python test_text.py --display <display_type> --text "Your Text"`
  * **Examples:**
    ```bash
    # For the ILI9225 display
    uv run python test_text.py --display ili9225 --text "Hello ILI9225!"

    # For the ST7789V display
    uv run python test_text.py --display st7789v --text "Hello ST7789V!"
    ```

### ninja\_faces.py

This is the main application, displaying an animated character face.

  * **Usage:**
    `uv run python ninja_faces.py --display <display_type> [options]`
  * **Arguments:**
      * `--display <type>`: **(Required)** Specify the display type. Choices: `st7789v`, `ili9225`.
      * `--expression <name>`: **(Optional)** Set the initial expression. Choices: `idle`, `happy`, `sad`, `angry`, `surprised`, `laughing`, etc.
      * `--diag`: **(Optional)** Run a hardware diagnostic pattern instead of the main application.
      * `--font <path>`: **(Optional)** Path to a `.ttf` font file.
  * **Examples:**
    ```bash
    # Run on ILI9225 display
    uv run python ninja_faces.py --display ili9225

    # Run on ST7789V and start with the "happy" expression
    uv run python ninja_faces.py --display st7789v --expression happy
    ```

Once running, you can type an expression name (e.g., `sad`, `angry`, `surprised`) into the terminal and press **Enter** to change the face. Use **Ctrl+C** to exit.

-----

## Performance and Troubleshooting

  * **SPI Speed:** The SPI clock speed is configured within each driver file (`spi.max_speed_hz`). The default values (e.g., 32MHz) are generally stable. If you experience artifacts or a blank screen, especially with long jumper wires, try reducing this value to `16000000` (16MHz) or lower.

  * **Frame Rate:** The Raspberry Pi Zero 2 W is capable of driving these displays at a smooth frame rate for simple animations. The primary bottleneck is the SPI bus transfer speed. The double-buffering technique used in `ninja_faces.py` ensures flicker-free updates.

  * **Problem:** Screen is blank, white, or shows nothing.

      * **Solution:** Double-check your VCC and GND connections. Ensure the SPI interface is enabled via `sudo raspi-config`. Verify that all GPIO pin connections are correct and secure.

  * **Problem:** Colors are wrong or inverted.

      * **Solution:** This may be due to a variation in the LCD panel. Some controllers have a "Color Inversion" command that can be sent during initialization. It could also be an issue with the RGB vs. BGR color order, which is typically set in the Entry Mode or Memory Access Control register.

  * **Problem:** Image is mirrored or rotated incorrectly.

      * **Solution:** The orientation is controlled by the `set_orientation()` method in the driver, which writes to a specific controller register. If the image is mirrored, you may need to adjust the bits corresponding to horizontal or vertical flip within that register's value.

-----

## Complete Source Code

This section provides the complete, copy-paste-ready source code for the new and modified Python files required for this project.

### pyproject.toml

```toml
[project]
name = "pi0disp-enhanced"
version = "1.0.0"
description = "Enhanced drivers and applications for SPI displays on Raspberry Pi."
dependencies = []

[tool.uv]
# This section can be used for uv-specific configurations if needed.
```

### pi0disp/display\_base.py

```python
# pi0disp/display_base.py
import abc

class Display(abc.ABC):
    """Abstract base class for display drivers."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

    @abc.abstractmethod
    def init(self):
        """Initialize the display controller."""
        pass

    @abc.abstractmethod
    def display(self, image):
        """
        Display a Pillow Image object on the screen.
        Args:
            image (PIL.Image.Image): The image to display.
        """
        pass

    @abc.abstractmethod
    def set_backlight(self, state):
        """
        Set the backlight state.
        Args:
            state (bool or int): True/1 for on, False/0 for off.
        """
        pass

    @abc.abstractmethod
    def cleanup(self):
        """Clean up GPIO resources."""
        pass
```

### pi0disp/ili9225.py (Updated)

```python
# pi0disp/ili9225.py
import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image
from .display_base import Display

# Constants for ILI9225 commands
ILI9225_DRIVER_OUTPUT_CTRL = 0x01
ILI9225_LCD_AC_DRIVING_CTRL = 0x02
ILI9225_ENTRY_MODE = 0x03
ILI9225_DISPLAY_CTRL1 = 0x07
ILI9225_BLANK_PERIOD_CTRL1 = 0x08
ILI9225_FRAME_CYCLE_CTRL = 0x0B
ILI9225_INTERFACE_CTRL = 0x0C
ILI9225_OSC_CTRL = 0x0F
ILI9225_POWER_CTRL1 = 0x10
ILI9225_POWER_CTRL2 = 0x11
ILI9225_POWER_CTRL3 = 0x12
ILI9225_POWER_CTRL4 = 0x13
ILI9225_POWER_CTRL5 = 0x14
ILI9225_VCI_RECYCLING = 0x15
ILI9225_RAM_ADDR_SET1 = 0x20
ILI9225_RAM_ADDR_SET2 = 0x21
ILI9225_GRAM_DATA_REG = 0x22
ILI9225_GATE_SCAN_CTRL = 0x30
ILI9225_VERTICAL_SCROLL_CTRL1 = 0x31
ILI9225_VERTICAL_SCROLL_CTRL2 = 0x32
ILI9225_VERTICAL_SCROLL_CTRL3 = 0x33
ILI9225_PARTIAL_DRIVING_POS1 = 0x34
ILI9225_PARTIAL_DRIVING_POS2 = 0x35
ILI9225_HORIZONTAL_WINDOW_ADDR1 = 0x36
ILI9225_HORIZONTAL_WINDOW_ADDR2 = 0x37
ILI9225_VERTICAL_WINDOW_ADDR1 = 0x38
ILI9225_VERTICAL_WINDOW_ADDR2 = 0x39
ILI9225_GAMMA_CTRL1 = 0x50
ILI9225_GAMMA_CTRL2 = 0x51
ILI9225_GAMMA_CTRL3 = 0x52
ILI9225_GAMMA_CTRL4 = 0x53
ILI9225_GAMMA_CTRL5 = 0x54
ILI9225_GAMMA_CTRL6 = 0x55
ILI9225_GAMMA_CTRL7 = 0x56
ILI9225_GAMMA_CTRL8 = 0x57
ILI9225_GAMMA_CTRL9 = 0x58
ILI9225_GAMMA_CTRL10 = 0x59

class ILI9225(Display):
    def __init__(self, rst_pin=19, dc_pin=18, bl_pin=20, cs_pin=8, spi_bus=0, spi_device=0, spi_speed=32000000):
        super().__init__(width=176, height=220)
        self.rst_pin = rst_pin
        self.dc_pin = dc_pin
        self.bl_pin = bl_pin
        self.cs_pin = cs_pin
        self.spi_bus = spi_bus
        self.spi_device = spi_device
        self.spi_speed = spi_speed

    def _command(self, cmd, *args):
        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.writebytes([cmd])
        if args:
            GPIO.output(self.dc_pin, GPIO.HIGH)
            self.spi.writebytes(list(args))

    def _data(self, *args):
        GPIO.output(self.dc_pin, GPIO.HIGH)
        self.spi.writebytes(list(args))

    def _write_register(self, reg, value):
        self._command(reg)
        self._data(value >> 8, value & 0xFF)

    def init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.bl_pin, GPIO.OUT)

        self.spi = spidev.SpiDev()
        self.spi.open(self.spi_bus, self.spi_device)
        self.spi.max_speed_hz = self.spi_speed
        self.spi.mode = 0b00

        # Hardware Reset
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.05)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.1)

        # Initialization Sequence based on datasheet and reference drivers
        self._write_register(ILI9225_POWER_CTRL1, 0x0000)
        self._write_register(ILI9225_POWER_CTRL2, 0x0000)
        self._write_register(ILI9225_POWER_CTRL3, 0x0000)
        self._write_register(ILI9225_POWER_CTRL4, 0x0000)
        self._write_register(ILI9225_POWER_CTRL5, 0x0000)
        time.sleep(0.04)

        self._write_register(ILI9225_POWER_CTRL2, 0x0018)
        self._write_register(ILI9225_POWER_CTRL3, 0x6121)
        self._write_register(ILI9225_POWER_CTRL4, 0x006F)
        self._write_register(ILI9225_POWER_CTRL5, 0x495F)
        self._write_register(ILI9225_POWER_CTRL1, 0x0800)
        time.sleep(0.01)
        self._write_register(ILI9225_POWER_CTRL2, 0x103B)
        time.sleep(0.05)

        self._write_register(ILI9225_DRIVER_OUTPUT_CTRL, 0x011C)
        self._write_register(ILI9225_LCD_AC_DRIVING_CTRL, 0x0100)
        self._write_register(ILI9225_ENTRY_MODE, 0x1030) # BGR=1
        self._write_register(ILI9225_DISPLAY_CTRL1, 0x0000)
        self._write_register(ILI9225_BLANK_PERIOD_CTRL1, 0x0808)
        self._write_register(ILI9225_FRAME_CYCLE_CTRL, 0x1100)
        self._write_register(ILI9225_INTERFACE_CTRL, 0x0000)
        self._write_register(ILI9225_OSC_CTRL, 0x0D01)
        self._write_register(ILI9225_VCI_RECYCLING, 0x0020)
        self._write_register(ILI9225_RAM_ADDR_SET1, 0x0000)
        self._write_register(ILI9225_RAM_ADDR_SET2, 0x0000)

        self._write_register(ILI9225_GATE_SCAN_CTRL, 0x0000)
        self._write_register(ILI9225_VERTICAL_SCROLL_CTRL1, 0x00DB)
        self._write_register(ILI9225_VERTICAL_SCROLL_CTRL2, 0x0000)
        self._write_register(ILI9225_VERTICAL_SCROLL_CTRL3, 0x0000)
        self._write_register(ILI9225_PARTIAL_DRIVING_POS1, 0x00DB)
        self._write_register(ILI9225_PARTIAL_DRIVING_POS2, 0x0000)
        self._write_register(ILI9225_HORIZONTAL_WINDOW_ADDR1, 0x00AF)
        self._write_register(ILI9225_HORIZONTAL_WINDOW_ADDR2, 0x0000)
        self._write_register(ILI9225_VERTICAL_WINDOW_ADDR1, 0x00DB)
        self._write_register(ILI9225_VERTICAL_WINDOW_ADDR2, 0x0000)

        self._write_register(ILI9225_GAMMA_CTRL1, 0x0000)
        self._write_register(ILI9225_GAMMA_CTRL2, 0x0808)
        self._write_register(ILI9225_GAMMA_CTRL3, 0x080A)
        self._write_register(ILI9225_GAMMA_CTRL4, 0x000A)
        self._write_register(ILI9225_GAMMA_CTRL5, 0x0A08)
        self._write_register(ILI9225_GAMMA_CTRL6, 0x0808)
        self._write_register(ILI9225_GAMMA_CTRL7, 0x0000)
        self._write_register(ILI9225_GAMMA_CTRL8, 0x0A00)
        self._write_register(ILI9225_GAMMA_CTRL9, 0x0710)
        self._write_register(ILI9225_GAMMA_CTRL10, 0x0710)

        self._write_register(ILI9225_DISPLAY_CTRL1, 0x0012)
        time.sleep(0.05)
        self._write_register(ILI9225_DISPLAY_CTRL1, 0x1017)

        self.set_orientation(0)
        self.set_backlight(True)

    def set_orientation(self, angle):
        if angle == 0: # Portrait
            self.width, self.height = 176, 220
            self._write_register(ILI9225_ENTRY_MODE, 0x1030)
        elif angle == 90: # Landscape
            self.width, self.height = 220, 176
            self._write_register(ILI9225_ENTRY_MODE, 0x1028)
        elif angle == 180: # Inverted Portrait
            self.width, self.height = 176, 220
            self._write_register(ILI9225_ENTRY_MODE, 0x1000)
        elif angle == 270: # Inverted Landscape
            self.width, self.height = 220, 176
            self._write_register(ILI9225_ENTRY_MODE, 0x1018)
        else:
            raise ValueError("Angle must be 0, 90, 180, or 270.")

    def _set_window(self, x0, y0, x1, y1):
        self._write_register(ILI9225_HORIZONTAL_WINDOW_ADDR1, x1)
        self._write_register(ILI9225_HORIZONTAL_WINDOW_ADDR2, x0)
        self._write_register(ILI9225_VERTICAL_WINDOW_ADDR1, y1)
        self._write_register(ILI9225_VERTICAL_WINDOW_ADDR2, y0)
        self._write_register(ILI9225_RAM_ADDR_SET1, x0)
        self._write_register(ILI9225_RAM_ADDR_SET2, y0)
        self._command(ILI9225_GRAM_DATA_REG)

    def display(self, image):
        if image.width != self.width or image.height != self.height:
            image = image.resize((self.width, self.height))

        pixels = image.load()
        buffer = bytearray(self.width * self.height * 2)
        idx = 0
        for y in range(self.height):
            for x in range(self.width):
                r, g, b = pixels[x, y]
                color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                buffer[idx] = color >> 8
                buffer[idx+1] = color & 0xFF
                idx += 2

        self._set_window(0, 0, self.width - 1, self.height - 1)
        GPIO.output(self.dc_pin, GPIO.HIGH)
        for i in range(0, len(buffer), 4096):
            self.spi.writebytes(buffer[i:i+4096])

    def set_backlight(self, state):
        GPIO.output(self.bl_pin, state)

    def cleanup(self):
        self.set_backlight(False)
        self.spi.close()
        GPIO.cleanup([self.rst_pin, self.dc_pin, self.bl_pin])
```

### test\_text.py (Updated)

```python
# test_text.py
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

def main():
    parser = argparse.ArgumentParser(description="Display text on an LCD.")
    parser.add_argument('--display', type=str, required=True, choices=['st7789v', 'ili9225'], help='Type of display.')
    parser.add_argument('--text', type=str, required=True, help='Text to display.')
    args = parser.parse_args()

    if args.display == 'st7789v':
        from pi0disp.st7789v import ST7789V
        disp = ST7789V()
        disp.set_orientation(90) # Landscape for ST7789V
    elif args.display == 'ili9225':
        from pi0disp.ili9225 import ILI9225
        disp = ILI9225()
        disp.set_orientation(90) # Landscape for ILI9225
    else:
        print(f"Error: Unsupported display type '{args.display}'")
        sys.exit(1)

    try:
        print(f"Initializing {args.display} display...")
        disp.init()
        disp.set_backlight(True)
        print("Display initialized.")

        image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except IOError:
            font = ImageFont.load_default()
            print("Default font loaded.")

        text_bbox = draw.textbbox((0, 0), args.text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (disp.width - text_width) // 2
        y = (disp.height - text_height) // 2

        draw.text((x, y), args.text, font=font, fill="WHITE")

        print(f"Displaying text: '{args.text}'")
        disp.display(image)
        
        import time
        time.sleep(10)

    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        disp.cleanup()
        print("Resources cleaned up.")

if __name__ == "__main__":
    main()
```

### ninja\_faces.py (Updated)

```python
# ninja_faces.py
import sys
import time
import argparse
import random
import threading
from PIL import Image, ImageDraw, ImageFont

# --- Face Rendering Logic ---
class Face:
    def __init__(self, width, height, bg_color="black"):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.eye_color = "white"
        self.mouth_color = "white"
        self.eye_y = int(height * 0.4)
        self.eye_radius = int(height * 0.12)
        self.eye_spacing = int(width * 0.25)
        self.left_eye_x = int(width / 2 - self.eye_spacing)
        self.right_eye_x = int(width / 2 + self.eye_spacing)

    def _draw_eyes_idle(self, draw):
        draw.ellipse((self.left_eye_x - self.eye_radius, self.eye_y - self.eye_radius, self.left_eye_x + self.eye_radius, self.eye_y + self.eye_radius), fill=self.eye_color)
        draw.ellipse((self.right_eye_x - self.eye_radius, self.eye_y - self.eye_radius, self.right_eye_x + self.eye_radius, self.eye_y + self.eye_radius), fill=self.eye_color)

    def _draw_eyes_blink(self, draw):
        draw.line((self.left_eye_x - self.eye_radius, self.eye_y, self.left_eye_x + self.eye_radius, self.eye_y), fill=self.eye_color, width=5)
        draw.line((self.right_eye_x - self.eye_radius, self.eye_y, self.right_eye_x + self.eye_radius, self.eye_y), fill=self.eye_color, width=5)

    def _draw_eyes_happy(self, draw):
        draw.arc((self.left_eye_x - self.eye_radius, self.eye_y - self.eye_radius, self.left_eye_x + self.eye_radius, self.eye_y + self.eye_radius), 180, 0, fill=self.eye_color, width=5)
        draw.arc((self.right_eye_x - self.eye_radius, self.eye_y - self.eye_radius, self.right_eye_x + self.eye_radius, self.eye_y + self.eye_radius), 180, 0, fill=self.eye_color, width=5)

    def _draw_eyes_angry(self, draw):
        draw.line((self.left_eye_x - self.eye_radius, self.eye_y - self.eye_radius, self.left_eye_x + self.eye_radius, self.eye_y), fill=self.eye_color, width=5)
        draw.line((self.right_eye_x + self.eye_radius, self.eye_y - self.eye_radius, self.right_eye_x - self.eye_radius, self.eye_y), fill=self.eye_color, width=5)

    def _draw_mouth_smile(self, draw):
        mouth_y = int(self.height * 0.7)
        mouth_radius = int(self.width * 0.3)
        draw.arc((self.width/2 - mouth_radius, mouth_y - mouth_radius, self.width/2 + mouth_radius, mouth_y + mouth_radius), 0, 180, fill=self.mouth_color, width=5)

    def _draw_mouth_sad(self, draw):
        mouth_y = int(self.height * 0.8)
        mouth_radius = int(self.width * 0.3)
        draw.arc((self.width/2 - mouth_radius, mouth_y - mouth_radius, self.width/2 + mouth_radius, mouth_y + mouth_radius), 180, 360, fill=self.mouth_color, width=5)

    def _draw_mouth_surprised(self, draw):
        mouth_y = int(self.height * 0.75)
        mouth_radius = int(self.height * 0.1)
        draw.ellipse((self.width/2 - mouth_radius, mouth_y - mouth_radius, self.width/2 + mouth_radius, mouth_y + mouth_radius), fill=self.mouth_color)

    def draw_expression(self, draw, expression="idle", blink_state=False):
        draw.rectangle((0, 0, self.width, self.height), fill=self.bg_color)
        
        if blink_state:
            self._draw_eyes_blink(draw)
        else:
            if expression in ["happy", "laughing"]:
                self._draw_eyes_happy(draw)
            elif expression == "angry":
                self._draw_eyes_angry(draw)
            else:
                self._draw_eyes_idle(draw)

        if expression in ["happy", "smile"]:
            self._draw_mouth_smile(draw)
        elif expression == "sad":
            self._draw_mouth_sad(draw)
        elif expression == "surprised":
            self._draw_mouth_surprised(draw)
        elif expression == "laughing":
            mouth_y = int(self.height * 0.7)
            mouth_radius = int(self.width * 0.35)
            draw.arc((self.width/2 - mouth_radius, mouth_y - mouth_radius * 1.2, self.width/2 + mouth_radius, mouth_y + mouth_radius * 1.2), 0, 180, fill=self.mouth_color, width=5)
        elif expression == "angry":
            mouth_y = int(self.height * 0.75)
            draw.line((self.width/2 - 30, mouth_y, self.width/2 + 30, mouth_y + 10), fill=self.mouth_color, width=5)

# --- Diagnostic Drawing ---
def draw_diagnostics(draw, width, height, font):
    draw.rectangle((0, 0, width//3, height//2), fill="red")
    draw.rectangle((width//3, 0, 2*width//3, height//2), fill="green")
    draw.rectangle((2*width//3, 0, width, height//2), fill="blue")
    draw.rectangle((0, 0, width-1, height-1), outline="white")
    draw.text((5, 5), "Top-Left (0,0)", font=font, fill="white")
    draw.text((width-100, height-20), "Bottom-Right", font=font, fill="white")
    draw.text((5, height-20), "Landscape", font=font, fill="white")

# --- Main Application Logic ---
def main():
    parser = argparse.ArgumentParser(description="Animated faces on an LCD.")
    parser.add_argument('--display', type=str, required=True, choices=['st7789v', 'ili9225'], help='Type of display.')
    parser.add_argument('--expression', type=str, default='idle', help='Initial facial expression.')
    parser.add_argument('--diag', action='store_true', help='Run diagnostics pattern.')
    parser.add_argument('--font', type=str, default="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", help='Path to TTF font file.')
    args = parser.parse_args()

    if args.display == 'st7789v':
        from pi0disp.st7789v import ST7789V
        disp = ST7789V()
        disp.set_orientation(90)
    elif args.display == 'ili9225':
        from pi0disp.ili9225 import ILI9225
        disp = ILI9225()
        disp.set_orientation(90)
    else:
        print(f"Error: Unsupported display type '{args.display}'")
        sys.exit(1)

    try:
        print(f"Initializing {args.display} display...")
        disp.init()
        disp.set_backlight(True)
        print("Display initialized.")

        image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        draw = ImageDraw.Draw(image)
        face = Face(disp.width, disp.height)

        try:
            font = ImageFont.truetype(args.font, 12)
        except IOError:
            font = ImageFont.load_default()
            print(f"Warning: Font '{args.font}' not found. Using default font.")

        if args.diag:
            print("Running diagnostics...")
            draw_diagnostics(draw, disp.width, disp.height, font)
            disp.display(image)
            time.sleep(10)
            return

        current_expression = args.expression
        def get_input():
            nonlocal current_expression
            while True:
                try:
                    new_expr = input("Enter expression (e.g., happy, sad, angry): ").strip().lower()
                    current_expression = new_expr
                except (EOFError, KeyboardInterrupt):
                    break
        
        input_thread = threading.Thread(target=get_input, daemon=True)
        input_thread.start()
        
        print("Application running. Type an expression and press Enter. Ctrl+C to exit.")
        
        blink_timer = time.time()
        is_blinking = False
        next_blink_interval = random.uniform(2, 7)

        while True:
            if time.time() - blink_timer > next_blink_interval:
                is_blinking = True
                blink_timer = time.time()
                next_blink_interval = random.uniform(2, 7)
            
            if is_blinking and time.time() - blink_timer > 0.15:
                is_blinking = False

            face.draw_expression(draw, current_expression, blink_state=is_blinking)
            disp.display(image)
            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        disp.cleanup()
        print("Resources cleaned up.")

if __name__ == "__main__":
    main()
```

-----

## Appendix: Detailed Project Analysis

### Part 1: Foundational Analysis and Hardware Integration

This report provides a comprehensive guide to enhancing the `pi0disp` repository for the Raspberry Pi Zero 2 W. The project involves adding support for a new ILI9225-based SPI LCD, modernizing the development workflow with the `uv` package manager, and creating a feature-rich animated application. The final result is a robust, well-documented, and high-performance display solution suitable for advanced hobbyist and embedded systems projects.

#### Section 1.1: Architectural Review of the pi0disp Repository

A thorough analysis of the existing `pi0disp` repository is the first step toward extending its functionality. Understanding its architecture allows for new components to be integrated in a modular and consistent manner, respecting the original design philosophy while introducing significant improvements.

  * **Display Initialization Flow:** The initialization process in the existing drivers follows a standard pattern for embedded displays. It begins with the configuration of GPIO pins for control signals such as Reset (RST), Data/Command (DC), and Backlight (BL). An interface object, either from the `spidev` or `smbus` library, is then instantiated to handle the low-level communication. A hardware reset is performed by toggling the RST pin, which puts the display controller into a known state. Following the reset, a specific sequence of commands and data bytes is transmitted to configure the controller's internal registers. This sequence typically includes commands to exit sleep mode, set the pixel color format, define the memory access orientation, and enable the display output.
  * **Communication Protocols:** The repository effectively utilizes standard Linux interfaces for hardware communication. For SPI displays like the ST7789V, it relies on the `spidev` Python library, which provides a wrapper around the `/dev/spidevX.Y` kernel device. The key function used is `spi.xfer2()`, which facilitates efficient, full-duplex block data transfers. For I²C devices, the `smbus` library is used. Control of non-SPI/I²C pins like DC and RST is managed directly through the `RPi.GPIO` library, using `GPIO.output()` to set their state.
  * **Image Buffer Pipeline:** Graphics rendering is handled through an off-screen buffer methodology using the powerful Python Imaging Library (Pillow). An in-memory image buffer is created with `Image.new('RGB',...)`, matching the resolution of the target display. All drawing operations—such as rendering shapes, text, or pasting other images—are performed on this buffer using the `ImageDraw` module. This approach is computationally efficient as memory operations are significantly faster than repeated hardware bus transactions. Once the frame is fully rendered in the buffer, its raw pixel data is extracted as a byte string using `image.tobytes()` and transmitted to the display in a single, high-speed burst. This forms the core graphics pipeline that will be replicated for the new ILI9225 driver.
  * **Rotation and Orientation:** The existing `st7789v.py` driver manages display rotation by sending a "Memory Access Control" (MADCTL) command to the controller. This command alters how the display's internal Graphics RAM (GRAM) addresses are mapped to the physical screen coordinates, allowing for portrait, landscape, and inverted orientations without requiring software-based pixel manipulation, which would be prohibitively slow. Identifying and implementing the equivalent command for the ILI9225 controller is a critical task for the new driver.

#### Section 1.2: Implementing the ILI9225 Python Driver

The core technical task of this project is the development of a new Python driver module, `ili9225.py`. This module will encapsulate all the low-level logic required to control a 2.2-inch, 176x220 pixel SPI LCD based on the Ilitek ILI9225 controller.

  * **Datasheet and Reference Implementation Analysis:** The primary source of truth for this task is the ILI9225 controller datasheet, which details the command set, register maps, and electrical characteristics. By cross-referencing existing open-source C/C++ and MicroPython drivers for the ILI9225 with the official datasheet, a highly reliable initialization sequence can be constructed.
  * **Driver Implementation Details:** The new `ili9225.py` module is implemented as a Python class, `ILI9225`, adhering to the unified display interface. The initialization sequence translates the complex startup procedure from the datasheet into a precise sequence of SPI transactions. The `Entry Mode` register (R03h) is used to control orientation by altering how the GRAM address counter is updated. A critical step in the `display` method is the conversion of image data from Pillow's 24-bit RGB888 format to the 16-bit RGB565 format native to the ILI9225 controller.

### Part 2: Application Development with Modern Tooling

#### Section 2.1: Establishing a Modern, High-Performance Workflow with uv

The traditional Python development workflow can be fragmented and slow. For this project, a modern, unified tool called `uv` is adopted. Developed by Astral, `uv` is an extremely fast package and project manager written in Rust that consolidates these functions into a single binary. Its performance benefits are especially noticeable on resource-constrained devices like the Raspberry Pi Zero 2 W.

The workflow with `uv` is streamlined:

1.  **Installation:** `uv` is installed system-wide with a single command.
2.  **Project Initialization:** `uv init` generates a `pyproject.toml` file.
3.  **Adding Dependencies:** `uv add` installs packages and updates `pyproject.toml`.
4.  **Running Scripts:** `uv run` executes scripts within the managed virtual environment.

#### Section 2.2: Crafting the ninja\_faces.py Application

The `ninja_faces.py` application serves as the primary demonstration of the display drivers' capabilities. It is controlled via a robust command-line interface built using Python's standard `argparse` library. The application is structured with a main execution block, a display factory to load the correct driver, and a `Face` class to encapsulate rendering logic.

#### Section 2.3: Achieving Flicker-Free Animation

To provide a smooth, professional-quality animation, this project implements a double-buffering strategy. All drawing operations for a given frame are performed on an off-screen, in-memory Pillow Image object. This process is extremely fast. Only when the frame is 100% complete in memory is the `display.display(image)` method called. This transmits the entire buffer to the display's GRAM in a single, high-speed, atomic operation, resulting in fluid, flicker-free animation.

#### Section 2.4: Diagnostic and Testing Utilities

To aid users in debugging, a diagnostic mode is included in `ninja_faces.py`, activated with the `--diag` flag. It renders a test pattern with color bars, a bounding box, and orientation text. A separate, minimal script named `test_text.py` is also provided to act as a "Hello, World\!" for the hardware setup.

```
```
