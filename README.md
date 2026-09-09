# Web Scraper & OCR Toolkit

A flexible Python toolkit for scraping web content and extracting text via OCR. Perfect for archiving articles, building datasets, or batch processing documents.

## Features

- **Page Scraper** — Scrapes listing pages, follows pagination, downloads embedded images
- **PDF Scraper** — Extracts PDFs from articles or compiles images into PDFs
- **Image OCR** — Converts images to text with customizable language support
- **PDF OCR** — Extracts text from PDF files page-by-page
- **Resume Support** — Already-processed files are skipped, so you can pause and resume
- **Progress Logging** — Track what's been downloaded in real-time

## Installation

### 1. Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Tesseract OCR (for image/PDF text extraction)

**Mac:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
Download and run the installer from [UB-Mannheim/tesseract-ocr](https://github.com/UB-Mannheim/tesseract-ocr/wiki)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

## Usage

### 1. Page Scraper — Download Images from Articles

Edit the `START_URL` in `page_scraper.py` to point to your target website, then run:

```bash
python page_scraper.py
```

Images are saved to `~/Desktop/page_scraper_downloads/`

### 2. PDF Scraper — Download or Create PDFs

Edit the `START_URL` in `pdf_scraper.py`, then run:

```bash
python pdf_scraper.py
```

Looks for embedded PDFs first, then falls back to compiling page images into PDFs.
Output: `~/Desktop/page_scraper_downloads/PDFs/`

### 3. Image to Text — OCR for Images

Edit `INPUT_DIR` and `OCR_LANGUAGES` in `image_to_text.py`, then run:

```bash
python image_to_text.py
```

Creates `.txt` files for each image + a combined `_FULL_TEXT.txt` file.

### 4. PDF to Text — OCR for PDFs

Edit `INPUT_DIR` and `OCR_LANGUAGES` in `pdf_to_text.py`, then run:

```bash
python pdf_to_text.py
```

Extracts text from each PDF page and creates a combined text file.

## Configuration

Each script has configuration at the top:

```python
START_URL = "https://example.com/articles/"  # Target listing page
OCR_LANGUAGES = "eng"                         # "eng", "jpn", "fra", "jpn+eng", etc.
DELAY_BETWEEN_PAGES = 2.0                     # Seconds between requests
```

## Output Structure

```
~/Desktop/page_scraper_downloads/
├── Article Title 1/
│   ├── Article Title 1_01.png
│   ├── Article Title 1_01.txt
│   ├── Article Title 1_02.png
│   └── Article Title 1_FULL_TEXT.txt
├── Article Title 2/
│   └── ...
├── PDFs/
│   ├── Article Title 1.pdf
│   └── Article Title 2.pdf
├── Temp_Images/
│   └── (temporary images during PDF generation)
└── progress.log
```

## Language Support

Change `OCR_LANGUAGES` in the OCR scripts to match your content:

- `"eng"` — English
- `"jpn"` — Japanese
- `"fra"` — French
- `"deu"` — German
- `"jpn+eng"` — Japanese + English (auto-detect)

## Troubleshooting

**Tesseract not found:**
Make sure you installed the Tesseract engine (not just the Python package).
Check the path: `which tesseract`

**Images not downloading:**
Check your `START_URL` and verify the website's HTML structure matches the CSS selectors in the script.

**OCR not recognizing text:**
Ensure you have the correct language pack installed: `brew install tesseract-lang`

## License

MIT
