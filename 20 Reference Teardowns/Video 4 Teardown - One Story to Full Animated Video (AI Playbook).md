---
title: Video 4 Teardown — One Story to Full Animated Video (AI Playbook)
tags:
  - teardown
  - ai-playbook
  - cartoon-audio-short
  - playwright
  - threejs
area: teardowns
style: 2d-in-3d-toon
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete technical breakdown of AI Playbook's standalone Playwright + Three.js pipeline (youtu.be/W3q1_MpWkok) building the 1918 WWI Pigeon and Hachiko (10 Years at Shibuya) shorts.
---

# Video 4 Teardown — I Gave Claude AI One Story… It Created an Entire Video! (AI Playbook)

- **Creator**: **AI Playbook** (`@AIPlaybook-b5c`)
- **Video URL**: [https://youtu.be/W3q1_MpWkok](https://youtu.be/W3q1_MpWkok)
- **Kit Unpacked & Vendored**: `cartoon-short-kit.zip` + `SKILL.md` → `.agents/skills/cartoon-audio-short/` (and `90 Templates & Starter Kits/cartoon-audio-short-kit/`)
- **Demo Shorts Built in Video**:
  1. **1918 WWI Carrier Pigeon (*Cher Ami*)**: The pigeon that flew 25 miles through German artillery fire in October 1918, blinded in one eye and missing a leg, to save 194 trapped American soldiers (*The Lost Battalion*).
  2. **Hachiko (*The Dog Who Waited 10 Years*)**: In 1925 Tokyo, Professor Ueno dies at work; his Akita dog Hachiko walks to Shibuya Station at `4:00 PM` every single day for nearly 10 years until his own death in 1935.
  3. **Bundled Kit Worked Example (`example/soldier/`)**: *In 212 BC, a Roman soldier killed Archimedes over a sand drawing.*

---

## 1. Architectural Breakthrough: Why `cartoon-audio-short` Drops Remotion

While Mr omi's `cartoon-3d-short` uses **Remotion + React Three Fiber**, AI Playbook and mr miro's standalone kit (`cartoon-audio-short`) strips out React, Remotion, and Webpack entirely in favor of a **pure ES-module Three.js engine driven by a 70-line Playwright script (`tools/render.mjs`)**.

### Remotion (`cartoon-3d-short`) vs. Standalone Playwright (`cartoon-audio-short`)

| Feature | `cartoon-3d-short` (Remotion + R3F) | `cartoon-audio-short` (Standalone Playwright) |
| :--- | :--- | :--- |
| **Build / Bundle Step** | Webpack bundle per render (`~1.9 GB` temp dir) | **Zero build step** (loads ES modules via local HTTP server) |
| **Scene Authoring** | `Bridge.tsx`, `world.ts`, `story.ts`, `toon.ts` (TypeScript) | Single **`story.js`** file (`export const DURATION`, `buildWorld`, `update`) |
| **Headless GPU Fallback** | Requires WebGL angle/GPU flags | Built-in **SwiftShader CPU WebGL** (`--enable-unsafe-swiftshader`) — runs on any machine or cloud VM without a GPU |
| **Word Timing Tool** | External Whisper JSON | Built-in **`tools/timing.py`** (`faster-whisper` fuzzy DP match to script text) |
| **Contact Sheet Tool** | `scripts/sbs_sheet.py` | Built-in **`tools/sheet.py`** (extracts 1fps + cut frames into `stills.jpg`) |
| **Best Use Case** | Multi-agent 4-sandbox look-match with complex React overlays | **Fast single-agent story-to-MP4 builds** where you only edit `story.js` and `audio.py` |

---

## 2. The 4-Stage Intake-to-MP4 Pipeline (`cartoon-audio-short`)

### Stage 0: First-Run Setup (`bash tools/setup.sh`)
Installs Three.js, Postprocessing, Playwright Chromium, `faster-whisper`, `scipy`, `numpy`, and `pillow`, then pre-downloads the `tiny.en` Whisper model (`~75 MB`) so timing runs offline in `<5 seconds`.

### Stage 1: Intake & Script Approval
- When the user provides a topic (e.g., *"The dog who waited 10 years at Shibuya station"*) without a voiceover:
  1. The agent writes a **45–55s script (~165 words at `3.7 wps`)** following the 6-part structure:
     - **Hook**: *"In 1925, a dog walked to a Tokyo train station at four PM—and didn't leave for ten years."*
     - **`Luckily / Unluckily`**: *"Luckily, the station master fed him yakitori scraps. Unluckily, the 4:00 PM express never brought the professor back."*
     - **`"You see,"` Pivot**: *"You see, dogs don't track time with calendars—they track it by the fading scent of the person who left..."*
     - **Callback Twist**: *"And today, the busiest meeting spot in Tokyo isn't a landmark—it's a bronze statue of a dog still waiting for the four o'clock train."*
  2. The user records/generates `voice.mp3` in ElevenLabs (`10–15%` faster energetic delivery) and drops it in the project folder.

### Stage 2: Exact Word Alignment (`tools/timing.py`)
Running `python tools/timing.py voice.mp3 story.txt words.json` outputs every spoken word's exact start and end time:
```json
[
  {"word": "In", "start": 0.08, "end": 0.20},
  {"word": "1925,", "start": 0.20, "end": 0.72},
  {"word": "a", "start": 0.72, "end": 0.80},
  {"word": "dog", "start": 0.80, "end": 1.12}
]
```
Every shot cut (`SHOTS`), eyebrow/mouth swap (`2f` before word onset), and SFX trigger in `audio.py` is hardcoded to these exact timestamps—**never estimated by word count**.

### Stage 3: Building `story.js` & `audio.py`
The engine (`engine/main.js`, `engine/roman.js`, `engine/paint.js`, `engine/motion.js`) stays completely untouched. For a new video, the agent writes **only two files**:
1. **`story.js`**:
   - Imports `shade`, `cardShade`, `enableNoInk`, `make sky/water/stone/planks` from `./engine/paint.js`, `Pen`, `drawChar`, `makeCharCard` from `./engine/roman.js`, and `cut/glide/push/kick` from `./engine/motion.js`.
   - Defines `SHOTS` (timestamped to `words.json`), builds distinct 3D zones (`buildWorld(scene)`), and animates camera + character mouths/blinks/props in `update(f, t)`.
2. **`audio.py`**:
   - Synthesizes background score + timestamped sound effects (train chugs, station bell, rain pattering, footsteps on wet stone) and mixes them at **`-6 dB` gated RMS** under `voice.mp3`.

### Stage 4: Render, Contact Sheet Inspection & Explicit Mux
```bash
# 1. Render silent video at 30fps
node tools/render.mjs engine/index.html out/video.mp4 52.8

# 2. Build contact sheet (1fps + cut midpoints) & inspect visually!
python tools/sheet.py out/video.mp4 out/stills.jpg 5.0,11.2,17.8,24.4,31.0,38.5,45.2

# 3. Synthesize SFX/music & mux with explicit stream mapping
python audio.py
bash tools/finish.sh out/video.mp4 out/mix.wav out/final.mp4
```

---

## 3. Related Vault Notes
- [[Style 2 - Standalone 2D-in-3D Kit (Playwright + Three.js, No Remotion)]]
- [[01 Voiceover & Word-Level Timing (ElevenLabs + Whisper + DP)]]
- [[Procedural Python Audio Synthesis (Music & SFX)]]
