# sensors.py
import RPi.GPIO as GPIO
import time

# Button Pin (change from PIR_PIN)
BUTTON_PIN = 17  # Same pin, or choose another like 18, 22, etc.

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Important: add pull-up
print("Waiting for button to be ready...")

def user_interaction_detected():
    """Detect if button is pressed (with debounce)."""
    print("Checking for user interaction...")
    if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # LOW means pressed (with pull-up)
        time.sleep(0.03)  # Wait 30ms debounce window
        return GPIO.input(BUTTON_PIN) == GPIO.LOW  # Confirm still pressed
    return False