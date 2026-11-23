---
title: Reference Video Music & Audio Catalog
tags:
  - audio
  - music
  - sfx
  - reference-music
  - catalog
area: audio
style: all
status: evergreen
created: 2026-11-16
updated: 2026-11-16
summary: Extracted MP3 audio tracks and credited instrumental music from the 8 YouTube reference videos, stored locally in 60 Audio & SFX Engineering/reference-music/.
---

# Reference Video Music & Audio Catalog

All audio tracks below were extracted via `yt-dlp` (`--audio-format mp3 --audio-quality 0`) into `60 Audio & SFX Engineering/reference-music/` for ear-candy study, pacing/ducking reference, and instrumental sampling.

> [!NOTE] Clean Instrumental vs. Full Video Mix
> - **`LEMMINO_ulfoU2MziOc.mp3`** is the **clean, un-narrated instrumental** explicitly credited in Video 9 (`gEQ0BLyVJhY`).
> - The other 8 `.mp3` files contain the **full creator audio mix** (narration + background music bed + SFX risers/whooshes/impacts), useful for analyzing exact music-to-voice ducking (`-14 LUFS` / `-6 dB` gated RMS), SFX timing, and `nbwQWTR0SV4` (Render Queue's 1,240+ SFX showcase).

| # | Video ID | Channel | Title | Duration | Credited Music / Audio Notes | Local File |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **1** | `ulfoU2MziOc` | **LEMMINO** | *Credited BGM from Video 9 (`gEQ0BLyVJhY`)* | Clean BGM | **Clean instrumental track** — moody atmospheric synth/ambient bed | `reference-music/LEMMINO_ulfoU2MziOc.mp3` |
| **2** | `gEQ0BLyVJhY` | **LOGAN SMITH** | *How to make shorts that go viral every time* | `9:41` (`581s`) | Credits **LEMMINO** (`ulfoU2MziOc`) in description | `reference-music/gEQ0BLyVJhY.mp3` |
| **3** | `LmXpbP7dD48` | **Kallaway** | *How to Create Irresistible Hooks (and blow up your content)* | `16:34` (`994s`) | Full mix: crisp talking-head + subtle synth bed + transition whooshes | `reference-music/LmXpbP7dD48.mp3` |
| **4** | `dNT7gd3ulAg` | **Jade Beason** | *I studied 100+ hooks, this strategy will make you go viral* | `13:44` (`824s`) | Full mix: upbeat creator lo-fi/pop bed + pop-in SFX | `reference-music/dNT7gd3ulAg.mp3` |
| **5** | `2byPP_9F0-Q` | **Kallaway** | *Give me 15 mins, and I'll make your hooks impossible to skip* | `15:48` (`948s`) | Full mix: low-end tension bed + punchy whoosh/hit transitions | `reference-music/2byPP_9F0-Q.mp3` |
| **6** | `8sb2R11FeVw` | **Thomas Creates** | *How to Make VIRAL YouTube Shorts Captions in One Click* | `9:55` (`595s`) | Full mix: fast-paced tutorial bed + caption pop SFX | `reference-music/8sb2R11FeVw.mp3` |
| **7** | `6US1-_bBS28` | **Ben Kaluza** | *10 Must-Know Tips for Short-Form Content Creators* | `14:45` (`885s`) | Full mix: rhythmic ambient bed + cut transitions | `reference-music/6US1-_bBS28.mp3` |
| **8** | `ds7DDgGgiVs` | **Joseph \| Video Editing** | *The Ultimate Guide to Editing Short-Form Content in 2026!* | `16:48` (`1008s`) | Full mix: modern editing showcase + J-cut whooshes/risers | `reference-music/ds7DDgGgiVs.mp3` |
| **9** | `nbwQWTR0SV4` | **Render Queue** | *The Most Popular Sound Effects for Editing (1240+)* | `1:15` (`75s`) | **Pure SFX & Music Pack Demo** (whooshes, risers, bass hits, UI pops) | `reference-music/nbwQWTR0SV4.mp3` |

---

## Next-Generation Recommended Music Pool (Use Only When Fitting)

See **[[04 Next-Generation Retention, Subtitles & Audio Spec]]** for the recommended Top-10 background tracks (scanned from `36 / 36` past-week uploads on `@r6rants`, `@Gneef`, `@RyexRBLX`, and `@nitrogeniofalante`: led by *Numbers — TEMPOREX*, *Cry — Cigarettes After Sex*, *Fallen Down (Reprise) — Toby Fox*) plus the 5 curated storytelling/ambient tracks (**use only when fitting** the video's tone and pacing) and the complete `nbwQWTR0SV4` + Openverse CC0 SFX cross-reference.

---

## Keeping the Space YouTube Upload & Iteration Plan Intact

Your **Orbit Oddities** (`@OrbitOddities`) Space YouTube pipeline remains completely untouched and ready to upload and iterate on later:
- **Completed Space Video**: [[Mars - What Would Kill You First (Completed Video)]] (`videos/mars-orbit/out/mars_final.mp4`, `1920×1080`, `144.45s`, `-14.7 LUFS`)
- **Space Upload Kit & Manifest**: [[Upload Package - Mars What Would Kill You First]] | `videos/mars-orbit/upload.md` | `scripts/upload_manifest.json`
- **Automated Uploaders**: `scripts/youtube_upload.py` | `scripts/omnichannel_publish.py`
- **Next Iteration Path**: When ready to iterate on Space YouTube videos, apply the retention & SFX rules from [[Deep Research - Viral Shortform Hooks, Storytelling & 1M+ Algorithm]], [[Deep Research - Viral Shortform Visuals, Subtitles, Motion, VFX & SFX]], and [[In This World Roblox Storytime - Editing, Zooms & VFX Bible]] to future **Orbit Oddities** episodes and Shorts funnels.
