---
title: Uploading, Algorithm Packaging & Retention Optimization
tags:
  - upload
  - youtube-shorts
  - tiktok
  - reels
  - algorithm
  - retention
area: tools
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: End-to-end guide to exporting, packaging, and uploading viral animated shorts across YouTube Shorts, TikTok, and Instagram Reels—encoding specs, Frame-0 hooks, loop seams, and retention diagnostics.
---

# Uploading, Algorithm Packaging & Retention Optimization

> [!IMPORTANT] Connected to the Omnichannel Social Media & Auto-Publishing Vault
> For platform-by-platform algorithm playbooks, description/hashtag SEO templates, global upload timing (`EST` / `UTC` / `WIB UTC+7`), and **100% automated API/browser uploading**, jump to the connected vault:
> - **Master Hub**: [[00 Social Publishing Home]] (`[[Omnichannel Auto-Upload Pipeline.canvas]]`)
> - **Platform Guides**: [[01 YouTube Shorts & Long-Form Master Guide]] | [[02 TikTok Algorithm, SEO & Publishing Guide]] | [[03 Instagram Reels, Trial Reels & Threads Guide]] | [[04 X (Twitter), Facebook Reels, LinkedIn, Snapchat & Reddit Guide]]
> - **SEO & Timing**: [[20 Description, Hashtag & SEO Optimization Bible]] | [[30 Upload Timing, Cadence & Global Timezone Matrix]]
> - **Full Upload Automation**: [[40 Automated Uploading Research & Full Engineering Architecture]] (`scripts/omnichannel_publish.py`)

Building a 9/10 animated short is half the battle; **packaging and encoding it so the YouTube Shorts, TikTok, and Instagram Reels algorithms push it past the 10K–50K seed cohort into 1M–10M+ views** requires strict technical discipline.

---

## 1. Master Export & Encoding Spec (Anti-Compression Settings)

Platform transcoders crush dark shadows and soften `3px` screen-space ink outlines if you upload low-bitrate 1080p files.

| Parameter | YouTube Shorts Target | TikTok / Instagram Reels Target | Why It Matters |
| :--- | :--- | :--- | :--- |
| **Resolution** | **`1440 × 2560` (2K Vertical)** or `1080 × 1920` | **`1080 × 1920` (Exact 9:16)** | YouTube Shorts awards a higher VP9/AV1 bitrate bucket to `1440×2560`; TikTok downscales >1080p aggressively so feed it clean `1080×1920`. |
| **Frame Rate** | **`30.00 fps` CFR** (or `60 fps` for Roblox) | **`30.00 fps` CFR** | Always enforce Constant Frame Rate (`-vsync cfr -r 30`) so word-level lip sync and SFX never drift. |
| **Video Codec** | `libx264`, `-crf 15` or `-b:v 22M`, `-pix_fmt yuv420p` | `libx264`, `-crf 16`, `-maxrate 18M -bufsize 36M` | Prevents macroblocking in painted sky gradients and dark golden-hour violet shadows (`#5b5173`). |
| **Color Space Tags** | `-colorspace bt709 -color_primaries bt709 -color_trc bt709` | Same (`bt709`) | Prevents the infamous washed-out gamma shift on macOS/iOS devices. |
| **Audio Stream** | `AAC-LC`, `48,000 Hz`, Stereo, `192–256 kbps`, **`-14.0 LUFS`**, `-1.0 dBTP` | Same | Prevents platform limiters from pumping your voiceover when a bass impact hits. |

### Master Export FFmpeg Command
```powershell
ffmpeg -y -i out/video_raw.mp4 -i out/mix.wav `
  -map 0:v:0 -map 1:a:0 `
  -c:v libx264 -preset slow -crf 15 -pix_fmt yuv420p `
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 `
  -af "loudnorm=I=-14:TP=-1.0:LRA=7" `
  -c:a aac -b:a 256k -ar 48000 `
  -movflags +faststart -shortest `
  out/upload_master.mp4
```

---

## 2. The 9:16 UI Safe Zone (Never Put Key Visuals in the Red Zones!)

All three platforms cover the edges of your `1080×1920` frame with UI chrome:
- **Top `0 – 220 px` (`0% – 11.5%`)**: Covered by status bar, Search icon, and Shorts/Reels header. (Keep `KAZ` top HUD cards starting at `y ≥ 140px`).
- **Bottom `1420 – 1920 px` (`74% – 100%`)**: Covered by channel handle, title, audio ticker, and progress bar.
  - **Caption Safe Zone**: Place burned-in captions (`remotion-captions` or `KAZ` `hud.cap`) at **`y = 1280 – 1400 px` (`66% – 73%` from top)**—never at the very bottom!
- **Right Margin `x = 920 – 1080 px` (`85% – 100%`)**: Covered by Like, Comment, Share, and Remix buttons. Keep hero character heads inside `x = 160 – 880 px`.

---

## 3. The 2 Algorithm Gate Metrics You Must Beat

Every short-form platform tests a new upload on an initial seed cohort (`1,000 – 5,000` impressions) and evaluates two numbers:

| Metric | Mediocre (Dies at `<10K` views) | Viral Threshold (`100K – 1M+`) | Mega-Outlier (`5M – 50M+`) | What Controls It |
| :--- | :--- | :--- | :--- | :--- |
| **1. Viewed vs. Swiped Away (0–3s Hook Rate)** | `< 68%` | **`76% – 82%`** | **`> 83%`** | **Frame 0 visual anomaly** + **First 6 spoken words** (Paradox stated as fact at `t = 0.06s`, zero intro breath). |
| **2. Average Percentage Viewed (APV)** (`42–50s` short) | `< 75%` | **`92% – 105%`** | **`> 110%`** | **`3.7 wps` zero dead air** + **`"You see,"` pivot at 60%** + **Seamless loop seam** at the end. |

---

## 4. Engineering the Seamless Loop Seam (`>105%` APV Trick)

To push Average Percentage Viewed above `100%` on a 45-second short:
1. **Cut the Final Frame `<0.08s` After the Final Syllable**: Never hold a 1.5-second silent tail at the end of the video—viewers immediately swipe the moment the voice stops.
2. **Grammatical Bridge Loop (Optional)**: End the final sentence on a clause that flows seamlessly into Sentence 1 (e.g., Final line: *"...which is why nobody believed that—"* → Frame 0 Hook: *"In 1880, a British bridge collapsed because soldiers were too polite to march out of step."*).
3. **Visual Match-Cut**: Match the lighting preset (`day`) and camera horizon height of the final shot to Shot 0 so the visual loop feels instantaneous.

---

## 5. Title, Thumbnail Frame & Upload Checklist

- **Select the Custom Thumbnail Frame (In-Feed Shelf Traffic)**:
  - Up to `15–25%` of YouTube Shorts views come from Browse/Search shelves where the static thumbnail frame is shown.
  - Pick the **highest-contrast close-up frame** where the character has `'wide'` eyes + `'o'`/`'open'` mouth or where the bridge/planet is mid-collapse—never a distant establishing wide.
- **Title Formula (`≤ 52 characters` so it never truncates)**:
  - Pair a **concrete noun + impossible verb/outcome**:
    - *"The Bridge That Collapsed From a Song 😭"*
    - *"When Napoleon Lost a War to 3,000 Rabbits 🐇"*
    - *"Why You Forget 95% of Dreams in 5 Minutes 🧠"*
- **Pinned Comment**: Ask a polarizing 1-sentence question tied to the `"You see,"` mechanism or historical irony to drive comment-reading dwell time (while comments are open, the video loops in the background, boosting APV past `120%`!).
