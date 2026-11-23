---
title: Style 2 — Standalone 2D-in-3D Kit (Playwright + Three.js, No Remotion)
tags:
  - engine
  - playwright
  - threejs
  - cartoon-audio-short
  - 2d-in-3d
area: engines
style: 2d-in-3d-toon
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete guide to the zero-React, zero-Webpack Playwright + Three.js 2D-in-3D engine (cartoon-audio-short) used by AI Playbook and mr miro.
---

# Style 2 — Standalone 2D-in-3D Kit (`cartoon-audio-short` — Playwright + Three.js)

> [!NOTE] Vendored Skill & Starter Kit
> - **Skill Path**: `.agents/skills/cartoon-audio-short/SKILL.md`
> - **Full Starter Code**: `90 Templates & Starter Kits/cartoon-audio-short-kit/`

When you want the exact **2D-in-3D Toon look** of Track 1 **without React, Remotion, TypeScript compilation, or 1.9 GB webpack temp bundles**, use Track 2 (`cartoon-audio-short`). It renders directly from a plain ES-module HTML page (`engine/index.html`) via headless Playwright Chromium (with built-in SwiftShader CPU WebGL fallback) and pipes PNG frames straight into FFmpeg.

---

## 1. Directory Layout & Frozen Engine Rule

```text
cartoon-audio-short-kit/
├── engine/                  # FROZEN ENGINE — DO NOT EDIT PER VIDEO
│   ├── index.html           # Loads Three.js + Postprocessing + ../story.js
│   ├── main.js              # Renderer, InkPass, LensBlur, Bloom, Grade & window.__step(f)
│   ├── roman.js             # Pen API, superellipse bean heads, drawChar(), makeCharCard()
│   ├── paint.js             # shade(), cardShade(), enableNoInk(), procedural Canvas2D textures
│   └── motion.js            # smootherstep(), cut(), glide(), push(), kick(), walkPose()
├── tools/                   # CLI PIPELINE TOOLS
│   ├── setup.sh             # One-time npm + pip + Playwright + Whisper tiny.en installer
│   ├── timing.py            # faster-whisper word-level timestamp extractor -> words.json
│   ├── render.mjs           # Headless Chromium frame stepper -> H.264 MP4
│   ├── sheet.py             # Extracts 1fps + cut midpoints -> stills.jpg contact sheet
│   └── finish.sh            # Explicit -map 0:v:0 -map 1:a:0 FFmpeg muxer
├── example/soldier/         # Worked Reference: Archimedes & The Roman Soldier (212 BC)
│   ├── story.js             # Complete 3D world, shots, and acting
│   ├── audio.py             # Complete procedural score + SFX + -6dB gated mixer
│   └── stills.jpg           # Verified contact sheet
├── story.js                 # <-- WRITE THIS FILE FOR YOUR NEW VIDEO
└── audio.py                 # <-- WRITE THIS FILE FOR YOUR NEW VIDEO
```

---

## 2. How `story.js` Works (Complete Contract)

`engine/main.js` imports three exports from `../story.js`:
1. `export const DURATION = <seconds>;` (matched to `voice.mp3` length + `0.4s` tail)
2. `export function buildWorld(scene, camera, env) { ... }` (called once at frame 0)
3. `export function update(f, t, state) { ... }` (called on every frame `f` at `30 fps`, where `t = f / 30`)

### Minimal `story.js` Skeleton
```javascript
import * as THREE from 'three';
import { shade, cardShade, enableNoInk, planksHD, stoneHD, grassHD } from './engine/paint.js';
import { makeCharCard, updateCharCard } from './engine/roman.js';
import { glide, push, kick, walkCycle } from './engine/motion.js';

export const DURATION = 48.5; // exact duration from words.json

// Shot table synced to words.json timestamps (t * 30 = frame)
export const SHOTS = [
  { s: 0,   e: 114, cam: { p: [0, 2.1, 7.5], l: [0, 1.4, 0], fov: 38 }, dof: [7.5, 12], preset: 'day' },
  { s: 114, e: 240, cam: { p: [-1.8, 1.65, 4.2], l: [-0.4, 1.45, 0], fov: 32 }, dof: [4.2, 15], preset: 'day' },
  // ...
];

export function buildWorld(scene, camera, env) {
  // 1. Ground & architecture using shade() + procedural Canvas2D textures
  const groundMat = shade(new THREE.MeshStandardMaterial({ map: stoneHD() }), 0xd8c39e, 0x8c7355);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(120, 120), groundMat);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  // 2. 2D-in-3D Character Cards (enableNoInk is automatically applied inside makeCharCard)
  const hero = makeCharCard({
    shirt: '#b83a2e',
    skin: '#f2ccb0',
    hat: 'helmet',
    prop: 'sword',
  });
  hero.group.position.set(-0.4, 0, 0);
  scene.add(hero.group);

  return { hero };
}

export function update(f, t, { scene, camera, setLightPreset, setDOF, world }) {
  // 1. Find active shot & apply mandatory camera hold creep (push)
  const shot = SHOTS.find(sh => f >= sh.s && f < sh.e) || SHOTS[SHOTS.length - 1];
  const u = (f - shot.s) / Math.max(1, shot.e - shot.s);
  setLightPreset(shot.preset);
  setDOF(shot.dof[0], shot.dof[1]);

  // Mandatory 0.25%/frame push so no hold is ever static:
  push(camera, shot.cam, u, 0.0025);

  // 2. Update character pose, 4-frame blinks & 2-frame lead expressions
  updateCharCard(world.hero, f, {
    brows: t > 3.72 ? 'v' : 'neutral', // 2 frames (0.067s) before punch word at 3.79s!
    eyes: 'lidded',
    mouth: (Math.sin(t * 62) > 0.1) ? 'open' : 'line',
    walk: t < 3.5 ? walkCycle(f, 0.12) : 0,
  });
}
```

---

## 3. Why `tools/render.mjs` Works Everywhere (Even Without a GPU)

`tools/render.mjs` spins up a tiny local static file server and launches Chromium with:
```javascript
const browser = await chromium.launch({
  args: [
    '--use-gl=angle',
    '--use-angle=swiftshader',
    '--enable-unsafe-swiftshader',
    '--ignore-gpu-blocklist',
  ],
});
```
This guarantees WebGL2 + float framebuffers (`HalfFloatType`) render identically on Windows laptops, headless Linux servers, and Docker containers.

---

## 4. Mandatory Visual Inspection Loop (`stills.jpg`)

Never mux final audio before checking `stills.jpg`:
```powershell
# Render video
node tools/render.mjs engine/index.html out/video.mp4 48.5

# Generate contact sheet with 1 frame/sec + all shot cut midpoints
python tools/sheet.py out/video.mp4 out/stills.jpg 3.8,8.0,13.5,19.2,25.0,32.4,40.1
```
Open `out/stills.jpg` with `read_file` and verify:
- Are any character heads or hands clipped by the frame edge or props?
- Are any transparent cards outlined by a black box (forgot `enableNoInk`)?
- Does every shot have a distinct silhouette and clear focal point?
Only after passing inspection, run `python audio.py` and `bash tools/finish.sh out/video.mp4 out/mix.wav out/final.mp4`.
