#!/usr/bin/env python3
"""
YouTube to CSV - GUI
--------------------
Paste a YouTube playlist or video URL, pick where to save the CSV, and click Start.
Uses the same logic as youtube_to_csv.py.

USAGE:
    python3 youtube_to_csv_gui.py
"""

import csv
import os
import queue
import threading
from tkinter import Tk, Label, Entry, Button, Frame, Text, Scrollbar, filedialog, messagebox
from tkinter import END, LEFT, RIGHT, BOTH, X

from youtube_to_csv import CSV_COLUMNS, list_entries, build_row


class YouTubeToCsvGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube to CSV")
        self.root.geometry("700x520")
        self.root.configure(bg="#ffffff")
        self.root.attributes("-topmost", True)

        self.messages = queue.Queue()
        self.worker = None

        self.setup_ui()
        self.root.after(100, self.poll_messages)

    def setup_ui(self):
        Label(
            self.root, text="YouTube to CSV", font=("Arial", 16, "bold"),
            fg="#000000", bg="#ffffff"
        ).pack(pady=10)

        url_frame = Frame(self.root, bg="#ffffff")
        url_frame.pack(fill=X, padx=15, pady=5)
        Label(
            url_frame, text="URL:", font=("Arial", 11), fg="#000000", bg="#ffffff"
        ).pack(side=LEFT, padx=5)
        self.url_entry = Entry(url_frame, font=("Arial", 11), fg="#000000", bg="#ffffff")
        self.url_entry.pack(side=LEFT, fill=X, expand=True, padx=5)

        out_frame = Frame(self.root, bg="#ffffff")
        out_frame.pack(fill=X, padx=15, pady=5)
        Label(
            out_frame, text="Save to:", font=("Arial", 11), fg="#000000", bg="#ffffff"
        ).pack(side=LEFT, padx=5)
        self.output_entry = Entry(out_frame, font=("Arial", 11), fg="#000000", bg="#ffffff")
        self.output_entry.insert(0, os.path.expanduser("~/Desktop/videos.csv"))
        self.output_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        Button(
            out_frame, text="Choose...", font=("Arial", 10, "bold"),
            bg="#2196F3", fg="white", activebackground="#0b7dda",
            activeforeground="white", relief="raised", bd=2,
            command=self.choose_output
        ).pack(side=LEFT, padx=5)

        self.start_button = Button(
            self.root, text="START", font=("Arial", 14, "bold"), width=20,
            bg="#4CAF50", fg="white", activebackground="#45a049",
            activeforeground="white", relief="raised", bd=3,
            command=self.start
        )
        self.start_button.pack(pady=10)

        log_frame = Frame(self.root, bg="#ffffff")
        log_frame.pack(fill=BOTH, expand=True, padx=15, pady=5)
        scrollbar = Scrollbar(log_frame)
        scrollbar.pack(side=RIGHT, fill="y")
        self.log = Text(
            log_frame, font=("Courier", 10), fg="#000000", bg="#f7f7f7",
            yscrollcommand=scrollbar.set, height=14, wrap="word"
        )
        self.log.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.log.yview)

        self.status = Label(
            self.root, text="Ready", font=("Arial", 10), fg="#4CAF50", bg="#ffffff"
        )
        self.status.pack(pady=5)

    def choose_output(self):
        path = filedialog.asksaveasfilename(
            title="Save CSV as", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if path:
            self.output_entry.delete(0, END)
            self.output_entry.insert(0, path)

    def start(self):
        url = self.url_entry.get().strip()
        output = os.path.expanduser(self.output_entry.get().strip())

        if not url:
            messagebox.showwarning("Missing URL", "Paste a YouTube playlist or video URL first.")
            return
        if not output:
            messagebox.showwarning("Missing file", "Choose where to save the CSV.")
            return

        self.start_button.config(state="disabled", text="RUNNING...")
        self.log.delete(1.0, END)
        self.status.config(text="Working...", fg="#2196F3")

        self.worker = threading.Thread(target=self.run_job, args=(url, output), daemon=True)
        self.worker.start()

    def run_job(self, url, output):
        try:
            self.messages.put(("log", "Reading playlist..."))
            entries = list_entries(url)
            self.messages.put(("log", f"Found {len(entries)} video(s)"))

            rows, failed = [], []
            for order, (video_id, video_url) in enumerate(entries, start=1):
                self.messages.put(("log", f"[{order}/{len(entries)}] {video_id}"))
                try:
                    rows.append(build_row(order, video_id, video_url))
                except Exception as e:
                    failed.append(video_id)
                    self.messages.put(("log", f"  skipped: {e}"))

            os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
            with open(output, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                writer.writerows(rows)

            missing = sum(1 for r in rows if not r["transcript"])
            summary = (
                "\nSummary\n"
                f"  Found:              {len(entries)}\n"
                f"  Saved:              {len(rows)} -> {output}\n"
                f"  Missing transcript: {missing}\n"
                f"  Skipped (errors):   {len(failed)}"
            )
            self.messages.put(("done", summary))
        except Exception as e:
            self.messages.put(("error", str(e)))

    def poll_messages(self):
        try:
            while True:
                kind, text = self.messages.get_nowait()
                if kind == "log":
                    self.log.insert(END, text + "\n")
                    self.log.see(END)
                elif kind == "done":
                    self.log.insert(END, text + "\n")
                    self.log.see(END)
                    self.finish("Done", "#4CAF50")
                elif kind == "error":
                    self.log.insert(END, f"Error: {text}\n")
                    self.finish("Failed", "#f44336")
        except queue.Empty:
            pass
        self.root.after(100, self.poll_messages)

    def finish(self, status_text, color):
        self.start_button.config(state="normal", text="START")
        self.status.config(text=status_text, fg=color)


def main():
    root = Tk()
    YouTubeToCsvGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
