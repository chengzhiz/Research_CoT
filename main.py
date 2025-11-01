import time
import threading
from sensors import user_interaction_detected
from chatgpt_interface import ask_chatgpt
from output_devices import control_led, play_wav_file, stop_playback
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
    if "no" in answer:
        return "no.wav"
    if "none" in answer:
        return "none.wav"
    if "don't know" in answer or "idk" in answer:
        return "idk.wav"
    return "idk.wav" # as a fallback

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
                    response = ask_chatgpt(user_input)
                    print(response)
                    answer_sound_file = get_sound_file_from_answer(response['answer'])
                    terminal_ui.append_text("GPT: " + response['answer'] + '\n')
                    try:
                        terminal_ui.append_text("Category: " + response['category_name'] + '\n')
                    except KeyError:
                        # do nothing
                        pass
                    try:
                        categories = {
                            "1. Personal and Contextual Insight": " Chatbots do not know your personal details that they are not told, and do not understand real-life human experience; take the advice they provide with skepticism.",
                            "2. Emotions and Relationships": " Chatbots can not experience human emotions or relationships; Be skeptical when chatting about human relationships, as they could pretend to have simulated empathy.",
                            "3. Identity and Personhood": "Chatbots can roleplay different identities or personalities, but these are computational. So do not form strong emotional attachments to them.",
                            "4. Predicting the Future": "Chatbots can not accurately predict future events. Their predictions are not always right, so treat chatbots’ predictions with skepticism.",
                            "5. Medical and Legal Advice": "Chatbots’ health or legal advice is for reference only. Consult a qualified professional in these fields, especially in high-risk scenarios.",
                            "6. Sensory and Perceptual Limitations": "Chatbots operate on fewer senses than humans do. They can not interpret physical sensations like smells, tastes, and touch. Be cautious about their advice on topics where sensory experience is critical.",
                            "7. General Knowledge and Fact-Checking": "Chatbots can share general knowledge in areas like history, science, and technology, but sometimes they can go wrong or make things up. Please double-check for important facts."        
                        }
                        #terminal_ui.append_text('Justification: ' + categories['category_name'] + '\n')
                        terminal_ui.append_text('Justification: ' + response['justification'] + '\n')
                    except KeyError:
                        # do nothing
                        pass
                    play_wav_file(answer_sound_file,delay = 1)
                    # wait_for_playback_to_finish()
                    try:
                        category_name = response['category_name']
                        category_sound = category_name[0] + ".wav"
                        play_wav_file(category_sound,delay = 1)
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
                    play_wav_file("intro.wav", loop=True,delay = 10)

                if not last_was_else:
                    threading.Thread(target=else_run, daemon=True).start()
                    last_was_else = True

            play_wav_file("intro.wav", loop=False)
            print("looping")
            time.sleep(10)

    # Run the main loop in a separate thread to keep the GUI responsive
    import threading
    threading.Thread(target=run, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()
