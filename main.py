import time
import threading
from sensors import user_interaction_detected
from chatgpt_interface import ask_chatgpt
from output_devices import control_led, play_wav_file, stop_playback, wait_for_specific_audio_to_finish
from voice_recognition import recognize_speech_from_mic



import tkinter as tk
from tkinter import scrolledtext
class TerminalUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal UI")
        self.root.geometry("480x320")  # Set the resolution to 480x320

        # Create a scrolled text widget with black background and white text
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20, font=("Courier", 40), bg="black", fg="white")
        self.text_area.pack(padx=100, pady=10)

        # Disable editing
        self.text_area.config(state=tk.DISABLED)

    def append_text(self, text, prefix=""):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, f"{prefix}{text}\n")
        self.text_area.config(state=tk.DISABLED)
        self.text_area.yview(tk.END)  # Auto-scroll to the end

    def clear_text(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)

def get_sound_file_from_answer(answer):
    answer = answer.lower()
    if "yes" in answer:
        return "yes.wav"
    if "don't know" in answer or "idk" in answer:
        return "idk.wav"
    if "no" in answer:
        return "no.wav"
    if "none" in answer:
        return "none.wav"
    return "none.wav" # as a fallback

def main():
    root = tk.Tk()
    terminal_ui = TerminalUI(root)

    terminal_ui.append_text("System starting...")

    def run():
        last_was_else = False
        while True:
            if user_interaction_detected():
                #clear the terminal all the past text, all clean
                terminal_ui.clear_text()
                terminal_ui.append_text("Please ask a yes-or-no question, I'm listening...\n")
                control_led("on")  # Turn on LED light when user interaction is detected.
                stop_playback()  # Stop any ongoing playback
                user_input = recognize_speech_from_mic()
                if user_input:
                    terminal_ui.append_text(user_input + "?\n", prefix="User: ")
                    # Stop recognition and process the text with GPT
                    terminal_ui.append_text("Processing user input with GPT...\n")
                    # program only continues after getting gpt responses
                    response = ask_chatgpt(user_input) 
                    print(response)

                    # return the correctly mapped file name
                    terminal_ui.append_text("GPT: " + response['answer'] + '\n')
                    answer_sound_file = get_sound_file_from_answer(response['answer']) 
                    try:
                        terminal_ui.append_text("Category: " + response['category_name'] + '\n')
                    except KeyError:
                        # do nothing
                        pass
                    try:
                        #terminal_ui.append_text('Justification: ' + categories['category_name'] + '\n')
                        terminal_ui.append_text('Justification: ' + response['justification'] + '\n')
                    except KeyError:
                        # do nothing
                        pass
                    play_wav_file(answer_sound_file, delay = 2)
                    wait_for_specific_audio_to_finish(answer_sound_file)
                    try:
                        category_name = response['category_name']
                        category_sound_file = category_name[0] + ".wav"
                        play_wav_file(category_sound_file, delay = 5)
                        wait_for_specific_audio_to_finish(category_sound_file)
                    except KeyError:
                        pass
                time.sleep(10)  # Add a small delay to avoid rapid looping
                last_was_else = False
            else:
                terminal_ui.append_text("No user interaction detected.")
                # make the remain part into thread from control led to play wav file
                def else_run():
                    control_led("breathing")  # Revert to breathing light if no user interaction is detected.
                    stop_playback()  # Stop any ongoing playback
                    # Play loop sound to attract attention
                    play_wav_file("intro.wav", loop=True)

                if not last_was_else:
                    threading.Thread(target=else_run, daemon=True).start()
                    last_was_else = True

            play_wav_file("intro.wav", loop=False)
            print("looping")
            time.sleep(10)

    # Run the main loop in a separate thread to keep the GUI responsive
    threading.Thread(target=run, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()
