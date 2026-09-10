#!/usr/bin/env python3
"""
Folder to PDF Converter
-----------------------
Converts all images in a folder into a single PDF file.

Scans a folder for images (.png, .jpg, .jpeg, .webp, .gif),
sorts them numerically, and combines them into one PDF.

SETUP (run once):
    pip install pillow

USAGE:
    python folder_to_pdf.py

OUTPUT:
    PDF is saved in the same folder as the images with the folder name.
    e.g., ~/Desktop/my_photos/ -> ~/Desktop/my_photos.pdf
"""

import os
import re
from PIL import Image
from pathlib import Path

# ---- CONFIGURATION ----
# Edit this to point to your folder with images
FOLDER_PATH = os.path.expanduser("~/Desktop/my_photos")

# Where to save the PDF (leave as None to save in parent directory)
OUTPUT_PATH = None  # e.g., ~/Desktop/my_photos.pdf

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def natural_sort_key(filename: str):
    """Sort filenames numerically (so _02 sorts before _10, not after)."""
    parts = re.split(r"(\d+)", filename)
    return [int(p) if p.isdigit() else p for p in parts]


def get_images_from_folder(folder_path: str) -> list:
    """Get all image files from a folder, sorted numerically."""
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found: {folder_path}")
        return []

    images = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(IMAGE_EXTENSIONS)
    ]

    if not images:
        print(f"No images found in {folder_path}")
        return []

    images.sort(key=natural_sort_key)
    return images


def convert_folder_to_pdf(folder_path: str, output_path: str = None):
    """Convert all images in a folder to a single PDF."""
    images = get_images_from_folder(folder_path)

    if not images:
        return

    # Load and prepare images
    image_objects = []
    for img_file in images:
        img_path = os.path.join(folder_path, img_file)
        try:
            img = Image.open(img_path)
            # Convert to RGB (PDF standard)
            if img.mode != "RGB":
                img = img.convert("RGB")
            image_objects.append(img)
            print(f"  ✓ Loaded: {img_file}")
        except Exception as e:
            print(f"  ✗ Failed to load {img_file}: {e}")
            continue

    if not image_objects:
        print("No valid images to convert.")
        return

    # Determine output path
    if output_path is None:
        folder_name = os.path.basename(folder_path.rstrip("/"))
        parent_dir = os.path.dirname(folder_path.rstrip("/"))
        output_path = os.path.join(parent_dir, f"{folder_name}.pdf")

    # Create PDF
    try:
        first_image = image_objects[0]
        remaining_images = image_objects[1:]
        first_image.save(
            output_path,
            save_all=True,
            append_images=remaining_images,
            optimize=False,
            duration=100,
            loop=0,
        )
        print(f"\n✓ PDF created successfully!")
        print(f"  Location: {output_path}")
        print(f"  Images combined: {len(image_objects)}")
    except Exception as e:
        print(f"Error creating PDF: {e}")


def main():
    print(f"Converting images in: {FOLDER_PATH}")
    print(f"Looking for: {', '.join(IMAGE_EXTENSIONS)}\n")

    convert_folder_to_pdf(FOLDER_PATH, OUTPUT_PATH)


if __name__ == "__main__":
    main()
