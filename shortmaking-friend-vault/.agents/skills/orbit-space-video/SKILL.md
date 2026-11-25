---
name: orbit-space-video
description: Build a 2D Space Survival & Cosmic Explainer video in the Orbit 2D style ("What Would Kill You First On [Planet/Moon]?") using the Orbit 2D Canvas kit, real NASA/JPL photos from images-api.nasa.gov, animated gauges/X-rays/receipt gags, calm narration, sound mix, sources.md, and upload.md. Trigger whenever the user asks for an Orbit-style 2D space video, "what kills you first on [planet]", or space survival story using NASA resources.
---

# Orbit 2D Space Video Workflow

Build a deterministic 2D animated space survival explainer in **1920×1080 @ 30 fps** (or 9:16 portrait when requested) using `90 Templates & Starter Kits/orbit-2d-space-kit/`.

## Step 1 — Concept & Viral Hook Framing
1. Frame a concrete **"tiny YOU vs. giant cosmic body"** survival premise (*"What Would Kill You First On [Planet/Moon]?"*).
2. Write the opening using **Rule 1 (Open on a rule, then break it)**: state a seemingly calm intuition (*"just a cold desert — deserts don't kill astronauts. That's the rule."*) then break it in sentence 3–4 with a visceral physical detail (*"Then your tongue starts to fizz."*).

## Step 2 — Script & NASA/JPL/ESA Fact-Check (`SCRIPT.md` + `sources.md`)
Enforce the **4 Orbit Script Laws**:
1. **Opens on a rule, then breaks it** (`~2.5–2.8 wps` calm, deliberate narrator delivery).
2. **Every number gets a human comparison** (e.g., `6 mbar` = `<1%` of Earth's `1,013 mbar`, water boils at body temp `37°C`; `-125°C` = colder than Antarctica; `0.64 mSv/day` = `6 chest X-rays`).
3. **A dry joke + 1 visual gag after every scary fact** (e.g., thermal receipt gag, doormat notice, one-way radio delay).
4. **`"What can you do?"` — knock every option down** one by one using real physics, ending on a dry callback punchline.

Separate **Verified NASA/JPL/ESA Facts** from **Unproven Hypotheses** in `sources.md`, and mark any unconfirmed idea on-screen as **`UNPROVEN`** or **`POSSIBLE, NOT FOUND`**.

## Step 3 — Voiceover & Word/Beat Timings (`make_voice.py` -> `beats.json`)
- Default voice system (matching *The Great Emu War*): **`edge-tts` with `en-AU-WilliamNeural` (`rate="+4%"`)**, trim silence, output `48 kHz` WAV (`voice/voice_raw.wav`), and save exact beat timestamps to `beats.json`. Optional local neural voices (`--engine kokoro --voice orbit_us|orbit_uk|fenrir|lewis`) are also available if requested.

## Step 4 — Fetch Real NASA Imagery & Stills QA (`fetch_nasa.py` + `render.js --stills`)
1. Run `python fetch_nasa.py` against `https://images-api.nasa.gov/search?q=...&media_type=image` (using `ssl._create_unverified_context()` fallback if certificate verification fails on Windows).
2. Save images to `assets/` and exact institutional credits to `assets/nasa_manifest.json`.
3. Author `scenes.js` synchronized directly to `beats.json` using all 8 scene archetypes (`orbit_establish`, `planet_compare`, `killer_card`, `surface_gauge`, `xray`, `evidence`, `magma_twist`).
4. Run `node render.js scenes.js --stills stills` and inspect `stills/sheet.jpg` visually for the **3 Orbit QA Traps**:
   - Never round sub-1% gauge values to `1%` or `0%` (`0.6%` / `<1%`).
   - Keep thermometer temperatures spaced so numerals never collide.
   - Keep upper-left counter cards well above bottom-left `NASA/JPL` photo credit tags.

## Step 5 — Space Mix (`-14 LUFS`), MP4 Render, `short_qa.py` & `upload.md`
1. Synthesize deep space ambient pad + spot SFX (`audio.py`: pre-cut whooshes 2–4 frames before cuts, spotlight impacts, gauge ticks, fizzing bubbles, rubber stamp thuds, Geiger clicks, radio pings) and normalize mix to **`-14 LUFS`** (`TP = -1.0 dBTP`).
2. Render `node render.js scenes.js --out out/video_raw.mp4`.
3. Mux with explicit mapping: `ffmpeg -y -i out/video_raw.mp4 -i audio/mix.wav -c:v copy -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 -shortest out/final.mp4`.
   - **Audio-Only Changes**: Never re-render video frames when only the voice or audio mix changes — copy the existing video stream directly (`ffmpeg -y -i out/final.mp4 -i audio/mix.wav -c:v copy -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 -shortest out/final_new.mp4`).
4. Run `short_qa.py` / FFprobe loudness + frame diff check (`0` black frames, `0` frozen spans `>=12f`) and write `upload.md` (3 viral titles, YouTube description with NASA credits, and 3 thumbnail concepts).
