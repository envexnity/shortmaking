---
title: 04 Next-Generation Retention, Subtitles & Audio Spec
tags:
  - next-generation
  - subtitles
  - retention
  - camera
  - pacing
  - music
  - sfx
  - style
area: pipeline
style: all
status: evergreen
created: 2026-11-16
updated: 2026-11-16
summary: Mandatory next-generation visual, subtitle, camera-pacing, music-whitelist, and SFX production directives derived from 8sb2R11FeVw, nbwQWTR0SV4, and a past-week (2026-11-09 to 2026-11-16) empirical scan of @r6rants, @Gneef, @RyexRBLX, and @nitrogeniofalante.
---

# 04 Next-Generation Retention, Subtitles & Audio Spec

> [!IMPORTANT] Mandatory Standing Directive for All Future Videos
> Every video generated after `2026-11-16` MUST obey the four rules below without exception:
> 1. **Exact `8sb2R11FeVw` Black-Background Subtitle Pill Style** (eye-catching, oversized, high-contrast).
> 2. **Minimal On-Screen Text** — remove extra HUD paragraphs, telemetry boxes, and bottom headlines; let subtitles carry the text.
> 3. **Maximum-Retention Rapid Cuts & Camera Motion** — `~0.9–1.5 s/cut` (`~1 cut/sec` during story beats), zero static holds.
> 4. **Recommended Music Pool (Use Only When Fitting) & Verified SFX Pack** — draw from the Top 10 songs from our past-week scan of `@r6rants`, `@Gneef`, `@RyexRBLX`, and `@nitrogeniofalante` and the 5 curated storytelling/ambient tracks **only when fitting** the video's tone and pacing, paired with matched SFX from `nbwQWTR0SV4` and verified CC0/Foley fallbacks.

---

## 1. Subtitle Style Spec (Measured Directly from `youtu.be/8sb2R11FeVw`)

Verified by extracting `1280×720` frames (`1:45–2:25`) and measuring pixel RGB values & box proportions inside the `405×720` centered `9:16` viewport:

- **Container Style**: Auto-width **dark translucent / near-opaque black rounded pill box** tightly hugging the phrase (`no outer colored border`).
  - Measured `720p` box fill: BGR `[19.1, 18.7, 22.5]` vs surrounding frame `[53.2, 55.1, 66.4]` → **`rgba(8, 8, 10, 0.88)`** (or `0.90` for even stronger contrast).
  - Corner radius: **`14 – 16 px`** at `1080×1920`.
  - Padding: **`20–24 px` vertical × `34–42 px` horizontal** at `1080×1920` (measured `~11 px` top/bottom at `720p` on a `40 px` pill height).
- **Typography (Eye-Catching & Noticeable)**:
  - Font family: Clean heavy geometric sans-serif — **`Inter Black` / `Inter Bold` / `Montserrat ExtraBold`** (`weight 800–900`).
  - Size at `1080×1920`: **`56 – 64 px`** (oversized so it dominates mobile attention even at arm's length, larger than `8sb2R11FeVw`'s `~45 px` baseline while keeping exact pill proportions).
  - Base color: Pure crisp **`#FFFFFF`** with clean subtle text shadow (`0 2px 8px rgba(0,0,0,0.45)`).
  - Active-word / keyword pop: Optional high-salience emphasis on the currently spoken or hook-critical word in **`#FFE600` (Electric Yellow)**, **`#22EE66` (Neon Green)**, or **`#FF3344` (Crimson)** + subtle `1.06×` scale pulse *inside* the black pill.
- **Phrase Rhythm & Entry Motion**:
  - **`2 – 4 words` per pill (`1` compact horizontal line)**, matching examples like `"landed on the moon"`, `"And Nintendo started"`, `"the Great Pyramid."`
  - Snap-in micro-pop on phrase transition: `3-frame` `easeOutBack` (`scale 0.88 → 1.05 → 1.00`, `opacity 0 → 1`).
- **Safe-Zone Placement (`1080×1920`)**:
  - Centered horizontally (`x = 540 px`), positioned at **`y = 1280 – 1420 px` (`67–74%` down)** — prominently noticeable in the lower visual focal zone while staying safely clear of YouTube Shorts / TikTok bottom UI chrome (`y ≥ 1500 px`).

### Copy-Paste Canvas2D Implementation (`1080×1920`)

```javascript
function drawNextGenSubtitlePill(ctx, W, wordsChunk, activeIdx, tSinceChunkStart, yCenter = 1360) {
  if (!wordsChunk || !wordsChunk.length) return;
  const fontSize = 58;
  ctx.save();
  ctx.font = `800 ${fontSize}px Inter, Montserrat, "Segoe UI", sans-serif`;
  ctx.textBaseline = 'middle';

  const pieces = wordsChunk.map((w, i) => (i < wordsChunk.length - 1 ? w.w + ' ' : w.w));
  const widths = pieces.map((p) => ctx.measureText(p).width);
  const textW = widths.reduce((a, b) => a + b, 0);

  const padX = 38;
  const padY = 22;
  const boxW = textW + padX * 2;
  const boxH = fontSize + padY * 2;

  // 3-frame (0.10s) easeOutBack pop-in
  const u = Math.min(1, Math.max(0, tSinceChunkStart / 0.10));
  const c1 = 1.70158, c3 = c1 + 1;
  const popScale = u < 1 ? 0.88 + 0.12 * (1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2)) : 1;

  ctx.translate(W * 0.5, yCenter);
  ctx.scale(popScale, popScale);

  // Solid/near-opaque black pill background (8sb2R11FeVw style)
  ctx.fillStyle = 'rgba(8, 8, 10, 0.90)';
  ctx.shadowColor = 'rgba(0, 0, 0, 0.45)';
  ctx.shadowBlur = 18;
  ctx.beginPath();
  ctx.roundRect(-boxW * 0.5, -boxH * 0.5, boxW, boxH, 16);
  ctx.fill();
  ctx.shadowBlur = 0;

  let x = -textW * 0.5;
  ctx.textAlign = 'left';
  pieces.forEach((p, i) => {
    ctx.fillStyle = i === activeIdx ? '#FFE600' : '#FFFFFF';
    ctx.fillText(p, x, 2);
    x += widths[i];
  });
  ctx.restore();
}
```

---

## 2. Minimal On-Screen Text Rule

- **Subtitles Only by Default**: Strip multi-line explainer cards, stacked bottom headlines, floating mission banners, and multi-stat sidebars from future Shorts.
- **Visuals Carry the Concept**: Show the action through dramatic framing, props, animated gauges/meters (numbers only, e.g. `475°C`, `92 BAR`), or single-word `YOU` / `X` indicators rather than sentences on screen.
- **Target Ratio**: **`≥ 90%`** of all visible words across the video come exclusively from the black-pill subtitles.

---

## 3. Rapid Camera Movements & Maximum-Retention Cut Cadence

Measured directly across viral past-week uploads from our benchmark channels:

| Reference Video | Duration | Detected Hard Cuts | Avg Seconds / Cut | Mean Frame Diff | Verified Pattern |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`@RyexRBLX`** (`RvaEBKl_MKw`) | `179.2 s` | **`185`** | **`0.97 s/cut`** | `8.72` | Almost 1 cut/sec + blurred hook snap-in + rapid angle swaps |
| **`@Gneef`** (`gL8ab61OWRg`) | `177.8 s` | **`176`** | **`1.01 s/cut`** | `9.77` | Continuous orbital/aerial glides + reverse-angle dialogue cuts |
| **`@r6rants`** (`3hqpNG9HG3k`) | `156.6 s` | **`138`** | **`1.13 s/cut`** | `5.32` | Staccato room/POV cuts + punch-in zooms on punchlines |

### Next-Generation Motion Rules
1. **Cut Cadence**: Cut every **`0.9 – 1.6 seconds` (`27 – 48 frames` at 30fps)**; never let a static framing sit longer than `2.0 s` without either a hard angle change or an aggressive `≥15%` punch-in cut.
2. **Every Shot Moves**: Combine continuous zoom creeps (`+0.35% to +0.85% / frame`), `130% → 100%` blurred opening hook snaps (`8–12f`), `100% → 122%` punch-in zooms (`5–7f`, `Back.Out`), `±5°–10°` Dutch tilts on suspense beats, whip-pan transitions (`6–10f`), and `7-frame` alternating-sign impact `KICKS`.
3. **Cut-Synced Audio Transients**: Pair rapid cuts with `2–4 frame` pre-cut whooshes and frame-0 sub-bass impacts (measured **`3.5×–9.6×`** above median high-frequency floor at cut boundaries in `@Gneef`, `@RyexRBLX`, and `@r6rants`).

---

## 4. Recommended Music Pool — Use Only When Fitting (`@r6rants`, `@Gneef`, `@RyexRBLX`, `@nitrogeniofalante`)

> [!NOTE] Scan Window & Music Selection Policy
> **Scan Window**: `2026-11-09` through `2026-11-16` (`36 / 36` unique videos across all 4 channels: `@r6rants` 5, `@Gneef` 26, `@RyexRBLX` 2, `@nitrogeniofalante` 3 compilations). Voiceover was stripped with `UVR_MDXNET_KARA_2.onnx` (`audio-separator`) and every isolated BGM segment was identified via `shazamio`.
> **Policy**: **Only use songs from this pool when fitting** the video's mood, pacing, and narrative tone (do not force-fit a track if another score fits the story better).

| Rank | Song Title | Artist | Segment Hits | Unique Videos | Total Video Views | Observed Channels |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | **`Numbers`** | **TEMPOREX** | `32` | `21` | `49,373,006` | `@Gneef`, `@RyexRBLX`, `@nitrogeniofalante` |
| **2** | **`Cry`** | **Cigarettes After Sex** | `25` | `23` | `55,422,339` | `@Gneef`, `@RyexRBLX`, `@nitrogeniofalante` |
| **3** | **`Fallen Down (Reprise)`** | **Toby Fox** | `13` | `10` | `17,229,477` | `@r6rants` (`5/5`), `@Gneef` (`5`) |
| **4** | **`MTG CABELO PRETINHO OU REFLEXO ALINHADO x NUMBERS 150BPM`** | **weeb!** | `9` | `3` | `43,286` | `@nitrogeniofalante` *(high-BPM funk/Numbers remix)* |
| **5** | **`playing with numbers`** | **MidnightClub** | `4` | `2` | `10,853` | `@nitrogeniofalante` *(Numbers edit/variation)* |
| **6** | **`Dream Playground`** | **1MIRACLE** | `2` | `2` | `10,850,426` | `@Gneef` |
| **7** | **`nosleep funk`** | **akinari** | `2` | `2` | `9,833,058` | `@Gneef` |
| **8** | **`Levels`** | **Avicii** | `2` | `2` | `900,737` | `@r6rants` |
| **9** | **`In This Shirt`** | **The Irrepressibles** | `1` | `1` | `4,419,035` | `@Gneef` *(emotional climax)* |
| **10** | **`Thunderstorm`** | **Javier Cordón Fernandez** | `1` | `1` | `2,310,011` | `@Gneef` *(suspense/storm)* |

*Other single-hit tracks observed once across the 36 videos (ranked below #10 by views): `DIGIDIGI BAM BAM — Bootscoot Radio` (`2.17M`), `Aren't You Tired of Fighting — KxlearnUS` (`1.15M`), `Eurasier (Trance Mix) — Hasenchat Music` (`0.96M`), `Nothing Can Be Explained (Instumental Version) — Shiro SAGISU`, `feature — Moomed`, `Abandoned — Jius Braselz`, `Transgender — Crystal Castles`.*

### User-Curated Storytelling & Dark Ambient Pool (Use Only When Fitting)
Use these **5 core atmospheric / storytelling tracks** **only when fitting** the mood, pacing, and story arc of a next-generation video:

| Track | Artist | Role / Scene Placement |
| :--- | :--- | :--- |
| **`Snowfall (Slowed + Reverb)`** | **Øneheart & reidenshi** | Primary atmospheric, melancholic & cinematic storytelling bed |
| **`Apathy (Slowed + Reverb)`** | **Øneheart** | Darker, tense, slow-building emotional synth — ideal for dramatic twists |
| **`Sleepwalker (Slowed)`** | **akiaura, LONOWN & STM** | Heavy, hypnotic, ominous electronic atmosphere for suspense & dark edits |
| **`Resonance (Slowed + Reverb)`** | **HOME** | Classic nostalgic, floating synth for the *"good / dreamy"* opening phase before the twist |
| **`Controlled Chaos` / `Private Reflection` / `Unseen Horrors`** *("Limbo / Abyss" Dark Ambient)* | **Kevin MacLeod** | Royalty-free dark ambient tension for YouTube storytelling & mystery arcs |

---

## 5. Popular SFX Catalog — `nbwQWTR0SV4` vs. External Verified Sources

Audited visually and acoustically from **`https://youtu.be/nbwQWTR0SV4`** (*Render Queue Ultimate SFX & Music Pack*, 4 folders: `Default`, `Cartoon`, `Meme`, `Popular`, plus `Music`), cross-referenced against the transient profiles of `@r6rants`, `@Gneef`, and `@RyexRBLX`.

### A. Popular SFX Found Inside `nbwQWTR0SV4`
| Category | Exact Clip Names Seen / Heard in `nbwQWTR0SV4` | Folder | Best Narrative Use |
| :--- | :--- | :--- | :--- |
| **Cut Impacts & Bass Drops** | `BOOM HIT`, `boom hit`, `atomic impact`, `Collapsing Impact`, `INTRO HIT 1`, `atencion impacto` | `Default/` | Hard frame-0 twist reveals, rule shockers, `Ryex`/`r6rants` cut punches |
| **Risers & Tension Swells** | `RISE`, `aggressive rise hit`, `Creepy Tone Sub Ba...`, `EPIC SOUND SCARY` | `Default/` / `Popular/` | `0.5–1.5 s` pre-climax build before the `"Unluckily..."` reversal |
| **Whoosh / Slide** | `Abduction swish`, `CHANGE SLIDE` | `Default/` | Pre-cut `2–4f` lead-in transition & camera whip-pans |
| **Comedy / Cartoon Punctuation** | `BLINK`, `CARTOON BOING`, `CARTOON HORN`, `GOOFY AHH`, `awkward cricket`, `Awkward moment`, `CRAZY REALISTIC KNOCKING`, `Alarm Clock Classic`, `BARREL EXPLODING` | `Cartoon/` / `Default/` | Deadpan silence breaks, character blinks, doors/alarms, slapstick fails |
| **Viral Meme Stingers** | `among`, `cave`, `Camera Flash`, `bruh`, `cr siiiiiiu`, `deja vu`, `fbi open up`, `galaxy brain`, `illuminati`, `coffin dance`, `bass boost discord`, `clash royale laugh`, `he knew` | `Meme/` / `Popular/` | Plot-twist shock cuts, freeze-frame flash callbacks, ironic realizations |

### B. Essential Popular SFX NOT Shown in `nbwQWTR0SV4` (Source Elsewhere — Openverse CC0 / Mixkit / Freesound)
Because `nbwQWTR0SV4` focuses heavily on big cinematic impacts and meme clips rather than the subtle micro-SFX triggered **every `~1 second`** in `@Gneef`, `@RyexRBLX`, and `@r6rants`, source these missing workhorses via the zero-key **Openverse CC0 API** (`api.openverse.org/v1/audio/?license=cc0`):

| Missing Popular SFX Category | Why It Is Needed | Verified Openverse CC0 Asset (Tested Live) |
| :--- | :--- | :--- |
| **Crisp Short Air Whoosh / Whip Swish** | `2–4f` pre-cut glue on `~1 cut/sec` rapid edits (not long sci-fi swishes) | `swosh-08.flac - 'stick cutting air'` (`https://cdn.freesound.org/previews/59/59995_71257-hq.mp3`), `whoosh_short_low.wav` (`https://cdn.freesound.org/previews/449/449992_3217484-hq.mp3`) |
| **Subtle Caption Pop / UI Click** | Tactile `2–5 kHz` micro-tick on subtitle pill changes & emphasis words | `UI Button Click` (`https://cdn.freesound.org/previews/467/467951_6769414-hq.mp3`), `UI Series: Hollow pop` (`https://cdn.freesound.org/previews/333/333428_4682121-hq.mp3`) |
| **Sub-Bass / Horror Riser Hit** | Clean modern short-form riser-into-boom (less meme-heavy than `atomic impact`) | `Riser Hit sfx 046.wav` (`https://cdn.freesound.org/previews/649/649933_8698658-hq.mp3`), `Metallic Horror Riser FX.wav` (`https://cdn.freesound.org/previews/545/545798_11961848-hq.mp3`) |
| **Camera Shutter / Flash Snap** | Freeze-frame evidence / callback punctuation | `iOS Camera flash` (`https://cdn.freesound.org/previews/455/455511_9453283-hq.mp3`), `Vintage Camera Flash` (`https://cdn.freesound.org/previews/232/232130_525427-hq.mp3`) |
| **Cartoon Spring Boing** | Clean crisp spring bounce (standalone, no narrator overlap) | `Cartoon Boing.wav` (`https://cdn.freesound.org/previews/161/161122_2750714-hq.mp3`), `Boing Spring` (`https://cdn.freesound.org/previews/334/334031_2064400-hq.mp3`) |
| **Roblox Foley (`Oof` / Plastic Footstep / Slap / Cash Register)** | Story-specific physical Roblox / cartoon actions | Mixkit / Openverse CC0 (`wooden tap`, `cash register`, `slap`) or `earshot` bank |
