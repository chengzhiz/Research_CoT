# sensors.py  — KEYBOARD MODE (spacebar replaces physical button)
# Drop-in replacement for the GPIO version: same user_interaction_detected() API.
# Switch back to the GPIO version when running on the Raspberry Pi.
#
# NOTE: pynput does NOT work when a Tkinter window owns keyboard focus.
# Instead, main.py binds root.bind('<space>', ...) and calls trigger_interaction().

import threading

# Internal flag: set to True whenever spacebar is pressed
_space_pressed = False
_lock = threading.Lock()

print("[Sensor] Keyboard mode active — click the window and press SPACE to simulate button press.")


def trigger_interaction():
    """Called by Tkinter's spacebar binding in main.py to simulate a button press."""
    global _space_pressed
    with _lock:
        _space_pressed = True
    print("[DEBUG] Spacebar pressed — simulating button press")


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