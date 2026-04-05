"""
fetch_translations.py
---------------------
Fetches the pt-BR localizations (translated title and description) for every
video whose ID is present in the descriptions/ folder and saves each one as a
Markdown file under videos/translations/pt-BR/.

YouTube stores per-language metadata under the `localizations` part of the
videos resource.  A localization entry only exists if the channel owner
explicitly added a translation in YouTube Studio.

Usage:
    python fetch_translations.py [--skip-existing] [--batch-size N]

Options:
    --skip-existing     Skip videos that already have a translation file.
    --batch-size N      How many video IDs to request per API call (max 50,
                        default 50).

Configuration is read from a .env file (see .env.example).
The script re-uses the cached OAuth token from token.json.  If the token is
missing it will open a browser for consent.
"""

import argparse
import os
import sys
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
TRANSLATIONS_DIR = os.getenv("TRANSLATIONS_DIR", "videos/translations/pt-BR")
LANGUAGE = "pt-BR"

# Read-only scope is enough for fetching localizations.
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
def get_authenticated_service() -> object:
    """Return an authenticated YouTube API client, refreshing or creating
    OAuth credentials as needed."""
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
                "\n(it will show an error — that's fine). Copy the full URL from the"
                " address bar and paste it below.\n"
            )
            redirect_response = input("Paste the full redirect URL: ").strip()
            flow.fetch_token(authorization_response=redirect_response)
            creds = flow.credentials

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------
def collect_video_ids(descriptions_dir: str) -> list[str]:
    """Return a sorted list of video IDs from the descriptions directory."""
    return sorted(
        p.stem
        for p in Path(descriptions_dir).glob("*.md")
    )


def write_translation_file(
    output_dir: str,
    video_id: str,
    title: str,
    description: str,
    url: str,
    skip_existing: bool,
) -> bool:
    """Write a Markdown file for the translated metadata.

    Returns True if the file was written, False if skipped.
    """
    filepath = os.path.join(output_dir, f"{video_id}.md")

    if skip_existing and os.path.exists(filepath):
        return False

    post = frontmatter.Post(
        description or "",
        id=video_id,
        title=title,
        url=url,
        lang=LANGUAGE,
    )
    with open(filepath, "wb") as f:
        frontmatter.dump(post, f)

    return True


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def fetch_localizations_batch(
    youtube, video_ids: list[str]
) -> dict[str, dict]:
    """Fetch localizations for up to 50 video IDs in one API call.

    Returns a dict mapping video_id → localization dict (may be empty).
    """
    response = youtube.videos().list(
        part="localizations,snippet",
        id=",".join(video_ids),
        hl=LANGUAGE,
    ).execute()

    result: dict[str, dict] = {}
    for item in response.get("items", []):
        vid = item["id"]
        result[vid] = {
            "localizations": item.get("localizations", {}),
            "default_title": item.get("snippet", {}).get("title", ""),
        }
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch pt-BR localizations for all videos and save them as "
            "Markdown files under videos/translations/pt-BR/."
        )
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip videos that already have a translation file.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        metavar="N",
        help="Number of video IDs per API request (max 50, default 50).",
    )
    args = parser.parse_args()

    batch_size = min(max(1, args.batch_size), 50)

    video_ids = collect_video_ids(DESCRIPTIONS_DIR)
    if not video_ids:
        sys.exit(f"No description files found in '{DESCRIPTIONS_DIR}/'.")

    print(f"Found {len(video_ids)} video(s) in '{DESCRIPTIONS_DIR}/'.")

    os.makedirs(TRANSLATIONS_DIR, exist_ok=True)

    youtube = get_authenticated_service()

    written = skipped = missing = 0

    for i in range(0, len(video_ids), batch_size):
        batch = video_ids[i : i + batch_size]
        print(
            f"\nFetching localizations for videos {i + 1}–{min(i + batch_size, len(video_ids))}"
            f" of {len(video_ids)} …"
        )

        try:
            data = fetch_localizations_batch(youtube, batch)
        except HttpError as exc:
            print(f"  API error: {exc}", file=sys.stderr)
            continue

        for video_id in batch:
            video_data = data.get(video_id)
            if video_data is None:
                print(f"  NOT FOUND  [{video_id}]")
                missing += 1
                continue

            localizations = video_data["localizations"]
            localization = localizations.get(LANGUAGE) or localizations.get(
                LANGUAGE.lower()
            )

            if not localization:
                print(f"  NO TRANSLATION [{video_id}] {video_data['default_title']}")
                missing += 1
                continue

            title = localization.get("title", "")
            description = localization.get("description", "")
            url = f"https://www.youtube.com/watch?v={video_id}"

            saved = write_translation_file(
                TRANSLATIONS_DIR,
                video_id,
                title,
                description,
                url,
                args.skip_existing,
            )

            if saved:
                print(f"  SAVED      [{video_id}] {title}")
                written += 1
            else:
                print(f"  SKIPPED    [{video_id}] {title}")
                skipped += 1

    print(
        f"\nDone. {written} file(s) written to '{TRANSLATIONS_DIR}/'."
        + (f" {skipped} skipped (already existed)." if skipped else "")
        + (f" {missing} video(s) had no pt-BR translation." if missing else "")
    )


if __name__ == "__main__":
    main()
