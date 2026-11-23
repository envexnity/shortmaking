---
title: Omnichannel Social Media & Auto-Publishing Vault — Home
tags:
  - moc
  - dashboard
  - social-media
  - distribution
  - seo
  - hashtags
  - automation
  - auto-upload
area: distribution
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Master command center for packaging, optimizing, scheduling, and automatically uploading short-form and long-form videos across YouTube, TikTok, Instagram Reels, X, Facebook, LinkedIn, Threads, Snapchat, and Reddit.
---

# Omnichannel Social Media & Auto-Publishing Vault

> [!IMPORTANT] Mandatory Default Rule: "Upload" = ALL Configured Platforms (`YouTube` + `TikTok` + `Instagram`)
> Whenever the user asks to **"upload"**, **"post"**, or **"publish"** a video (without explicitly naming a single platform), **ALWAYS upload to ALL 3 live platforms simultaneously** (`YouTube Shorts`, `TikTok`, and `Instagram Reels`) via the Antigravity MCP stack in `.agents/skills/social-posting/SKILL.md`:
> 1. **YouTube Shorts** (`youtube:upload_video` — channel `"pixelate past"`, supports RFC3339 `publish_at` + `privacy="private"` for scheduled drops)
> 2. **TikTok** (`tiktok:creator_info` → `tiktok:post_video` → `tiktok:post_status` — `@pixelatepast`)
> 3. **Instagram Reels** (`C:\Users\AFADAZIO\.gemini\config\social-posting\media-host.ps1 start` → `instagram:instagram_post_reel` with `apply: true` → `media-host.ps1 stop` — `@pixelatepast`)
>
> Adapt title/caption/hashtags per platform (never word-for-word identical), log every upload receipt in `scripts/daily_post_queue.json`, and report all 3 permalinks/IDs.

> [!IMPORTANT] Connected Sister Vault to the Shortmaking Studio
> This vault is **bidirectionally wired** into the **[[00 Home|Shortmaking Engineering Vault]]** (`[[AGENTS]]`).
> - **Parent Studio Dashboard**: [[00 Home|Shortmaking Engineering Vault — Home]]
> - **Quick Engineering Cheat Sheet**: [[01 Quick Reference]]
> - **Encoding & Retention Pre-Flight**: [[Uploading, Algorithm Packaging & Retention Optimization]]
> - **Completed Videos Ready to Publish**: [[00 Completed Videos]] ([[Emu War (1932) - Completed Video]] | [[Mars - What Would Kill You First (Completed Video)]])
> - **Visual Pipeline Canvas**: [[Omnichannel Auto-Upload Pipeline.canvas]] ↔ [[Shortmaking Master Pipeline.canvas]]

Welcome to the **Omnichannel Social Media & Auto-Publishing Vault**. Rendering a 9/10 video is only Phase 1—this vault governs **Phase 2: Packaging, Multimodal SEO, Description & Hashtag Engineering, Global Upload Timing, and 100% Zero-Touch Automated Uploading**.

---

## 1. Master Platform Comparison Matrix (2026 Algorithm & Spec Rules)

Every social platform runs a distinct recommendation model, OCR/ASR indexing pipeline, and metadata parser. Never blast identical raw metadata across all networks:

| Platform | Aspect Ratio & Res | Sweet-Spot Length | #1 Algorithm Signal (2026) | Title / Caption Limit | Optimal Hashtags | Link Placement | Auto-Upload API | Master Playbook |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **YouTube Shorts** | `9:16` (`1440×2560` 2K or `1080×1920`) | **`< 45s`** (`28–42s` sweet spot; max `180s`) | **Viewed vs. Swiped Away (`>78%`)** + **APV (`>98%`)** | Title: `≤52 chars` visible (`100` max) | **`3–5` tags** (`#Shorts` + `2–4` niche; `>15` = spam penalty) | Native **"Related Video"** pill + Pinned Comment | YouTube Data API v3 (`videos.insert`) | [[01 YouTube Shorts & Long-Form Master Guide]] |
| **YouTube Long-Form** | `16:9` (`1920×1080` or `3840×2160`) | `2:15–3:30` (Mini) or `8:05–14:00` | **CTR (`>7.5%`)** + **AVD (`>50%`)** + **Session Watch Time** | Title: `48–60 chars` + Custom `1280×720` Thumb | **`3` tags** above title (`first 3 in description`) | First 2 lines of Description + Pinned Comment | YouTube Data API v3 + `thumbnails.set` | [[01 YouTube Shorts & Long-Form Master Guide]] |
| **TikTok** | `9:16` (`1080×1920` strict; `>1080p` downscaled) | **`< 45s`** (`28–42s` velocity sweet spot) | **Rewatches (`5 pts`)** + **DM Shares (`5 pts`)** + **85%+ Completion** | `4,000 chars` (First `90 chars` visible before *"…more"*) | **`3–5` search-intent tags** (Avoid generic `#fyp` only) | Bio Link (`1,000+` followers) | TikTok Content Posting API v2 (`video.publish`) | [[02 TikTok Algorithm, SEO & Publishing Guide]] |
| **Instagram Reels** | `9:16` (`1080×1920`, `3:4` grid safe zone) | **`< 45s`** (`28–42s` sweet spot) | **Sends per Reach (DM Shares)** + **<3s Skip Rate** | `2,200 chars` (First `125 chars` visible) | **Strict `3–5` max** (NLP indexes caption keywords) | Automation DM keyword (*"Comment MARS"*) or Bio | Instagram Graph API v21.0 (`media_type=REELS`) | [[03 Instagram Reels, Trial Reels & Threads Guide]] |
| **Facebook Reels** | `9:16` (`1080×1920`) | **`< 45s`** (`28–42s`) | **Completion Rate** + **Shares to Groups/Feed** | `2,200 chars` (Short 1-line hook best) | **`3–5` niche tags** | First Comment (Never in main post body) | Meta Graph API (`/me/video_reels`) | [[04 X (Twitter), Facebook Reels, LinkedIn, Snapchat & Reddit Guide]] |
| **X (Twitter) Video** | `9:16` or `16:9` (`1080p`) | `35–90s` (`≤140s` standard, `≤4h` Premium) | **Author-Engaged Replies (`+75x`)** + **30s+ Dwell Time** | `280 chars` hook (Longer on Premium, keep punchy) | **`1–2` max** (or `0`—inline keywords perform better) | **Reply #1 ONLY** (Main-post links get `-50%` reach penalty!) | X API v2 (`/2/tweets`) + v1.1 Chunked Media | [[04 X (Twitter), Facebook Reels, LinkedIn, Snapchat & Reddit Guide]] |
| **LinkedIn Video** | `9:16` (Mobile Video Tab) or `4:5` / `16:9` | `45–90s` | **Dwell Time** + **Substantive Comments (`15+ words`)** | `3,000 chars` (`140–210 chars` before *"…see more"*) | **`3` industry tags** at bottom of post | First Comment or bottom of post | LinkedIn Videos API (`/rest/videos`) | [[04 X (Twitter), Facebook Reels, LinkedIn, Snapchat & Reddit Guide]] |
| **Snapchat / Pinterest / Reddit** | `9:16` (Snap/Pin) or `9:16`/`16:9` (Reddit) | `30–60s` | **Completion + Screenshots/Saves** (Pin) / **Upvote Velocity** (Reddit) | Snap: `100 chars` / Pin: `100 chars` / Reddit: `<120 chars` | Snap: `2–4` / Pin: `0` (use Keywords) / Reddit: `0` | Native Outbound Link (Pinterest) / Comments (Reddit) | Pinterest API v5 / Snap Marketing API / PRAW | [[04 X (Twitter), Facebook Reels, LinkedIn, Snapchat & Reddit Guide]] |

---

## 2. Vault Navigation & Core Engineering Guides

### 📱 `10 Platform Playbooks` — Deep-Dive Rules Per Network
1. [[01 YouTube Shorts & Long-Form Master Guide]] — Seed cohort tiers, Engaged Views vs. Impressions, the `Related Video` Shorts-to-Long-Form bridge, title truncation limits, and synthetic media flags.
2. [[02 TikTok Algorithm, SEO & Publishing Guide]] — Point-weight scoring formula, 4-layer TikTok Search SEO (ASR + OCR + Caption + Tags), Creator Search Insights, and `60s+` RPM vs. `<60s` viral reach.
3. [[03 Instagram Reels, Trial Reels & Threads Guide]] — Adam Mosseri's Connected vs. Unconnected reach ranking (DM Sends per Reach), Trial Reels testing on non-followers, `3:4` profile grid safe zones, and `Collab` multipliers.
4. [[04 X (Twitter), Facebook Reels, LinkedIn, Snapchat & Reddit Guide]] — X open-source algorithm weights (why links must go in Reply #1), Facebook Reels originality scoring, LinkedIn B2B/science explainers, and Reddit/Pinterest evergreen syndication.

### ✍️ `20 Description, Hashtag & SEO Optimization Bible`
- [[20 Description, Hashtag & SEO Optimization Bible]] — The **3-Layer Multimodal SEO Law** (aligning spoken first 6 words, Frame-0 on-screen text, and Line-1 description keywords), copy-paste description templates for all 6 Shortmaking tracks, hashtag anti-spam rules, pinned-comment loop engineering, and ready-to-paste omnichannel metadata for **The Great Emu War** and **What Would Kill You First On Mars?**.

### ⏰ `30 Upload Timing, Cadence & Global Timezone Matrix`
- [[30 Upload Timing, Cadence & Global Timezone Matrix]] — The **90-Minute Pre-Peak Indexing Law**, hour-by-hour day-of-week posting heatmaps across **US Eastern (`EST/EDT`)**, **UK/Europe (`GMT/CET`)**, and **Southeast Asia (`UTC+7 WIB`)**, the **Private-to-Public VP9 Warm-Up Protocol**, and anti-cannibalization cooldown windows.

### 🤖 `40 Automated Uploading Research & Full Engineering Architecture`
- [[40 Automated Uploading Research & Full Engineering Architecture]] — Complete engineering teardown of **100% hands-free video publishing**:
  - **Tier 1**: Direct Official APIs (**YouTube Data API v3**, **TikTok Content Posting API v2**, **Instagram Graph API v21.0 Reels**, **Facebook Graph API**, **X API v2 + v1.1 Media**, **LinkedIn API**).
  - **Tier 2**: Open-Source Self-Hosted Schedulers (**Postiz** Docker + REST API + MCP) & Unified Aggregator APIs (**Upload-Post**, **Ayrshare**, **Bundle.social**, **Late**).
  - **Tier 3**: Stealth Headless Browser Uploaders (**Playwright / Patchright** persistent Chrome profiles, `tiktok-uploader`, `social-auto-upload`) for zero-API-audit features like YouTube's `Related Video` pill and trending audio attachment.
  - **Tier 4**: Zero-Touch Pipeline (`FFmpeg` → `Cloudflare R2` zero-egress bucket → `scripts/omnichannel_publish.py` / `n8n` → `Obsidian Upload Queue`).

---

## 3. Live Databases & Interactive Architecture Canvas

- **Visual Pipeline Flowchart**: [[Omnichannel Auto-Upload Pipeline.canvas]]
- **Live Platform Spec Matrix**:

![[Platform Spec Matrix.base]]

- **Live Omnichannel Upload Queue & Tracker**:

![[Upload Queue & Tracker.base]]

---

## 4. One-Line CLI Triggers (`scripts/omnichannel_publish.py`)

```powershell
# 1. Pre-flight dry run: validate video codec/aspect ratio + check titles/descriptions/hashtags across all platforms:
python scripts/omnichannel_publish.py --manifest scripts/omnichannel_manifest.json --dry-run

# 2. Publish to YouTube Shorts/Long-Form via YouTube Data API v3 (+ auto-post pinned comment):
python scripts/omnichannel_publish.py --manifest scripts/omnichannel_manifest.json --platforms youtube --privacy public

# 3. Stage MP4 to Cloudflare R2 and publish simultaneously to YouTube, TikTok, Instagram Reels, and X:
python scripts/omnichannel_publish.py --manifest scripts/omnichannel_manifest.json --platforms youtube tiktok instagram x

# 4. Route through a self-hosted Postiz instance (single API call -> all connected social accounts):
python scripts/omnichannel_publish.py --manifest scripts/omnichannel_manifest.json --provider postiz
```
