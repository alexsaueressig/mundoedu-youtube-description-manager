"""
add_book_offers.py
------------------
Inserts a "📚 LEITURA RECOMENDADA:" block into every description file
for the four target disciplines: História, Biologia, Matemática, Química.

Each discipline maps to the corresponding "O Grande Livro de..." affiliate link.
The block is placed after the Plano de Estudos line and before the #ENEM hashtags.

Usage:
    python add_book_offers.py [--dry-run]
"""

import argparse
import re
from pathlib import Path

DESCRIPTIONS_DIR = Path("videos/descriptions")

PLANO_LINE_RE = re.compile(r"^✨ Plano de Estudos: https://mundoedu\.com\.br/plano-de-estudos\s*$")
HASHTAG_LINE_RE = re.compile(r"^#ENEM\b")
LEITURA_MARKER = "LEITURA RECOMENDADA"

SUBJECT_KEYWORDS = {
    "história": "História",
    "biologia": "Biologia",
    "matemática": "Matemática",
    "química": "Química",
}

OFFERS = {
    "História": (
        "📚 LEITURA RECOMENDADA:\n"
        "📖 O Grande Livro de História do Manual do Mundo — visual, completo e perfeito pra gabaritar História no ENEM! 🎯 https://amzn.to/4eVqLCI"
    ),
    "Biologia": (
        "📚 LEITURA RECOMENDADA:\n"
        "🧬 O Grande Livro de Biologia do Manual do Mundo — ilustrações incríveis pra te ajudar a dominar a matéria! https://amzn.to/4t9eEWa"
    ),
    "Matemática": (
        "📚 LEITURA RECOMENDADA:\n"
        "📐 O Grande Livro de Matemática do Manual do Mundo — explica tudo de forma visual e descomplicada! https://amzn.to/4cJ6cYS"
    ),
    "Química": (
        "📚 LEITURA RECOMENDADA:\n"
        "🧪 O Grande Livro de Química do Manual do Mundo — ideal pra entender Química de verdade e arrasar no ENEM! https://amzn.to/3P03ghj"
    ),
}


def detect_subject(title: str) -> str | None:
    title_lower = title.lower()
    for keyword, subject in SUBJECT_KEYWORDS.items():
        if keyword in title_lower:
            return subject
    return None


def extract_title_from_text(text: str) -> str:
    """Extract the title value from YAML frontmatter in the raw file text."""
    # Match: title: 'Foo' or title: "Foo" or title: Foo (possibly multiline quoted)
    m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Handle block-style (title span two lines with leading spaces)
    m = re.search(r'^title:\s*["\'](.+)', text, re.MULTILINE)
    if m:
        return m.group(1).strip(" \"'")
    return ""


def process_file(path: Path, dry_run: bool) -> bool:
    """
    Returns True if the file was (or would be) modified.
    """
    text = path.read_text(encoding="utf-8")

    # Skip if already has the block
    if LEITURA_MARKER in text:
        return False

    title = extract_title_from_text(text)
    subject = detect_subject(title)
    if subject is None:
        return False

    offer_block = OFFERS[subject]

    # Split into lines, find insertion point:
    # We want to insert AFTER the "✨ Plano de Estudos" line and any blank lines
    # that follow it, but BEFORE the "#ENEM" hashtag line.
    lines = text.splitlines(keepends=True)

    plano_idx = None
    hashtag_idx = None

    for i, line in enumerate(lines):
        if PLANO_LINE_RE.match(line.rstrip("\n")):
            plano_idx = i
        if hashtag_idx is None and HASHTAG_LINE_RE.match(line.strip()):
            hashtag_idx = i

    if plano_idx is None or hashtag_idx is None:
        # Can't determine insertion point — skip
        return False

    # The insert point is right before the hashtag line
    # Ensure there's a blank line before the offer block and after it
    insert_at = hashtag_idx

    # Build inserted lines: blank + offer + blank
    offer_lines = ["\n", offer_block + "\n", "\n"]

    new_lines = lines[:insert_at] + offer_lines + lines[insert_at:]
    new_text = "".join(new_lines)

    if dry_run:
        print(f"\n{'='*60}")
        print(f"FILE: {path}")
        print(f"SUBJECT: {subject}")
        print(f"TITLE: {title}")
        print(f"--- INSERTED BLOCK (before line {insert_at + 1}) ---")
        print(offer_block)
        print("---")
    else:
        path.write_text(new_text, encoding="utf-8")

    return True


def main():
    parser = argparse.ArgumentParser(description="Add book offer blocks to discipline descriptions.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files.")
    args = parser.parse_args()

    files = sorted(DESCRIPTIONS_DIR.glob("*.md"))
    modified = 0
    skipped_already = 0
    skipped_no_subject = 0

    subject_counts: dict[str, int] = {}

    for path in files:
        text = path.read_text(encoding="utf-8")

        if LEITURA_MARKER in text:
            skipped_already += 1
            continue

        title = extract_title_from_text(text)
        subject = detect_subject(title)
        if subject is None:
            skipped_no_subject += 1
            continue

        changed = process_file(path, dry_run=args.dry_run)
        if changed:
            modified += 1
            subject_counts[subject] = subject_counts.get(subject, 0) + 1

    action = "Would modify" if args.dry_run else "Modified"
    print(f"\n{'='*60}")
    print(f"{action}: {modified} files")
    print(f"  Skipped (already has block): {skipped_already}")
    print(f"  Skipped (not a target discipline): {skipped_no_subject}")
    for subj, count in sorted(subject_counts.items()):
        print(f"  {subj}: {count} files")


if __name__ == "__main__":
    main()
