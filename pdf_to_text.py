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
"""

import os
import re
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

# ---- CONFIGURATION ----
# Edit this to point to your PDF directory
INPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "page_scraper_downloads")

LOG_PATH = os.path.join(INPUT_DIR, "progress_pdf_ocr.log")
OCR_LANGUAGES = "eng"  # Change to "jpn+eng" for Japanese + English, "fra" for French, etc.


def log(message: str):
    print(message)
    os.makedirs(INPUT_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
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


def main():
    if not os.path.isdir(INPUT_DIR):
        log(f"Could not find folder: {INPUT_DIR}")
        return

    log("=== Starting PDF OCR run ===")
    log(f"Reading PDFs from: {INPUT_DIR}")
    log(f"OCR Language: {OCR_LANGUAGES}")

    for root, dirs, files in os.walk(INPUT_DIR):
        has_pdfs = any(f.lower().endswith(".pdf") for f in files)
        if has_pdfs:
            folder_name = os.path.basename(root)
            process_folder(root, folder_name)

    log("\n=== PDF OCR run complete ===")


if __name__ == "__main__":
    main()
