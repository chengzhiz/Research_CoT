import os
import time
import threading
from rpi_ws281x import PixelStrip, Color
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio


# LED strip configuration:
LED_COUNT = 30      # Number of LEDs in the strip (adjust this to your setup)
LED_PIN = 18        # GPIO pin connected to the LED strip (must support PWM on Raspberry Pi)
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800kHz)
LED_DMA = 10        # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255 # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (depends on your setup)
LED_CHANNEL = 0     # Set to 0 for GPIO 18, 1 for GPIO 10

# Create PixelStrip object with the above configuration:
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

# Initialize the library (must be called once before using the LED strip)
strip.begin()

def control_led(mode):
    """Control LED strip for different modes like 'off', 'breathing', 'on', etc."""
    global is_breathing
    if mode == "breathing":
        print("Breathing light activated")
        is_breathing = True
        breathing_light(strip)
    elif mode == "off":
        print("LED turned off")
        is_breathing = False
        set_strip_brightness(strip, 0)  # Turn off all LEDs
    elif mode == "on":
        print("LED turned on")
        is_breathing = False
        set_strip_brightness(strip, LED_BRIGHTNESS)  # Turn on all LEDs to maximum brightness

def breathing_light(strip, wait_ms=50, max_brightness=255):
    """Create a more visible breathing light effect by smoothly changing LED brightness."""
    try:
        # Gradually increase and decrease the brightness in a breathing pattern
        while True:
            # Gradually increase brightness
            for brightness in range(0, max_brightness + 1, 10):
                set_strip_brightness(strip, brightness)
                time.sleep(wait_ms / 1000.0)

            # Gradually decrease brightness
            for brightness in range(max_brightness, -1, -10):
                set_strip_brightness(strip, brightness)
                time.sleep(wait_ms / 1000.0)

    except KeyboardInterrupt:
        # Stop and turn off LEDs when exiting the loop
        set_strip_brightness(strip, 0)

def set_strip_brightness(strip, brightness):
    """Set the brightness of the entire strip to a single color (e.g., white)."""
    color = Color(brightness, brightness, brightness)  # Grayscale color based on brightness
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
def display_on_tv(text):
    """Display text on the TV screen."""
    os.system(f"echo '{text}' > /dev/tty1")  # Replace with the appropriate command to display on your TV setup

def play_on_speaker(text):
    """Convert text to speech and play it through the speaker."""
    os.system(f'espeak "{text}"')  # You can replace 'espeak' with another TTS library if needed.


# Global flag to control playback
is_playing = False
audio_controllers = {}

def play_wav_file(file_name, loop=False, delay = 10):
    """Play a WAV file from the Assets folder with optional looping in a separate thread."""
    def play_audio():
        audio_controllers[file_name] = True
        try:
            # Construct the full file path
            file_path = os.path.join('Assets', file_name)
            # Load the WAV file
            audio = AudioSegment.from_wav(file_path)

            # Play the audio
            while audio_controllers.get(file_name, False):
                playback = _play_with_simpleaudio(audio)
                playback.wait_done()
                if not loop:
                    break
                time.sleep(delay)  # Delay of 10 seconds before playing again
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if file_name in audio_controllers:
                del audio_controllers[file_name]

    # Start the audio playback in a separate thread
    threading.Thread(target=play_audio, daemon=True).start()
    print(f"Playing {file_name}...")

def stop_playback():
    """Stop the playback of the WAV file."""
    print("Stopping playback...")
    global is_playing
    is_playing = False

def wait_for_specific_audio_to_finish(file_name):
    """Wait for a specific audio file to finish"""
    while file_name in audio_controllers:
        time.sleep(1.2)