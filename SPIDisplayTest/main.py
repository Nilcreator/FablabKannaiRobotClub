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
