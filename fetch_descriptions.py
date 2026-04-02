"""
fetch_descriptions.py
---------------------
Fetches all video descriptions from a YouTube channel and saves each one
as a Markdown file in the descriptions/ folder.

Uses yt-dlp — no API key or OAuth required for public channels.

Usage:
    python fetch_descriptions.py [--skip-existing]

Options:
    --skip-existing     Do not overwrite description files that already exist.

Configuration is read from a .env file (see .env.example).
"""

import argparse
import os
import sys

import frontmatter
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CHANNEL_HANDLE = os.getenv("CHANNEL_HANDLE", "portalmundoedu")
DESCRIPTIONS_DIR = os.getenv("DESCRIPTIONS_DIR", "videos/descriptions")


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------
def write_description_file(
    output_dir: str,
    video_id: str,
    title: str,
    description: str,
    skip_existing: bool,
) -> bool:
    """Write a Markdown file for the video. Returns True if written."""
    filepath = os.path.join(output_dir, f"{video_id}.md")

    if skip_existing and os.path.exists(filepath):
        return False

    post = frontmatter.Post(
        description or "",
        id=video_id,
        title=title,
        url=f"https://www.youtube.com/watch?v={video_id}",
    )
    with open(filepath, "wb") as f:
        frontmatter.dump(post, f)

    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch all video descriptions from a YouTube channel using yt-dlp."
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip videos whose description file already exists.",
    )
    args = parser.parse_args()

    os.makedirs(DESCRIPTIONS_DIR, exist_ok=True)

    channel_url = f"https://www.youtube.com/user/{CHANNEL_HANDLE}/videos"
    print(f"Fetching video list from {channel_url} …")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,       # we need full metadata including description
        "skip_download": True,       # don't download video files
        "ignoreerrors": True,        # skip unavailable videos
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)

    if not info or "entries" not in info:
        sys.exit(f"ERROR: Could not retrieve videos for '{CHANNEL_HANDLE}'. Check the channel handle in .env.")

    entries = [e for e in info["entries"] if e]  # filter None (unavailable videos)
    print(f"Found {len(entries)} videos. Saving descriptions…")

    written = 0
    skipped = 0
    for entry in entries:
        video_id = entry.get("id", "")
        title = entry.get("title", video_id)
        description = entry.get("description", "")

        saved = write_description_file(
            DESCRIPTIONS_DIR, video_id, title, description, args.skip_existing
        )
        if saved:
            print(f"  SAVED   [{video_id}] {title}")
            written += 1
        else:
            print(f"  SKIPPED [{video_id}] {title}")
            skipped += 1

    print(
        f"\nDone. {written} file(s) written to '{DESCRIPTIONS_DIR}/'."
        + (f" {skipped} skipped (already existed)." if skipped else "")
    )


if __name__ == "__main__":
    main()
