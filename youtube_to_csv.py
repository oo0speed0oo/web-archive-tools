#!/usr/bin/env python3
"""
YouTube to CSV
--------------
Give it a YouTube playlist URL (or a single video URL) and it writes a CSV
with one row per video: order, video_id, title, url, duration_seconds,
upload_date, transcript.

The transcript is English captions as plain text (manual captions first,
otherwise auto-generated). It has no timestamps, no duplicate lines and no
[Music]-style tags, and it is one paragraph. It is empty when no captions exist.

USAGE:
    python3 youtube_to_csv.py "<playlist or video url>" -o videos.csv
"""

import argparse
import csv
import json
import os
import re
import sys

import yt_dlp

CSV_COLUMNS = [
    "order", "video_id", "title", "url",
    "duration_seconds", "upload_date", "transcript",
]


def list_entries(url: str) -> list:
    """Return (video_id, url) pairs for a playlist, or the single video."""
    opts = {"quiet": True, "no_warnings": True, "skip_download": True,
            "extract_flat": "in_playlist"}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if info.get("_type") == "playlist" or "entries" in info:
        entries = [e for e in (info.get("entries") or []) if e]
        return [(e["id"], e.get("url") or f"https://www.youtube.com/watch?v={e['id']}")
                for e in entries]
    return [(info["id"], info.get("webpage_url") or url)]


def fetch_video_info(video_url: str) -> dict:
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(video_url, download=False)


def format_upload_date(raw: str) -> str:
    if raw and len(raw) == 8 and raw.isdigit():
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"
    return raw or ""


def english_caption_tracks(info: dict) -> list:
    """Return caption track entries for English, manual first, then auto."""
    for key in ("subtitles", "automatic_captions"):
        tracks = (info.get(key) or {})
        for lang, entries in tracks.items():
            if lang == "en" or lang.startswith("en-") or lang.startswith("en_"):
                if entries:
                    return entries
    return []


def download_caption_text(ydl: yt_dlp.YoutubeDL, entries: list):
    """Download the first usable caption track; return (raw_text, extension)."""
    preferred = sorted(entries, key=lambda e: 0 if e.get("ext") == "json3" else 1)
    for entry in preferred:
        if not entry.get("url"):
            continue
        try:
            raw = ydl.urlopen(entry["url"]).read().decode("utf-8", errors="replace")
            return raw, entry.get("ext")
        except Exception:
            continue
    return "", None


def parse_json3(raw: str) -> list:
    data = json.loads(raw)
    cues = []
    for event in data.get("events", []):
        segs = event.get("segs")
        if not segs:
            continue
        cues.append("".join(seg.get("utf8", "") for seg in segs))
    return cues


def parse_vtt(raw: str) -> list:
    cues = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line == "WEBVTT" or "-->" in line:
            continue
        if line.startswith(("Kind:", "Language:", "NOTE")):
            continue
        if re.fullmatch(r"\d+", line):
            continue
        cues.append(line)
    return cues


def clean_transcript(cues: list) -> str:
    """Strip tags, drop sound markers, merge rolling duplicates, make one paragraph."""
    lines = []
    for cue in cues:
        text = re.sub(r"<[^>]+>", "", cue)
        text = re.sub(r"\[[^\]]*\]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        if lines and text == lines[-1]:
            continue
        if lines and text.startswith(lines[-1]):
            lines[-1] = text
            continue
        if lines and lines[-1].startswith(text):
            continue
        lines.append(text)
    return " ".join(lines)


def get_transcript(info: dict, ydl: yt_dlp.YoutubeDL) -> str:
    entries = english_caption_tracks(info)
    if not entries:
        return ""
    raw, ext = download_caption_text(ydl, entries)
    if not raw:
        return ""
    try:
        cues = parse_json3(raw) if ext == "json3" else parse_vtt(raw)
    except (ValueError, json.JSONDecodeError):
        cues = parse_vtt(raw)
    return clean_transcript(cues)


def build_row(order: int, video_id: str, video_url: str) -> dict:
    info = fetch_video_info(video_url)
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as ydl:
        transcript = get_transcript(info, ydl)
    return {
        "order": order,
        "video_id": video_id,
        "title": info.get("title", ""),
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "duration_seconds": info.get("duration") or "",
        "upload_date": format_upload_date(info.get("upload_date", "")),
        "transcript": transcript,
    }


def main():
    parser = argparse.ArgumentParser(description="Save a YouTube playlist or video to CSV.")
    parser.add_argument("url", help="YouTube playlist URL or single video URL")
    parser.add_argument("-o", "--output", default="videos.csv", help="CSV file to write")
    args = parser.parse_args()

    output = os.path.expanduser(args.output)
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)

    print("Reading playlist...")
    entries = list_entries(args.url)
    print(f"Found {len(entries)} video(s)")

    rows, failed = [], []
    for order, (video_id, video_url) in enumerate(entries, start=1):
        print(f"[{order}/{len(entries)}] {video_id}")
        try:
            rows.append(build_row(order, video_id, video_url))
        except Exception as e:
            failed.append(video_id)
            print(f"  skipped: {e}", file=sys.stderr)

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    missing = sum(1 for r in rows if not r["transcript"])
    print()
    print("Summary")
    print(f"  Found:              {len(entries)}")
    print(f"  Saved:              {len(rows)} -> {output}")
    print(f"  Missing transcript: {missing}")
    print(f"  Skipped (errors):   {len(failed)}")


if __name__ == "__main__":
    main()
