
# NinjaRobotV3 User Guide (taniguide.md)

This guide provides a comprehensive overview of the `pi0disp`, `piservo0`, and `vl53l0x_pigpio` libraries and how to use them within the `NinjaRobotV3` project.

## 1. Initial Setup

This project uses `uv` for managing Python virtual environments and dependencies.

### 1.1. Create and Activate the Virtual Environment

It is recommended to use a virtual environment for this project.

```bash
# Create the virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate
```

### 1.2. Install Dependencies

Install the necessary packages for all three libraries using `uv`.

```bash
# Install all dependencies from the subdirectories
uv pip install -e pi0disp
uv pip install -e piservo0
uv pip install -e vl53l0x_pigpio
```

## 2. Using the Libraries

### 2.1. `pi0disp` - Display Driver

The `pi0disp` library is a high-speed driver for ST7789V-based displays on Raspberry Pi.

#### As a Library

You can use the `ST7789V` class to control the display in your Python scripts.

```python
from pi0disp import ST7789V
from PIL import Image, ImageDraw
import time

# Initialize the display
with ST7789V() as lcd:
    # Create an image with PIL
    image = Image.new("RGB", (lcd.width, lcd.height), "black")
    draw = ImageDraw.Draw(image)

    # Draw a blue circle
    draw.ellipse(
        (10, 10, lcd.width - 10, lcd.height - 10),
        fill="blue",
        outline="white"
    )

    # Display the image
    lcd.display(image)

    time.sleep(5)

    # Example of partial update
    draw.rectangle((50, 50, 100, 100), fill="red")
    lcd.display_region(image, 50, 50, 100, 100)

    time.sleep(5)
```

#### CLI Usage

The `pi0disp` command provides a simple CLI for testing the display.

```bash
# Run the ball animation demo
uv run pi0disp ball_anime

# Turn the display off
uv run pi0disp off
```

### 2.2. `piservo0` - Servo Motor Control

The `piservo0` library provides precise control over servo motors.

#### As a Library

Use the `PiServo` or `CalibrableServo` class to control your servos.

**Basic Usage (`PiServo`)**

```python
import time
import pigpio
from piservo0 import PiServo

PIN = 17

pi = pigpio.pi()
servo = PiServo(pi, PIN)

servo.move_pulse(1000)
time.sleep(0.5)

servo.move_max()
time.sleep(0.5)

servo.off()
pi.stop()
```

**Calibrated Usage (`CalibrableServo`)**

```python
import time
import pigpio
from piservo0 import CalibrableServo

PIN = 17

pi = pigpio.pi()
servo = CalibrableServo(pi, PIN) # Loads calibration from servo.json

servo.move_angle(45)  # Move to 45 degrees
time.sleep(1)

servo.move_center()
time.sleep(1)

servo.off()
pi.stop()
```

#### CLI Usage

The `piservo0` command allows for calibration and remote control.

**Calibration**

```bash
# Calibrate the servo on GPIO 17
uv run piservo0 calib 17
```

**API Server**

```bash
# Start the API server for servos on GPIO 17, 27, 22, 25
uv run piservo0 api-server 17 27 22 25
```

**API Client**

```bash
# Connect to the API server
uv run piservo0 api-client
```

### 2.3. `vl53l0x_pigpio` - Distance Sensor

The `vl53l0x_pigpio` library is a driver for the VL53L0X time-of-flight distance sensor.

#### As a Library

Use the `VL53L0X` class to get distance measurements.

```python
import pigpio
from vl53l0x_pigpio import VL53L0X
import time

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio")

try:
    with VL53L0X(pi) as tof:
        distance = tof.get_range()
        if distance > 0:
            print(f"Distance: {distance} mm")
        else:
            print("Invalid data.")
finally:
    pi.stop()
```

#### CLI Usage

The `vl53l0x_pigpio` command provides tools for interacting with the sensor.

**Get Distance**

```bash
# Get 5 distance readings
uv run vl53l0x_pigpio get --count 5
```

**Performance Test**

```bash
# Run a performance test with 500 measurements
uv run vl53l0x_pigpio performance --count 500
```

**Calibration**

```bash
# Calibrate the sensor with a target at 150mm
uv run vl53l0x_pigpio calibrate --distance 150
```

