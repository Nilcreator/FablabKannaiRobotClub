import RPi.GPIO as GPIO  # Import RPi.GPIO module
import time

# Define the GPIO pins connected to the servo signal wires
servo1_pin = 16  # Change this to the correct GPIO pin
servo2_pin = 17  # Change this to the correct GPIO pin
servo3_pin = 18  # Change this to the correct GPIO pin
servo4_pin = 19  # Change this to the correct GPIO pin

# Software PWM frequency (adjust as needed)
pwm_frequency = 50  # Standard servo PWM frequency is 50Hz

# Duty cycle range (adjust as needed)
min_duty_cycle = 2.5  # Corresponds to 0 degrees (adjust if needed)
max_duty_cycle = 12.5  # Corresponds to 180 degrees (adjust if needed)

# Setup GPIO
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setup(servo1_pin, GPIO.OUT)
GPIO.setup(servo2_pin, GPIO.OUT)
GPIO.setup(servo3_pin, GPIO.OUT)
GPIO.setup(servo4_pin, GPIO.OUT)

# Initialize PWM objects (software PWM)
pwm1 = GPIO.PWM(servo1_pin, pwm_frequency)
pwm2 = GPIO.PWM(servo2_pin, pwm_frequency)
pwm3 = GPIO.PWM(servo3_pin, pwm_frequency)
pwm4 = GPIO.PWM(servo4_pin, pwm_frequency)

pwm1.start(0)  # Start with 0% duty cycle
pwm2.start(0)
pwm3.start(0)
pwm4.start(0)


def set_angle(pwm, angle):
    """Sets the angle of the servo.

    Args:
        pwm: The PWM object.
        angle: The angle in degrees (0-180).
    """
    duty_cycle = (angle / 180) * (max_duty_cycle - min_duty_cycle) + min_duty_cycle
    pwm.ChangeDutyCycle(duty_cycle)
    #time.sleep(0.1)  # Allow time for the servo to move


def set_servo_positions(s1_angle, s2_angle, s3_angle, s4_angle):

    set_angle(pwm1, s1_angle)
    set_angle(pwm2, s2_angle)
    set_angle(pwm3, s3_angle)
    set_angle(pwm4, s4_angle)
    time.sleep(1)

try:
    while True:
        # Set all servos to center position
        print("Centering")
        set_servo_positions(90, 90, 90, 90) #Angle are between 0 and 180
        time.sleep(2)

        # Move servos to specific positions (adjust values as needed)
        print("moving specific positions")
        set_servo_positions(45, 135, 60, 120)
        time.sleep(2)

        # Move to max and min position
        print("Moving max and min")
        set_servo_positions(0, 180, 0, 180)
        time.sleep(2)

except KeyboardInterrupt:
    print("Program stopped")
    pwm1.stop()
    pwm2.stop()
    pwm3.stop()
    pwm4.stop()
    GPIO.cleanup()  # Clean up GPIO on exit
