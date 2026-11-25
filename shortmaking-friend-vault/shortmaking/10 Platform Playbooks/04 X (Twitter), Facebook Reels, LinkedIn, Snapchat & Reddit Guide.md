---
title: 04 X (Twitter), Facebook Reels, LinkedIn, Snapchat & Reddit Guide
tags:
  - x-twitter
  - facebook-reels
  - linkedin
  - snapchat
  - reddit
  - pinterest
  - algorithm
  - distribution
area: distribution
platform: "X / Facebook / LinkedIn / Reddit / Snap"
aspect_ratio: "9:16 or 16:9"
optimal_duration: "35-140s"
hashtag_cap: "0-3 tags (0 on Reddit/X, 3 on FB/LinkedIn)"
primary_signal: "Author Replies (X) / Shares (FB) / Dwell Time (LI)"
automation_api: "X API v2, Meta Graph API, LinkedIn API, PRAW"
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete optimization playbook for syndicating animated shorts and explainers across X (Twitter), Facebook Reels, LinkedIn Video, Snapchat Spotlight, Pinterest, and Reddit.
---

# 04 X (Twitter), Facebook Reels, LinkedIn, Snapchat & Reddit Guide

← Back to [[00 Social Publishing Home]] | [[00 Home|Shortmaking Studio Home]]

Most creators stop after uploading to YouTube, TikTok, and Instagram—leaving **40–60% of total views, high-ticket B2B/tech impressions, and viral Reddit/X threads** on the table. Because you already have the rendered `.mp4` and `SCRIPT.md`, syndicating to these 5 secondary platforms takes **zero extra rendering time** and can be 100% automated.

---

## 1. X (Twitter) Video — The Open-Source Algorithm Rules

X's open-sourced recommendation algorithm (`For You` Heavy Ranker) has very specific rules for native video and outbound links:

### A. The 5 Non-Negotiable Laws of X Video
1. **NEVER Put an External Link (`youtube.com`, `youtu.be`, etc.) in the Main Post**:
   - X's feed ranker actively penalizes posts containing external URLs that take users off-platform (`-50% to -80%` reach reduction).
   - **The Fix**: Upload the `.mp4` **natively** in Tweet #1 with zero links, and **automatically post the YouTube/channel link in Reply #1** (`in_reply_to_tweet_id`).
2. **Replies That the Author Replies Back To Weight `+75.0x` vs. `+0.5x` for a Like**:
   - In X's Heavy Ranker weights, a Like is baseline (`~0.5`), a Retweet is `~1.0–20.0`, and **a Reply where the post author engages back weights `+75.0`**.
   - End Tweet #1 or Reply #1 with a sharp debate question and reply to the first 5–10 commenters within the first hour.
3. **Burned-In Captions Are Mandatory on X (Muted Autoplay)**:
   - Unlike TikTok and YouTube Shorts (where audio plays automatically), **X videos autoplay muted in the timeline**.
   - Your **Frame-0 visual hook** and **burned-in captions** must hook the viewer in the first `2.0 seconds` before they even tap for sound.
4. **Hashtag Rule on X: `0` to `1` Maximum**:
   - Multiple hashtags (`#Shorts #History #Viral`) look like bot spam on X and reduce engagement. Instead, use **natural inline keywords** (`"The 1932 Great Emu War"`, `"NASA Mars rover data"`).
5. **Both `9:16` Vertical (`1080×1920`) and `16:9` Horizontal (`1920×1080`) Work**:
   - X has a dedicated vertical video swipe player on mobile (`9:16`), while `16:9` (like [[Mars - What Would Kill You First (Completed Video)]]) plays wide in desktop and mobile timelines.

### B. High-Performing X Video Post Template
```text
In 1932, Australia sent soldiers armed with two Lewis machine guns and 10,000 rounds of ammunition to fight 20,000 emus.

After 6 days of ambushes, jammed guns, and birds sprinting at 50 km/h… the Australian Army officially withdrew in defeat.

Here is how the Great Emu War actually played out:
[Attach native emu-war.mp4 — 0 hashtags, 0 external links]
```
*(Auto-Reply #1)*:
```text
Full 4K breakdown + primary sources from the Australian War Memorial on our YouTube channel: https://youtube.com/@Warp_Scale
```

---

## 2. Facebook Reels & Facebook Video

Facebook Reels has an older, higher-purchasing-power demographic (`25–54`) and pays strong creator bonuses on original animated explainers.
- **Use Native Meta Graph API Upload (`/me/video_reels`) + Cross-Post from IG**:
  - If you only enable "Recommend on Facebook" inside Instagram, views count toward Instagram's cross-app pool, **not** your Facebook Page's native monetization/followers.
  - Uploading natively to your **Facebook Page as a Facebook Reel** via the Meta Graph API builds a standalone Facebook audience alongside Instagram.
- **Caption & Link Rule**:
  - Keep the main Facebook Reel caption to **`1–2 punchy sentences` + `3–5 hashtags`** (`#History #EmuWar #AnimatedHistory #HistoryFacts`).
  - Just like X, **never put external links in the main Facebook post caption**—drop links in the **first comment**.

---

## 3. LinkedIn Native Video (The Sleeper Goldmine for Science/Tech/History)

LinkedIn launched a dedicated **mobile vertical video feed** (`9:16`) and heavily boosts native educational explainers (`make-3d-video` low-poly 3D and `orbit-space-video` data-driven explainers perform exceptionally well here).
- **The 3-Line `"…see more"` Fold Hook (`≤ 180 characters`)**:
  - LinkedIn measures **Dwell Time** (how long a user pauses scrolling on your post) and **"See more" clicks**.
  - Frame your historical or scientific story around a **systems-engineering, physics, or decision-making lesson**:
    ```text
    In 1880, a British suspension bridge collapsed because 60 soldiers were too polite to march out of step.
    
    It remains one of the clearest real-world lessons in mechanical resonance and systems failure: 👇
    ```
- **Hashtags**: Exactly **`3` broad professional/educational tags** at the very bottom (`#Engineering #Science #History`).
- **Best Upload Window**: **Tuesday, Wednesday, or Thursday at `8:00 AM – 10:30 AM` EST**.

---

## 4. Reddit, Snapchat Spotlight & Pinterest Video Pins

| Platform | Why It's Worth Automating | Rules That Prevent Bans / Removal |
| :--- | :--- | :--- |
| **Reddit (`r/Damnthatsinteresting`, `r/HistoryMemes`, `r/space`, `r/educationalgifs`)** | A single front-page Reddit post drives `100K – 2M+` organic views in 12 hours and seeds external backlinks. | **0 hashtags**, **0 self-promo watermarks in the first 3s**, upload as **native Reddit MP4 (`v.redd.it`)** (never a YouTube link on video subreddits!), and cite your NASA/historical sources in your own top comment. |
| **Snapchat Spotlight** | Less saturated creator pool for 3D/2D educational animation; `9:16` `30–60s` MP4s map 1:1 from YouTube Shorts. | Must be `9:16` vertical, `≤ 60 seconds`, clean audio (`-14 LUFS`), **`2–4` hashtags** (`#Spotlight #History #Science`). |
| **Pinterest Video / Idea Pins** | **Longest shelf-life of any platform** (`6–24 months` of search traffic vs. `48h` on X). | Optimize Title (`≤ 100 chars`) and Description (`≤ 500 chars`) with **plain-text search keywords** (Pinterest retired hashtag priority in favor of visual + text search SEO). Allows a direct outbound **Destination URL** to your YouTube video! |
