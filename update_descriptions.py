"""
update_descriptions.py
----------------------
Reads description Markdown files from the descriptions/ folder and pushes
any changes back to YouTube via the Data API v3.

Usage:
    python update_descriptions.py [--dry-run] [--file PATH]

Options:
    --dry-run           Print what would be updated without making API calls.
    --file PATH         Update only the specified Markdown file instead of all.

Configuration is read from a .env file (see .env.example).
The script re-uses the cached OAuth token from token.json (created by
fetch_descriptions.py). If the token is missing it will open a browser
for consent with the write scope.
"""

import argparse
import os
import sys
import time
from pathlib import Path

import frontmatter
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# Allow OAuth over plain HTTP for localhost redirects (no actual network risk).
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE", "client_secrets.json")
TOKEN_FILE = os.getenv("TOKEN_FILE", "token.json")
DESCRIPTIONS_DIR = os.getenv("DESCRIPTIONS_DIR", "videos/descriptions")
PROGRESS_FILE = os.getenv("PROGRESS_FILE", "progress.txt")

# Write access requires the force-ssl scope.
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
def get_authenticated_service() -> object:
    """Return an authenticated YouTube API client with write access,
    refreshing or creating OAuth credentials as needed."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                sys.exit(
                    f"ERROR: '{CLIENT_SECRETS_FILE}' not found.\n"
                    "Download your OAuth 2.0 client secrets from Google Cloud Console\n"
                    "and save them as client_secrets.json in the project root."
                )
            flow = Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES, redirect_uri="http://localhost"
            )
            auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
            print("\nOpen this URL in your browser to authorize:\n")
            print(auth_url)
            print(
                "\nAfter authorizing, your browser will try to open http://localhost/?code=..."
                "\n(it will show an error — that's fine). Copy the full URL from the address bar and paste it below.\n"
            )
            redirect_response = input("Paste the full redirect URL: ").strip()
            flow.fetch_token(authorization_response=redirect_response)
            creds = flow.credentials

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def fetch_current_snippet(youtube, video_id: str) -> dict:
    """Return the current snippet resource for a video ID."""
    response = youtube.videos().list(
        part="snippet",
        id=video_id,
    ).execute()

    items = response.get("items", [])
    if not items:
        raise ValueError(f"Video '{video_id}' not found or not accessible.")

    return items[0]["snippet"]


def update_video_description(youtube, video_id: str, new_description: str) -> None:
    """Replace a video's description while preserving all other snippet fields."""
    snippet = fetch_current_snippet(youtube, video_id)
    snippet["description"] = new_description

    youtube.videos().update(
        part="snippet",
        body={
            "id": video_id,
            "snippet": snippet,
        },
    ).execute()


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------
def load_description_file(filepath: str) -> tuple[str, str, str]:
    """Parse a Markdown file with YAML frontmatter.

    Returns:
        (video_id, title, description_body)

    Raises:
        ValueError: if required frontmatter fields are missing.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    video_id = post.metadata.get("id")
    title = post.metadata.get("title", "")

    if not video_id:
        raise ValueError(f"Missing 'id' in frontmatter of '{filepath}'.")

    return video_id, title, post.content


def load_progress() -> set:
    """Return the set of video IDs already successfully updated."""
    if not os.path.exists(PROGRESS_FILE):
        return set()
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def save_progress(video_id: str) -> None:
    """Append a video ID to the progress file."""
    with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
        f.write(video_id + "\n")


def collect_md_files(directory: str) -> list[Path]:
    """Return all .md files in the given directory (non-recursive)."""
    d = Path(directory)
    if not d.is_dir():
        sys.exit(
            f"ERROR: Descriptions directory '{directory}' not found.\n"
            "Run fetch_descriptions.py first to populate it."
        )
    return sorted(d.glob("*.md"))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Push updated video descriptions to YouTube."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned updates without calling the API.",
    )
    parser.add_argument(
        "--file",
        metavar="PATH",
        help="Update only the specified Markdown file.",
    )
    parser.add_argument(
        "--limit",
        metavar="N",
        type=int,
        help="Process only the first N files (useful for testing).",
    )
    parser.add_argument(
        "--batch-size",
        metavar="N",
        type=int,
        default=10,
        help="Number of videos per batch (default: 10). Pauses between batches.",
    )
    parser.add_argument(
        "--batch-pause",
        metavar="SECONDS",
        type=float,
        default=2.0,
        help="Seconds to wait between batches (default: 2).",
    )
    args = parser.parse_args()

    if args.file:
        md_files = [Path(args.file)]
        if not md_files[0].exists():
            sys.exit(f"ERROR: File '{args.file}' not found.")
    else:
        md_files = collect_md_files(DESCRIPTIONS_DIR)

    if args.limit:
        md_files = md_files[: args.limit]

    if not md_files:
        print(f"No Markdown files found in '{DESCRIPTIONS_DIR}/'. Nothing to update.")
        return

    done_ids = load_progress()
    if done_ids:
        before = len(md_files)
        md_files = [f for f in md_files if f.stem not in done_ids]
        print(f"Resuming: {before - len(md_files)} already done, {len(md_files)} remaining.")
    else:
        print(f"Found {len(md_files)} file(s) to process.")

    if not args.dry_run:
        print("Authenticating with YouTube API…")
        youtube = get_authenticated_service()

    updated = 0
    failed = 0

    for i, md_path in enumerate(md_files):
        if not args.dry_run and i > 0 and i % args.batch_size == 0:
            print(f"\n--- Batch {i // args.batch_size} done. Pausing {args.batch_pause}s… ---\n")
            time.sleep(args.batch_pause)

        try:
            video_id, title, description = load_description_file(str(md_path))
        except (ValueError, Exception) as e:
            print(f"  SKIP  {md_path.name}: {e}")
            failed += 1
            continue

        label = f"[{video_id}] {title or md_path.name}"

        if args.dry_run:
            desc_preview = description[:60].replace("\n", " ")
            print(f"  DRY-RUN  {label}")
            print(f"           description starts with: \"{desc_preview}…\"")
            updated += 1
            continue

        try:
            update_video_description(youtube, video_id, description)
            print(f"  UPDATED  {label}")
            save_progress(video_id)
            updated += 1
        except HttpError as e:
            if "quotaExceeded" in str(e):
                print(f"  QUOTA EXCEEDED — stopping. Run again tomorrow to resume.")
                break
            print(f"  FAILED   {label}: {e}")
            failed += 1
        except ValueError as e:
            print(f"  FAILED   {label}: {e}")
            failed += 1

    action = "would be updated" if args.dry_run else "updated"
    print(f"\nDone. {updated} video(s) {action}." + (f" {failed} failed." if failed else ""))


if __name__ == "__main__":
    main()
