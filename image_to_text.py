#!/usr/bin/env python3
"""
OCR Image-to-Text Extractor
----------------------------
Walks through a directory, finds all image files, runs OCR (text recognition)
on each one, and saves the extracted text as .txt files.

Creates two types of outputs:
    1. Individual .txt file per image
    2. Combined _FULL_TEXT.txt for each directory

SETUP (run once):
    1. Install the Tesseract OCR engine (not a pip package):
         Mac:     brew install tesseract tesseract-lang
         Windows: download & run the installer from
                  https://github.com/UB-Mannheim/tesseract/wiki

    2. Install the Python packages:
         pip install pytesseract pillow

RUN:
    python image_to_text.py

A folder picker popup will appear—select your folder with images.
"""

import os
import re
import pytesseract
from PIL import Image
from tkinter import Tk, filedialog, Button, Label, Listbox

# Language options for OCR
LANGUAGE_OPTIONS = {
    "English": "eng",
    "Japanese": "jpn",
    "Japanese + English": "jpn+eng",
    "French": "fra",
    "German": "deu",
    "Spanish": "spa",
    "Chinese (Simplified)": "chi_sim",
}

OCR_LANGUAGES = "eng"  # Default, will be set by user

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def print_progress(current: int, total: int, filename: str = ""):
    """Print a nice progress bar."""
    if total == 0:
        return

    percent = (current / total) * 100
    bar_length = 40
    filled = int((current / total) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)

    status = f"{current}/{total}"
    file_info = f" - {filename}" if filename else ""
    print(f"\r[{bar}] {percent:.0f}% ({status}){file_info}", end="", flush=True)

    if current == total:
        print()  # New line when complete


def natural_sort_key(filename: str):
    """Sort filenames numerically (so _02 sorts before _10, not after)."""
    parts = re.split(r"(\d+)", filename)
    return [int(p) if p.isdigit() else p for p in parts]


def ocr_image(image_path: str) -> str:
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=OCR_LANGUAGES)
        return text.strip()
    except Exception as e:
        log(f"    FAILED to OCR {os.path.basename(image_path)}: {e}")
        return ""


def process_folder(folder_path: str, folder_name: str):
    log(f"\nProcessing: {folder_name}")

    image_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(IMAGE_EXTENSIONS)
    ]
    image_files.sort(key=natural_sort_key)

    if not image_files:
        log("  no images found here")
        return

    combined_text_parts = []

    for idx, image_file in enumerate(image_files, 1):
        print_progress(idx, len(image_files), image_file)

        image_path = os.path.join(folder_path, image_file)
        txt_filename = os.path.splitext(image_file)[0] + ".txt"
        txt_path = os.path.join(folder_path, txt_filename)

        if os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
            with open(txt_path, "r", encoding="utf-8") as f:
                combined_text_parts.append(f.read())
            continue

        text = ocr_image(image_path)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        combined_text_parts.append(text)

    combined_path = os.path.join(folder_path, f"{folder_name}_FULL_TEXT.txt")
    with open(combined_path, "w", encoding="utf-8") as f:
        f.write("\n\n----- page break -----\n\n".join(combined_text_parts))
    log(f"  combined text saved -> {combined_path}")


def ask_language() -> str:
    """Ask user which language to use for OCR."""
    root = Tk()
    root.title("OCR Language")
    root.geometry("300x350")
    root.attributes('-topmost', True)
    root.resizable(False, False)

    selected = [None]

    Label(root, text="Select OCR Language:", font=("Arial", 14, "bold")).pack(pady=10)

    # Listbox with languages
    listbox = Listbox(root, font=("Arial", 11), height=10, width=35)
    listbox.pack(pady=10, padx=10)

    for lang_name in LANGUAGE_OPTIONS.keys():
        listbox.insert(len(listbox.get(0, "end")), lang_name)

    # Select button
    def select_language():
        selection = listbox.curselection()
        if selection:
            lang_name = listbox.get(selection[0])
            selected[0] = LANGUAGE_OPTIONS[lang_name]
        root.destroy()

    Button(
        root,
        text="Select",
        font=("Arial", 12),
        bg="#4CAF50",
        fg="white",
        command=select_language
    ).pack(pady=10)

    root.mainloop()

    return selected[0] if selected[0] else "eng"


def get_folder_from_user() -> str:
    """Show a folder picker popup and return the selected path."""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title="Select folder with images")
    root.destroy()
    return folder_path


def setup_logging(input_dir: str):
    """Set up log file in the selected directory."""
    log_path = os.path.join(input_dir, "progress_ocr.log")
    return log_path


def log(message: str):
    print(message)
    if hasattr(log, 'path') and log.path:
        os.makedirs(os.path.dirname(log.path), exist_ok=True)
        with open(log.path, "a", encoding="utf-8") as f:
            f.write(message + "\n")


def main():
    global OCR_LANGUAGES

    print("Select OCR language...\n")
    OCR_LANGUAGES = ask_language()
    print(f"Selected language: {OCR_LANGUAGES}\n")

    print("Select a folder with images...\n")
    input_dir = get_folder_from_user()

    if not input_dir:
        print("No folder selected. Exiting.")
        return

    if not os.path.isdir(input_dir):
        print(f"Could not find folder: {input_dir}")
        return

    log.path = os.path.join(input_dir, "progress_ocr.log")

    log(f"=== Starting OCR run ===")
    log(f"Reading images from: {input_dir}")
    log(f"OCR Language: {OCR_LANGUAGES}")

    for root, dirs, files in os.walk(input_dir):
        has_images = any(f.lower().endswith(IMAGE_EXTENSIONS) for f in files)
        if has_images:
            folder_name = os.path.basename(root)
            process_folder(root, folder_name)

    log(f"\n=== OCR run complete ===")


if __name__ == "__main__":
    main()
