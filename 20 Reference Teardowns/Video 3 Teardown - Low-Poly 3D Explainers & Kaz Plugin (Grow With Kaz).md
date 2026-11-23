---
title: Video 3 Teardown — Low-Poly 3D Explainers & Kaz Plugin (Grow With Kaz)
tags:
  - teardown
  - kaz
  - make-3d-video
  - low-poly
  - threejs
area: teardowns
style: low-poly-3d
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete technical breakdown of Grow With Kaz's 3-niche Low-Poly 3D explainer workflow and the 3d-kaz.plugin (make-3d-video) engine (youtu.be/46C6qLvTjnU).
---

# Video 3 Teardown — Viral Low-Poly 3D Animation Videos Using Claude (Grow With Kaz)

- **Creator**: **Grow With Kaz** (`@GrowWithKaz`)
- **Video URL**: [https://youtu.be/46C6qLvTjnU](https://youtu.be/46C6qLvTjnU)
- **Plugin Unpacked & Vendored**: `3d-kaz.plugin` → `.agents/skills/make-3d-video/` (and `90 Templates & Starter Kits/kaz-3d-studio-kit/`)
- **Demo Shorts Built in Video**:
  1. **Science**: *"Why You Forget 95% of Your Dreams Within 5 Minutes of Waking Up"* (`examples/dreams/shots.js`)
  2. **History**: *"How One Wrong Turn in 1914 Triggered Both World Wars"* (`examples/road-to-ww2/shots.js`)
  3. **What-If**: *"What If Earth Suddenly Had Two Moons?"* (`examples/two-moons/shots.js`)
  4. **Math / Probability**: *"Why Your Friends Always Have More Friends Than You (The Friendship Paradox / Luck Demo)"* (`examples/luck-demo/shots.js`)

---

## 1. The 3 High-CPM Faceless 3D Niches

Kaz identifies three evergreen niches where **Low-Poly Flat-Shaded 3D + Telemetry HUD Overlays** consistently outperform 2D stock footage:

| Niche | Visual Archetype in `KAZ` Kit | Example Hook | Why Low-Poly 3D Wins |
| :--- | :--- | :--- | :--- |
| **1. Science & Body/Brain** | `KAZ.indoor`, `KAZ.person`, `KAZ.sit`, glowing neural/chemical particles, HUD retention decay bar (`100% → 5%`) | *"Five minutes after you open your eyes, ninety-five percent of your dream is gone."* | Lets the camera dolly inside a bedroom, orbit a glowing prefrontal cortex, and display live neurotransmitter status (`Norepinephrine: OFF`) in the glass HUD. |
| **2. History & Geopolitics** | `KAZ.mapScene` (extruded 3D country polygons with borders, labels, and `KAZ.arrow` troop vectors) + low-poly props | *"In 1914, a driver took one wrong turn in Sarajevo—and sixty million people died."* | Replaces flat 2D map animations with physical 3D extruded territories (`map.tint('DE', KAZ.PAL.red, t)`), rising domino blocks, and troop arrows. |
| **3. "What If" Space & Planet Scale** | `KAZ.space`, `KAZ.planet`, `KAZ.blackHole`, `KAZ.orbitRing`, tidal water shells, volcanic debris | *"If a second moon appeared in our sky tonight, the first thing to go would be the coastlines."* | Gives full 3D orbital mechanics, dual moonlighting, rising ocean shells (`scale.set`), and real-time HUD telemetry (`TIDE HEIGHT: +420m`). |

---

## 2. Inside the `3d-kaz.plugin` (`make-3d-video`) Architecture

Unlike Remotion (which bundles React + Webpack on every render), Kaz's engine is a **zero-build Three.js r160 studio** driven by Playwright headless Chromium:

```text
.agents/skills/make-3d-video/
├── SKILL.md                        # Orchestrator instructions
├── references/
│   ├── kit-api.md                  # Full KAZ.* API reference
│   └── style-and-planning.md       # Pacing, camera, and HUD rules
└── studio/
    ├── kit.js                      # Global KAZ helper library (scenes, characters, maps, camera, HUD)
    ├── page.html                   # Portrait 9:16 HTML5 canvas + CSS glass HUD (--u = calc(100vw/540))
    ├── render.js                   # Deterministic frame stepper (__renderFrame(t)) -> FFmpeg MP4
    ├── tools/
    │   └── timing.py               # Audio silence DP beat timer (~2.6 words/s default)
    └── examples/
        ├── dreams/shots.js         # 12-beat Science short
        ├── road-to-ww2/shots.js    # 12-beat History extruded map short
        ├── two-moons/shots.js      # 12-beat Space/What-If short
        └── luck-demo/shots.js      # Probability explainer short
```

### How Deterministic Frame Rendering Works (`studio/render.js`)
1. `render.js` launches headless Chromium via Playwright at `1080×1920` (or `540×960` preview) with `--use-gl=angle`.
2. It injects the user's `shots.js` into `page.html`, which exposes `window.__renderFrame(t)`.
3. For every frame `f = 0 .. totalFrames - 1`, it calls `window.__renderFrame(f / 30)`, captures the JPEG/PNG buffer (`quality: 92`), and pipes raw frames directly into `ffmpeg -f image2pipe -framerate 30 ... -c:v libx264 -pix_fmt yuv420p`.
4. If `--audio voiceover.mp3` is provided, it automatically muxes the AAC audio stream in a single command.

---

## 3. How `timing.py` Aligns Shots Without Whisper

While `cartoon-audio-short` uses `faster-whisper` for word-level timestamps, `make-3d-video` includes a lightweight **Dynamic Programming (DP) silence-matching script** (`studio/tools/timing.py`):
1. Decodes the MP3 via `ffmpeg` at `16 kHz` mono PCM and computes short-time RMS energy in `20ms` windows.
2. Detects all natural speech pauses (`RMS < 18%` of median energy for `≥120ms`).
3. Estimates each beat's expected duration from its word share (`words_i / total_words × audio_duration`).
4. Runs **Dynamic Programming** to snap each beat boundary to the nearest natural pause in the voiceover, subtracting a `0.12s` transition pad so visual cuts land cleanly inside the breath between sentences.

---

## 4. Model Comparison from Video 3: Opus 4.6 vs. Fable / Sonnet

In the video (`08:45`), Kaz compares running `make-3d-video` across Claude model tiers:
- **Opus (High Effort)**: Best spatial reasoning when placing multi-part low-poly assemblies (e.g., aligning the Sarajevo open-top car on the street intersection in `road-to-ww2/shots.js` without buildings clipping into the road).
- **Sonnet**: Fast for tweaking HUD labels, colour palettes (`KAZ.PAL`), or camera speeds (`KAZ.orbit`), but occasionally stacks 3D labels on top of each other unless prompted with explicit `[x, y, z]` offsets.

---

## 5. Related Vault Notes
- [[Style 3 - Low-Poly Flat-Shaded 3D (Kaz Studio Kit)]]
- [[01 Voiceover & Word-Level Timing (ElevenLabs + Whisper + DP)]]
- [[50 Plug-and-Play Viral Video Ideas (All Styles)]]
