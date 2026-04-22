import RPi.GPIO as GPIO
import time

# Button Pin
BUTTON_PIN = 17
# LED inside/next to button
BUTTON_LED_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Your working setup
GPIO.setup(BUTTON_LED_PIN, GPIO.OUT)
GPIO.output(BUTTON_LED_PIN, GPIO.HIGH)  # LED on at startup
print("Waiting for button to be ready...")

def user_interaction_detected():
    """Detect if button is pressed (with debounce).
    PUD_UP + button to GND: pressed=LOW, released=HIGH.
    LED is ON at rest, turns OFF when pressed.
    """
    raw = GPIO.input(BUTTON_PIN)
    print(f"[DEBUG] GPIO pin {BUTTON_PIN} raw value: {raw} (1=HIGH/released, 0=LOW/pressed)")
    
    if raw == GPIO.LOW:  # LOW means pressed (button to GND)
        GPIO.output(BUTTON_LED_PIN, GPIO.LOW)  # Turn LED OFF when pressed
        time.sleep(0.03)  # Debounce window
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Confirm still pressed
            return True
        else:
            # False alarm (bounce), turn LED back on
            GPIO.output(BUTTON_LED_PIN, GPIO.HIGH)
    else:
        # Button released, LED should be on
        GPIO.output(BUTTON_LED_PIN, GPIO.HIGH)
    
    return False