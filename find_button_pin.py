"""
Run this on the Raspberry Pi to find which GPIO pin your button is connected to.
It scans all common GPIO pins and prints which one goes LOW when you press the button.

Usage:  python3 find_button_pin.py
"""
import RPi.GPIO as GPIO
import time

# All common usable BCM GPIO pins on a Raspberry Pi
CANDIDATE_PINS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                  16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]

GPIO.setmode(GPIO.BCM)

# Set up all pins as input with pull-up
for pin in CANDIDATE_PINS:
    try:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    except Exception:
        pass  # Skip pins that can't be set up

print("=" * 50)
print("Button pin finder — press your button now!")
print("Scanning all GPIO pins for LOW signal...")
print("Press Ctrl+C to stop.")
print("=" * 50)

try:
    while True:
        for pin in CANDIDATE_PINS:
            try:
                if GPIO.input(pin) == GPIO.LOW:
                    print(f">>> BUTTON DETECTED on BCM GPIO pin {pin}! <<<")
            except Exception:
                pass
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nDone.")
finally:
    GPIO.cleanup()
