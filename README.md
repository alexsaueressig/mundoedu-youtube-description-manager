# mundoedu-description-manager

Keep the MundoEdu YouTube channel (`@portalmundoedu`) with proper video descriptions.

Two scripts let you **fetch** all video descriptions to individual Markdown files and **push** edits back to YouTube via the Data API v3.

---

## Project structure

```
.
├── fetch_descriptions.py   # Download all descriptions → descriptions/*.md
├── update_descriptions.py  # Push edited descriptions back to YouTube
├── descriptions/           # Auto-created; one .md file per video
├── requirements.txt
├── .env.example            # Copy to .env and fill in your values
├── client_secrets.json     # YOU provide this (see setup below) — git-ignored
└── token.json              # Auto-created on first run — git-ignored
```

---

## Setup

### 1 — Clone & install dependencies

```bash
git clone <repo-url>
cd mundoedu-youtube-description-manager
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
```

### 2 — Enable the YouTube Data API v3

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create (or select) a project.
2. Navigate to **APIs & Services → Library**, search for **YouTube Data API v3**, and click **Enable**.

### 3 — Create OAuth 2.0 credentials

1. Go to **APIs & Services → Credentials**.
2. Click **+ Create Credentials → OAuth client ID**.
3. Choose **Desktop app**, give it a name, and click **Create**.
4. Click **Download JSON** and save the file as `client_secrets.json` in the project root.

> **Note:** If this is a new project you may need to configure the OAuth consent screen first (External, test mode is fine). Add your Google account as a test user.

### 4 — Configure environment

```bash
cp .env.example .env
# Edit .env if you need to override any defaults.
# The defaults (CHANNEL_HANDLE=portalmundoedu, descriptions/) work out of the box.
```

---

## Usage

### Fetch all descriptions

```bash
python fetch_descriptions.py
```

A browser window opens for OAuth consent on the first run. The token is saved to `token.json` for subsequent runs.

Each video is saved as `descriptions/{sanitized_title}_{videoId}.md`:

```markdown
---
id: dQw4w9WgXcQ
title: My Awesome Video
url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
---

Full video description here…
```

**Options:**

| Flag              | Description                                 |
| ----------------- | ------------------------------------------- |
| `--skip-existing` | Skip videos whose `.md` file already exists |

```bash
python fetch_descriptions.py --skip-existing
```

---

### Update descriptions

Edit any `.md` file(s) in `descriptions/` (change the body after the `---` frontmatter block), then run:

```bash
python update_descriptions.py
```

**Options:**

| Flag          | Description                                           |
| ------------- | ----------------------------------------------------- |
| `--dry-run`   | Preview changes without calling the API               |
| `--file PATH` | Update only a single file instead of the whole folder |

```bash
# Preview all changes
python update_descriptions.py --dry-run

# Update a single video
python update_descriptions.py --file descriptions/my_video_dQw4w9WgXcQ.md
```

---

## Notes

- **Quota**: The YouTube Data API v3 has a default quota of 10,000 units/day. Fetching all videos from a channel typically costs well under 100 units.
- **Re-fetching**: Running `fetch_descriptions.py` again overwrites existing files by default. Use `--skip-existing` to preserve local edits.
- **Scopes**: Fetching uses `youtube.readonly`; updating uses `youtube.force-ssl`. If you run `update_descriptions.py` first, the token will include both scopes.
