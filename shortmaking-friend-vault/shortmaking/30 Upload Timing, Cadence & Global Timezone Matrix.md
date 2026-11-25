---
title: 30 Upload Timing, Cadence & Global Timezone Matrix
tags:
  - upload-timing
  - schedule
  - cadence
  - timezones
  - algorithm
  - distribution
area: distribution
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Exact upload windows converted across US EST, UTC/GMT, and Southeast Asia WIB (UTC+7), the 90-minute pre-peak indexing law, the Private-to-Public VP9 warm-up protocol, and upload frequency limits.
---

# 30 Upload Timing, Cadence & Global Timezone Matrix

← Back to [[00 Social Publishing Home]] | [[00 Home|Shortmaking Studio Home]]

While short-form algorithms can push a great video at any hour, **uploading at the right time maximizes the velocity of your initial `500–2,500` seed cohort**—and prevents your video from serving low-bitrate H.264 streams during its most critical first 10 minutes.

---

## 1. The 2 Golden Technical Laws of Upload Timing

### Law 1: The 90-Minute Pre-Peak Indexing Lead Time
Never publish *at* the exact minute your audience peaks—publish **`60 to 120 minutes BEFORE` the peak window**:
1. **Minutes `0 – 25` Post-Publish**: Platform servers run Whisper ASR audio transcription, Vision OCR frame scanning, copyright fingerprinting, and topic-vector embedding.
2. **Minutes `25 – 75` Post-Publish**: The algorithm serves your video to the **Stage 1 Cold Seed Test (`500 – 2,000` impressions)** and measures `Viewed vs. Swiped Away` and `APV`.
3. **Minutes `75 – 120+` Post-Publish**: Just as your video passes Stage 1, the main global peak traffic wave hits, giving the algorithm maximum active inventory to scale Stage 2 (`10K–50K`) and Stage 3 (`100K–1M+`).

### Law 2: The 45-Minute `Private / Scheduled` Warm-Up Protocol
> [!WARNING] Never Click "Upload → Public" Directly on a Fresh MP4!
> When you upload a `1440×2560` or `1080×1920` video and set it to `Public` immediately, **the first 300 viewers receive the low-resolution, blocky SD/H.264 fallback stream** while YouTube/TikTok/Meta is still transcoding the high-bitrate VP9/AV1/HEVC streams in the background. Poor visual quality in the first 300 views tanks your Stage-1 hook rate!
- **Mandatory Workflow**:
  1. Upload via API or Studio as **`private`** (or **`scheduled`** for `≥ 45 minutes` in the future).
  2. Wait **`30–45 minutes`** for HD/2K VP9 processing, audio normalization checks, and ad-suitability checks to reach `100% Complete`.
  3. Flip to **`public`** (or let the scheduled timer fire) at the exact pre-peak slot below.

---

## 2. Global Upload Timezone Matrix (`US EST` vs `UTC` vs `WIB UTC+7`)

For English-language educational, history, science, space, and gaming channels (`@Warp_Scale`, `@OrbitOddities`), **North America (`US/Canada EST & PST`) + UK/Europe (`GMT/CET`)** drive **`75% – 85%` of total RPM and high-tier sponsor value**.

Because your workstation runs on **WIB (`UTC+7`, Jakarta/Bangkok)**, use this exact conversion table to hit North American & European prime windows effortlessly:

| Slot Name | Target Audience Wave | US Eastern (`EST` / `UTC-5`) | UK / UTC (`GMT` / `UTC+0`) | **Your Local Time (`WIB` / `UTC+7`)** | Best Platforms for This Slot |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Slot A (Primary Daily Sweet Spot)** | **US Morning Commute + UK/EU Afternoon/Evening Peak** | **`08:00 – 10:00 AM`** | `13:00 – 15:00` | **`20:00 – 22:00` (8:00 PM – 10:00 PM)** | **YouTube Shorts, YouTube 16:9, LinkedIn, X, Instagram Reels** |
| **Slot B (US Lunch + EU Late Night)** | **US East Coast Lunch + US West Coast Morning** | **`11:30 AM – 01:30 PM`** | `16:30 – 18:30` | **`23:30 – 01:30` (11:30 PM – 1:30 AM)** | **TikTok, Instagram Reels, YouTube Shorts, Reddit** |
| **Slot C (US Evening Prime Scroll)** | **US East/West Evening Downtime (Peak Binge Window)** | **`05:00 – 07:00 PM`** | `22:00 – 00:00` | **`05:00 – 07:00` (5:00 AM – 7:00 AM next day)** | **YouTube Shorts, TikTok, Facebook Reels, X** |
| **Slot D (APAC + Early EU Wave)** | **Asia-Pacific Evening + Europe Morning** | `11:00 PM – 01:00 AM` | `04:00 – 06:00` | **`11:00 – 13:00` (11:00 AM – 1:00 PM)** | Secondary TikTok / Reels test slot |

> [!TIP] Best Single Daily Upload Window From `UTC+7`
> **Publish (or schedule to go live) between `20:30 and 21:30 WIB` (`8:30 PM – 9:30 PM` your local time)**, OR schedule overnight for **`05:30 WIB` (`5:30 AM` local / `5:30 PM EST`)**.
> - `20:30 WIB` catches **UK/Europe afternoon peak immediately** and finishes its 90-minute Stage-1 seed test right as **US East Coast wakes up at 9:30 AM EST**!

---

## 3. Day-of-Week Performance Heatmap by Platform

| Platform | Best Days of the Week | Highest-Velocity Hours (`EST` / **`WIB UTC+7`**) | Lowest-Velocity Day (Use for Testing / Rest) |
| :--- | :--- | :--- | :--- |
| **YouTube Shorts** | **Thursday, Friday, Saturday, Sunday** | `9:00 AM EST` (**`21:00 WIB`**) & `5:00 PM EST` (**`05:00 WIB`**) | Tuesday |
| **YouTube Long-Form (`16:9`)** | **Thursday, Friday, Saturday, Sunday** | `10:00 AM – 12:00 PM EST` (**`22:00 – 00:00 WIB`**) | Monday / Tuesday |
| **TikTok** | **Tuesday, Thursday, Friday, Sunday** | `9:00 AM EST` (**`21:00 WIB`**) & `6:00 PM EST` (**`06:00 WIB`**) | Saturday afternoon |
| **Instagram Reels** | **Tuesday, Wednesday, Thursday, Friday** | `9:00 AM EST` (**`21:00 WIB`**) & `12:00 PM EST` (**`00:00 WIB`**) | Sunday afternoon |
| **X (Twitter) Video** | **Tuesday, Wednesday, Thursday** | `8:30 AM – 10:30 AM EST` (**`20:30 – 22:30 WIB`**) | Saturday / Sunday |
| **LinkedIn Video** | **Tuesday, Wednesday, Thursday** | `8:00 AM – 10:00 AM EST` (**`20:00 – 22:00 WIB`**) | Saturday & Sunday (Avoid weekends!) |
| **Reddit (`r/space`, `r/HistoryMemes`)** | **Monday, Saturday, Sunday** | `7:30 AM – 9:30 AM EST` (**`19:30 – 21:30 WIB`**) | Friday night |

---

## 4. Upload Frequency, Cooldowns & Anti-Cannibalization Rules

1. **Minimum Cooldown Between Posts on the Same Channel (`≥ 4 Hours`)**:
   - Never publish two YouTube Shorts or two TikToks within `15 minutes` of each other on the same account.
   - On YouTube Shorts especially, uploading Short #2 while Short #1 is still in its first `3–4 hours` of Stage-1/Stage-2 cohort testing splits your channel's active subscriber notification/home-shelf allocation.
   -*(Exception: Uploading 1 vertical Short + 1 horizontal `16:9` Long-Form video linked via the **"Related Video"** pill is encouraged—publish the `16:9` video first, then publish the linked Short **`30–60 minutes` later**!)*
2. **Ideal Weekly Cadence for High-Craft Animated Channels**:
   - **Quality > Daily Slop**: Unlike low-effort talking-head channels that spam 4 clips a day, animated explainer channels (*Nutshell*, *Hoog*, *Orbit*, *Zack D. Films*, *Grow With Kaz*) win on **per-video outlier reach (`500K – 10M views/video`)**:
     - **YouTube Shorts / TikTok / IG Reels / X / FB**: **`3 to 5` high-craft Shorts per week** (same master video syndicated across all 5 vertical platforms!).
     - **YouTube `16:9` Long-Form (`orbit-space-video` / `make-3d-video`)**: **`1 to 2` videos per week**, each backed by `2` teaser Shorts linked via the Related Video pill.
3. **Should You Stagger Across Platforms or Publish Simultaneously?**
   - Because YouTube, TikTok, Instagram, and X have completely isolated recommendation graphs, **you can publish the same video across all 5 platforms in the same `20:30 WIB` window**—just ensure each platform receives its **clean native MP4 without any third-party watermark** and its **platform-specific description/hashtag package** via `scripts/omnichannel_publish.py`.
