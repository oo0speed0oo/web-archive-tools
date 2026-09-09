#!/usr/bin/env python3
"""
Web Page Scraper & PDF Generator
---------------------------------
1. Scrapes listing pages and follows pagination.
2. Checks for embedded Google Drive PDF files and downloads them via `gdown`.
3. Falls back to scraping images from articles and compiles them into a single PDF.

Saved output:
    ~/Desktop/page_scraper_downloads/PDFs/<Article Title>.pdf
"""

import os
import re
import time
import requests
import gdown
from PIL import Image
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# ---- CONFIGURATION ----
START_URL = "https://example.com/articles/"

DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
BASE_DIR = os.path.join(DESKTOP_DIR, "page_scraper_downloads")
PDF_OUTPUT_DIR = os.path.join(BASE_DIR, "PDFs")
TEMP_IMG_DIR = os.path.join(BASE_DIR, "Temp_Images")
LOG_PATH = os.path.join(BASE_DIR, "progress.log")

DELAY_BETWEEN_PAGES = 2.0
DELAY_BETWEEN_DOWNLOADS = 0.5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}


def log(message: str):
    print(message)
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip()[:100] or "untitled"


def get_page_links_and_next(listing_url: str):
    resp = requests.get(listing_url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    article_urls = []
    for h in soup.find_all(["h2", "h3"], class_=re.compile("(title|heading)")):
        a = h.find("a", href=True)
        if a:
            article_urls.append(a["href"])

    if not article_urls:
        for a in soup.select("article a[href]"):
            href = a["href"]
            if href and href.startswith(("http", "/")):
                article_urls.append(href)

    next_link = soup.find("a", class_=re.compile("(next|older|pager)"))
    next_url = next_link["href"] if next_link else None

    return list(dict.fromkeys(article_urls)), next_url


def extract_gdrive_ids(soup: BeautifulSoup) -> list:
    drive_pattern = re.compile(r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)")
    file_ids = []
    for a in soup.find_all("a", href=True):
        match = drive_pattern.search(a["href"])
        if match:
            file_ids.append(match.group(1))
    return list(dict.fromkeys(file_ids))


def extract_image_urls(soup: BeautifulSoup) -> list:
    urls = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(href.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".webp")):
            urls.add(href)
    for img in soup.find_all("img", src=True):
        src = img["src"]
        if any(src.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".webp")):
            urls.add(src)
    return sorted(urls)


def download_gdrive_file(file_id: str, dest_path: str) -> bool:
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        output = gdown.download(url, dest_path, quiet=True, fuzzy=True)
        if output and os.path.exists(dest_path) and os.path.getsize(dest_path) > 10000:
            log(f"    Direct Google Drive PDF downloaded: {os.path.basename(dest_path)}")
            return True
    except Exception as e:
        log(f"    gdown download skipped/failed for {file_id}: {e}")

    if os.path.exists(dest_path):
        os.remove(dest_path)
    return False


def convert_images_to_pdf(image_paths: list, pdf_path: str):
    """Opens image files and merges them into a single PDF."""
    if not image_paths:
        return

    valid_images = []
    for img_path in image_paths:
        try:
            im = Image.open(img_path)
            if im.mode != "RGB":
                im = im.convert("RGB")
            valid_images.append(im)
        except Exception as e:
            log(f"    Failed to open image {img_path}: {e}")

    if valid_images:
        first_image = valid_images[0]
        remaining_images = valid_images[1:]
        first_image.save(pdf_path, save_all=True, append_images=remaining_images)
        log(f"    Compiled {len(valid_images)} images into PDF: {os.path.basename(pdf_path)}")


def process_article(article_url: str):
    log(f"\nProcessing Article: {article_url}")
    try:
        resp = requests.get(article_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        log(f"  Could not load article: {e}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    title = sanitize_filename(soup.title.string.split(" - ")[0] if soup.title else "article")
    target_pdf_path = os.path.join(PDF_OUTPUT_DIR, f"{title}.pdf")

    if os.path.exists(target_pdf_path):
        log(f"  PDF already exists for '{title}', skipping.")
        return

    # Method 1: Check for Direct Google Drive PDF Link
    gdrive_ids = extract_gdrive_ids(soup)
    if gdrive_ids:
        log(f"  Found Google Drive link(s). Attempting direct download...")
        for file_id in gdrive_ids:
            if download_gdrive_file(file_id, target_pdf_path):
                return

    # Method 2: Fallback to Page Image Scans -> Single PDF
    image_urls = extract_image_urls(soup)
    if not image_urls:
        log("  No downloadable drive files or images found.")
        return

    log(f"  Downloading {len(image_urls)} images to compile into PDF...")
    article_temp_dir = os.path.join(TEMP_IMG_DIR, title)
    os.makedirs(article_temp_dir, exist_ok=True)

    local_image_paths = []
    for i, img_url in enumerate(image_urls, start=1):
        ext = os.path.splitext(urlparse(img_url).path)[1] or ".png"
        img_dest = os.path.join(article_temp_dir, f"page_{i:02d}{ext}")

        if not os.path.exists(img_dest):
            try:
                r = requests.get(img_url, headers=HEADERS, timeout=30)
                r.raise_for_status()
                with open(img_dest, "wb") as f:
                    f.write(r.content)
            except Exception as e:
                log(f"    Failed to download image page {i}: {e}")
                continue

        local_image_paths.append(img_dest)
        time.sleep(DELAY_BETWEEN_DOWNLOADS)

    convert_images_to_pdf(local_image_paths, target_pdf_path)


def main():
    os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_IMG_DIR, exist_ok=True)
    log(f"=== Starting Run: {time.strftime('%Y-%m-%d %H:%M:%S')} ===")

    all_article_urls = []
    current_url = START_URL

    while current_url:
        log(f"\nFetching listing page: {current_url}")
        try:
            article_urls, next_url = get_page_links_and_next(current_url)
        except Exception as e:
            log(f"  Error loading listing page: {e}")
            break

        all_article_urls.extend(article_urls)
        current_url = next_url
        time.sleep(DELAY_BETWEEN_PAGES)

    all_article_urls = list(dict.fromkeys(all_article_urls))
    log(f"\nTotal articles found across all pages: {len(all_article_urls)}")

    for article_url in all_article_urls:
        process_article(article_url)
        time.sleep(DELAY_BETWEEN_PAGES)

    log(f"\n=== Finished Run: {time.strftime('%Y-%m-%d %H:%M:%S')} ===")


if __name__ == "__main__":
    main()
