#!/usr/bin/env python3
"""
Text to Speech Reader
--------------------
Convert text to audio with a simple GUI.
Read text from clipboard, files, or paste text directly.

SETUP (run once):
    pip install pyttsx3

USAGE:
    python text_to_speech.py

Features:
- Type or paste text and click "Speak"
- Adjust speed and volume
- Load text from files
- Save text to file
"""

import pyttsx3
from tkinter import Tk, Button, Label, Frame, Text, Scrollbar, Scale, filedialog, messagebox
from tkinter import END, BOTH, LEFT, RIGHT, VERTICAL
import os
import threading


class TextToSpeechGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech Reader")
        self.root.geometry("700x600")
        self.root.configure(bg="#ffffff")
        self.root.resizable(True, True)
        self.root.attributes('-topmost', True)

        self.engine = pyttsx3.init()
        self.is_speaking = False

        self.setup_ui()

    def setup_ui(self):
        """Create the GUI layout."""
        # Title
        Label(
            self.root,
            text="Text to Speech Reader",
            font=("Arial", 16, "bold"),
            fg="#000000",
            bg="#ffffff"
        ).pack(pady=10)

        # Control buttons frame
        control_frame = Frame(self.root, bg="#ffffff")
        control_frame.pack(pady=5, padx=10, fill="x")

        Button(
            control_frame,
            text="Load File",
            font=("Arial", 10, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#0b7dda",
            activeforeground="white",
            relief="raised",
            bd=2,
            command=self.load_file
        ).pack(side=LEFT, padx=5)

        Button(
            control_frame,
            text="Save Text",
            font=("Arial", 10, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#0b7dda",
            activeforeground="white",
            relief="raised",
            bd=2,
            command=self.save_file
        ).pack(side=LEFT, padx=5)

        Button(
            control_frame,
            text="Clear",
            font=("Arial", 10, "bold"),
            bg="#FF9800",
            fg="white",
            activebackground="#e68900",
            activeforeground="white",
            relief="raised",
            bd=2,
            command=self.clear_text
        ).pack(side=LEFT, padx=5)

        Button(
            control_frame,
            text="Stop",
            font=("Arial", 10, "bold"),
            bg="#f44336",
            fg="white",
            activebackground="#da190b",
            activeforeground="white",
            relief="raised",
            bd=2,
            command=self.stop_speaking
        ).pack(side=LEFT, padx=5)

        # Text area with scrollbar
        text_frame = Frame(self.root, bg="#ffffff")
        text_frame.pack(pady=10, padx=10, fill=BOTH, expand=True)

        scrollbar = Scrollbar(text_frame)
        scrollbar.pack(side=RIGHT, fill="y")

        self.text_input = Text(
            text_frame,
            font=("Arial", 11),
            fg="#000000",
            bg="#ffffff",
            yscrollcommand=scrollbar.set,
            height=15,
            wrap="word"
        )
        self.text_input.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.text_input.yview)

        # Speed and volume controls
        control_frame2 = Frame(self.root, bg="#ffffff")
        control_frame2.pack(pady=5, padx=10, fill="x")

        Label(
            control_frame2,
            text="Speed:",
            font=("Arial", 10),
            fg="#000000",
            bg="#ffffff"
        ).pack(side=LEFT, padx=5)

        self.speed_slider = Scale(
            control_frame2,
            from_=50,
            to=300,
            orient="horizontal",
            bg="#ffffff",
            fg="#000000",
            troughcolor="#f0f0f0"
        )
        self.speed_slider.set(150)
        self.speed_slider.pack(side=LEFT, padx=5)

        Label(
            control_frame2,
            text="Volume:",
            font=("Arial", 10),
            fg="#000000",
            bg="#ffffff"
        ).pack(side=LEFT, padx=5)

        self.volume_slider = Scale(
            control_frame2,
            from_=0,
            to=100,
            orient="horizontal",
            bg="#ffffff",
            fg="#000000",
            troughcolor="#f0f0f0"
        )
        self.volume_slider.set(100)
        self.volume_slider.pack(side=LEFT, padx=5)

        # Speak button
        Button(
            self.root,
            text="SPEAK",
            font=("Arial", 14, "bold"),
            width=30,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief="raised",
            bd=3,
            command=self.speak_text
        ).pack(pady=10)

        # Status label
        self.status_label = Label(
            self.root,
            text="Ready to speak",
            font=("Arial", 10),
            fg="#4CAF50",
            bg="#ffffff"
        )
        self.status_label.pack(pady=5)

    def load_file(self):
        """Load text from a file."""
        file_path = filedialog.askopenfilename(
            title="Load text file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.text_input.delete(1.0, END)
                    self.text_input.insert(1.0, content)
                    self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}", fg="#4CAF50")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def save_file(self):
        """Save text to a file."""
        text = self.text_input.get(1.0, END).strip()

        if not text:
            messagebox.showwarning("Warning", "No text to save")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save text file",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                    self.status_label.config(text=f"Saved: {os.path.basename(file_path)}", fg="#4CAF50")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def clear_text(self):
        """Clear the text area."""
        self.text_input.delete(1.0, END)
        self.status_label.config(text="Text cleared", fg="#FF9800")

    def speak_text(self):
        """Speak the text in the text area."""
        text = self.text_input.get(1.0, END).strip()

        if not text:
            messagebox.showwarning("Warning", "Enter text to speak")
            return

        # Run in background thread so UI doesn't freeze
        thread = threading.Thread(target=self._speak_thread, args=(text,))
        thread.start()

    def _speak_thread(self, text):
        """Background thread for speaking."""
        try:
            self.is_speaking = True
            self.status_label.config(text="Speaking...", fg="#2196F3")
            self.root.update()

            self.engine.setProperty("rate", self.speed_slider.get())
            self.engine.setProperty("volume", self.volume_slider.get() / 100)

            self.engine.say(text)
            self.engine.runAndWait()

            self.status_label.config(text="Done speaking", fg="#4CAF50")
            self.is_speaking = False
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="#f44336")
            self.is_speaking = False

    def stop_speaking(self):
        """Stop the current speech."""
        try:
            self.engine.stop()
            self.is_speaking = False
            self.status_label.config(text="Stopped", fg="#FF9800")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop: {e}")


def main():
    root = Tk()
    app = TextToSpeechGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
