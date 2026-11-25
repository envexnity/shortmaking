"""YouTube Shorts / Video uploader using the YouTube Data API v3.

Usage:
    python scripts/youtube_upload.py --manifest scripts/upload_manifest.json
    python scripts/youtube_upload.py --video path/to/video.mp4 --title "..." --description "..."
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SECRETS = ROOT / "client_secrets.json"
DEFAULT_TOKEN = ROOT / "token.json"


def get_authenticated_service(secrets_path: Path, token_path: Path):
    """Authenticate via OAuth 2.0 (env JSON for headless CI, or local secrets/token files)."""
    creds = None
    env_token = os.environ.get("YOUTUBE_TOKEN_JSON")
    if env_token:
        creds = Credentials.from_authorized_user_info(json.loads(env_token), SCOPES)
    elif token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            if not env_token:
                token_path.write_text(creds.to_json(), encoding="utf-8")
        else:
            env_secrets = os.environ.get("YOUTUBE_CLIENT_SECRETS_JSON")
            if env_secrets:
                flow = InstalledAppFlow.from_client_config(json.loads(env_secrets), SCOPES)
            elif secrets_path.exists():
                flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
            else:
                print(
                    f"\n[ERROR] Missing OAuth client secrets file: {secrets_path}\n"
                    "To create it:\n"
                    "  1. Open Google Cloud Console -> APIs & Services -> Library -> Enable 'YouTube Data API v3'\n"
                    "  2. Configure OAuth consent screen (External) & add your Google account under Test users\n"
                    "  3. Create Credentials -> OAuth client ID -> Desktop app\n"
                    f"  4. Download the JSON and save it as: {secrets_path}\n",
                    file=sys.stderr,
                )
                sys.exit(1)
            creds = flow.run_local_server(port=0)
            token_path.write_text(creds.to_json(), encoding="utf-8")

    return build("youtube", "v3", credentials=creds)


def probe_video(video_path: Path) -> tuple[int, int, float] | None:
    """Return (width, height, duration_sec) using ffprobe, or None if unavailable."""
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height,duration",
                "-of",
                "csv=p=0",
                str(video_path),
            ],
            text=True,
        ).strip()
        parts = [p for p in out.split(",") if p]
        return int(parts[0]), int(parts[1]), float(parts[2])
    except Exception:
        return None


def upload_video(
    youtube,
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    category_id: str = "27",
    privacy_status: str = "private",
    pinned_comment: str | None = None,
    publish_at: str | None = None,
) -> str:
    """Upload a single video with resumable upload, optional schedule (publishAt), and optional comment."""
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    meta = probe_video(video_path)
    if meta:
        w, h, dur = meta
        print(f"Uploading {video_path.name} ({w}x{h}, {dur:.1f}s) -> privacy={privacy_status}")
        if w > h:
            print(
                f"  [WARNING] {video_path.name} is landscape ({w}x{h}). "
                "YouTube only classifies vertical (9:16) or square (1:1) videos <= 3 min as Shorts."
            )
    else:
        print(f"Uploading {video_path.name} -> privacy={privacy_status}")

    status_body: dict[str, object] = {
        "privacyStatus": "private" if publish_at else privacy_status,
        "selfDeclaredMadeForKids": False,
    }
    if publish_at:
        status_body["publishAt"] = publish_at

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": status_body,
    }

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        chunksize=8 * 1024 * 1024,
        resumable=True,
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"  Uploaded! Video ID: {video_id} | https://youtu.be/{video_id}")

    if pinned_comment:
        try:
            youtube.commentThreads().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "topLevelComment": {"snippet": {"textOriginal": pinned_comment}},
                    }
                },
            ).execute()
            print("  Posted engagement comment (pin manually in YouTube Studio).")
        except HttpError as exc:
            print(f"  [Note] Could not post comment automatically: {exc}")

    return video_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload YouTube Shorts via Data API v3")
    parser.add_argument("--secrets", type=Path, default=DEFAULT_SECRETS)
    parser.add_argument("--token", type=Path, default=DEFAULT_TOKEN)
    parser.add_argument("--manifest", type=Path, help="JSON manifest of videos to upload")
    parser.add_argument("--video", type=Path)
    parser.add_argument("--title")
    parser.add_argument("--description", default="")
    parser.add_argument("--tags", nargs="*", default=[])
    parser.add_argument("--category", default="27")
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    parser.add_argument("--comment", default=None)
    args = parser.parse_args()

    youtube = get_authenticated_service(args.secrets, args.token)

    if args.manifest:
        items = json.loads(args.manifest.read_text(encoding="utf-8"))
        for item in items:
            vpath = (ROOT / item["video"]).resolve()
            upload_video(
                youtube,
                video_path=vpath,
                title=item["title"],
                description=item["description"],
                tags=item.get("tags", []),
                category_id=item.get("category_id", "27"),
                privacy_status=item.get("privacy", args.privacy),
                pinned_comment=item.get("pinned_comment"),
            )
    elif args.video and args.title:
        upload_video(
            youtube,
            video_path=args.video.resolve(),
            title=args.title,
            description=args.description,
            tags=args.tags,
            category_id=args.category,
            privacy_status=args.privacy,
            pinned_comment=args.comment,
        )
    else:
        parser.error("Provide either --manifest or both --video and --title")


if __name__ == "__main__":
    main()
