---
title: 01 YouTube Shorts & Long-Form Master Guide
tags:
  - youtube
  - youtube-shorts
  - algorithm
  - seo
  - hashtags
  - thumbnails
  - distribution
area: distribution
platform: YouTube
aspect_ratio: "9:16 (Shorts) / 16:9 (Long-Form)"
optimal_duration: "38-58s (Shorts) / 8-14m (Long)"
hashtag_cap: "3-5 tags (Max 15 hard limit)"
primary_signal: "Viewed vs Swiped Away (>78%) & APV (>95%)"
automation_api: "YouTube Data API v3 (videos.insert)"
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete technical guide to the YouTube Shorts and Long-Form recommendation algorithms, description SEO, hashtag rules, the Related Video funnel bridge, and encoding buckets.
---

# 01 YouTube Shorts & Long-Form Master Guide

← Back to [[00 Social Publishing Home]] | [[00 Home|Shortmaking Studio Home]] | [[Uploading, Algorithm Packaging & Retention Optimization]]

YouTube operates **two separate recommendation engines** under one channel roof: the **Shorts Feed** (swipe-based velocity + loop retention) and **Browse / Suggested Long-Form** (thumbnail CTR + session watch time). Pairing both—like our vertical [[Emu War (1932) - Completed Video]] (`9:16`) and horizontal [[Mars - What Would Kill You First (Completed Video)]] (`16:9`)—is the highest-leverage growth loop on the internet.

---

## 1. How the 2026 YouTube Shorts Algorithm Actually Works

### A. Views vs. Engaged Views (The 2025/2026 Analytics Update)
- **Views (Impressions-Based)**: Increments as soon as a Short starts playing or loops in the feed.
- **Engaged Views (The Real Ranking & Monetization Metric)**: Only counts viewers who **stay past the initial swipe window (`~3–5 seconds`) without swiping away**. YouTube Partner Program (YPP) eligibility (`10M` valid public Engaged Shorts views in 90 days) and creator revenue sharing depend strictly on **Engaged Views**.

### B. The 4-Stage Seed Cohort Ladder
Every new Short enters a staged multi-armed bandit tournament:

| Stage | Impression Cohort | Gate Metrics Required to Advance | Typical Timing After Upload |
| :--- | :--- | :--- | :--- |
| **Stage 1: Cold Seed Test** | `500 – 2,500` views | **Viewed vs. Swiped Away `≥ 72%`** + **APV `≥ 85%`** | `0 – 6 hours` |
| **Stage 2: Warm Niche Pool** | `10,000 – 50,000` views | **Viewed vs. Swiped Away `≥ 76%`** + **APV `≥ 92%`** + comment/rewatch velocity | `6 – 48 hours` |
| **Stage 3: Broad Shelf Expansion** | `100,000 – 1,000,000` views | **Viewed vs. Swiped Away `≥ 79%`** + **APV `≥ 98%`** across adjacent interest graphs | `Day 2 – Day 14` |
| **Stage 4: Evergreen / Mega-Outlier** | `5,000,000 – 50,000,000+` views | **Viewed vs. Swiped Away `≥ 82%`** + **APV `≥ 108%`** + Search/Browse shelf CTR `> 9%` | `Weeks to Months` |

> [!TIP] The Delayed Shorts Pop ("Flatline Then Spike")
> Do **not** delete or re-upload a Short if it stalls at `1,200 views` for the first 12–24 hours. YouTube routinely holds a Short after Stage 1 while gathering audience satisfaction signals, then triggers Stage 2/3 `24–72 hours` later. Deleting and re-uploading flags the channel for duplicate spam.

---

## 2. Title Optimization Rules (Shorts vs. Long-Form)

| Rule | YouTube Shorts (`9:16`) | YouTube Long-Form (`16:9`) |
| :--- | :--- | :--- |
| **Hard Character Limit** | `100 characters` | `100 characters` |
| **Mobile Non-Truncation Limit** | **`≤ 52 characters`** (Truncates in Shorts player & Home shelf beyond 52 chars) | **`48 – 60 characters`** (Truncates on mobile Home feed beyond ~60 chars) |
| **Hook Structure** | **Concrete Noun + Paradox Outcome** (*"How Australia Lost a War to 20,000 Emus 😭"*) | **Curiosity Gap Question or Extreme Stake** (*"What Would Actually Kill You First on Mars?"*) |
| **Should `#Shorts` Be in the Title?** | **Optional (`0` or `1` tag at the very end)**. Putting `#Shorts` in the **Description** is sufficient; saving title characters for the hook increases Browse shelf CTR. | **Never** (Long-form videos >3 min or `16:9` must never use `#Shorts`). |
| **Emoji Rule** | Maximum **1 high-contrast emoji** at the end of the title (`😭`, `💀`, `🚀`, `🧠`). Never put emojis at the start of the title (hurts search prefix matching). | **0 emojis** recommended for documentary/explainer niches (*Orbit*, *Fern*, *Kurzgesagt* style). |

---

## 3. Description & Hashtag Optimization (YouTube SEO)

YouTube uses your Description, Whisper ASR transcript, and Backend Tags to classify **who** should receive your initial `1,000–2,500` seed impressions.

### A. The 4-Block Description Architecture
```text
[LINE 1-2: THE 120-CHAR SEARCH HOOK — Restate the core paradox using exact search keywords]
In 1932, Australia sent soldiers with machine guns into the Great Emu War — and lost to 20,000 flightless birds.

[BLOCK 2: ENTITY-RICH SUMMARY (50-90 words for semantic indexing)]
When 20,000 emus stormed Western Australian wheat farms during the Great Depression, Major G.P.W. Meredith of the Royal Australian Artillery deployed two Lewis automatic machine guns and 10,000 rounds of ammunition. Between jammed guns, 50 km/h sprints across rough outback terrain, and flocks posting tall lookouts, the emus walked away undefeated.

[BLOCK 3: CREDITS, SOURCES & CHANNEL CTA]
Subscribe to @Warp_Scale for weekly animated history, science & cosmic scale shorts!
Sources: Australian War Memorial, National Archives of Australia.

[BLOCK 4: 3 TO 5 HASHTAGS (Never exceed 15!)]
#Shorts #History #EmuWar #AnimatedHistory #HistoryFacts
```

### B. The YouTube Hashtag Law (`3–5` Optimal, `>15` = Total Penalty)
> [!WARNING] YouTube's Official 15-Hashtag Spam Rule
> According to Google's official YouTube Help documentation, **if a video has more than 15 hashtags in its title/description, YouTube ignores ALL hashtags on that video** and may suppress it for metadata stuffing.
- **For Shorts**: Use **`3 to 5` hashtags** at the very bottom of the description:
  1. `#Shorts` (Format classifier)
  2. `#History` or `#Science` or `#Space` (Broad vertical bucket)
  3. `#EmuWar` or `#Mars` (Specific topic entity)
  4. `#AnimatedHistory` or `#SpaceFacts` (Sub-niche community tag)
- **For Long-Form (`16:9`)**: The **first 3 hashtags** in your description appear as clickable blue links directly above your video title. Choose exactly **3 high-intent topic tags** (`#Mars #Space #Astronomy`).

### C. Backend Tags (`snippet.tags`) — How Many & Why
- YouTube allows up to `500 characters` of backend tags, but **sweet spot is `8–12 tags` (`180–280 characters`)**.
- Use backend tags for **exact search phrases, synonyms, and common misspellings** (`"what would kill you first on mars"`, `"mars survival"`, `"great emu war 1932"`, `"australia vs emus"`).

---

## 4. The "Related Video" Bridge (Turning Shorts Views into High-RPM 16:9 Views)

YouTube Shorts RPM averages `$0.05 – $0.22 per 1,000 Engaged Views`, whereas Long-Form (`16:9`) science/history explainer RPM averages **`$4.50 – $12.00 per 1,000 views`**.
- Every Short you publish should set the **"Related Video"** field in YouTube Studio to point to a full `16:9` explainer on your channel (e.g., linking a 55s *MarsBoiling Saliva* Short directly to the `144.45s` `16:9` [[Mars - What Would Kill You First (Completed Video)]]).
- This renders a **clickable pill directly above the Short's title** inside the Shorts player (`▶ What Would Actually Kill You First on Mars?`), converting `1.5% – 4.0%` of Shorts viewers into long-form viewers!
- **Verbal Bridge CTA (`Last 2 Seconds` of a Teaser Short)**: Instead of *"Subscribe for more"*, end a teaser clip with a cliffhanger pointing down at the pill: *"…which is only the third worst thing on the planet—tap the linked video right here for the full countdown."*

---

## 5. Custom Thumbnail Frames, Categories & Compliance Flags

1. **Shorts Thumbnail Frame**:
   - You cannot upload an external `.png` thumbnail for Shorts via desktop web, **except** by selecting a frame on mobile or embedding a **1-frame high-contrast poster at Frame 0** (`t = 0.00s`).
   - Because our Shortmaking pipeline designs **Frame 0** as an immediate visual paradox (`YOU →` tiny astronaut next to giant Mars, or Lewis gun vs. giant emu), Frame 0 naturally serves as a high-CTR shelf thumbnail.
2. **Best `categoryId` Values for Animated Shorts**:
   - **`27` (`Education`)**: Best for History (`cartoon-3d-short`, `make-3d-video`) and Science explainers.
   - **`28` (`Science & Technology`)**: Best for Space/Physics (`orbit-space-video`, `What Would Kill You First On Mars?`).
   - **`24` (`Entertainment`)** or **`1` (`Film & Animation`)**: Best for emotional storytime (`cartoon-audio-short`).
   - **`20` (`Gaming`)**: Best for Roblox R6/R15 shorts (`Style 5`).
3. **Made for Kids & Synthetic Media Flags**:
   - **Always set `selfDeclaredMadeForKids: false`**. Even though the video is animated, setting "Made for Kids" disables comments, disables the pinned comment loop trick, disables notification bells, and cuts RPM by `~80%`.
   - **Altered / Synthetic Content (`containsSyntheticMedia`)**: YouTube only requires checking *"Yes"* if a video makes a **realistic** person appear to say/do something they didn't, or alters footage of a real event/place in a **realistic** way. Stylized 2D cartoons, low-poly 3D (`KAZ`), and standard AI voiceover narration on educational animations do **not** require the realistic synthetic media warning label.
