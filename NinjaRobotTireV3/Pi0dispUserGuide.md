# Pi0disp User Guide

## Introduction

`pi0disp` is a Python library for controlling ST7789V-based LCD displays on a Raspberry Pi. It is designed to be easy to use and provides a simple interface for displaying images and animations. The library is built on top of the `pigpio` library for high-speed SPI communication and GPIO control, ensuring smooth and fast graphics rendering.

## Features

*   Easy-to-use Python API for controlling ST7789V displays.
*   High-speed SPI communication using the `pigpio` library.
*   Support for displaying [Pillow (PIL)](https://python-pillow.org/) Image objects.
*   Optimized pixel data conversion using `numpy` for better performance.
*   Support for display rotation.
*   Includes example scripts to demonstrate usage and advanced features like animation and partial screen updates.

## Hardware Requirements

*   A Raspberry Pi (any model with GPIO pins).
*   An ST7789V-based LCD display (typically 240x320 or 320x240 pixels).
*   Jumper wires to connect the LCD to the Raspberry Pi.

## Hardware Setup

Connect the LCD to your Raspberry Pi's GPIO pins as follows. Please note that the default pin configuration can be changed when you instantiate the `ST7789V` class.

| LCD Pin | Raspberry Pi Pin (BCM) | Description      |
| :------ | :--------------------- | :--------------- |
| VCC     | 3.3V or 5V             | Power            |
| GND     | GND                    | Ground           |
| SCL/CLK | GPIO 11 (SCLK)         | SPI Clock        |
| SDA/MOSI| GPIO 10 (MOSI)         | SPI Data         |
| RES/RST | GPIO 19                | Reset            |
| DC      | GPIO 18                | Data/Command     |
| BL/BLK  | GPIO 20                | Backlight Control|
| CS      | GPIO 8 (CE0)           | SPI Chip Select  |

**Note:** The `CS` pin is handled by the SPI channel and does not need to be specified in the code. By default, the library uses SPI channel 0, which corresponds to `CE0` (GPIO 8).

## Software Prerequisites

Before installing and using the `pi0disp` library, you need to make sure that the `pigpio` daemon is installed and running on your Raspberry Pi.

1.  **Install `pigpio`:**
    ```bash
    sudo apt-get update
    sudo apt-get install pigpio
    ```

2.  **Start the `pigpio` daemon:**
    ```bash
    sudo pigpiod
    ```
    It is recommended to enable the `pigpio` daemon to start on boot:
    ```bash
    sudo systemctl enable pigpiod
    ```

## Installation

You can install the `pi0disp` library using `pip`:

```bash
pip install pi0disp
```

This will also install the required dependencies: `click`, `numpy`, `pigpio`, and `pillow`.

## Usage

### Basic Usage

Here is a simple example of how to initialize the display and draw a blue screen:

```python
from PIL import Image
from pi0disp import ST7789V

# Initialize the LCD
with ST7789V() as lcd:
    # Create a blue image
    img = Image.new("RGB", (lcd.width, lcd.height), "blue")

    # Display the image
    lcd.display(img)
```

### Running the Example Scripts

The `pi0disp` library comes with a few example scripts in the `samples` directory. To run them, you can either download the repository or install the library and run the scripts from the installation directory.

*   **`test1.py`**: A simple test that draws some shapes and text on the display.
*   **`test2.py`**: An animation of a bouncing ball.
*   **`test3.py`**: A more advanced animation that demonstrates techniques like dirty rectangle updates and frame rate capping for better performance.

To run an example, navigate to the `samples` directory and execute the Python script:

```bash
python3 test1.py
```

## API Reference

### `ST7789V(channel=0, rst_pin=19, dc_pin=18, backlight_pin=20, speed_hz=80000000, width=240, height=320, rotation=90)`

The main class for controlling the ST7789V display.

*   **`channel`**: SPI channel (0 for CE0, 1 for CE1).
*   **`rst_pin`**: GPIO pin for the reset signal.
*   **`dc_pin`**: GPIO pin for the data/command signal.
*   **`backlight_pin`**: GPIO pin for the backlight control.
*   **`speed_hz`**: SPI clock speed in Hz.
*   **`width`**: The physical width of the display in pixels.
*   **`height`**: The physical height of the display in pixels.
*   **`rotation`**: The rotation of the display in degrees (0, 90, 180, or 270).

#### Methods

*   **`display(image)`**: Displays a Pillow `Image` object on the screen. The image will be automatically resized to fit the display.
*   **`set_rotation(rotation)`**: Sets the rotation of the display.
*   **`set_window(x0, y0, x1, y1)`**: Sets the drawing window to a specific area of the display.
*   **`write_pixels(pixel_bytes)`**: Writes a raw byte array of pixel data to the display.
*   **`close()`**: Cleans up the GPIO pins and closes the SPI connection.

## Troubleshooting

*   **`RuntimeError: pigpio daemon is not running.`**: Make sure the `pigpio` daemon is running. You can start it with `sudo pigpiod`.
*   **`RuntimeError: SPI bus open failed.`**: Check your SPI configuration and make sure that the SPI interface is enabled on your Raspberry Pi (`sudo raspi-config`).
*   **The display is not working or showing garbage:** Double-check your wiring and make sure you are using the correct GPIO pins. Also, ensure that the `speed_hz` is not too high for your display or wiring. You can try a lower value like `40000000`.
