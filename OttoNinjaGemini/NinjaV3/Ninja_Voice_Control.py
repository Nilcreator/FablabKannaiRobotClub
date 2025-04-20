# -*- coding:utf-8 -*-
# Filename: ninja_voice_control.py

import sys
import os
import time
# import json # No longer needed here
from datetime import datetime

# --- Configuration ---
# WAKE_WORD = "ninja" # Wake word is handled inside ninja_core now for logic
CONVERSATION_LOG_FILE = "conversation.log"
STOP_FLAG_FILE = "stop_voice.flag"
LISTEN_TIMEOUT = 10 # Seconds to listen before looping if no speech
PHRASE_TIME_LIMIT = 15 # Max seconds for a single utterance

# --- Turn off Pygame welcome ---
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
# --- Suppress TensorFlow/Google warnings ---
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# --- Imports ---
try:
    import speech_recognition as sr
    from gtts import gTTS
    from io import BytesIO
    from pygame import mixer
    import ninja_core # Your robot control logic
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please ensure 'SpeechRecognition', 'gTTS', 'pygame', 'google-generativeai', 'RPi.GPIO' etc. are installed.")
    sys.exit(1)

# --- Global Variables ---
recognizer = None
microphone = None
mixer_initialized = False

# --- Helper Functions ---

def initialize_audio_systems():
    """Initialize Pygame Mixer and Speech Recognition."""
    global recognizer, microphone, mixer_initialized
    try:
        print("Initializing Pygame Mixer...")
        mixer.pre_init(frequency=24000, size=-16, channels=1, buffer=1024)
        mixer.init()
        mixer.music.set_volume(1.0)
        mixer_initialized = True
        print("Mixer initialized.")

        print("Initializing Speech Recognition...")
        recognizer = sr.Recognizer()
        # --- Select Microphone ---
        # Option 1: Default Mic
        # microphone = sr.Microphone()
        # Option 2: Explicitly find the I2S mic (RECOMMENDED)
        mic_index = find_mic_index(keyword="googlevoicehatsc") # Or "I2S", "dmic", "plughw:CARD=googlevoicehatsc" etc.
        if mic_index is None:
            print("ERROR: Could not find the specified I2S microphone. Using default.")
            microphone = sr.Microphone()
        else:
            print(f"Using microphone index {mic_index}")
            microphone = sr.Microphone(device_index=mic_index)
        # --- End Mic Selection ---

        # Adjust recognizer settings
        recognizer.energy_threshold = 500 # START VALUE - TUNE THIS! Higher might be needed for I2S
        recognizer.dynamic_energy_threshold = False # Static usually better for consistent env
        recognizer.pause_threshold = 0.8 # Default is usually fine
        print("Speech Recognition initialized.")
        # Perform initial ambient noise adjustment
        with microphone as source:
            print("Adjusting for ambient noise (please be quiet)...")
            recognizer.adjust_for_ambient_noise(source, duration=1.5) # Longer duration might help
            print(f"Ambient noise adjustment complete. Threshold set to: {recognizer.energy_threshold:.2f}")
        return True
    except Exception as e:
        print(f"Error initializing audio systems: {e}")
        if mixer_initialized: mixer.quit()
        return False

# --- NEW: Microphone finder ---
def find_mic_index(keyword):
    """Finds the index of a microphone containing the keyword."""
    print("Available microphones:")
    mic_list = sr.Microphone.list_microphone_names()
    for index, name in enumerate(mic_list):
        print(f"  Index {index}: {name}")
        if keyword.lower() in name.lower():
            print(f"--> Found target microphone '{name}' at index {index}")
            return index
    print(f"Warning: Microphone containing '{keyword}' not found.")
    return None
# --- End Microphone finder ---

def speak_text(text):
    """Convert text to speech and play it."""
    if not mixer_initialized:
        print("Error: Mixer not initialized, cannot speak.")
        return
    if not text: # Avoid errors with empty strings
        print("Warning: speak_text called with empty string.")
        return
    try:
        print(f"ASSISTANT SPEAKING: {text}")
        log_conversation("Assistant", text)

        mp3file = BytesIO()
        tts = gTTS(text=text, lang="en", tld='com', slow=False)
        tts.write_to_fp(mp3file)
        mp3file.seek(0)

        # Ensure previous playback stopped (less critical with short TTS)
        if mixer.music.get_busy():
             mixer.music.stop()
             time.sleep(0.05)

        mixer.music.load(mp3file, "mp3")
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.1)
        mp3file.close()
    except Exception as e:
        print(f"Error during TTS or playback: {e}")
        # Attempt to stop mixer music in case of error
        try: mixer.music.stop()
        except Exception: pass

def log_conversation(speaker, text):
    """Appends a line to the conversation log file."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(CONVERSATION_LOG_FILE, "a", encoding='utf-8') as f:
            f.write(f"[{timestamp}] {speaker}: {text}\n")
    except Exception as e:
        print(f"Error writing to conversation log: {e}")

def check_stop_flag():
    """Checks if the stop flag file exists."""
    return os.path.exists(STOP_FLAG_FILE)

def cleanup():
    """Cleanup resources."""
    print("\nCleaning up voice control...")
    if mixer_initialized:
        mixer.quit()
    if os.path.exists(STOP_FLAG_FILE):
        try:
            os.remove(STOP_FLAG_FILE)
            print("Removed stop flag file.")
        except OSError as e: print(f"Error removing stop flag file: {e}")
    # Let ninja_core handle its own cleanup
    ninja_core.cleanup_all()
    print("Voice control cleanup finished.")

# --- Main Loop (Modified) ---
def main():
    global recognizer, microphone

    print("--- Initializing Robot Core (Hardware & AI) ---")
    if not ninja_core.initialize_gemini():
        print("CRITICAL: Failed to initialize Gemini. Exiting.")
        sys.exit(1)
    if not ninja_core.initialize_hardware():
        # Hardware init plays startup sound and does hello move now
        print("CRITICAL: Failed to initialize Hardware. Exiting.")
        sys.exit(1) # Exit if hardware fails

    if not initialize_audio_systems():
        print("CRITICAL: Failed to initialize Audio Systems. Exiting.")
        ninja_core.cleanup_all() # Cleanup core if audio fails
        sys.exit(1)

    print(f"\n--- Ninja Voice Control Ready ---")
    # Startup sequence (sound + move) is now handled in ninja_core.initialize_hardware()
    # speak_text("Ninja robot ready.") # Optional additional verbal confirmation
    log_conversation("System", "Ninja robot ready and listening.")

    # --- Continuous Listening Loop (Requirement 1) ---
    while True:
        if check_stop_flag():
            print("Stop flag detected. Exiting...")
            speak_text("Stopping voice control.")
            break

        print(f"\nListening... (Timeout: {LISTEN_TIMEOUT}s)")
        with microphone as source:
            # Optional: Adjust periodically if noise level changes significantly
            # recognizer.adjust_for_ambient_noise(source, duration=0.2)
            try:
                # Listen for audio within the timeout
                audio = recognizer.listen(source, timeout=LISTEN_TIMEOUT, phrase_time_limit=PHRASE_TIME_LIMIT)
                print("Got audio, recognizing...")

                # Recognize speech
                transcript = recognizer.recognize_google(audio) # Keep original case
                print(f"Heard: '{transcript}'")
                log_conversation("User", transcript) # Log what user said

                # --- Process Transcript with Ninja Core ---
                # ninja_core handles whether it's a command or question
                print("Processing input with ninja_core...")
                result = ninja_core.process_user_input(transcript) # Pass the full transcript

                # --- Handle Core Response ---
                if not result:
                     print("Error: Received no result from ninja_core.")
                     speak_text("Sorry, I encountered an internal error.")
                     continue

                result_type = result.get("type")

                if result_type == "answer":
                    # Gemini provided a text answer to a question
                    speak_text(result.get("text", "I have no answer for that."))

                elif result_type == "action":
                    # Gemini interpreted a command and returned action data
                    action_data = result.get("data")
                    if action_data:
                        print(f"Executing action based on interpretation: {action_data}")
                        # Log the intended action
                        log_conversation("Assistant", f"Understood. Executing: {action_data}")
                        ninja_core.execute_action(action_data) # Core handles sound + move
                        # Optional: Confirmation after execution
                        # speak_text("Okay.")
                        # ninja_core.play_robot_sound('yes')
                    else:
                        print("Error: Action type specified but no action data found.")
                        speak_text("Sorry, I couldn't figure out how to do that.")

                elif result_type == "error":
                    # Gemini or Core reported an error
                    error_text = result.get("text", "I encountered an error.")
                    print(f"Processing Error: {error_text}")
                    speak_text(f"Sorry, {error_text}")

                else:
                    # Unknown result type from core
                    print(f"Error: Unknown result type '{result_type}' from ninja_core.")
                    speak_text("Sorry, something went wrong internally.")

                # Short pause after processing before listening again
                time.sleep(0.5)

            except sr.WaitTimeoutError:
                # No speech detected within the timeout - THIS IS NORMAL
                print(" - No speech detected, listening again. -")
                continue # Loop back to listen immediately
            except sr.UnknownValueError:
                print("Could not understand audio, please try again.")
                # Optional: provide audio/verbal feedback
                # speak_text("Sorry, I didn't catch that.")
                # ninja_core.play_robot_sound('no')
                pass # Loop back and listen
            except sr.RequestError as e:
                print(f"Could not request results from Speech Recognition service; {e}")
                speak_text("Sorry, I'm having trouble reaching the speech service.")
                time.sleep(3) # Wait longer if network issue
            except Exception as e:
                print(f"An unexpected error occurred in listen/recognize loop: {e}")
                import traceback
                traceback.print_exc()
                speak_text("Sorry, a system error occurred.")
                time.sleep(1)

# --- Entry Point ---
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Shutting down.")
    finally:
        cleanup() # Ensure cleanup runs

# --- END OF FILE Ninja_Voice_Control.py ---
