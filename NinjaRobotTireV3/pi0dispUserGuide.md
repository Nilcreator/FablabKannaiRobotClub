# pi0disp User Manual

## 1. Introduction

`pi0disp` is a Python library for controlling ST7789V-based LCD displays with a Raspberry Pi. It uses the `pigpio` library for fast and reliable SPI communication and GPIO control.

## 2. Installation

### 2.1. Dependencies

Before installing `pi0disp`, you need to install its dependencies.

**1. pigpio C library and daemon**

The `pigpio` C library and daemon must be installed and running.

```bash
# Install pigpio
sudo apt-get update
sudo apt-get install pigpio

# Start the pigpio daemon
sudo pigpiod
```

**2. Python libraries**

The following Python libraries are required:

*   `pigpio`: A Python wrapper for the `pigpio` C library.
*   `Pillow`: A powerful image processing library.
*   `numpy` (optional but recommended for better performance): A library for numerical operations.

You can install these with `pip`:

```bash
pip install pigpio Pillow numpy
```

### 2.2. Installing pi0disp

You can install `pi0disp` from PyPI:

```bash
pip install pi0disp
```

Or, if you have the source code, you can install it locally:

```bash
pip install .
```

## 3. Usage

### 3.1. Basic Initialization

Here's how to initialize the display:

```python
from pi0disp import ST7789V
from PIL import Image, ImageDraw, ImageFont

# Initialize the display
# The default settings are for a 240x320 display rotated 90 degrees (landscape)
lcd = ST7789V()

# If your display has different wiring or you want a different rotation,
# you can specify it in the constructor:
# lcd = ST7789V(rst_pin=25, dc_pin=24, backlight_pin=23, rotation=180)
```

The `ST7789V` class can be used with a `with` statement to ensure that the resources are properly released:

```python
with ST7789V() as lcd:
    # Your code here
```

### 3.2. Displaying an Image

The `display()` method takes a Pillow `Image` object and displays it on the screen.

```python
from pi0disp import ST7789V
from PIL import Image

with ST7789V() as lcd:
    # Create a new blue image
    img = Image.new("RGB", (lcd.width, lcd.height), "blue")

    # Display the image
    lcd.display(img)
```

### 3.3. Drawing on the Display

You can use Pillow's `ImageDraw` module to draw shapes and text on the display.

```python
from pi0disp import ST7789V
from PIL import Image, ImageDraw, ImageFont

with ST7789V() as lcd:
    # Create a black image
    img = Image.new("RGB", (lcd.width, lcd.height), "black")
    draw = ImageDraw.Draw(img)

    # Draw a red rectangle
    draw.rectangle((10, 10, 100, 50), fill="red")

    # Draw some text
    # Make sure to have a font file available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    draw.text((10, 70), "Hello, World!", font=font, fill="white")

    # Display the image
    lcd.display(img)
```

## 4. Example

Here is a complete example that clears the screen to black, draws a red rectangle, and then displays "Hello, World!".

```python
import time
from pi0disp import ST7789V
from PIL import Image, ImageDraw, ImageFont

def main():
    try:
        with ST7789V() as lcd:
            # Create a black image
            img = Image.new("RGB", (lcd.width, lcd.height), "black")
            draw = ImageDraw.Draw(img)

            # Draw a red rectangle
            draw.rectangle((10, 10, lcd.width - 10, 50), fill="red", outline="white")

            # Draw some text
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
            except IOError:
                font = ImageFont.load_default()

            text = "Hello, World!"
            draw.text((10, 10), text=text, font=font, fill=(255, 255, 0))

            # Display the image
            lcd.display(img)

            time.sleep(5)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
```

This should give you a good starting point for using the `pi0disp` library.
