---
title: 01 Quick Reference — Numbers, Shaders & Commands Cheat Sheet
tags:
  - quick-reference
  - cheatsheet
  - shaders
  - commands
  - ffmpeg
  - remotion
area: overview
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-21
summary: Single-page engineering cheat sheet with exact measured constants, colour palettes, camera speeds, FFmpeg commands, and one-liner triggers for all 7 animation engines (including Blender 5.3 Cycles OptiX & EEVEE) and omnichannel auto-publishing.
---

# 01 Quick Reference — Measured Numbers, Palettes & Commands

> [!TIP] Copy-Paste Engineering Reference
> Every number on this page was measured directly from the 32,000-frame reference study (`cartoon-3d-short`), `cartoon-audio-short`, and `make-3d-video`. Use these exact constants instead of guessing.
> - **Next-Generation Updates (`2026-11-16`)**: See [[04 Next-Generation Retention, Subtitles & Audio Spec]] for mandatory black-pill subtitles (`8sb2R11FeVw`), minimal extra text, `~1 cut/sec` rapid camera pacing, curated music pool (use only when fitting), and `nbwQWTR0SV4` SFX mapping.
> - **Deep Research Masterclass Trilogy (`2026-11-18`, 120 Sources)**:
>   - **Story Writing & Delivery**: [[Deep Research - How to Write & Tell Stories (Narrative Architecture Bible)]]
>   - **Animation Layout & Composition**: [[Deep Research - Animation Layout, Staging & Visual Composition]]
>   - **Joke Writing & Comedy Science**: [[Deep Research - How Humans Write Funny Jokes & Comedy Engineering]]
>   - **Unified Master Synthesis**: [[Deep Research - Masterclass on Story Writing, Animation Layout & Comedy Science]]
> - **Blender 5.3 Look-Dev & API Mastery (`2026-11-20`)**: See [[Blender 5.3 Cinematic Rendering & Animation Mastery Bible]] & `90 Templates & Starter Kits/blender-cinema-kit/blender_cinema_lib.py` (`BLENDER_EEVEE`, Cycles `OPTIX` + GPU `OPENIMAGEDENOISE`, `AgX - Punchy`, `scene.compositor_effects`, `OutputFile.file_name = ""`, Slotted Actions `channelbag(slot).fcurves`).
> - **Undershine 3D Pixel Art in Blender 5.3 (`2026-11-20`)**: See [[Deep Research - Undershine 3D Pixel Art, Atmospheric Shadows & Multi-Angle Blender Cinematography]] & [[Style 7 - Undershine 3D Pixel Art in Blender (EEVEE Next + Multi-Angle)]] (`270×480` 4× integer scale, `filter_size=0.01`, `sun.angle=0.018`, `t3ssel8r` Normal/Depth outlines, 8-camera multi-angle switching).
> - **Roblox R6 Story Cast & Marketplace Factory (`2026-11-21`)**: See [[Roblox R6 Story Cast & Marketplace Character Factory (Blender 5.3)]] & `assets/roblox-r6-characters/` — 8 rigged Aeresei R6 IK+FK V2.22 `.blend` characters (`MBlocky`/`FBlocky`), 50 real Roblox Marketplace assets, `Roblox_R6_Story_Cast.blend`, and automated download/bake/build scripts.
> - **Non-3D Studio Expansion (`2026-11-21`)**: See [[Non-3D Visual Styles Encyclopedia (2D Vector, Storytime Animatics, Documentary Collage, 8-Bit & ASCII Horror)]], [[Voice Acting, Expressive TTS Direction & Vocal Processing Bible]], [[Music Scoring, Dynamic Ducking, Mastering & Copyright Safety Bible]], [[05 Editing Rhythm, Pre-Vis Animatics & Retention Graph Forensics]], [[Color Psychology, Typography Pairing & Frame-0 Thumbnail Engineering]], and [[Channel Strategy, Series IP, Batch Ops & Monetization Playbook]].

---

## 1. Master Spec & Pacing Table

| Parameter | Track 1 & 2: 2D-in-3D Toon | Track 3: Low-Poly 3D (`KAZ`) | Track 4: Realistic Blender 5.3 | Track 5: Roblox R6/R15 Shorts | Track 6: Orbit 2D Space (`orbit-space-video`) | Track 7: Undershine 3D Pixel (Blender 5.3) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Resolution (Base / Master)** | `1080×1920` (`--scale 1.3333` → `1440×2560`) | `1080×1920` (9:16 portrait) | `1080×1920` (`CYCLES` OptiX or `BLENDER_EEVEE` RT) | `1080×1920` (Studio / Blender 5.3 30/60fps) | `1920×1080` (16:9 YouTube, `30 fps`) | `270×480` → `4×` `1080×1920` (`BLENDER_EEVEE`) |
| **Frame Rate** | `30 fps` (`dt = 33.33ms`) | `30 fps` | `30 fps` | `60 fps` (or `30 fps` cinematic) | `30 fps` | `30 fps` world / `15 fps` stepped characters |
| **Duration Sweet Spot (`< 45s` Cap)** | **`< 45s`** (`28–42s`, `840–1260 frames`) | **`< 45s`** (`28–42s`, `8–12 shots`) | **`< 45s`** (`28–42s`) | **`< 45s`** (`25–42s`) | **`< 45s`** (`30–42s` Short) / `75–140s` (16:9) | **`< 45s`** (`20–42s`, `6–12` camera angles) |
| **Speaking Rate (WPS)** | `3.5–4.1 wps` (median **`3.7 wps`**) | **`~2.6 wps`** (`timing.py` default) | `3.4–3.8 wps` | `3.8–4.3 wps` | **`~2.5–2.8 wps`** (calm, dry delivery) | `3.2–3.8 wps` |
| **Max Pause / Dead Air** | `<0.25s` per pause (`<1.0s` total) | `0.3s` beat gap (`gap=0.12s`) | `<0.20s` per pause | `<0.15s` (J-cut overlap) | `0.15–0.3s` beat gap (comic beat pauses) | `<0.20s` per pause |
| **Integrated Loudness** | **`-14.0 LUFS`** (`LRA ~2.4 LU`, `TP -1.0 dBTP`) | **`-14.0 LUFS`** | **`-14.0 LUFS`** | **`-14.0 LUFS`** | **`-14.0 LUFS`** (`TP -1.0 dBTP`) | **`-14.0 LUFS`** |
| **Music + SFX vs. VO** | **`-6 dB` gated RMS** (`0.28×` gain under VO) | `-8 dB` to `-6 dB` | `-6 dB` gated RMS | `-5 dB` SFX / `-10 dB` Music | `-8 dB` ambient bed + spot telemetry SFX | `-6 dB` gated RMS |

---

## 2. 2D-in-3D Toon Look Constants (`cartoon-3d-short`)

### Character Card Spec (`toon.ts`)
- **Canvas Size**: `600 × 1000 px` (`soles at y = 975`, world card `1.32m × 2.20m` → `2.15m` tall in scene)
- **Adult Proportions (`3.5 HH`)**: Head = `1.0 HH` (`rx=115, ry=108`), Torso bean = `1.1 HH`, Stick legs = `1.4 HH` (`5.8u` stroke), Ink-dot hands = `5.5u` radius
- **Superellipse Bean Head**: `H/W = 0.94`, top exponent `nTop = 1.75`, jaw exponent `nBot = 2.30`, jaw widen `egg = -0.12`, cheek asymmetry `asym = +0.08`
- **Outline Ink**: **`#241726`** (dark warm plum — **never `#000000`**), variable width `w=4.4` (`1.38×` on shadow side `64°`, `0.58×` on lit side `~3:1` ratio)
- **Eyes & Brows**: Spacing `0.26 × headW`, vertical `0.45` down from crown. Default eye = `'lidded'` (droopy upper lid over black pupil disc). **No blush, no white eye catchlights.**
- **Blink Cadence**: Every `0.5–2.3s` (median `1.2s`), duration **`4 frames`** (`blink = [0.5, 1.0, 1.0, 0.5]`), plus mandatory blink on every expression change.
- **Mouth Shapes (5 total)**: `'line'`, `'smirk'`, `'frown'`, `'o'`, `'open'` (tongue `#d4625a` at bottom of `'open'`). Speech cycle at `10 Hz` gated by voice amplitude.

### World Outlines, Lighting & Post (`ink.ts`, `shade.ts`, `lensblur.ts`, `grade.ts`)
- **Composer Order**: `RenderPass` → `InkPass` (Pass, NOT merged Effect!) → `EffectPass(LensBlurEffect, BloomEffect, ToneMappingEffect(NEUTRAL), GradeEffect)`
- **`NOINK` Layer**: `export const NOINK = 3;` — call `enableNoInk(obj)` on all character cards, sky dome, clouds, water sheets, smoke, and painted signs.
- **Ink Width vs. Distance (1080p)**: `5.1 px` at `6m` → `3.8 px` at `25m` → `2.2 px` at `90m`, colour `#0b0a0c`, `inkStr = 0.88`.
- **Day Palette**: Sky zenith `#36a3eb` → horizon `#9ed4f0`, Sun `#fff6e5` (`intensity 2.5`), Hemisphere `#9bd3f5 / #8c7853` (`1.05`), Fog `#9bd0ec` (`25m → 300m`).
- **Golden Hour Backlit Palette**: Sun ahead (`az 6–15°, el 7–9°`), Ground lit `#db9044` → **Violet-Blue Shadow `#5b5173`** (`B ratio 1.35–3.0×` lit!).
- **Thin-Lens DOF (`LensBlurEffect`)**: `cInf = 12–16 px` on Close-Ups (`focusDist` locked to character eye distance, `focusRange = 2.2m`), `cInf = 0` on establishing wides.

---

## 3. Low-Poly 3D Studio Palette & Camera Grammar (`make-3d-video`)

```javascript
// Built-in KAZ.PAL (studio/kit.js)
{
  bg: 0x0b0d13, skyTop: 0x0d1b2a, skyBot: 0x1b263b,
  grass: 0x4a7c59, dirt: 0x8b6f47, sand: 0xd4a373,
  stone: 0x6c757d, snow: 0xf1faee, water: 0x2ec4b6,
  wood: 0x7f4f24, leaves: 0x3a5a40,
  red: 0xe63946, orange: 0xf4a261, gold: 0xe9c46a,
  teal: 0x2a9d8f, blue: 0x457b9d, navy: 0x1d3557,
  purple: 0x7209b7, pink: 0xf72585,
  white: 0xf8f9fa, gray: 0xadb5bd, dark: 0x212529, black: 0x0f1117,
  skin1: 0xf1c27d, skin2: 0xe0ac69, skin3: 0xc68642, skin4: 0x8d5524
}
```

---

## 4. Essential CLI One-Liners

### A. Word-Level Timing & Silence DP
```powershell
# Whisper word-level alignment (cartoon-audio-short)
python tools/timing.py voice.mp3 story.txt words.json

# Energy-based dynamic programming beat alignment (make-3d-video)
python studio/tools/timing.py voiceover.mp3 "Beat 1 text" "Beat 2 text" "Beat 3 text" --json > timing.json
```

### B. Render & Disk-Safe Remotion (`cartoon-3d-short`)
```powershell
# Prevent 60-110GB Remotion webpack temp bundle disk exhaustion:
$env:TMPDIR = "C:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\scratch_tmp"
New-Item -ItemType Directory -Force -Path $env:TMPDIR | Out-Null
Remove-Item -Recurse -Force "$env:TMPDIR\remotion-*" -ErrorAction SilentlyContinue

# Render 2K vertical master (1440x2560 @ 30fps)
npx remotion render Bridge out/bridge_2k.mp4 --scale=1.3333 --codec=h264 --crf=16
```

### C. Render Standalone Playwright + Three.js (`cartoon-audio-short` / `make-3d-video`)
```powershell
# Standalone 2D-in-3D Toon (Playwright headless Chromium -> FFmpeg)
node tools/render.mjs engine/index.html out/video.mp4 52.8

# Low-Poly 3D Kaz Studio (Playwright headless -> FFmpeg + VO mux)
node studio/render.js --shots ./shots.js --audio ./voiceover.mp3 --out ./final.mp4

# Orbit 2D Space Survival Kit (NASA Image API + Playwright Canvas2D + FFmpeg)
python "../90 Templates & Starter Kits/orbit-2d-space-kit/fetch_nasa.py" assets "Phoenix lander scoop soil Mars"
node "../90 Templates & Starter Kits/orbit-2d-space-kit/render.js" scenes.js --stills stills
node "../90 Templates & Starter Kits/orbit-2d-space-kit/render.js" scenes.js --audio audio/mix.wav --out out/final.mp4

# Blender 5.3 Headless Render (Track 4 Cinema / Track 5 R6-R15 / Track 7 Undershine)
& "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe" --background --python build_scene.py
ffmpeg -y -framerate 30 -i out/frames/f_%04d.png -i out/mix.wav -map 0:v:0 -map 1:a:0 -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k -shortest out/final.mp4
```

### D. Broadcast Voice Processing, Sidechain Ducking & Explicit `-14 LUFS` Mux
```powershell
# 1. Broadcast vocal EQ + dead-air trim + 3:1 compression + -14 LUFS:
ffmpeg -y -i voice_raw.wav -af "silenceremove=start_periods=1:start_silence=0.02:start_threshold=-42dB,highpass=f=85,equalizer=f=250:t=q:w=1.4:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=6800:t=q:w=2.0:g=-2.0,treble=g=1.2:f=11000,acompressor=threshold=-18dB:ratio=3:attack=8:release=110:makeup=2,loudnorm=I=-14:TP=-1.0:LRA=5" -ar 48000 -ac 2 voice_master.wav

# 2. One-pass VO + sidechain-ducked music (-4.5dB @ 2.4kHz vocal pocket) + SFX mix:
ffmpeg -y -i voice_master.wav -i music_bed.wav -i sfx_bus.wav -filter_complex "[0:a]asplit=2[vo_main][vo_sc];[1:a]highpass=f=45,equalizer=f=2400:t=q:w=1.2:g=-4.5,volume=0.34[mus_eq];[mus_eq][vo_sc]sidechaincompress=threshold=0.03:ratio=4:attack=15:release=180:makeup=1[mus_duck];[2:a]volume=0.80[sfx_lvl];[vo_main][mus_duck][sfx_lvl]amix=inputs=3:duration=first:dropout_transition=0:normalize=0,loudnorm=I=-14:TP=-1.0:LRA=6" -ar 48000 -ac 2 mix.wav

# 3. Explicit stream map (mandatory when video.mp4 has a silent audio track):
ffmpeg -y -i video.mp4 -i mix.wav -af "loudnorm=I=-14:TP=-1.0:LRA=7" -c:v copy -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 -shortest final.mp4
```

### E. Automated Frame QA & Mandatory Post-Completion Visual Check
```powershell
# 1. Verify 0 black frames, 0 unplanned white flashes, 0 frozen spans (>=12f), & build 2s sheets:
python "90 Templates & Starter Kits/cartoon-3d-short-kit/scripts/short_qa.py" final.mp4 out/qa_visual

# 2. Extract readable 540x960 stills (Frame 0 + 1fps) for mandatory visual inspection:
ffmpeg -y -i final.mp4 -vf "fps=1,scale=540:960" out/qa_stills/sec_%03d.jpg
```
> Always inspect the resulting stills and `sheet_*.jpg` visually using [[Post-Completion Visual QA — What, How & Why to Fix]] before shipping.

### F. Omnichannel Auto-Publishing (Default = ALL Platforms: YouTube + TikTok + Instagram)
> **Rule 33:** Whenever asked to `"upload"` / `"post"`, ALWAYS publish to **ALL 3 live platforms** (`youtube`, `tiktok`, `instagram`) via `.agents/skills/social-posting/SKILL.md` unless explicitly told otherwise:
> 1. **YouTube Shorts** (`youtube:upload_video`) — local 9:16 MP4 (`≤60s`), `title`, `description`, `tags`, `visibility` (or `publish_at` RFC3339 + `privacy="private"` when scheduled).
> 2. **TikTok** (`tiktok:creator_info` → `tiktok:post_video` → `tiktok:post_status`) — local MP4 + platform-adapted `caption` (`@pixelatepast`).
> 3. **Instagram Reels** (`media-host.ps1 start -File <mp4>` → `instagram:instagram_post_reel(videoUrl, caption, apply=true)` → `media-host.ps1 stop`).

```powershell
# Instagram public HTTPS tunnel (start before instagram_post_reel, stop right after):
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\AFADAZIO\.gemini\config\social-posting\media-host.ps1" start -File "videos/<slug>/out/final.mp4"
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\AFADAZIO\.gemini\config\social-posting\media-host.ps1" stop

# Legacy/CLI Batch Manifest Validator & Publisher:
python scripts/omnichannel_publish.py --manifest scripts/omnichannel_manifest.json --dry-run
python scripts/omnichannel_publish.py --manifest scripts/omnichannel_manifest.json --platforms youtube tiktok instagram
```
> See [[00 Social Publishing Home]], [[20 Description, Hashtag & SEO Optimization Bible]], [[30 Upload Timing, Cadence & Global Timezone Matrix]], and [[40 Automated Uploading Research & Full Engineering Architecture]].
