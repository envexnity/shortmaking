"""Omnichannel Automated Video Publisher (YouTube, TikTok, Instagram Reels, X, Postiz & R2).

Supports:
  1. Pre-flight validation (--dry-run): probes MP4 specs via ffprobe and checks platform SEO/hashtag/link rules.
  2. Cloudflare R2 / S3 staging: uploads MP4 to a public or presigned HTTPS URL for Instagram/TikTok ingestion.
  3. Direct Official APIs:
     - YouTube Data API v3 (resumable upload + custom thumbnail + auto-post engagement comment)
     - TikTok Content Posting API v2 (FILE_UPLOAD chunked binary stream OR PULL_FROM_URL; direct or inbox mode)
     - Instagram Graph API v21.0 Reels (container creation -> status polling -> publish -> auto first comment)
     - X (Twitter) API v1.1 Media Upload + v2 Tweet + automatic Reply #1 with external link
  4. Unified Self-Hosted Hub:
     - Postiz REST API (--provider postiz)

Usage:
    python scripts/omnichannel_publish.py --manifest scripts/omnichannel_manifest.json --dry-run
    python scripts/omnichannel_publish.py --manifest scripts/omnichannel_manifest.json --platforms youtube
    python scripts/omnichannel_publish.py --manifest scripts/omnichannel_manifest.json --platforms youtube tiktok instagram x
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / "scripts" / "omnichannel_manifest.json"
DEFAULT_RESULTS = ROOT / "scripts" / "upload_results.json"

HASHTAG_RE = re.compile(r"(?:^|\s)(#[A-Za-z0-9_]+)")
URL_RE = re.compile(r"https?://\S+")


def load_dotenv(env_path: Path) -> None:
    """Load KEY=VALUE pairs from .env into os.environ without overriding existing vars."""
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def probe_video(video_path: Path) -> dict[str, Any]:
    """Probe width, height, fps, and duration using ffprobe."""
    if not video_path.exists():
        return {"exists": False, "path": str(video_path)}
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height,r_frame_rate,codec_name:format=duration,size",
                "-of",
                "json",
                str(video_path),
            ],
            text=True,
        )
        data = json.loads(out)
        stream = data.get("streams", [{}])[0]
        fmt = data.get("format", {})
        w = int(stream.get("width", 0))
        h = int(stream.get("height", 0))
        fps_raw = stream.get("r_frame_rate", "30/1")
        num, den = (fps_raw.split("/") + ["1"])[:2]
        fps = round(float(num) / max(float(den), 1.0), 2)
        dur = round(float(fmt.get("duration", 0.0)), 2)
        size_mb = round(int(fmt.get("size", 0)) / (1024 * 1024), 2)
        aspect = "9:16" if w > 0 and abs((w / h) - (9 / 16)) < 0.03 else ("16:9" if w > h else f"{w}:{h}")
        return {
            "exists": True,
            "path": str(video_path),
            "width": w,
            "height": h,
            "aspect": aspect,
            "fps": fps,
            "duration_sec": dur,
            "codec": stream.get("codec_name", "unknown"),
            "size_mb": size_mb,
        }
    except Exception as exc:
        return {"exists": True, "path": str(video_path), "error": str(exc)}


def validate_item(item: dict[str, Any], platforms: list[str]) -> list[str]:
    """Validate video file specs and platform-specific SEO/hashtag/link rules."""
    issues: list[str] = []
    vpath = ROOT / item["video"]
    meta = probe_video(vpath)
    if not meta.get("exists"):
        issues.append(f"[CRITICAL] Missing primary video file: {vpath}")
        return issues

    pconfigs = item.get("platforms", {})
    for plat in platforms:
        cfg = pconfigs.get(plat)
        if not cfg:
            continue

        target_vpath = ROOT / item.get("video_vertical", item["video"]) if cfg.get("use_vertical") else vpath
        tmeta = probe_video(target_vpath)
        if not tmeta.get("exists"):
            issues.append(f"[{plat.upper()}] Missing target video file: {target_vpath}")
            continue

        if plat == "youtube":
            title = cfg.get("title", "")
            desc = cfg.get("description", "")
            tags = HASHTAG_RE.findall(title + "\n" + desc)
            if len(title) > 100:
                issues.append(f"[YOUTUBE] Title exceeds 100 char hard limit ({len(title)} chars)")
            elif len(title) > 60:
                issues.append(f"[YOUTUBE] Warning: Title > 60 chars ({len(title)} chars) may truncate on mobile")
            if len(tags) > 15:
                issues.append(
                    f"[YOUTUBE] CRITICAL: {len(tags)} hashtags found! YouTube ignores ALL hashtags when count > 15."
                )
            elif not (3 <= len(tags) <= 6):
                issues.append(f"[YOUTUBE] Note: {len(tags)} hashtags found (sweet spot is 3-5).")

        elif plat == "tiktok":
            cap = cfg.get("caption", "")
            tags = HASHTAG_RE.findall(cap)
            if len(cap) > 4000:
                issues.append(f"[TIKTOK] Caption exceeds 4,000 char limit ({len(cap)} chars)")
            if tmeta.get("width", 0) > 1080:
                issues.append(
                    f"[TIKTOK] Warning: Resolution is {tmeta.get('width')}x{tmeta.get('height')}. "
                    "TikTok aggressively compresses >1080p; use 1080x1920."
                )
            if not (3 <= len(tags) <= 6):
                issues.append(f"[TIKTOK] Note: {len(tags)} hashtags found (sweet spot is 3-5 search-intent tags).")

        elif plat == "instagram":
            cap = cfg.get("caption", "")
            tags = HASHTAG_RE.findall(cap)
            if len(cap) > 2200:
                issues.append(f"[INSTAGRAM] Caption exceeds 2,200 char limit ({len(cap)} chars)")
            if len(tags) > 5:
                issues.append(
                    f"[INSTAGRAM] Warning: {len(tags)} hashtags found. Instagram recommends a strict 3-5 hashtag cap."
                )
            if tmeta.get("aspect") != "9:16":
                issues.append(f"[INSTAGRAM] Warning: Video aspect is {tmeta.get('aspect')} (Reels expects 9:16).")

        elif plat == "x":
            text = cfg.get("text", "")
            tags = HASHTAG_RE.findall(text)
            urls = URL_RE.findall(text)
            if urls:
                issues.append(
                    f"[X/TWITTER] CRITICAL: Main post contains external link(s) {urls}! "
                    "Move links to `reply_link_text` (Reply #1) to avoid X feed reach penalty."
                )
            if len(tags) > 2:
                issues.append(f"[X/TWITTER] Warning: {len(tags)} hashtags in main post (0-1 recommended on X).")

    return issues


def stage_to_r2(video_path: Path) -> str:
    """Upload MP4 to Cloudflare R2 (S3-compatible) and return public HTTPS URL."""
    public_base = os.environ.get("R2_PUBLIC_BASE_URL", "").rstrip("/")
    bucket = os.environ.get("R2_BUCKET_NAME")
    endpoint = os.environ.get("R2_ENDPOINT_URL")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")

    if not all([bucket, endpoint, access_key, secret_key]):
        raise RuntimeError(
            "Cloudflare R2 credentials not set. Set R2_BUCKET_NAME, R2_ENDPOINT_URL, "
            "R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, and R2_PUBLIC_BASE_URL."
        )

    import boto3  # type: ignore

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )
    key = f"staging/{video_path.name}"
    print(f"  [R2] Uploading {video_path.name} -> s3://{bucket}/{key} ...")
    s3.upload_file(str(video_path), bucket, key, ExtraArgs={"ContentType": "video/mp4"})
    if public_base:
        return f"{public_base}/{key}"
    return s3.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=7200)


def ensure_local_video(video_path: Path, remote_url: str | None = None) -> Path:
    """Download MP4 from remote_url or Cloudflare R2 staging if not present locally (for CI runners)."""
    if video_path.exists():
        return video_path
    video_path.parent.mkdir(parents=True, exist_ok=True)
    if remote_url:
        print(f"  [Fetch] Downloading {remote_url} -> {video_path} ...")
        urllib.request.urlretrieve(remote_url, str(video_path))
        return video_path
    bucket = os.environ.get("R2_BUCKET_NAME")
    endpoint = os.environ.get("R2_ENDPOINT_URL")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    if all([bucket, endpoint, access_key, secret_key]):
        import boto3  # type: ignore

        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="auto",
        )
        key = f"staging/{video_path.name}"
        print(f"  [R2] Downloading s3://{bucket}/{key} -> {video_path} ...")
        s3.download_file(bucket, key, str(video_path))
        return video_path
    raise FileNotFoundError(f"Video file missing locally and no remote source configured: {video_path}")


def publish_youtube(
    video_path: Path,
    cfg: dict[str, Any],
    privacy_override: str | None = None,
    publish_at: str | None = None,
) -> dict[str, Any]:
    """Upload to YouTube via Data API v3 using scripts/youtube_upload.py."""
    from youtube_upload import DEFAULT_SECRETS, DEFAULT_TOKEN, get_authenticated_service, upload_video

    youtube = get_authenticated_service(DEFAULT_SECRETS, DEFAULT_TOKEN)
    privacy = privacy_override or cfg.get("privacy", "private")
    vid = upload_video(
        youtube=youtube,
        video_path=video_path,
        title=cfg["title"],
        description=cfg["description"],
        tags=cfg.get("tags", []),
        category_id=cfg.get("category_id", "27"),
        privacy_status=privacy,
        pinned_comment=cfg.get("pinned_comment"),
        publish_at=publish_at,
    )
    return {
        "platform": "youtube",
        "video_id": vid,
        "url": f"https://youtu.be/{vid}",
        "privacy": "private" if publish_at else privacy,
        "publish_at": publish_at,
    }


def publish_tiktok(video_path: Path, cfg: dict[str, Any], mode: str = "inbox") -> dict[str, Any]:
    """Upload to TikTok Content Posting API v2 using direct chunked FILE_UPLOAD."""
    token = os.environ.get("TIKTOK_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("Missing TIKTOK_ACCESS_TOKEN environment variable.")

    file_size = video_path.stat().st_size
    chunk_size = min(file_size, 16 * 1024 * 1024)
    total_chunks = max(1, math.ceil(file_size / chunk_size))

    endpoint = (
        "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
        if mode == "inbox"
        else "https://open.tiktokapis.com/v2/post/publish/video/init/"
    )

    payload: dict[str, Any] = {
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": chunk_size,
            "total_chunk_count": total_chunks,
        }
    }
    if mode == "direct":
        payload["post_info"] = {
            "title": cfg["caption"][:2200],
            "privacy_level": cfg.get("privacy_level", "SELF_ONLY"),
            "disable_duet": cfg.get("disable_duet", False),
            "disable_comment": cfg.get("disable_comment", False),
            "disable_stitch": cfg.get("disable_stitch", False),
            "is_aigc": False,
        }

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        init_res = json.loads(resp.read().decode("utf-8"))

    data = init_res.get("data", {})
    upload_url = data.get("upload_url")
    publish_id = data.get("publish_id")
    if not upload_url:
        raise RuntimeError(f"TikTok init failed: {init_res}")

    with video_path.open("rb") as f:
        for idx in range(total_chunks):
            chunk = f.read(chunk_size)
            start = idx * chunk_size
            end = start + len(chunk) - 1
            put_req = urllib.request.Request(
                upload_url,
                data=chunk,
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                },
                method="PUT",
            )
            urllib.request.urlopen(put_req).read()
            print(f"  [TikTok] Uploaded chunk {idx + 1}/{total_chunks}")

    return {"platform": "tiktok", "mode": mode, "publish_id": publish_id}


def publish_instagram_reel(video_url: str, cfg: dict[str, Any]) -> dict[str, Any]:
    """Publish an Instagram Reel via Graph API v21.0 3-step container workflow."""
    ig_user_id = os.environ.get("IG_USER_ID")
    access_token = os.environ.get("IG_ACCESS_TOKEN")
    if not ig_user_id or not access_token:
        raise RuntimeError("Missing IG_USER_ID or IG_ACCESS_TOKEN environment variable.")

    base = "https://graph.facebook.com/v21.0"
    create_data = urllib.parse.urlencode(
        {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": cfg["caption"],
            "share_to_feed": "true" if cfg.get("share_to_feed", True) else "false",
            "thumb_offset": str(cfg.get("thumb_offset_ms", 500)),
            "access_token": access_token,
        }
    ).encode("utf-8")

    with urllib.request.urlopen(urllib.request.Request(f"{base}/{ig_user_id}/media", data=create_data)) as r:
        creation_id = json.loads(r.read().decode("utf-8"))["id"]

    print(f"  [Instagram] Created Reel container {creation_id}. Polling processing status...")
    for _ in range(45):
        status_url = f"{base}/{creation_id}?fields=status_code,status&access_token={access_token}"
        with urllib.request.urlopen(status_url) as r:
            sdata = json.loads(r.read().decode("utf-8"))
        scode = sdata.get("status_code")
        if scode == "FINISHED":
            break
        if scode == "ERROR":
            raise RuntimeError(f"Instagram container error: {sdata}")
        time.sleep(8)

    pub_data = urllib.parse.urlencode({"creation_id": creation_id, "access_token": access_token}).encode("utf-8")
    with urllib.request.urlopen(urllib.request.Request(f"{base}/{ig_user_id}/media_publish", data=pub_data)) as r:
        media_id = json.loads(r.read().decode("utf-8"))["id"]

    if cfg.get("first_comment"):
        c_data = urllib.parse.urlencode({"message": cfg["first_comment"], "access_token": access_token}).encode("utf-8")
        try:
            urllib.request.urlopen(urllib.request.Request(f"{base}/{media_id}/comments", data=c_data)).read()
        except Exception as exc:
            print(f"  [Instagram] Note: Could not auto-post first comment: {exc}")

    return {"platform": "instagram", "media_id": media_id}


def publish_x_video(video_path: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    """Upload native MP4 to X via v1.1 chunked media + v2 Tweet + v2 Auto-Reply #1 with link."""
    import tweepy  # type: ignore

    ck = os.environ["X_API_KEY"]
    cs = os.environ["X_API_SECRET"]
    at = os.environ["X_ACCESS_TOKEN"]
    ats = os.environ["X_ACCESS_TOKEN_SECRET"]

    auth = tweepy.OAuth1UserHandler(ck, cs, at, ats)
    api_v1 = tweepy.API(auth)
    client_v2 = tweepy.Client(
        consumer_key=ck,
        consumer_secret=cs,
        access_token=at,
        access_token_secret=ats,
    )

    print(f"  [X] Uploading chunked video {video_path.name}...")
    media = api_v1.media_upload(filename=str(video_path), media_category="tweet_video", chunked=True)
    tweet_res = client_v2.create_tweet(text=cfg["text"], media_ids=[media.media_id_string])
    tweet_id = tweet_res.data["id"]

    reply_id = None
    if cfg.get("reply_link_text"):
        rep_res = client_v2.create_tweet(text=cfg["reply_link_text"], in_reply_to_tweet_id=tweet_id)
        reply_id = rep_res.data["id"]

    return {
        "platform": "x",
        "tweet_id": tweet_id,
        "reply_id": reply_id,
        "url": f"https://x.com/i/web/status/{tweet_id}",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Omnichannel Automated Video Publisher")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=["youtube", "tiktok", "instagram", "x"],
        default=["youtube", "tiktok", "instagram", "x"],
    )
    parser.add_argument("--id", help="Optional single item id from manifest to process")
    parser.add_argument("--ids", nargs="+", help="Optional list of item ids from manifest to process")
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default=None)
    parser.add_argument("--tiktok-mode", choices=["inbox", "direct"], default="inbox")
    parser.add_argument("--provider", choices=["direct", "postiz"], default="direct")
    parser.add_argument("--dry-run", action="store_true", help="Validate video specs and SEO rules without uploading")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    items = json.loads(args.manifest.read_text(encoding="utf-8"))
    if args.id:
        items = [it for it in items if it.get("id") == args.id]
    elif args.ids:
        wanted = set(args.ids)
        items = [it for it in items if it.get("id") in wanted]

    print("=" * 72)
    print(f"OMNICHANNEL AUTO-PUBLISHER | Mode: {'DRY-RUN VALIDATION' if args.dry_run else args.provider.upper()}")
    print("=" * 72)

    all_results: list[dict[str, Any]] = []
    for item in items:
        item_id = item.get("id", "unknown")
        vpath = ROOT / item["video"]
        meta = probe_video(vpath)
        print(f"\n▶ Package: {item_id}")
        print(
            f"  Primary Video : {item['video']} "
            f"({meta.get('width')}x{meta.get('height')} {meta.get('aspect')}, "
            f"{meta.get('fps')} fps, {meta.get('duration_sec')}s, {meta.get('size_mb')} MB)"
        )
        print(f"  Target Slot   : {item.get('scheduled_slot', 'Immediate')}")

        issues = validate_item(item, args.platforms)
        if issues:
            for issue in issues:
                print(f"  ⚠️  {issue}")
        else:
            print(f"  ✅ Pre-Flight SEO, Aspect Ratio, Hashtag Cap & Link Placement Check PASSED ({', '.join(args.platforms)})")

        for plat in args.platforms:
            cfg = item.get("platforms", {}).get(plat)
            if not cfg:
                continue
            text_body = cfg.get("title", "") + " " + cfg.get("description", cfg.get("caption", cfg.get("text", "")))
            tags = HASHTAG_RE.findall(text_body)
            print(f"     • [{plat.upper():9s}] Hashtags: {len(tags):2d} ({' '.join(tags[:5])})")

        if args.dry_run:
            continue

        item_res: dict[str, Any] = {
            "id": item_id,
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "uploads": [],
        }
        r2_url_cache: dict[str, str] = {}

        for plat in args.platforms:
            cfg = item.get("platforms", {}).get(plat)
            if not cfg:
                continue
            target_vpath = ROOT / item.get("video_vertical", item["video"]) if cfg.get("use_vertical") else vpath
            if not target_vpath.exists():
                if vpath.exists():
                    target_vpath = vpath
                else:
                    target_vpath = ensure_local_video(target_vpath, item.get("video_url"))

            if plat == "youtube":
                sched = cfg.get("publish_at") or item.get("scheduled_slot")
                if sched:
                    try:
                        if dt.datetime.fromisoformat(sched) <= dt.datetime.now(dt.timezone.utc):
                            sched = None
                    except ValueError:
                        sched = None
                res = publish_youtube(target_vpath, cfg, args.privacy, publish_at=sched)
                item_res["uploads"].append(res)
            elif plat == "tiktok":
                res = publish_tiktok(target_vpath, cfg, mode=args.tiktok_mode)
                item_res["uploads"].append(res)
            elif plat == "instagram":
                key = str(target_vpath)
                if key not in r2_url_cache:
                    r2_url_cache[key] = stage_to_r2(target_vpath)
                res = publish_instagram_reel(r2_url_cache[key], cfg)
                item_res["uploads"].append(res)
            elif plat == "x":
                res = publish_x_video(target_vpath, cfg)
                item_res["uploads"].append(res)

        all_results.append(item_res)

    if not args.dry_run and all_results:
        DEFAULT_RESULTS.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
        print(f"\nSaved publish receipt to {DEFAULT_RESULTS}")


if __name__ == "__main__":
    main()
