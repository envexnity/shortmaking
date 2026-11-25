---
title: 02 TikTok Algorithm, SEO & Publishing Guide
tags:
  - tiktok
  - algorithm
  - tiktok-seo
  - hashtags
  - distribution
area: distribution
platform: TikTok
aspect_ratio: "9:16 (1080x1920 strict)"
optimal_duration: "35-55s (Viral) / 62-90s (Rewards)"
hashtag_cap: "3-5 search-intent tags"
primary_signal: "Rewatches (5pt) + Shares (5pt) + 80% Completion"
automation_api: "TikTok Content Posting API v2 / Playwright"
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete engineering guide to TikTok's point-weighted For You Page (FYP) algorithm, 4-layer TikTok Search SEO, 60s+ Creator Rewards packaging, and anti-compression export settings.
---

# 02 TikTok Algorithm, SEO & Publishing Guide

← Back to [[00 Social Publishing Home]] | [[00 Home|Shortmaking Studio Home]]

TikTok is no longer just a swipe feed—over **40% of Gen-Z and Millennial users use TikTok as a primary search engine**, and TikTok's **Creator Rewards Program** pays `$0.40 – $1.80+ RPM` on qualified views for videos **`≥ 60.0 seconds`**.

---

## 1. The TikTok FYP Point-Weight Scoring Formula

When TikTok serves your video to an initial test cohort of **`200 – 500` For You Page (FYP) viewers**, every viewer interaction contributes to a weighted velocity score before the algorithm decides whether to promote the video to the `5,000 → 50,000 → 500,000+` pools:

| User Action | Relative Algorithm Weight | How Our Shortmaking Pipeline Engineers It |
| :--- | :---: | :--- |
| **1. Rewatch / Full Loop** | **`5 Points`** | Seamless loop seam (`<0.08s` tail after final syllable) + `3.7 wps` zero dead air. |
| **2. Share (DM / Copy Link / Repost)** | **`5 Points`** | Absurd factual paradox (*"Australia lost a war to 20,000 birds"*) that viewers immediately send to a friend. |
| **3. Save / Add to Favorites** | **`4 Points`** | Dense visual telemetry (`KAZ` HUD cards, Orbit survival gauges, historical receipts) viewers bookmark to re-read. |
| **4. 100% Video Completion** | **`3 Points`** | Placing the `"You see,"` mechanism pivot at `60%` and holding the final callback punchline until the very last word. |
| **5. Comment + Dwell Time in Comments** | **`2 Points`** | Polarizing 2-option question in the caption/first comment + visual Easter eggs on character cards. |
| **6. Like (Heart)** | **`1 Point`** | Passive baseline signal—high likes with low completion/shares will still stall at `<5,000` views. |
| **❌ `< 2.0s` Immediate Swipe-Away** | **`-3 Points`** | Prevented by starting spoken word 1 at `t = 0.06s` + Frame-0 visual anomaly + pre-cut SFX transient. |

---

## 2. The 4-Layer TikTok Search SEO Architecture

TikTok indexes every video across **four simultaneous modalities** within the first `15 minutes` of upload to rank it in **TikTok Search** and earns an automatic **Blue Search Link Comment** at the top of your comment section (which boosts watch time by `15–30%`!).

### Layer 1: Audio ASR (First 3 Seconds Spoken Words)
- TikTok's Whisper-class speech-to-text transcribes your voiceover immediately.
- **Rule**: The exact primary keyword entity (`"Great Emu War"`, `"survive on Mars"`, `"Broughton suspension bridge"`) **must be spoken aloud in Sentence 1 (`0.0s – 3.5s`)**.

### Layer 2: Visual OCR (On-Screen Text & Captions)
- TikTok runs Optical Character Recognition on the first `5 seconds` of video frames.
- **Rule**: Ensure burned-in captions (`remotion-captions` / `KAZ hud.cap` / Orbit HUD banner) clearly display the core topic phrase in `y = 220 – 1380 px` during Shot 0.

### Layer 3: The `4,000-Character` SEO Caption Formula
TikTok expanded captions to `4,000 characters` specifically to compete with Google Search and YouTube descriptions.
- **Line 1 (`≤ 85 characters` visible before *"…more"*)**: Write a curiosity-gap question or statement containing your **#1 search phrase**.
- **Paragraph 2 (`60–120 words`, hidden under *"…more"*)**: Include natural long-tail question phrases from **TikTok Creator Search Insights** (e.g., *"What would happen if you stepped onto Mars without a spacesuit? Why did Australia fight the Great Emu War in 1932?"*). While a viewer taps *"…more"* to read your caption, the video keeps playing in the background!

### Layer 4: The `3–5` Hashtag Rule (Why `#fyp` Hurts New Accounts)
- **Never use only `#fyp #foryou #viral`**: Those tags have trillions of posts and give the cold-start classifier **zero topical signal**, causing your first `300` views to be served to random uninterested users who immediately swipe away (`<50%` retention = dead video).
- **Use the `2 + 2 + 1` TikTok Hashtag Formula (`4–5 tags total`)**:
  - **2 Specific Search-Intent Tags**: `#emuwar` `#weirdhistory` (or `#marssurvival` `#planetmars`)
  - **2 Broad Category Pillar Tags**: `#historyfacts` `#animatedhistory` (or `#spacefacts` `#astronomy`)
  - **1 Discovery / Format Tag**: `#learntok` or `#edutok`

---

## 3. `< 60s` Viral Velocity vs. `60s+` Creator Rewards Program

| Strategy Goal | Target Duration | Why |
| :--- | :--- | :--- |
| **Maximum Views, Follower Growth & Cross-Platform Syndication** | **`38.0s – 56.0s`** (like [[Emu War (1932) - Completed Video]] at `56.10s`) | Fits inside YouTube Shorts (`<60s` classic), Instagram Reels (`<90s`), and TikTok with ultra-high `90–110%` completion rates. |
| **Direct TikTok Ad Revenue (Creator Rewards Program)** | **`61.5s – 78.0s`** (Must be strictly `≥ 60.0s`—aim for `≥ 61.5s` so frame-rate rounding never drops it to `59.9s`!) | TikTok **only pays Creator Rewards RPM on videos over 1 minute long**. Expand the `"You see,"` mechanism beat by `20–25 words` (`~6 seconds`) to cross the `61.5s` threshold when optimizing for TikTok payouts. |

---

## 4. TikTok Encoding & Anti-Compression Rules

> [!CAUTION] Never Upload `1440×2560` (2K) or `4K` to TikTok!
> Unlike YouTube Shorts (which rewards `1440×2560` with a higher VP9 bitrate bucket), **TikTok forcibly downscales anything above `1080×1920` using a fast, lossy server transcoder** that introduces severe ringing artifacts around `3px` toon outlines!

- **Always feed TikTok exact `1080 × 1920`**, `30.00 fps` CFR, `H.264 High@L4.1`, `-crf 16 -maxrate 16M -bufsize 32M`, `yuv420p`, `bt709`, AAC `256 kbps`.
- If your master render is `1440×2560` (for YouTube Shorts), generate a dedicated clean Lanczos `1080×1920` downscale for TikTok and Instagram Reels:
```powershell
ffmpeg -y -i out/master_2k.mp4 -vf "scale=1080:1920:flags=lanczos" -c:v libx264 -preset slow -crf 16 -maxrate 16M -bufsize 32M -pix_fmt yuv420p -c:a copy out/tiktok_reels_1080p.mp4
```

---

## 5. TikTok Upload Cadence, Warm-Up & AIGC Rules

1. **Account Warm-Up (Brand New TikTok Accounts)**:
   - Never create a brand-new TikTok account on a datacenter VPN and immediately push API uploads within 5 minutes—TikTok's fraud filter will `0-view` jail the account.
   - Spend `2–3 days` browsing/interacting in your niche (`#historyfacts`, `#spacefacts`) from a residential IP before your first upload.
2. **Spacing Between Uploads**: Wait at least **`3–4 hours`** between TikTok uploads (max `1–3 posts/day`).
3. **AIGC Toggle (`is_aigc`)**:
   - TikTok requires the `AI-generated content` toggle (`is_aigc: true` in the Content Posting API) **only** for realistic AI video/images (Sora/Runway/Flow photorealistic humans or fake real-world events).
   - Code-rendered 3D/2D animation (`Three.js`, `Remotion`, `Blender`, `Orbit 2D Canvas`) is genuine digital animation and should leave `is_aigc: false`.
