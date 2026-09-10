#!/usr/bin/env python3
"""
Web Page Scraper - Image Downloader
------------------------------------
Scrapes a listing/index page, follows pagination through all pages,
visits each linked article/post, and downloads all embedded images.

Images are saved to:
    ~/Desktop/page_scraper_downloads/<Page Title>/<Page Title>_01.png, _02.png, ...

Progress is printed to the terminal AND written to:
    ~/Desktop/page_scraper_downloads/progress.log

Already-downloaded images are skipped automatically, so you can stop
(Ctrl+C) and re-run this script later to resume where you left off.

SETUP (run once):
    pip install requests beautifulsoup4

RUN:
    python page_scraper.py

A popup will ask for the starting URL.
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from tkinter import Tk, simpledialog

DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
OUTPUT_DIR = os.path.join(DESKTOP_DIR, "page_scraper_downloads")
LOG_PATH = os.path.join(OUTPUT_DIR, "progress.log")

DELAY_BETWEEN_PAGES = 2.0     # seconds between fetching each listing/post page
DELAY_BETWEEN_DOWNLOADS = 0.5  # seconds between each image download

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}


def log(message: str):
    print(message)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip()[:100] or "untitled"


def get_page_links_and_next(listing_url: str):
    """Fetch one listing page, return (list_of_article_urls, next_page_url_or_None)."""
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


def get_page_title(soup: BeautifulSoup, url: str) -> str:
    if soup.title and soup.title.string:
        title = soup.title.string.split(" - ")[0].split(" | ")[0].strip()
        if title:
            return title
    slug = urlparse(url).path.rstrip("/").split("/")[-1]
    return slug.replace(".html", "") or "page"


def extract_image_urls(soup: BeautifulSoup) -> list:
    urls = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(href.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp")):
            urls.add(href)
    for img in soup.find_all("img", src=True):
        src = img["src"]
        if any(src.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp")):
            urls.add(src)
    return sorted(urls)


def download_file(url: str, dest_path: str):
    if os.path.exists(dest_path):
        log(f"    already have {os.path.basename(dest_path)}, skipping")
        return
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(resp.content)
        log(f"    saved {os.path.basename(dest_path)}")
    except Exception as e:
        log(f"    FAILED {url}: {e}")


def process_article(article_url: str):
    log(f"\nArticle: {article_url}")
    try:
        resp = requests.get(article_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        log(f"  could not load article: {e}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    title = sanitize_filename(get_page_title(soup, article_url))
    image_urls = extract_image_urls(soup)

    if not image_urls:
        log("  no matching images found")
        return

    article_dir = os.path.join(OUTPUT_DIR, title)
    os.makedirs(article_dir, exist_ok=True)
    log(f"  {len(image_urls)} image(s) -> {article_dir}")

    for i, img_url in enumerate(image_urls, start=1):
        ext = os.path.splitext(urlparse(img_url).path)[1] or ".png"
        filename = f"{title}_{i:02d}{ext}"
        dest_path = os.path.join(article_dir, filename)
        download_file(img_url, dest_path)
        time.sleep(DELAY_BETWEEN_DOWNLOADS)


def get_url_from_user() -> str:
    """Show a popup asking for the starting URL."""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    url = simpledialog.askstring(
        "Web Scraper",
        "Enter the starting URL:\n\n(e.g., https://example.com/articles/)"
    )
    root.destroy()
    return url


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Enter the starting URL...\n")
    start_url = get_url_from_user()

    if not start_url:
        print("No URL provided. Exiting.")
        return

    log(f"=== Starting run: {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    log(f"Saving to: {OUTPUT_DIR}")
    log(f"Starting URL: {start_url}")

    all_article_urls = []
    current_url = start_url
    page_num = 1

    while current_url:
        log(f"\nFetching listing page {page_num}: {current_url}")
        try:
            article_urls, next_url = get_page_links_and_next(current_url)
        except Exception as e:
            log(f"  could not load listing page: {e}")
            break

        log(f"  found {len(article_urls)} article(s) on this page")
        all_article_urls.extend(article_urls)
        current_url = next_url
        page_num += 1
        time.sleep(DELAY_BETWEEN_PAGES)

    all_article_urls = list(dict.fromkeys(all_article_urls))
    log(f"\nTotal articles found across all pages: {len(all_article_urls)}")

    for article_url in all_article_urls:
        process_article(article_url)
        time.sleep(DELAY_BETWEEN_PAGES)

    log(f"\n=== Done: {time.strftime('%Y-%m-%d %H:%M:%S')} ===")


if __name__ == "__main__":
    main()
