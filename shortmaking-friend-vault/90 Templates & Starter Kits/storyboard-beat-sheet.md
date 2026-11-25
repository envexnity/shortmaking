---
title: Storyboard & Non-3D Beat Sheet Template
tags:
  - template
  - storyboard
  - pre-vis
  - editing
  - pacing
area: templates
style: all
status: evergreen
created: 2026-11-21
updated: 2026-11-21
summary: Frame-accurate pre-production storyboard & beat sheet template synchronizing spoken words, TTS emotion tags, visual composition, pattern interrupts (every 1.0-1.6s), black-pill captions, and 2-4 frame SFX lead-ins before rendering.
---

# Storyboard & Beat Sheet — `[VIDEO TITLE]`

- **Style / Track**: `[e.g., 2D Vector / Editorial Collage / 8-Bit Canvas / ASCII Horror / Roblox R6 / Kinetic Type]`
- **Target Duration**: **`< 45.0 s`** (`[e.g., 36.0 s]` = `[1080 frames @ 30 fps]`)
- **Word Count & WPS**: `[e.g., 135 words @ 3.75 wps]`
- **Voice Engine & Persona**: `[e.g., Fish Audio S2.1-Pro / Kokoro-82M / Edge-TTS]`
- **Music Bed & Rights Tier**: `[Track Name — Tier A/B/C]` (`-6 dB` gated RMS, `8f` pre-climax drop at `f = ___`)
- **Color Palette (60 / 30 / 10)**: `BG #______` · `Mid #______` · `Accent #______`

---

## Pre-Production Gates (Complete BEFORE Rendering!)
- [ ] **Gate 1 — Eyes-Closed Radio-Cut**: `voice_master.wav` runs `< 45 s`, starts at `t = 0.00 s`, zero unintended gaps `> 0.16 s`, hook stops scroll in `3.0 s`.
- [ ] **Gate 2 — Mute Visual Test**: Every `1.0–1.8 s` has a visual reset; story reads cleanly on mute from visuals + `2–4` word black-pill captions.
- [ ] **Frame-0 Squint Test**: `≤ 3` visual elements, focal eyes/prop at `y = 35–45%`, completely inside `9:16` safe zones (`x: 100–900 px`, `y: 230–1420 px`).

---

## Frame-Accurate Beat Table (`30 fps`)

| Beat | Time (`s`) | Frames | Spoken Line & `[TTS Emotion Tag]` | Visual Composition & Framing (`Wide / MS / CU / Diagram`) | Motion & Pattern Interrupt (`Zoom / Shake / Boil / Cut`) | Black-Pill Subtitle (`2–4 words` + Accent Color) | SFX Cue (`2–4f` Lead-In!) & Music State |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1A — Hook Context** | `0.0–1.5` | `0–45` | `[Paradox stated as fact]` | Frame-0 anomaly close-up; focal eyes `y = 38%` | Blurred punch-out `130%→100%` (`9f`) + `0.25%/f` creep | `HOOK NOUN` (`#FFE600`) | Crisp pop @ `f=0`; Music starts `-18 dB` (or silent until 1B) |
| **1B — Scroll-Stop** | `1.5–3.2` | `45–96` | `[But / Except... contrast]` | Hard cut to shocked reaction CU | Punch-in `100%→118%` (`Back.Out`) + `4f` CA + `7f` kick | `EXCEPT ME` (`#FF3344`) | Whoosh @ `f=42` (`3f` early) → `65 Hz` bass hit @ `f=45`; beat drops |
| **2 — Baseline** | `3.2–8.5` | `96–255` | `[How normal world works]` | Wide/MS establishing rule visually | Staggered `3f` icon pops + smooth glide | `2–4 word` pills | UI clicks / ambient Foley; Music steady `-6 dB` gated |
| **3 — Complication** | `8.5–15.5` | `255–465` | `[Stakes rise in concrete setting]` | Angle jump `≥35°` + prop clue planted | Rapid cuts every `1.3 s` + subtle `±5°` Dutch tilt | Highlight key threat `#FF3344` | Pre-cut swishes (`-3f`) + rising tension texture |
| **4A — Luckily...** | `15.5–19.0` | `465–570` | `[relieved] Luckily, ...` | Bright relief framing / prop rescue | Spring pop entrance (`damping 12`) | `LUCKILY...` (`#22EE66`) | Sparkle/chime transient on `Luckily` |
| **4B — Unluckily...** | `19.0–23.5` | `570–705` | `[deadpan] Unluckily, ...` | Extreme CU deadpan or chaotic reverse angle | `0.15 s` comic beat → snap zoom `128%` + `7f` kick | `UNLUCKILY...` (`#FF3344`) | Record scratch / dry bonk + sub thud |
| **5 — "You see," Pivot** | `23.5–31.0` | `705–930` | `[intrigued] You see, [everyday analogy]...` | Match-shape cut to clean visual diagram/analogy | Smooth evolving path / step-by-step highlight | Highlight analogy noun `#FFE600` | LPF music to `1.4 kHz` for intimate focus; crisp diagram ticks |
| **6 — Climax & Loop** | `31.0–37.5` | `930–1125` | `[Callback twist — zero outro!]` | Match lighting & horizon to Frame 0 | **`8f` silence vacuum** → impact payoff → hard cut `<0.08 s` after last syllable | Final punchline word pop | Music drops `-28 dB` for `8f` before payoff; `25 ms` clean end fade |

---

## Post-Render QA Sign-Off
- [ ] `short_qa.py` passed (`0` black frames, `0` unplanned white flashes, `0` frozen spans `≥12f`).
- [ ] `1 fps` + cut-midpoint stills visually verified ([[Post-Completion Visual QA — What, How & Why to Fix]]).
- [ ] Audio verified at `-14.0 LUFS` / `-1.0 dBTP` with explicit `-map 0:v:0 -map 1:a:0`.
