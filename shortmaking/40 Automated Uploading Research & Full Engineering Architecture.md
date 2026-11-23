---
title: 40 Automated Uploading Research & Full Engineering Architecture
tags:
  - automation
  - auto-upload
  - api
  - youtube-api
  - tiktok-api
  - instagram-api
  - postiz
  - playwright
  - n8n
  - cloudflare-r2
area: distribution
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Comprehensive technical research and implementation blueprint for 100% automated multi-platform video uploading via Official APIs, Self-Hosted Postiz, Playwright Stealth Browsers, Cloudflare R2, and Python/n8n pipelines.
---

# 40 Automated Uploading Research & Full Engineering Architecture

← Back to [[00 Social Publishing Home]] | [[00 Home|Shortmaking Studio Home]]

This document synthesizes our technical research on **100% hands-free, zero-touch video uploading** across YouTube, TikTok, Instagram Reels, Facebook Reels, X (Twitter), LinkedIn, Threads, and Reddit—and pairs directly with the runnable **`scripts/omnichannel_publish.py`** engine in this workspace.

---

## 1. Executive Architecture Comparison: The Live MCP Stack + 4 Automation Tiers

> [!IMPORTANT] Active Default Path (Tier 0 — Live Official API MCP Stack)
> When asked to **"upload"** or **"post"** any video, **ALWAYS upload to ALL 3 configured live platforms (`YouTube Shorts`, `TikTok`, `Instagram Reels`)** using the active Antigravity MCP servers (`youtube`, `tiktok`, `instagram`) documented in `.agents/skills/social-posting/SKILL.md`:
> - **YouTube (`youtube:upload_video`)**: Local 9:16 MP4, supports `publish_at` (RFC3339 with `privacy="private"`).
> - **TikTok (`tiktok:creator_info` → `tiktok:post_video` → `tiktok:post_status`)**: Local MP4 direct publish (`@pixelatepast`).
> - **Instagram Reels (`media-host.ps1` Cloudflare quick tunnel → `instagram:instagram_post_reel(apply=true)` → `media-host.ps1 stop`)**: Zero-cost HTTPS staging for `@pixelatepast`.

There are **four distinct engineering architectures** for automating social video uploads. Each solves a specific bottleneck (cost, API audit friction, quota limits, or platform-exclusive UI features):

```mermaid
flowchart TD
    MP4["Rendered Master MP4\n(out/emu-war.mp4 or mars_final.mp4)"] --> R2["Cloudflare R2 Staging Bucket\n(Zero-Egress Public/Presigned HTTPS URL)"]
    MP4 --> LOCAL["Local File Stream\n(Direct Chunked Upload)"]
    
    R2 --> T1["Tier 1: Official Direct Platform APIs\n(YouTube v3, TikTok v2, IG Graph v21, X v2)"]
    R2 --> T2["Tier 2: Unified Self-Hosted / Aggregator API\n(Postiz Docker / Upload-Post / Late)"]
    LOCAL --> T1
    LOCAL --> T3["Tier 3: Stealth Browser Automation\n(Playwright Persistent Chrome Profile)"]
    
    T1 --> OBS["Obsidian Upload Queue & Tracker.base\n(Auto-Updated Status + Live Video URLs)"]
    T2 --> OBS
    T3 --> OBS
```

| Tier | Architecture | Cost | API App Review Audit Required? | Best For | Limitations |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **Tier 1: Direct Official Platform APIs** (`scripts/omnichannel_publish.py`) | Python CLI calling YouTube Data API v3, TikTok Content Posting API v2, IG Graph API v21, X API v2 | **$0 / Free** | **No** for YouTube (Test User mode) & IG/FB (Dev mode for own pages); **Yes** for TikTok Public Direct Post (Inbox mode requires no public audit) | Maximum control, zero monthly SaaS fees, native scheduling & auto-comments | Requires setting up OAuth credentials once per platform; YouTube API cannot set "Related Video" pill. |
| **Tier 2A: Self-Hosted Open-Source Hub (`Postiz`)** | Dockerized `gitroomhq/postiz` + REST API / MCP (`POST /api/public/v1/posts`) | **$0 / Free** (Self-hosted) | Uses your own app keys or Postiz OAuth bridge | Visual calendar UI + 1 unified REST call to 10+ networks + AI agent MCP integration | Requires Docker running locally or on a $5 VPS. |
| **Tier 2B: Commercial Unified Upload APIs** (`Upload-Post`, `Late`, `Ayrshare`, `Bundle.social`) | Single REST endpoint (`POST /api/upload`) that fans out to YT, TikTok, IG, X, LinkedIn, FB | `$15 – $49/mo` | **Zero App Audits** (Uses the provider's pre-approved enterprise OAuth apps!) | Instant 5-minute setup with **zero** developer portal reviews or token maintenance | Monthly subscription cost. |
| **Tier 3: Stealth Browser Automation (`Playwright` / `Patchright`)** | Persistent local Chrome profile (`--user-data-dir`) + DOM automation (`tiktok-uploader`, `social-auto-upload`) | **$0 / Free** | **Zero App Audits & Unlimited Quota** | Setting YouTube Shorts **"Related Video"** link, attaching **Trending Platform Audio**, bypassing API quotas | Must run on your local residential IP (never a cheap datacenter VPN) and breaks if platform DOM selectors change. |

---

## 2. Tier 1 Deep-Dive: Official Direct Platform APIs

### A. YouTube Data API v3 (`videos.insert` + `thumbnails.set` + `commentThreads.insert`)
- **Endpoints & Scopes**:
  - `https://www.googleapis.com/auth/youtube.upload`
  - `https://www.googleapis.com/auth/youtube.force-ssl` (required to auto-post the engagement comment!)
- **How Shorts Classification Works via API**:
  - There is **no separate "Shorts API"**. Any video uploaded via `videos.insert` with an aspect ratio of **`9:16` (or `1:1`)** and duration **`≤ 180 seconds`** is automatically classified and routed as a **YouTube Short**.
- **Quota Math (`10,000 Units/Day` Free Tier)**:
  - `videos.insert` = **`1,600 units`** (approx. **6 uploads/day** on a single free Google Cloud project).
  - `thumbnails.set` = **`50 units`**.
  - `commentThreads.insert` = **`50 units`**.
  - *Scaling Trick*: You can either submit the free **YouTube API Quota Extension Form** (usually grants `50,000 – 1,000,000 units/day`) OR create 2 separate GCP projects (`12 uploads/day` free).
- **⚠️ Critical Gotcha — The "Unverified App = Forced Private Lock" Trap**:
  - If your Google Cloud OAuth Consent Screen is in **"Testing"** mode, you **MUST** add your YouTube channel's Google email to the **Test Users** list.
  - Furthermore, Google restricts unverified third-party apps from uploading `public` videos **unless** the OAuth client is owned by the exact same Google account/project or passes Google's free OAuth Verification check. If an upload ever gets locked as `Private (Locked by API)`, click **"Publish"** once in YouTube Studio or submit the OAuth verification screen in GCP Console.

### B. TikTok Content Posting API v2 (`Direct Post` vs. `Upload to Inbox`)
- **Two Modes in TikTok for Developers**:
  1. **Direct Post (`POST https://open.tiktokapis.com/v2/post/publish/video/init/`)**:
     - Scope: `video.publish`.
     - Publishes directly to your public TikTok profile with caption, hashtags, `privacy_level: "PUBLIC_TO_EVERYONE"`, and `thumb_offset`.
     - **Important Audit Rule**: Until your TikTok Developer App passes TikTok's free App Review (usually takes `2–5 business days` with a screen recording of your script), Direct Post API calls are restricted to `privacy_level: "SELF_ONLY"` (Private).
  2. **Upload to Inbox (`POST https://open.tiktokapis.com/v2/post/publish/inbox/video/init/`)**:
     - Scope: `video.upload`.
     - **Works immediately in Sandbox/Unaudited mode!** Pushes the fully rendered `.mp4` and caption straight into your TikTok mobile app's **System Notifications ("Your video is ready to post")** so you can tap **Post** in 3 seconds (and optionally attach a trending TikTok sound at `-20 dB`!).
- **Ingestion Methods (`PULL_FROM_URL` vs. `FILE_UPLOAD`)**:
  - `PULL_FROM_URL`: TikTok downloads the MP4 directly from your **Cloudflare R2** custom domain (requires adding a `tiktok-developers-site-verification=...` DNS TXT record on Cloudflare—takes 30 seconds!).
  - `FILE_UPLOAD`: Direct binary `PUT` chunk upload (`chunk_size = 10MB` to `64MB`) to the `upload_url` returned by `/init/`—requires **zero domain verification** and is built directly into `scripts/omnichannel_publish.py`!

### C. Instagram Graph API v21.0 (Automated Reels Publishing)
- **Prerequisites**:
  1. Convert your Instagram account to a free **Creator** or **Business** account.
  2. Link it to a Facebook Page and create a Meta Developer App with `instagram_basic` and `instagram_content_publish` permissions.
- **The 3-Step Container Pipeline**:
  - Instagram **does not** accept raw binary uploads in Step 1—it requires a **publicly reachable HTTPS URL** (`video_url` from Cloudflare R2 or S3):
  1. **Create Reel Container**:
     `POST https://graph.facebook.com/v21.0/{ig_user_id}/media`
     Payload: `media_type="REELS"`, `video_url="https://cdn.yourdomain.com/emu-war.mp4"`, `caption="..."`, `share_to_feed="true"`, `thumb_offset=500`.
  2. **Poll Processing Status**:
     `GET https://graph.facebook.com/v21.0/{creation_id}?fields=status_code,status` every `8 seconds` until `status_code == "FINISHED"`.
  3. **Publish Reel + Auto-Post First Comment**:
     `POST https://graph.facebook.com/v21.0/{ig_user_id}/media_publish` (`creation_id={creation_id}`) → returns `media_id` → immediately call `POST https://graph.facebook.com/v21.0/{media_id}/comments` with your engagement question!
- **60-Day Token Auto-Refresh**:
  - Exchange your short-lived token for a **60-day Long-Lived User Access Token** or a **Non-Expiring System User Token** inside Meta Business Settings so your cron job never stops for re-authentication.

### D. X (Twitter) API v2 + v1.1 Media Upload (With Auto-Reply Link)
- **Why Both v1.1 and v2 Are Used**:
  1. Upload the `.mp4` using the chunked media endpoint (`POST https://upload.twitter.com/1.1/media/upload.json` with `INIT` → `APPEND` 5MB chunks → `FINALIZE` → poll `STATUS` until `processing_info.state == "succeeded"`).
  2. Publish Tweet #1 via **X API v2 (`POST https://api.twitter.com/2/tweets`)** passing `{"text": caption, "media": {"media_ids": [media_id]}}` (**with zero external links!**).
  3. Capture `tweet_id = response["data"]["id"]` and immediately fire a second `POST /2/tweets` with `{"text": reply_with_youtube_link, "reply": {"in_reply_to_tweet_id": tweet_id}}`.
- **Cost Note**: Both endpoints work on the **X API Free / Basic tier** using `tweepy` (`OAuth1UserHandler` for media upload + `Client` for v2 tweet creation).

---

## 3. Tier 2 Deep-Dive: Self-Hosted `Postiz` + Cloudflare R2 + `n8n`

If you want a **visual calendar dashboard + 1 unified API call** that posts to **YouTube, TikTok, Instagram, Facebook, X, LinkedIn, Threads, Pinterest, and Reddit** simultaneously:

### A. Self-Hosting `Postiz` (`gitroomhq/postiz`) via Docker
```yaml
# docker-compose.postiz.yml
services:
  postiz:
    image: ghcr.io/gitroomhq/postiz-app:latest
    restart: always
    ports:
      - "5000:5000"
    environment:
      MAIN_URL: "http://localhost:5000"
      FRONTEND_URL: "http://localhost:5000"
      NEXT_PUBLIC_BACKEND_URL: "http://localhost:5000/api"
      DATABASE_URL: "postgresql://postiz-user:postiz-pass@postiz-postgres:5432/postiz-db"
      REDIS_URL: "redis://postiz-redis:6379"
      STORAGE_PROVIDER: "local"
    volumes:
      - ./postiz-uploads:/uploads
    depends_on:
      - postiz-postgres
      - postiz-redis
```
- Once running on `http://localhost:5000`, connect your social accounts once in the Web UI, copy your **Postiz API Key**, and run:
  ```powershell
  python scripts/omnichannel_publish.py --manifest scripts/omnichannel_manifest.json --provider postiz
  ```

### B. Why Cloudflare R2 Is the Ultimate Media Staging Layer
Instagram Graph API, Facebook Reels API, and TikTok `PULL_FROM_URL` all require a fast, public HTTPS link to fetch your rendered `.mp4`.
- **Cloudflare R2** offers **10 GB/month free storage** and **0% egress bandwidth fees** (`$0.00` even if 5 platforms download a 50 MB master file).
- Configure a lifecycle policy on your R2 bucket (`shortmaking-staging`) to **auto-delete staged `.mp4` files after 7 days**, keeping storage usage permanently at `$0.00`.

---

## 4. Tier 3 Deep-Dive: Stealth Headless Browser Automation (`Playwright` / `Patchright`)

When should you use **Playwright browser automation** instead of REST APIs?
1. **Setting the YouTube Shorts "Related Video" Bridge Pill**: Google's YouTube Data API v3 still does not expose the `relatedVideoId` field for Shorts—only YouTube Studio's web UI (`studio.youtube.com`) can set it.
2. **Zero API Quotas & Zero TikTok App Review Wait Time**: Uploading through a real authenticated Chrome session (`launch_persistent_context`) bypasses API unit limits completely.

### Rules for Zero-Ban Browser Upload Automation
1. **Always Use a Persistent Real Chrome Profile (`channel="chrome"`, `user_data_dir`)**:
   - Never log in from scratch on every run. Log in once manually in a dedicated Chrome profile (`C:\Users\AFADAZIO\.shortmaking_chrome_profile`), and reuse that persistent directory.
2. **Use `patchright` (Patched Playwright) or Disable Automation Flags**:
   - Standard headless Chromium leaks `navigator.webdriver = true` and CDP `Runtime.enable` fingerprints that TikTok's Arkose/Shapes anti-bot detects.
   - Run **headed (`headless=False`)** or use **`patchright`** (`pip install patchright`) with `--disable-blink-features=AutomationControlled` on your **local residential IP** (never a datacenter proxy).
3. **Hybrid API + Browser Best Practice**:
   - Upload the heavy `.mp4` file, title, description, tags, and pinned comment reliably via **YouTube Data API v3 (`scripts/omnichannel_publish.py`)**, then optionally use a 10-second Playwright step on `studio.youtube.com/video/{VIDEO_ID}/edit` solely to link the **Related Video** pill!

---

## 5. Using the Workspace's Built-In `scripts/omnichannel_publish.py`

We have built a complete, production-ready omnichannel publisher in `scripts/omnichannel_publish.py` paired with `scripts/omnichannel_manifest.json`.

### Supported Capabilities Out of the Box
- **Pre-Flight Validator (`--dry-run`)**: Probes every video with `ffprobe` (resolution, aspect ratio, FPS, duration) and verifies every platform's title length, description length, hashtag cap (`≤5` for IG/TikTok, `≤15` for YT, `≤1` for X), and file existence before touching any API.
- **Cloudflare R2 / S3 Auto-Stager**: Automatically uploads your local `.mp4` to Cloudflare R2 and generates a public or presigned URL when publishing to Instagram Reels or TikTok `PULL_FROM_URL`.
- **Direct Multi-Platform Fan-Out**:
  - `youtube`: Resumable `videos.insert` + custom thumbnail (`thumbnails.set`) + automatic engagement comment (`commentThreads.insert`).
  - `tiktok`: Supports **both** `FILE_UPLOAD` (direct local binary chunked upload—no R2 or domain verification needed!) and `PULL_FROM_URL`, plus `--tiktok-mode inbox` (zero app audit needed) or `direct`.
  - `instagram`: Full 3-step Reels container creation → status polling → publish → automatic first comment.
  - `x`: Chunked `v1.1` video upload + `v2` main post (zero links) + automatic `v2` Reply #1 containing your YouTube link!
  - `postiz`: Single unified API call to a self-hosted or cloud Postiz instance.
- **Automatic Log Output**: Writes `scripts/upload_results.json` with every published video ID, live URL, and timestamp.
