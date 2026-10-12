# YouTube to CSV

Turns a YouTube playlist (or a single video) into a spreadsheet-friendly CSV file.
Each row is one video, with its title, link, length, upload date, and English transcript.

## What you get

One row per video with these columns:

| Column | What it holds |
|---|---|
| order | Position in the playlist (1, 2, 3, ...) |
| video_id | The YouTube video ID |
| title | Video title |
| url | Link to the video |
| duration_seconds | Length in seconds |
| upload_date | Date as YYYY-MM-DD |
| transcript | English captions as one paragraph (empty if none exist) |

Manual captions are used first. If there are none, auto-generated captions are used.

## Install

You need Python 3. Then, in the project folder, run:

```bash
pip install yt-dlp
```

`yt-dlp` is a free, open-source tool that reads YouTube video information and captions.

## Run

For a playlist:

```bash
python3 youtube_to_csv.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" -o ~/Desktop/videos.csv
```

For a single video:

```bash
python3 youtube_to_csv.py "https://www.youtube.com/watch?v=VIDEO_ID" -o ~/Desktop/video.csv
```

If you leave out `-o`, the file is saved as `videos.csv` in the folder you ran it from.

## Summary at the end

When it finishes, it prints:

- **Found**: how many videos the playlist has
- **Saved**: how many rows were written to the CSV
- **Missing transcript**: how many videos had no English captions
- **Skipped (errors)**: videos that failed and were left out

Videos that fail are skipped, so one bad video does not stop the whole run.
