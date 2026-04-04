"""
Extract one-to-one relations between mundoedu videoaula IDs and YouTube video IDs.

For each videoaula ID found across all description files, picks the YouTube ID
that co-appears with it in the most files (majority vote). Tie-break: alphabetical.

Output: relations.md — a Markdown table sorted by videoaula ID numerically.
"""

import re
from collections import Counter
from pathlib import Path

DESCRIPTIONS_DIR = Path("videos/descriptions")
OUTPUT_FILE = Path("relations.md")
VIDEOAULA_RE = re.compile(r"mundoedu\.com\.br/videoaula/(\d+)")


def main():
    pair_count: Counter = Counter()

    for md_file in DESCRIPTIONS_DIR.glob("*.md"):
        youtube_id = md_file.stem
        content = md_file.read_text(encoding="utf-8")
        # Deduplicate within the same file so one file can't skew the count
        videoaula_ids = set(VIDEOAULA_RE.findall(content))
        for vid_id in videoaula_ids:
            pair_count[(vid_id, youtube_id)] += 1

    # Group by videoaula_id, pick youtube_id with the highest count (majority)
    best: dict[str, tuple[str, int]] = {}
    for (vid_id, yt_id), count in pair_count.items():
        if vid_id not in best:
            best[vid_id] = (yt_id, count)
        else:
            current_yt, current_count = best[vid_id]
            if count > current_count or (count == current_count and yt_id < current_yt):
                best[vid_id] = (yt_id, count)

    rows = sorted(best.items(), key=lambda x: int(x[0]))

    lines = [
        "| Video ID | YouTube ID |",
        "| --- | --- |",
    ]
    for vid_id, (yt_id, _) in rows:
        lines.append(f"| {vid_id} | {yt_id} |")

    OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Written {len(rows)} relations to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
