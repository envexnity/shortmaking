---
title: Video 7 Teardown — 3D Motion Graphics With Claude & Google Flow (AIpreneur)
tags:
  - teardown
  - motion-graphics
  - claude
  - google-flow
  - elevenlabs
  - capcut
  - ai-video
area: teardowns
style: motion-graphics
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Breakdown of AIpreneur's 3D Motion Graphics pipeline (youtu.be/t9MFvSJHLsI)—Claude Master Prompt + 6-second beat table, 1 anchor style image to prevent drift, Google Flow bulk image/motion generation, ElevenLabs VO, and CapCut paper-fade + text compositing.
---

# Video 7 Teardown — 3D Motion Graphics With Claude & Google Flow (`AIpreneur`)

- **Source Video**: [I Made Insane 3D Motion Graphics With Claude (Free)](https://youtu.be/t9MFvSJHLsI) (`182K+` views, `9:01`)
- **Creator**: **AIpreneur** (`@AIpreneur2176`)
- **Primary Vault Track**: [[Bonus Track - Kinetic Typography & Motion Graphics (Remotion + EffectCraft + GSAP)]] (AI-Generated Hybrid Variant)

---

## 1. The Zero-After-Effects AI Motion Graphics Stack

Instead of keyframing 3D cameras and shaders in After Effects or Remotion, AIpreneur uses **one master prompt inside a single Claude chat** to plan the entire video, then delegates rendering to **Google Flow** and final compositing to **CapCut**:

| Stage | Tool Used | What It Produces | Key Rule / Constraint |
| :--- | :--- | :--- | :--- |
| **1. Master Plan & Beat Table** (`0:47–1:52`) | **Claude** (1 chat) | Full script + **Beat Table** timing every spoken line against a **`6-second` clip** | One sentence expands into a locked clip-by-clip table so visuals never outrun or lag the narration. |
| **2. Style Lock** (`2:22`) | **Anchor Image** | **1 single reference anchor image** defining lighting, 3D material, palette, and framing | Every subsequent scene prompt references this anchor image so the 3D style never drifts across clips. |
| **3. Bulk Image Generation** (`2:38`) | **Google Flow** | Keyframe stills for every beat in bulk | **Do NOT generate text inside the images**—AI image generators mangle typography. |
| **4. Image-to-Motion** (`3:47`) | **Google Flow** | `6-second` 3D motion clips driven by per-beat motion prompts | Free tier daily credit limits spread generation over `2–3` days; paid plans finish in one sitting. |
| **5. Voiceover** (`5:18`) | **ElevenLabs** (Free tier) | Narration formatted by Claude for natural pacing/pauses | Claude formats punctuation/breaks before pasting into ElevenLabs. |
| **6. Final Composite & Text** (`6:25`) | **CapCut Desktop** | **Paper-fade transitions** (never fade to black) + crisp **kinetic text overlays** | Text is added cleanly in the editor on top of the 3D motion plates. |

---

## 2. Three High-Leverage Rules Worth Stealing for Any Track

1. **The Anchor-Image Anti-Drift Rule**: Never prompt 10 scenes independently in an AI generator. Generate **one hero anchor frame** first, lock its palette/material/lens language, and condition every following beat on it.
2. **Never Bake Text Into AI Image/Video Generators**: Keep generated 3D plates completely clean of typography. Add all titles, callouts, and captions in **Remotion (`remotion-captions`)**, **EffectCraft**, or **CapCut** where kerning, 9:16 safe zones, and contrast strokes are 100% deterministic.
3. **Fade Into Paper/Texture — Never Fade to Black**: Hard black dips between scenes feel like a broken render on mobile feeds and trigger swipe-aways; use textured paper/light transitions or crisp cuts.

---

## 3. When to Use This Workflow vs. Code-Driven Engines

- **Use Claude + Google Flow + CapCut/Remotion** when you want **cinematic, painterly, or photoreal 3D motion-graphics B-roll** without building custom Three.js/Blender geometry.
- **Use Code-Driven [[Bonus Track - Kinetic Typography & Motion Graphics (Remotion + EffectCraft + GSAP)|Remotion / EffectCraft / GSAP]]** (or Track 1–3) when you need **exact data charts, frame-accurate word sync (`words.json`), zero-drift recurring characters, or deterministic re-renders** in one pass without daily credit limits.
- **Post-Completion Rule**: Regardless of whether clips come from Google Flow or Three.js, run [[Post-Completion Visual QA — What, How & Why to Fix]] on the final exported `.mp4` to catch AI morphing artifacts, text safe-zone collisions, or audio-beat drift.
