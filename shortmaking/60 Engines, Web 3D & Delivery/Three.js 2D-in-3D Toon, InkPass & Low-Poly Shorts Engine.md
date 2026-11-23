---
title: Three.js 2D-in-3D Toon, InkPass & Low-Poly Shorts Engine
tags: [threejs, shortmaking, toon, inkpass, low-poly, remotion, playwright, shaders]
updated: 2026-11-20
---

# Three.js 2D-in-3D Toon, InkPass & Low-Poly Shorts Engine

Direct engineering bridge carrying the **Shortmaking Studio Vault's** battle-tested Three.js animation engines (measured across 32,000 viral frames) into **`3D-Master-Vault`**!

> [!TIP]
> Cross-reference full viral pacing, voiceover timing, and 12-agent look-match specs via `obsidian` MCP (`vault: "shortmaking"`): see [[Shortmaking Vault Bridge (Viral Animated Shorts Pipeline)]].

---

## 1. Engine A: 2D-in-3D Toon World (`cartoon-3d-short` & `cartoon-audio-short`)

Powers *Nutshell Animations / Mr Omi / mr miro* style 2D plum-inked character cards living inside 3D inked environments rendered via **Remotion 4 + Three.js** or **Playwright + Three.js**:

### The 5 Mandatory Three.js Shader & Render Laws
1. **Screen-Space Depth + Normal `InkPass` BEFORE `LensBlurEffect`:**
   - Render world edges in a dedicated `postprocessing` `Pass` (`ink.ts`) comparing depth + view-normal discontinuities (line weight scaling from `5.1 px` foreground → `2.2 px` background).
   - ALWAYS place `InkPass` **before** Depth of Field so distant ink outlines blur optically with the lens!
2. **`NOINK = 3` Layer Mask:**
   - Enable `obj.layers.enable(3)` (`NOINK`) on EVERY 2D character billboard card, sky dome, cloud card, smoke puff, text sign, and water sheet so `InkPass` never draws ugly rectangular borders around transparent quads!
3. **Two-Tone `shade()` Injection (`onBeforeCompile`):**
   - Replace default smooth PBR roll-off on 3D world props by capturing `sunVis` (shadow-map visibility) in `onBeforeCompile` and mixing explicit `uShadeCol` (violet-blue shifted in golden hour: `B/R ratio 1.35–3.0×`) and `uLitCol`!
4. **Character Card Shader (`cardShade()`, Floor `V ≥ 0.86`):**
   - Never use `emissiveMap` on 2D character cards (triggers unwanted bloom halos!). Use custom `cardShade()` with brightness floor `0.86`, `600×1000` Canvas2D textures (`#241726` plum ink, `3.5` head-heights), and a multiply-blended ground **contact shadow blob** (`0.7 × 1.1 m`) under every character's soles!
5. **Deterministic Motion & Impact Grammar:**
   - Never hold a static camera (`push(cam, 0.0015..0.0035)` per frame; `0.006/f` on punch words).
   - `7-frame` alternating-sign `KICKS` (`dy` + roll `da`) on impacts; `18–40f` smootherstep glides inside beats.

---

## 2. Engine B: Low-Poly Flat-Shaded 3D Explainer (`make-3d-video` / KAZ Studio)

Powers *Grow With Kaz / Hoog* science, history, and what-if 3D explainers in Three.js:
- **Flat-shaded procedural/Blender GLB meshes** (`flatShading: true`, vibrant palette colors from [[Style 10 — Low-Poly Flat-Shaded & Faceted (Monument Valley - Firewatch)]]).
- **Continuous Dual Motion:** Every shot moves BOTH the camera (`KAZ.orbit`, `KAZ.dolly`, `KAZ.pan`, `KAZ.flyThrough`) AND the 3D subject (staggered spring `KAZ.enter()`, subtle bob/rotation).
- **Deterministic Frame Capture:** Step `window.__setFrame(f)` cleanly via Playwright OR inspect/capture live frames via **`threejs-devtools` MCP (`capture_frames` + `take_screenshot`)**, then mux with explicit FFmpeg audio mapping (`-map 0:v:0 -map 1:a:0`)!

---

## 3. Upgrading Shortmaking Three.js Scenes with `3D-Master-Vault`
- Replace raw primitive Three.js boxes/spheres with **Blender 5.3 + TextureCraft exported `.glb` hero props** (passing `mesh_qa.py --profile web-prop`).
- Use **`threejs-devtools` MCP** (`set_camera`, `set_light`, `set_uniform`, `annotated_screenshot`, `draw_call_breakdown`) to visually debug framing, `NOINK` layers (`layer_details`), and ink shaders live without slow full-video re-renders!

## Related Notes
- [[Shortmaking Vault Bridge (Viral Animated Shorts Pipeline)]]
- [[Three.js Complete Master Guide — Scenes, Loaders, Post-Processing & MCP]]
- [[Style 07 — 2D-in-3D Grease Pencil & Comic Ink (Ligne Claire - Manga)]]
- [[Style 10 — Low-Poly Flat-Shaded & Faceted (Monument Valley - Firewatch)]]
