import speech_recognition as sr
import pyttsx3  # Optional, for text-to-speech output

# Initialize the recognizer
recognizer = sr.Recognizer()


def recognize_speech_from_mic():
    """Capture voice input from the microphone and convert it to text."""
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for your command...")

        try:
            audio = recognizer.listen(source) # now it has a 0.8 second default period
            #  audio = recognizer.listen(source, phrase_time_limit=5)  # Set time limit to stop after silence

            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        return None


def text_to_speech(text):
    """Convert text to speech."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()