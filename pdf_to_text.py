#!/usr/bin/env python3
"""
OCR PDF-to-Text Extractor
--------------------------
Walks through a directory, finds all PDF files, runs OCR on each page,
and saves the extracted text as .txt files.

Creates two types of outputs:
    1. Individual .txt file per PDF
    2. Combined _FULL_TEXT.txt for each directory

SETUP (run once):
    1. Install the Tesseract OCR engine (not a pip package):
         Mac:     brew install tesseract tesseract-lang
         Windows: download & run the installer from
                  https://github.com/UB-Mannheim/tesseract/wiki

    2. Install the Python packages:
         pip install pytesseract pillow pdf2image

RUN:
    python pdf_to_text.py

A folder picker popup will appear—select your folder with PDFs.
"""

import os
import re
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from tkinter import Tk, filedialog, Button, Label

OCR_LANGUAGES = "eng"  # Change to "jpn+eng" for Japanese + English, "fra" for French, etc.


def log(message: str):
    print(message)
    if hasattr(log, 'path') and log.path:
        os.makedirs(os.path.dirname(log.path), exist_ok=True)
        with open(log.path, "a", encoding="utf-8") as f:
            f.write(message + "\n")


def natural_sort_key(filename: str):
    parts = re.split(r"(\d+)", filename)
    return [int(p) if p.isdigit() else p for p in parts]


def ocr_pdf(pdf_path: str) -> str:
    """Converts PDF pages into images and runs Tesseract OCR."""
    try:
        pages = convert_from_path(pdf_path)
        extracted_pages = []

        for i, page_img in enumerate(pages, start=1):
            text = pytesseract.image_to_string(page_img, lang=OCR_LANGUAGES)
            extracted_pages.append(f"--- PAGE {i} ---\n{text.strip()}")

        return "\n\n".join(extracted_pages)
    except Exception as e:
        log(f"    FAILED to OCR PDF {os.path.basename(pdf_path)}: {e}")
        return ""


def process_folder(folder_path: str, folder_name: str):
    log(f"\nProcessing: {folder_name}")

    pdf_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(".pdf")
    ]
    pdf_files.sort(key=natural_sort_key)

    if not pdf_files:
        log("  no PDF files found here")
        return

    combined_text_parts = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        txt_filename = os.path.splitext(pdf_file)[0] + ".txt"
        txt_path = os.path.join(folder_path, txt_filename)

        if os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
            log(f"  already processed {pdf_file}, skipping")
            with open(txt_path, "r", encoding="utf-8") as f:
                combined_text_parts.append(f.read())
            continue

        log(f"  processing {pdf_file} ...")
        text = ocr_pdf(pdf_path)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        combined_text_parts.append(text)

    combined_path = os.path.join(folder_path, f"{folder_name}_FULL_TEXT.txt")
    with open(combined_path, "w", encoding="utf-8") as f:
        f.write("\n\n===== FILE BREAK =====\n\n".join(combined_text_parts))
    log(f"  combined text saved -> {combined_path}")


def ask_mode() -> str:
    """Ask user if they want to process a folder or single PDF."""
    root = Tk()
    root.title("PDF Mode")
    root.geometry("400x150")
    root.attributes('-topmost', True)
    root.resizable(False, False)

    mode = [None]

    Label(root, text="How do you want to process PDFs?", font=("Arial", 14, "bold")).pack(pady=15)

    def choose_folder():
        mode[0] = "folder"
        root.destroy()

    def choose_single():
        mode[0] = "single"
        root.destroy()

    Button(
        root,
        text="Process Folder",
        font=("Arial", 12),
        width=20,
        bg="#4CAF50",
        fg="white",
        command=choose_folder
    ).pack(pady=10)

    Button(
        root,
        text="Process Single PDF",
        font=("Arial", 12),
        width=20,
        bg="#2196F3",
        fg="white",
        command=choose_single
    ).pack(pady=10)

    root.mainloop()

    return mode[0] if mode[0] else "folder"


def get_folder_from_user() -> str:
    """Show a folder picker popup and return the selected path."""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title="Select folder with PDFs")
    root.destroy()
    return folder_path


def get_pdf_from_user() -> str:
    """Show a file picker popup to select a single PDF."""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    pdf_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    root.destroy()
    return pdf_path


def process_single_pdf(pdf_path: str):
    """Process a single PDF file."""
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    output_dir = os.path.dirname(pdf_path)
    log.path = os.path.join(output_dir, "progress_pdf_ocr.log")

    log("=== Starting Single PDF OCR ===")
    log(f"Processing: {os.path.basename(pdf_path)}")
    log(f"OCR Language: {OCR_LANGUAGES}")

    pdf_filename = os.path.basename(pdf_path)
    txt_filename = os.path.splitext(pdf_filename)[0] + ".txt"
    txt_path = os.path.join(output_dir, txt_filename)

    if os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
        log(f"Already OCR'd {pdf_filename}, skipping")
        return

    log(f"  OCR'ing {pdf_filename} ...")
    text = ocr_pdf(pdf_path)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    log(f"\n✓ Text saved -> {txt_filename}")
    log("=== Complete ===")


def main():
    print("Choose mode...\n")
    mode = ask_mode()

    if mode == "single":
        print("Select a PDF file...\n")
        pdf_path = get_pdf_from_user()

        if not pdf_path:
            print("No file selected. Exiting.")
            return

        process_single_pdf(pdf_path)

    else:
        print("Select a folder with PDFs...\n")
        input_dir = get_folder_from_user()

        if not input_dir:
            print("No folder selected. Exiting.")
            return

        if not os.path.isdir(input_dir):
            print(f"Could not find folder: {input_dir}")
            return

        log.path = os.path.join(input_dir, "progress_pdf_ocr.log")

        log("=== Starting PDF OCR run ===")
        log(f"Reading PDFs from: {input_dir}")
        log(f"OCR Language: {OCR_LANGUAGES}")

        for root, dirs, files in os.walk(input_dir):
            has_pdfs = any(f.lower().endswith(".pdf") for f in files)
            if has_pdfs:
                folder_name = os.path.basename(root)
                process_folder(root, folder_name)

        log("\n=== PDF OCR run complete ===")


if __name__ == "__main__":
    main()
