#!/usr/bin/env python3
"""
Folder to PDF Converter
-----------------------
Converts images in each folder into separate PDF files.

Walks through a folder structure, and for each subfolder containing images,
creates a single PDF. Each PDF is saved in its respective subfolder.

SETUP (run once):
    pip install pillow

USAGE:
    python folder_to_pdf.py

A folder picker popup will appear—select your root folder.
Each subfolder with images gets its own PDF.
"""

import os
import re
from PIL import Image
from tkinter import Tk, filedialog

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def natural_sort_key(filename: str):
    """Sort filenames numerically (so _02 sorts before _10, not after)."""
    parts = re.split(r"(\d+)", filename)
    return [int(p) if p.isdigit() else p for p in parts]


def get_images_in_folder(folder_path: str) -> list:
    """Get image files in a specific folder (not subfolders), sorted numerically."""
    if not os.path.isdir(folder_path):
        return []

    images = []
    for f in os.listdir(folder_path):
        if f.lower().endswith(IMAGE_EXTENSIONS):
            full_path = os.path.join(folder_path, f)
            if os.path.isfile(full_path):
                images.append(full_path)

    if not images:
        return []

    images.sort(key=natural_sort_key)
    return images


def create_pdf_from_images(images: list, output_path: str) -> bool:
    """Convert a list of images to a single PDF."""
    if not images:
        return False

    # Load and prepare images
    image_objects = []
    for img_path in images:
        try:
            img = Image.open(img_path)
            # Convert to RGB (PDF standard)
            if img.mode != "RGB":
                img = img.convert("RGB")
            image_objects.append(img)
        except Exception as e:
            print(f"    ✗ Failed to load {os.path.basename(img_path)}: {e}")
            continue

    if not image_objects:
        return False

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
        return True
    except Exception as e:
        print(f"    ✗ Error creating PDF: {e}")
        return False


def process_folders(root_path: str):
    """Walk through folders and create PDFs for each folder with images."""
    total_pdfs = 0

    for root, dirs, files in os.walk(root_path):
        # Check if this folder has images
        images = get_images_in_folder(root)

        if images:
            folder_name = os.path.basename(root)
            pdf_name = f"{folder_name}.pdf"
            pdf_path = os.path.join(root, pdf_name)

            # Skip if PDF already exists
            if os.path.exists(pdf_path):
                print(f"  ✓ Already exists: {folder_name}/{pdf_name}")
                total_pdfs += 1
                continue

            print(f"  Processing: {folder_name}/ ({len(images)} images)")

            if create_pdf_from_images(images, pdf_path):
                print(f"    ✓ Created: {pdf_name}")
                total_pdfs += 1
            else:
                print(f"    ✗ Failed to create PDF")

    return total_pdfs


def get_folder_from_user() -> str:
    """Show a folder picker popup and return the selected path."""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title="Select root folder with images")
    root.destroy()
    return folder_path


def main():
    print("Select a folder with images...\n")

    folder_path = get_folder_from_user()

    if not folder_path:
        print("No folder selected. Exiting.")
        return

    print(f"Processing: {folder_path}")
    print(f"Looking for: {', '.join(IMAGE_EXTENSIONS)}\n")

    total = process_folders(folder_path)

    print(f"\n✓ Complete! Created/Found {total} PDF(s)")


if __name__ == "__main__":
    main()
