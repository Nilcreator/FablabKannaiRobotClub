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
