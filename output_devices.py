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

# Global flags and controllers
is_breathing = False
audio_controllers = {}
active_playbacks = []

def control_led(mode):
    """Control LED strip for different modes like 'off', 'breathing', 'on', etc."""
    global is_breathing
    if mode == "breathing":
        print("Breathing light activated")
        if not is_breathing:
            is_breathing = True
            # Run breathing in a separate thread so it doesn't block main.py
            threading.Thread(target=breathing_light, args=(strip,), daemon=True).start()
    elif mode == "off":
        print("LED turned off")
        is_breathing = False
        set_strip_brightness(strip, 0)
    elif mode == "on":
        print("LED turned on")
        is_breathing = False
        set_strip_brightness(strip, LED_BRIGHTNESS)

def breathing_light(strip, wait_ms=50, max_brightness=255):
    """Create a breathing light effect that can be stopped via the is_breathing flag."""
    global is_breathing
    try:
        while is_breathing:
            # Gradually increase brightness
            for brightness in range(0, max_brightness + 1, 10):
                if not is_breathing: break
                set_strip_brightness(strip, brightness)
                time.sleep(wait_ms / 1000.0)

            # Gradually decrease brightness
            for brightness in range(max_brightness, -1, -10):
                if not is_breathing: break
                set_strip_brightness(strip, brightness)
                time.sleep(wait_ms / 1000.0)
    finally:
        set_strip_brightness(strip, 0)

def set_strip_brightness(strip, brightness):
    """Set the brightness of the entire strip to a single color (e.g., white)."""
    color = Color(brightness, brightness, brightness)
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def display_on_tv(text):
    """Display text on the TV screen."""
    os.system(f"echo '{text}' > /dev/tty1")

def play_on_speaker(text):
    """Convert text to speech and play it through the speaker."""
    os.system(f'espeak "{text}"')


def play_wav_file(file_name, loop=False, delay=10):
    """Play a WAV file with explicit tracking of the playback object for immediate stopping."""
    def play_audio():
        audio_controllers[file_name] = True
        try:
            file_path = os.path.join('Assets', file_name)
            if not os.path.exists(file_path):
                print(f"Error: File {file_path} not found.")
                return

            audio = AudioSegment.from_wav(file_path)

            while audio_controllers.get(file_name, False):
                playback = _play_with_simpleaudio(audio)
                active_playbacks.append(playback)

                # wait_done() blocks this thread, but we can now stop 'playback' from elsewhere
                playback.wait_done()

                if playback in active_playbacks:
                    active_playbacks.remove(playback)

                if not loop or not audio_controllers.get(file_name, False):
                    break
                time.sleep(delay)
        except Exception as e:
            print(f"Playback error: {e}")
        finally:
            if file_name in audio_controllers:
                del audio_controllers[file_name]

    threading.Thread(target=play_audio, daemon=True).start()
    print(f"Playing {file_name}...")

def stop_playback():
    """Immediately stop all active audio playback."""
    print("Stopping playback...")
    audio_controllers.clear() # Prevent loops from restarting
    for playback in list(active_playbacks):
        try:
            playback.stop() # Kill the current sound
        except:
            pass
    active_playbacks.clear()

def wait_for_specific_audio_to_finish(file_name):
    """Wait for a specific audio file to finish"""
    while file_name in audio_controllers:
        time.sleep(0.5)
