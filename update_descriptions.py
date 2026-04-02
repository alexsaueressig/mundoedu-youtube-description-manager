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
from pathlib import Path

import frontmatter
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE", "client_secrets.json")
TOKEN_FILE = os.getenv("TOKEN_FILE", "token.json")
DESCRIPTIONS_DIR = os.getenv("DESCRIPTIONS_DIR", "videos/descriptions")

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
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

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
    with open(filepath, "rb") as f:
        post = frontmatter.load(f)

    video_id = post.metadata.get("id")
    title = post.metadata.get("title", "")

    if not video_id:
        raise ValueError(f"Missing 'id' in frontmatter of '{filepath}'.")

    return video_id, title, post.content


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
    args = parser.parse_args()

    if args.file:
        md_files = [Path(args.file)]
        if not md_files[0].exists():
            sys.exit(f"ERROR: File '{args.file}' not found.")
    else:
        md_files = collect_md_files(DESCRIPTIONS_DIR)

    if not md_files:
        print(f"No Markdown files found in '{DESCRIPTIONS_DIR}/'. Nothing to update.")
        return

    print(f"Found {len(md_files)} file(s) to process.")

    if not args.dry_run:
        print("Authenticating with YouTube API…")
        youtube = get_authenticated_service()

    updated = 0
    failed = 0

    for md_path in md_files:
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
            updated += 1
        except HttpError as e:
            print(f"  FAILED   {label}: {e}")
            failed += 1
        except ValueError as e:
            print(f"  FAILED   {label}: {e}")
            failed += 1

    action = "would be updated" if args.dry_run else "updated"
    print(f"\nDone. {updated} video(s) {action}." + (f" {failed} failed." if failed else ""))


if __name__ == "__main__":
    main()
