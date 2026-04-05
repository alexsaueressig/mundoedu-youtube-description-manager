"""
fetch_subtitles.py
------------------
Downloads pt-BR subtitles/captions for every video in the descriptions/ folder
using yt-dlp and saves clean transcript text to videos/subtitles/pt-BR/.

Priority order for each video:
  1. Manual pt-BR subtitles (channel-uploaded)
  2. Auto-generated pt-orig (original-audio transcription — best for Brazilian content)
  3. Auto-generated pt or pt-PT
  4. Any available auto-generated language → translated to pt-BR via Google Translate

Transcripts are saved as Markdown files with frontmatter and can be used as
source material for improving video descriptions.

Usage:
    python fetch_subtitles.py [--skip-existing] [--limit N]

Options:
    --skip-existing     Skip videos that already have a subtitle file.
    --limit N           Process only the first N videos (useful for testing).

Configuration (via environment variables / .env):
    DESCRIPTIONS_DIR    Folder with video .md files   (default: videos/descriptions)
    SUBTITLES_DIR       Output folder                  (default: videos/subtitles/pt-BR)
"""

import argparse
import glob
import json
import os
import re
import sys
import tempfile
from pathlib import Path

import frontmatter
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DESCRIPTIONS_DIR = os.getenv("DESCRIPTIONS_DIR", "videos/descriptions")
SUBTITLES_DIR = os.getenv("SUBTITLES_DIR", "videos/subtitles/pt-BR")

# Subtitle language preference order.
# "pt-orig" = YouTube's original-audio auto-transcription (best for Brazilian content).
PREFERRED_LANGS = ["pt-BR", "pt-orig", "pt", "pt-PT"]


# ---------------------------------------------------------------------------
# yt-dlp helpers
# ---------------------------------------------------------------------------
def _quiet_ydl_opts(tmpdir: str) -> dict:
    return {
        "skip_download": True,
        "outtmpl": os.path.join(tmpdir, "%(id)s.%(lang)s.%(ext)s"),
        "subtitlesformat": "json3",
        "quiet": True,
        "no_warnings": True,
    }


def get_available_subtitle_langs(video_id: str) -> tuple[dict, dict]:
    """Return (manual_subs, auto_subs) dicts mapping lang → list of formats."""
    opts = {"skip_download": True, "quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(
            f"https://www.youtube.com/watch?v={video_id}", download=False
        )
    return info.get("subtitles", {}), info.get("automatic_captions", {})


def download_subtitles_json3(
    video_id: str,
    langs: list[str],
    auto: bool,
    tmpdir: str,
) -> list[str]:
    """Download subtitle files and return file paths for any that were created."""
    opts = _quiet_ydl_opts(tmpdir)
    opts["subtitleslangs"] = langs
    if auto:
        opts["writeautomaticsub"] = True
    else:
        opts["writesubtitles"] = True

    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        except Exception:
            pass

    return glob.glob(os.path.join(tmpdir, f"{video_id}.*.json3"))


# ---------------------------------------------------------------------------
# json3 → plain text
# ---------------------------------------------------------------------------
def parse_json3(filepath: str) -> str:
    """Extract clean transcript text from a yt-dlp json3 subtitle file."""
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    lines: list[str] = []
    current: list[str] = []

    for event in data.get("events", []):
        segs = event.get("segs")
        if not segs:
            # Empty event often marks a line break between sentences.
            if current:
                lines.append("".join(current).strip())
                current = []
            continue

        for seg in segs:
            text = seg.get("utf8", "")
            if text == "\n":
                if current:
                    lines.append("".join(current).strip())
                    current = []
            else:
                current.append(text)

    if current:
        lines.append("".join(current).strip())

    # Deduplicate consecutive identical lines (yt-dlp auto-captions overlap).
    deduped: list[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if not deduped or line != deduped[-1]:
            deduped.append(line)

    # Join into paragraphs: split at sentence-ending punctuation heuristically.
    text = " ".join(deduped)
    # Insert newlines after sentence-ending punctuation for readability.
    text = re.sub(r"([.!?])\s+", r"\1\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------
def translate_to_ptbr(text: str) -> str:
    """Translate text to pt-BR using Google Translate (via deep-translator)."""
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        print("  WARNING: deep-translator not installed; skipping translation.")
        return text

    # Google Translate has a ~5000-char limit per call; chunk if needed.
    chunk_size = 4500
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    translated_chunks: list[str] = []

    translator = GoogleTranslator(source="auto", target="pt")
    for chunk in chunks:
        try:
            translated_chunks.append(translator.translate(chunk))
        except Exception as exc:
            print(f"  WARNING: Translation chunk failed: {exc}")
            translated_chunks.append(chunk)

    return "\n".join(translated_chunks)


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------
def collect_video_ids(descriptions_dir: str) -> list[str]:
    return sorted(p.stem for p in Path(descriptions_dir).glob("*.md"))


def write_subtitle_file(
    output_dir: str,
    video_id: str,
    text: str,
    source_lang: str,
    translated: bool,
    skip_existing: bool,
) -> bool:
    """Write transcript Markdown file. Returns True if written."""
    filepath = os.path.join(output_dir, f"{video_id}.md")
    if skip_existing and os.path.exists(filepath):
        return False

    post = frontmatter.Post(
        text,
        id=video_id,
        url=f"https://www.youtube.com/watch?v={video_id}",
        lang="pt-BR",
        source_lang=source_lang,
        translated=translated,
    )
    with open(filepath, "wb") as f:
        frontmatter.dump(post, f)
    return True


# ---------------------------------------------------------------------------
# Per-video logic
# ---------------------------------------------------------------------------
def process_video(
    video_id: str,
    skip_existing: bool,
    output_dir: str,
) -> str:
    """Download and save subtitles for one video. Returns status string."""
    output_path = os.path.join(output_dir, f"{video_id}.md")
    if skip_existing and os.path.exists(output_path):
        return "SKIPPED"

    # Discover available subtitle languages.
    try:
        manual_subs, auto_subs = get_available_subtitle_langs(video_id)
    except Exception as exc:
        return f"ERROR (discovery): {exc}"

    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Try manual subtitles in preferred order.
        for lang in PREFERRED_LANGS:
            if lang in manual_subs:
                files = download_subtitles_json3(video_id, [lang], auto=False, tmpdir=tmpdir)
                if files:
                    text = parse_json3(files[0])
                    if text:
                        write_subtitle_file(output_dir, video_id, text, lang, False, skip_existing)
                        return f"SAVED (manual {lang})"

        # 2. Try auto-generated subtitles in preferred order.
        for lang in PREFERRED_LANGS:
            if lang in auto_subs:
                files = download_subtitles_json3(video_id, [lang], auto=True, tmpdir=tmpdir)
                if files:
                    text = parse_json3(files[0])
                    if text:
                        write_subtitle_file(output_dir, video_id, text, lang, False, skip_existing)
                        return f"SAVED (auto {lang})"

        # 3. Fall back to any available auto-generated language and translate.
        if auto_subs:
            fallback_lang = next(iter(auto_subs))
            files = download_subtitles_json3(video_id, [fallback_lang], auto=True, tmpdir=tmpdir)
            if files:
                raw_text = parse_json3(files[0])
                if raw_text:
                    translated_text = translate_to_ptbr(raw_text)
                    write_subtitle_file(
                        output_dir, video_id, translated_text, fallback_lang, True, skip_existing
                    )
                    return f"SAVED (translated from {fallback_lang})"

    return "NO_SUBTITLES"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Download pt-BR subtitles/captions for all videos and save transcripts "
            "to videos/subtitles/pt-BR/."
        )
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip videos that already have a subtitle file.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        metavar="N",
        help="Process only the first N videos (0 = all).",
    )
    args = parser.parse_args()

    video_ids = collect_video_ids(DESCRIPTIONS_DIR)
    if not video_ids:
        sys.exit(f"No description files found in '{DESCRIPTIONS_DIR}/'.")

    if args.limit > 0:
        video_ids = video_ids[: args.limit]

    print(f"Processing {len(video_ids)} video(s) → '{SUBTITLES_DIR}/'")
    os.makedirs(SUBTITLES_DIR, exist_ok=True)

    counts: dict[str, int] = {}

    for i, video_id in enumerate(video_ids, 1):
        status = process_video(video_id, args.skip_existing, SUBTITLES_DIR)
        key = status.split(" ")[0]  # e.g. "SAVED", "SKIPPED", "NO_SUBTITLES", "ERROR"
        counts[key] = counts.get(key, 0) + 1
        print(f"  [{i:>4}/{len(video_ids)}] {video_id}  {status}")

    print("\nSummary:")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
