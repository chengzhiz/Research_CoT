# sensors.py
import RPi.GPIO as GPIO
import time

# Button Pin
BUTTON_PIN = 17
# LED inside/next to button (lit when idle, off when pressed)
BUTTON_LED_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_LED_PIN, GPIO.OUT)
GPIO.output(BUTTON_LED_PIN, GPIO.HIGH)  # LED on at startup
print("Waiting for button to be ready...")

def user_interaction_detected():
    """Detect if button is pressed (with debounce).
    PUD_DOWN + button to 3.3V: pressed=HIGH, released=LOW.
    LED is ON at rest, turns OFF when pressed.
    """
    raw = GPIO.input(BUTTON_PIN)
    print(f"[DEBUG] GPIO pin {BUTTON_PIN} raw value: {raw} (1=HIGH/pressed, 0=LOW/rest)")
    if raw == GPIO.HIGH:  # HIGH means pressed (button connects to 3.3V)
        time.sleep(0.03)  # Wait 30ms debounce window
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:  # Confirm still pressed
            GPIO.output(BUTTON_LED_PIN, GPIO.LOW)   # Turn LED off
            return True
    else:
        GPIO.output(BUTTON_LED_PIN, GPIO.HIGH)      # LED on when not pressed
    return False