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
"""

import os
import re
import pytesseract
from PIL import Image

# ---- CONFIGURATION ----
# Edit this to point to your image directory
INPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "page_scraper_downloads")

LOG_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "page_scraper_downloads", "progress_ocr.log")
OCR_LANGUAGES = "eng"  # Change to "jpn+eng" for Japanese + English, "fra" for French, etc.

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def log(message: str):
    print(message)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(message + "\n")


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

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        txt_filename = os.path.splitext(image_file)[0] + ".txt"
        txt_path = os.path.join(folder_path, txt_filename)

        if os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
            log(f"  already processed {image_file}, skipping")
            with open(txt_path, "r", encoding="utf-8") as f:
                combined_text_parts.append(f.read())
            continue

        log(f"  processing {image_file} ...")
        text = ocr_image(image_path)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        combined_text_parts.append(text)

    combined_path = os.path.join(folder_path, f"{folder_name}_FULL_TEXT.txt")
    with open(combined_path, "w", encoding="utf-8") as f:
        f.write("\n\n----- page break -----\n\n".join(combined_text_parts))
    log(f"  combined text saved -> {combined_path}")


def main():
    if not os.path.isdir(INPUT_DIR):
        log(f"Could not find folder: {INPUT_DIR}")
        log("Edit INPUT_DIR at the top of this script if your images are elsewhere.")
        return

    log(f"=== Starting OCR run ===")
    log(f"Reading images from: {INPUT_DIR}")
    log(f"OCR Language: {OCR_LANGUAGES}")

    for root, dirs, files in os.walk(INPUT_DIR):
        has_images = any(f.lower().endswith(IMAGE_EXTENSIONS) for f in files)
        if has_images:
            folder_name = os.path.basename(root)
            process_folder(root, folder_name)

    log(f"\n=== OCR run complete ===")


if __name__ == "__main__":
    main()
