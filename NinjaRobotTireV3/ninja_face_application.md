Building an Advanced SPI LCD Application for Raspberry Pi Zero 2 WPart 1: Foundational Analysis and Hardware IntegrationThis report provides a comprehensive guide to enhancing the pi0disp repository for the Raspberry Pi Zero 2 W. The project involves adding support for a new ILI9225-based SPI LCD, modernizing the development workflow with the uv package manager, and creating a feature-rich animated application. The final result is a robust, well-documented, and high-performance display solution suitable for advanced hobbyist and embedded systems projects.Section 1.1: Architectural Review of the pi0disp RepositoryA thorough analysis of the existing pi0disp repository is the first step toward extending its functionality. Understanding its architecture allows for new components to be integrated in a modular and consistent manner, respecting the original design philosophy while introducing significant improvements.Analysis of Core ComponentsThe pi0disp repository is structured around individual Python modules for each supported display controller. The primary examples are st7789v.py for an SPI-based color LCD and sh1106.py for an I²C-based monochrome OLED display.Display Initialization Flow: The initialization process in the existing drivers follows a standard pattern for embedded displays. It begins with the configuration of GPIO pins for control signals such as Reset (RST), Data/Command (DC), and Backlight (BL). An interface object, either from the spidev or smbus library, is then instantiated to handle the low-level communication. A hardware reset is performed by toggling the RST pin, which puts the display controller into a known state. Following the reset, a specific sequence of commands and data bytes is transmitted to configure the controller's internal registers. This sequence typically includes commands to exit sleep mode, set the pixel color format, define the memory access orientation, and enable the display output.Communication Protocols: The repository effectively utilizes standard Linux interfaces for hardware communication. For SPI displays like the ST7789V, it relies on the spidev Python library, which provides a wrapper around the /dev/spidevX.Y kernel device. The key function used is spi.xfer2(), which facilitates efficient, full-duplex block data transfers. For I²C devices, the smbus library is used. Control of non-SPI/I²C pins like DC and RST is managed directly through the RPi.GPIO library, using GPIO.output() to set their state.Image Buffer Pipeline: Graphics rendering is handled through an off-screen buffer methodology using the powerful Python Imaging Library (Pillow). An in-memory image buffer is created with Image.new('RGB',...), matching the resolution of the target display. All drawing operations—such as rendering shapes, text, or pasting other images—are performed on this buffer using the ImageDraw module. This approach is computationally efficient as memory operations are significantly faster than repeated hardware bus transactions. Once the frame is fully rendered in the buffer, its raw pixel data is extracted as a byte string using image.tobytes() and transmitted to the display in a single, high-speed burst. This forms the core graphics pipeline that will be replicated for the new ILI9225 driver.Rotation and Orientation: The existing st7789v.py driver manages display rotation by sending a "Memory Access Control" (MADCTL) command to the controller. This command alters how the display's internal Graphics RAM (GRAM) addresses are mapped to the physical screen coordinates, allowing for portrait, landscape, and inverted orientations without requiring software-based pixel manipulation, which would be prohibitively slow. Identifying and implementing the equivalent command for the ILI9225 controller is a critical task for the new driver.An Architectural Enhancement: A Unified Display InterfaceThe existing example scripts in pi0disp often contain logic tightly coupled to a specific display driver. To support both the ST7789V and the new ILI9225 from a single, unified application (ninja_faces.py), a more robust software architecture is required. This project introduces a formal abstraction layer.A base class or an informal interface will be defined, establishing a common set of methods that all display drivers must implement. This API will include, at a minimum:init(): To perform the hardware reset and send the initialization sequence.display(image): To accept a Pillow Image object and push it to the screen.cleanup(): To properly release GPIO resources.set_backlight(state): To control the display's backlight.The ninja_faces.py application will then instantiate the appropriate driver class based on a command-line flag (e.g., --display st7789v). The remainder of the application will interact with the driver object through this common, abstract API, making the code cleaner, more modular, and easily extensible to support other displays in the future.Section 1.2: Implementing the ILI9225 Python DriverThe core technical task of this project is the development of a new Python driver module, ili9225.py. This module will encapsulate all the low-level logic required to control a 2.2-inch, 176x220 pixel SPI LCD based on the Ilitek ILI9225 controller.Datasheet and Reference Implementation AnalysisThe primary source of truth for this task is the ILI9225 controller datasheet, which details the command set, register maps, and electrical characteristics.1 However, datasheets can sometimes be ambiguous or lack practical implementation details regarding timing and command ordering. To mitigate this, existing open-source C/C++ and MicroPython drivers for the ILI9225 serve as invaluable references.4 By cross-referencing these battle-tested implementations with the official datasheet, a highly reliable initialization sequence can be constructed, avoiding common pitfalls and ensuring robust operation.Driver Implementation DetailsThe new ili9225.py module will be implemented as a Python class, ILI9225, adhering to the unified display interface.Initialization Sequence (_init method): This is the most critical section of the driver. It translates the complex startup procedure from the datasheet into a precise sequence of SPI transactions. The sequence will be heavily commented to clarify the purpose of each step:Hardware Reset: The RST pin is toggled low, then high, to ensure the controller starts in a predictable state.Power and Oscillator Setup: Commands are sent to configure the internal power control registers (0x10, 0x11, 0x12, 0x13) and start the internal oscillator. Appropriate delays (time.sleep()) are inserted to allow voltage levels and clocks to stabilize.Display Control Configuration: Registers are configured to set the driving output control, LCD driving waveform, and entry mode. The entry mode register (0x03) is particularly important as it controls the default orientation and color order (RGB vs. BGR).Gamma Correction: The ILI9225 allows for fine-tuning of the gamma curve via a set of dedicated registers (0x50 through 0x59). Values from reference implementations will be used to provide a good default color balance.Windowing Setup: The horizontal and vertical RAM address window is set to the full dimensions of the display (176x220 pixels), ensuring that subsequent display() calls will update the entire screen.Display On: Finally, the driver sends the command to exit sleep mode (0x01, Start Oscillator) followed by the command to turn the display on (0x07, Display Control 1), making the screen active.Orientation Handling (set_orientation method): The ILI9225 datasheet specifies that the Entry Mode register (R03h) controls how the GRAM address counter is updated. Specifically, the AM bit toggles between horizontal and vertical address updates, while the I/D[1:0] bits control the increment/decrement direction. The set_orientation method will accept a rotation value (0, 90, 180, or 270 degrees) and write a pre-calculated 16-bit value to this register, instantly changing the display's orientation without any software overhead.Image Data Transfer (display method): This method is the workhorse of the driver. It accepts a standard Pillow Image object in 'RGB' mode. A critical step within this method is the conversion of the image data from Pillow's 24-bit RGB888 format to the 16-bit RGB565 format native to the ILI9225 controller. Sending 24-bit data directly would result in severe color distortion and visual artifacts. This conversion is performed efficiently using bitwise operations on each pixel's color channels: ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3). This packs the 24-bit color into a 16-bit integer. The resulting buffer of 16-bit values is then sent to the display via a single, large spi.xfer2() call for maximum throughput.Low-Level Communication (_command, _data methods): To simplify the driver logic, two internal helper methods are used. The _command(cmd) method sets the DC pin low before sending a command byte, while the _data(data) method sets the DC pin high before sending parameter bytes or pixel data. This abstraction ensures the controller correctly distinguishes between commands and data on the SPI bus.Section 1.3: Hardware Connection GuideCorrect physical wiring is the most fundamental prerequisite for project success. Ambiguous or incorrect instructions are a common source of user frustration. This section provides clear, validated pinout tables for connecting both the Waveshare ST7789V and a generic ILI9225 LCD module to the Raspberry Pi Zero 2 W's 40-pin GPIO header.The Raspberry Pi Zero 2 W features a 1GHz quad-core 64-bit ARM Cortex-A53 CPU and 512MB of RAM, making it amply powerful for driving these displays with smooth animations.8 It exposes one primary SPI bus, SPI0, which will be used for this project.Voltage Level CompatibilityA crucial point of consideration in any hardware integration project is logic level compatibility. The Raspberry Pi's GPIO pins operate at 3.3V. The datasheets and specifications for both the ST7789V and the ILI9225 modules confirm that their logic inputs are also 3.3V tolerant.11This direct compatibility is a significant advantage. Unlike projects involving 5V microcontrollers like the Arduino Uno, where logic level shifters are mandatory to prevent damage to the display, no level shifting is required when interfacing these displays with a Raspberry Pi. This simplifies the wiring, reduces the component count, and eliminates potential points of failure. This fact will be explicitly highlighted in the user documentation to prevent confusion.Pinout TablesThe following tables provide the exact pin-to-pin connections for each display. They map the label on the LCD module's PCB to its function, the corresponding physical pin number on the Raspberry Pi's 40-pin header, and the BCM GPIO number used by the software libraries.LCD PinFunctionRPi Physical PinRPi BCM GPIOVCC3.3V PowerPin 1 (3.3V)N/AGNDGroundPin 6 (GND)N/ADINSPI Data In (MOSI)Pin 19 (SPI0_MOSI)GPIO 10CLKSPI Clock (SCLK)Pin 23 (SPI0_SCLK)GPIO 11CSSPI Chip SelectPin 24 (SPI0_CE0_N)GPIO 8DCData/Command SelectPin 22GPIO 25RSTResetPin 18GPIO 24BLBacklight Control (PWM)Pin 12GPIO 18Table 1.3.1: Raspberry Pi Zero 2 W to Waveshare ST7789V (2") PinoutLCD PinFunctionRPi Physical PinRPi BCM GPIOVCC3.3V PowerPin 1 (3.3V)N/AGNDGroundPin 9 (GND)N/ACSSPI Chip SelectPin 24 (SPI0_CE0_N)GPIO 8RESET (RES)ResetPin 22GPIO 25RS (DC)Register Select (D/C)Pin 18GPIO 24SDA (MOSI)SPI Data In (MOSI)Pin 19 (SPI0_MOSI)GPIO 10SCK (SCL)SPI Clock (SCLK)Pin 23 (SPI0_SCLK)GPIO 11LEDBacklight Control (3.3V)Pin 17 (3.3V)N/ATable 1.3.2: Raspberry Pi Zero 2 W to ILI9225 (2.2") Pinout 11Part 2: Application Development with Modern ToolingWith the hardware drivers defined, the focus shifts to building the user-facing application and establishing a modern, efficient development environment. This part details the adoption of the uv package manager, the design of the ninja_faces.py application, and the implementation of strategies for smooth, flicker-free animation.Section 2.1: Establishing a Modern, High-Performance Workflow with uvThe traditional Python development workflow, which often involves separate tools like pip, venv, pip-tools, and pipx, can be fragmented and slow. For this project, a modern, unified tool called uv is adopted. Developed by Astral (the creators of Ruff), uv is an extremely fast package and project manager written in Rust that consolidates these functions into a single binary.13 Its performance benefits are especially noticeable on resource-constrained devices like the Raspberry Pi Zero 2 W, where it can be 10-100x faster than its predecessors.The workflow with uv is streamlined and declarative:Installation: uv is installed system-wide on the Raspberry Pi with a single command. This provides the uv executable for all subsequent steps.13Bashcurl -LsSf https://astral.sh/uv/install.sh | sh
Project Initialization: Instead of manually creating a virtual environment, the uv init command is used. This generates a pyproject.toml file, the modern standard for defining Python project metadata and dependencies.Bashuv init
Adding Dependencies: Dependencies are added using uv add. This command automatically creates a local .venv directory if one doesn't exist, resolves the dependency graph, installs the packages, and updates pyproject.toml.Bashuv add spidev RPi.GPIO Pillow
Running Scripts: Scripts are executed using the uv run command. This automatically runs the target script within the context of the managed virtual environment, eliminating the need to manually source.venv/bin/activate. This approach makes execution explicit and reproducible.Bashuv run ninja_faces.py --display ili9225
Section 2.2: Crafting the ninja_faces.py ApplicationThe ninja_faces.py application serves as the primary demonstration of the display drivers' capabilities. It is designed to be a complete, interactive, and feature-rich example.Command-Line Interface (CLI)The application is controlled via a robust command-line interface built using Python's standard argparse library.18 This allows users to easily configure the application without modifying the source code.The following arguments are implemented:--display: A required argument with a choice between 'st7789v' and 'ili9225'. This determines which display driver class is loaded at runtime.--expression: An optional argument to set the initial facial expression (e.g., 'happy', 'sad', 'angry'). If omitted, the application defaults to an 'idle' state.--diag: An optional boolean flag (action='store_true') that, when present, bypasses the main application and runs a hardware diagnostic routine instead.--font: An optional path to a .ttf font file for rendering text.Application StructureThe code is organized into a clear, logical structure to promote readability and maintainability:Main Execution Block: The if __name__ == "__main__": block is responsible for parsing command-line arguments.Display Factory: A simple conditional block uses the --display argument to import and instantiate the correct driver object (ST7789V or ILI9225). This object is then passed to the main application logic.Face Class: A Face class encapsulates the state and rendering logic for the animated character. It holds attributes for the current state of the eyes and mouth and contains methods like draw_expression(draw, expression_name) that render the corresponding facial features onto a provided Pillow ImageDraw context.Animation Loop: The core of the application is a while True loop. In each iteration, it updates the face's state (e.g., handling blinking logic), calls the Face class to redraw the entire scene onto an in-memory image buffer, and then calls the display.display(buffer) method to push the completed frame to the LCD.Interactive Prompt: The application includes a simple text-based prompt that allows the user to type in an expression name (e.g., "happy", "surprised") at runtime to change the ninja's face dynamically.Font HandlingTo ensure robustness, the application implements a graceful fallback mechanism for font loading. It first attempts to load a user-specified TrueType Font (.ttf) file using ImageFont.truetype().21 If the file is not found or cannot be loaded, it catches the exception and falls back to Pillow's built-in default bitmap font via ImageFont.load_default(). This ensures that the application can always render text and remains functional even if custom assets are missing.Section 2.3: Achieving Flicker-Free AnimationA common challenge when driving displays over an SPI bus is visual flicker. This occurs when the screen is cleared and then elements are drawn one by one directly to the display's memory. Because the SPI bus has limited bandwidth, the user can perceive this partial redrawing process, which manifests as an unpleasant flicker or tearing effect.To provide a smooth, professional-quality animation, this project implements a double-buffering strategy. All drawing operations for a given frame are performed on an off-screen, in-memory buffer—a Pillow Image object. This process is extremely fast because it involves only CPU and RAM operations.The animation loop follows these steps for every frame:A new, blank Pillow Image object is created in memory (this is the "back buffer").The ImageDraw module is used to render the complete, final scene for that frame onto this back buffer. This includes the background, eyes, mouth, and any text.Only when the frame is 100% complete in memory is the display.display(image) method called. This method handles the color conversion and transmits the entire buffer to the display's GRAM in a single, high-speed, atomic operation.Because the display's memory is updated in one swift pass, the user never sees an intermediate or partially drawn state. The transition from one complete frame to the next is seamless, resulting in fluid, flicker-free animation, which is essential for the blinking eyes and changing expressions of the ninja face.Section 2.4: Diagnostic and Testing UtilitiesTo aid users in debugging their hardware setup and verifying that the drivers are functioning correctly, two key utilities are included.Diagnostic ModeWhen the ninja_faces.py application is run with the --diag flag, it enters a diagnostic mode. Instead of the animated face, it renders a specialized test pattern designed to verify several aspects of the hardware and driver at once:Color Bars: A series of red, green, and blue vertical bars are drawn to confirm that the color mapping and RGB565 conversion are working correctly.Bounding Box: A one-pixel-wide white rectangle is drawn at the very edge of the display area. This allows the user to visually confirm that the driver's configured resolution matches the physical screen and that there are no off-by-one errors in the windowing commands.Orientation Text: Text labels such as "Top-Left (0,0)" and "Bottom-Right" are rendered in the corners of the screen. This provides an unambiguous check that the display's coordinate system and rotation handling are behaving as expected.Simple Text Test ScriptA separate, minimal script named test_text.py is provided. Its sole purpose is to initialize a chosen display and render a single line of user-provided text in the center. This script acts as the "Hello, World!" for the hardware setup. It allows users to perform a quick, simple test to confirm that their wiring is correct and the SPI interface is enabled and functional before moving on to the more complex ninja_faces.py application.Part 3: Final Deliverables and User DocumentationThis final part consolidates all project components into a complete, user-friendly package. It includes a step-by-step guide for setting up the project from a fresh system image, the updated pi0dispUserGuide.md documentation, and the complete, copy-paste-ready source code for all new and modified modules.Section 3.1: End-to-End Project Setup GuideThis guide provides a linear set of instructions that a user can follow to replicate the project on their own Raspberry Pi Zero 2 W. All commands are designed to be copied and pasted directly into the terminal.1. System PrerequisitesIt is assumed you are starting with a fresh installation of Raspberry Pi OS (Bookworm, 64-bit Lite is recommended) on your SD card.Update System Packages:Bashsudo apt update && sudo apt upgrade -y
Enable SPI Interface: The SPI hardware interface is disabled by default. Enable it using the raspi-config utility.23Bashsudo raspi-config
Navigate to 3 Interface Options -> I3 SPI. Select <Yes> to enable the SPI interface and reboot when prompted.2. Software InstallationInstall git and uv:Bashsudo apt install git -y
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
Explanation: This installs git for cloning the repository and uv for managing the Python project.3. Project SetupClone the Repository:Bashgit clone https://github.com/ytani01/pi0disp.git
cd pi0disp
Install Python Dependencies: Use uv to create the virtual environment and install the required packages from the pyproject.toml file.Bashuv sync
Explanation: uv sync reads the pyproject.toml and uv.lock files, creates a .venv directory, and installs the exact versions of the dependencies, ensuring a reproducible environment.4. Running the CodeEnsure your chosen LCD is wired correctly according to the tables in Section 1.3.Run the Text Test Utility: This is a quick test to ensure your wiring and SPI configuration are correct.Bash# For the ILI9225 display
uv run python test_text.py --display ili9225 --text "Hello ILI9225!"

# For the ST7789V display
uv run python test_text.py --display st7789v --text "Hello ST7789V!"
Run the Diagnostic Mode: This test verifies colors, resolution, and orientation.Bash# For the ILI9225 display
uv run python ninja_faces.py --display ili9225 --diag
Run the Main Application: Launch the animated ninja face application.Bash# For the ILI9225 display
uv run python ninja_faces.py --display ili9225

# Start with a specific expression
uv run python ninja_faces.py --display st7789v --expression happy
Once running, you can type an expression name (e.g., sad, angry, surprised) into the terminal and press Enter to change the face. Use Ctrl+C to exit.Section 3.2: The Definitive pi0dispUserGuide.mdThis section contains the complete content for the updated user guide, intended to replace or supplement the existing documentation in the repository.pi0disp User GuideThis repository provides Python drivers and example applications for various small displays on the Raspberry Pi Zero 2 W and other Raspberry Pi models. This guide covers hardware setup, software installation, and usage instructions.Supported HardwareWaveshare 2inch LCD Module: A 240x320 pixel color LCD based on the ST7789V controller.Generic 2.2inch SPI TFT LCD: A 176x220 pixel color LCD based on the ILI9225 controller.Hardware WiringConnect your display to the Raspberry Pi's 40-pin GPIO header as shown in the tables below. Both displays operate on 3.3V logic, so no logic level shifters are required.Waveshare ST7789V (2") WiringLCD PinFunctionRPi Physical PinRPi BCM GPIOVCC3.3V PowerPin 1 (3.3V)N/AGNDGroundPin 6 (GND)N/ADINSPI Data In (MOSI)Pin 19 (SPI0_MOSI)GPIO 10CLKSPI Clock (SCLK)Pin 23 (SPI0_SCLK)GPIO 11CSSPI Chip SelectPin 24 (SPI0_CE0_N)GPIO 8DCData/Command SelectPin 22GPIO 25RSTResetPin 18GPIO 24BLBacklight Control (PWM)Pin 12GPIO 18Generic ILI9225 (2.2") WiringLCD PinFunctionRPi Physical PinRPi BCM GPIOVCC3.3V PowerPin 1 (3.3V)N/AGNDGroundPin 9 (GND)N/ACSSPI Chip SelectPin 24 (SPI0_CE0_N)GPIO 8RESET (RES)ResetPin 22GPIO 25RS (DC)Register Select (D/C)Pin 18GPIO 24SDA (MOSI)SPI Data In (MOSI)Pin 19 (SPI0_MOSI)GPIO 10SCK (SCL)SPI Clock (SCLK)Pin 23 (SPI0_SCLK)GPIO 11LEDBacklight Control (3.3V)Pin 17 (3.3V)N/ASoftware SetupFollow the step-by-step instructions in Section 3.1 of this report to configure your Raspberry Pi, install dependencies with uv, and prepare the project.Running the ApplicationsAll scripts should be run from the root of the pi0disp directory using the uv run command.ninja_faces.pyThis is the main application, displaying an animated character face.Usage:uv run python ninja_faces.py --display <display_type> [options]Arguments:--display <type>: (Required) Specify the display type. Choices: st7789v, ili9225.--expression <name>: (Optional) Set the initial expression. Choices: idle, happy, sad, angry, surprised, laughing, etc.--diag: (Optional) Run a hardware diagnostic pattern instead of the main application.--font <path>: (Optional) Path to a .ttf font file.Examples:Bash# Run on ILI9225 display
uv run python ninja_faces.py --display ili9225

# Run on ST7789V and start with the "happy" expression
uv run python ninja_faces.py --display st7789v --expression happy
test_text.pyA simple utility to display a line of text. Useful for initial hardware verification.Usage:uv run python test_text.py --display <display_type> --text "Your Text"Performance NotesSPI Speed: The SPI clock speed is configured within each driver file (spi.max_speed_hz). The default values (e.g., 32MHz) are generally stable. If you experience artifacts or a blank screen, especially with long jumper wires, try reducing this value to 16000000 (16MHz) or lower.Frame Rate: The Raspberry Pi Zero 2 W is capable of driving these displays at a smooth frame rate for simple animations. The primary bottleneck is the SPI bus transfer speed. The double-buffering technique used in ninja_faces.py ensures flicker-free updates.TroubleshootingProblem: Screen is blank, white, or shows nothing.Solution: Double-check your VCC and GND connections. Ensure the SPI interface is enabled via sudo raspi-config. Verify that all GPIO pin connections (CS, DC, RST, MOSI, SCLK) are correct and secure.Problem: Colors are wrong or inverted.Solution: This may be due to a variation in the LCD panel. Some controllers have a "Color Inversion" command that can be sent during initialization. It could also be an issue with the RGB vs. BGR color order, which is typically set in the Entry Mode or Memory Access Control register.Problem: Image is mirrored or rotated incorrectly.Solution: The orientation is controlled by the set_orientation() method in the driver, which writes to a specific controller register. If the image is mirrored, you may need to adjust the bits corresponding to horizontal or vertical flip within that register's value.Problem: PermissionError: [Errno 13] Permission denied: '/dev/spidev0.0'Solution: Accessing the SPI device /dev/spidev0.0 typically requires root privileges. While it's possible to add the user to the spi group and configure udev rules, the simplest solution is to run the script with sudo: sudo uv run python ninja_faces.py....Part 4: Complete Source CodeThis section provides the complete, copy-paste-ready source code for the new and modified Python files required for this project.pyproject.tomlIni, TOML[project]
name = "pi0disp-enhanced"
version = "1.0.0"
description = "Enhanced drivers and applications for SPI displays on Raspberry Pi."
dependencies =

[tool.uv]
dev-dependencies =
pi0disp/display_base.pyPython# pi0disp/display_base.py
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
            state (bool): True for on, False for off.
        """
        pass

    @abc.abstractmethod
    def cleanup(self):
        """Clean up GPIO resources."""
        pass
pi0disp/ili9225.pyPython# pi0disp/ili9225.py
import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image
from.display_base import Display

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
    def __init__(self, rst_pin=25, dc_pin=24, cs_pin=8, spi_bus=0, spi_device=0, spi_speed=32000000):
        super().__init__(width=176, height=220)
        self.rst_pin = rst_pin
        self.dc_pin = dc_pin
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

        # Initialization Sequence
        self._write_register(ILI9225_POWER_CTRL1, 0x0000) # Set SAP, DSTB, STB
        self._write_register(ILI9225_POWER_CTRL2, 0x0000) # Set APON, PON, AON, VCI1EN, VC
        self._write_register(ILI9225_POWER_CTRL3, 0x0000) # Set BT, DC1, DC2, DC3
        self._write_register(ILI9225_POWER_CTRL4, 0x0000) # Set GVDD
        self._write_register(ILI9225_POWER_CTRL5, 0x0000) # Set VCOMH/VCOML voltage
        time.sleep(0.04)

        # Power-on sequence
        self._write_register(ILI9225_POWER_CTRL2, 0x0018) # Set APON, PON, AON, VCI1EN, VC
        self._write_register(ILI9225_POWER_CTRL3, 0x6121) # Set BT, DC1, DC2, DC3
        self._write_register(ILI9225_POWER_CTRL4, 0x006F) # Set GVDD
        self._write_register(ILI9225_POWER_CTRL5, 0x495F) # Set VCOMH/VCOML voltage
        self._write_register(ILI9225_POWER_CTRL1, 0x0800) # Set SAP, DSTB, STB
        time.sleep(0.01)
        self._write_register(ILI9225_POWER_CTRL2, 0x103B) # Set APON, PON, AON, VCI1EN, VC
        time.sleep(0.05)

        self._write_register(ILI9225_DRIVER_OUTPUT_CTRL, 0x011C) # set the display line number and display direction
        self._write_register(ILI9225_LCD_AC_DRIVING_CTRL, 0x0100) # set 1 line inversion
        self._write_register(ILI9225_ENTRY_MODE, 0x1030) # set GRAM write direction and BGR=1.
        self._write_register(ILI9225_DISPLAY_CTRL1, 0x0000) # Display off
        self._write_register(ILI9225_BLANK_PERIOD_CTRL1, 0x0808) # set the front porch and back porch
        self._write_register(ILI9225_FRAME_CYCLE_CTRL, 0x1100) # set the clocks number per line
        self._write_register(ILI9225_INTERFACE_CTRL, 0x0000) # CPU interface
        self._write_register(ILI9225_OSC_CTRL, 0x0D01) # Set Oscillation
        self._write_register(ILI9225_VCI_RECYCLING, 0x0020) # Set VCI recycling
        self._write_register(ILI9225_RAM_ADDR_SET1, 0x0000) # RAM Address
        self._write_register(ILI9225_RAM_ADDR_SET2, 0x0000) # RAM Address

        # Set GRAM area
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

        # Set GAMMA curve
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
        if image.width!= self.width or image.height!= self.height:
            image = image.resize((self.width, self.height))

        # Convert Pillow image from RGB888 to RGB565
        pixels = image.load()
        buffer = bytearray(self.width * self.height * 2)
        idx = 0
        for y in range(self.height):
            for x in range(self.width):
                r, g, b = pixels[x, y]
                # Bitwise conversion
                color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                buffer[idx] = color >> 8
                buffer[idx+1] = color & 0xFF
                idx += 2

        self._set_window(0, 0, self.width - 1, self.height - 1)
        GPIO.output(self.dc_pin, GPIO.HIGH)
        # Write buffer in chunks
        for i in range(0, len(buffer), 4096):
            self.spi.writebytes(buffer[i:i+4096])

    def set_backlight(self, state):
        # Backlight for this module is hardwired to 3.3V, so this is a no-op
        pass

    def cleanup(self):
        self.spi.close()
        GPIO.cleanup([self.rst_pin, self.dc_pin])
test_text.pyPython# test_text.py
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
        print("Display initialized.")

        image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except IOError:
            font = ImageFont.load_default()
            print("Default font loaded.")

        text_bbox = draw.textbbox((0, 0), args.text, font=font)
        text_width = text_bbox - text_bbox
        text_height = text_bbox - text_bbox
        
        x = (disp.width - text_width) // 2
        y = (disp.height - text_height) // 2

        draw.text((x, y), args.text, font=font, fill="WHITE")

        print(f"Displaying text: '{args.text}'")
        disp.display(image)
        
        # Keep the text on screen for a while
        import time
        time.sleep(10)

    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        disp.cleanup()
        print("Resources cleaned up.")

if __name__ == "__main__":
    main()
ninja_faces.pyPython# ninja_faces.py
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

        # Define geometry relative to screen size
        self.eye_y = int(height * 0.4)
        self.eye_radius = int(height * 0.12)
        self.eye_spacing = int(width * 0.25)
        self.left_eye_x = int(width / 2 - self.eye_spacing)
        self.right_eye_x = int(width / 2 + self.eye_spacing)

    def _draw_eyes_idle(self, draw):
        draw.ellipse((self.left_eye_x - self.eye_radius, self.eye_y - self.eye_radius,
                      self.left_eye_x + self.eye_radius, self.eye_y + self.eye_radius), fill=self.eye_color)
        draw.ellipse((self.right_eye_x - self.eye_radius, self.eye_y - self.eye_radius,
                      self.right_eye_x + self.eye_radius, self.eye_y + self.eye_radius), fill=self.eye_color)

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
    # Color bars
    draw.rectangle((0, 0, width//3, height//2), fill="red")
    draw.rectangle((width//3, 0, 2*width//3, height//2), fill="green")
    draw.rectangle((2*width//3, 0, width, height//2), fill="blue")
    
    # Bounding box
    draw.rectangle((0, 0, width-1, height-1), outline="white")
    
    # Orientation text
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

    # Display Factory
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

        # Interactive input thread
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
        
        # Animation loop
        blink_timer = time.time()
        is_blinking = False
        next_blink_interval = random.uniform(2, 7)

        while True:
            # Blinking logic
            if time.time() - blink_timer > next_blink_interval:
                is_blinking = True
                blink_timer = time.time()
                next_blink_interval = random.uniform(2, 7)
            
            if is_blinking and time.time() - blink_timer > 0.15:
                is_blinking = False

            face.draw_expression(draw, current_expression, blink_state=is_blinking)
            disp.display(image)
            time.sleep(0.02) # ~50 FPS cap

    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        disp.cleanup()
        print("Resources cleaned up.")

if __name__ == "__main__":
    main()
