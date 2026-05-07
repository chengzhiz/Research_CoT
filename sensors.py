# sensors.py  — KEYBOARD MODE (spacebar replaces physical button)
# Drop-in replacement for the GPIO version: same user_interaction_detected() API.
# Switch back to the GPIO version when running on the Raspberry Pi.

import threading
from pynput import keyboard

# Internal flag: set to True whenever spacebar is pressed
_space_pressed = False
_listener_started = False
_lock = threading.Lock()

def _on_press(key):
    """pynput callback — fires in its own thread."""
    global _space_pressed
    if key == keyboard.Key.space:
        with _lock:
            _space_pressed = True
        print("[DEBUG] Spacebar pressed — simulating button press")

def _start_listener():
    """Start the background keyboard listener once."""
    global _listener_started
    if not _listener_started:
        _listener_started = True
        listener = keyboard.Listener(on_press=_on_press)
        listener.daemon = True
        listener.start()
        print("[Sensor] Keyboard mode active — press SPACE to simulate button press.")

# Auto-start listener when this module is imported
_start_listener()


def user_interaction_detected():
    """Return True once per spacebar press (clears the flag after reading).

    Mirrors the one-shot debounce behaviour of the GPIO button version:
    each press triggers exactly one interaction event.
    """
    global _space_pressed
    with _lock:
        if _space_pressed:
            _space_pressed = False  # Consume the event
            return True
    return False