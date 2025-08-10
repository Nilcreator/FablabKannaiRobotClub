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