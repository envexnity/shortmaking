---
title: Style 3 — Low-Poly Flat-Shaded 3D (Kaz Studio Kit)
tags:
  - engine
  - low-poly
  - threejs
  - make-3d-video
  - kaz
area: engines
style: low-poly-3d
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete engineering reference for Track 3 (make-3d-video / 3d-kaz.plugin) — building viral Low-Poly 3D Science, History, and What-If explainers with glass telemetry HUDs.
---

# Style 3 — Low-Poly Flat-Shaded 3D (`make-3d-video` / Kaz Studio Kit)

> [!NOTE] Vendored Skill & Starter Kit
> - **Skill Path**: `.agents/skills/make-3d-video/SKILL.md`
> - **API Reference**: `.agents/skills/make-3d-video/references/kit-api.md`
> - **Full Studio & 4 Examples**: `90 Templates & Starter Kits/kaz-3d-studio-kit/`

Track 3 powers the viral **Hoog / Grow With Kaz / Low-Poly 3D Explainer** aesthetic: crisp, flat-shaded geometric 3D dioramas (`MeshStandardMaterial({ flatShading: true })`), blocky characters, extruded 3D geopolitical maps, and orbital space scenes paired with a **responsive glassmorphism telemetry HUD**.

---

## 1. The `KAZ` Global API (`studio/kit.js`)

When `studio/page.html` loads your `shots.js`, `THREE` (r160) and `KAZ` are pre-loaded globally. You define `window.SHOTS = [ ... ]`, where each shot has `{ duration, hud, build(ctx) }`.

### A. Scene Presets (Pick 1 Per Shot)

| Helper | Usage & Options | Best For |
| :--- | :--- | :--- |
| `KAZ.outdoor(scene, opts)` | `{ groundColor, skyTop, skyBot, trees: 18, rocks: 8, mountains: true, clouds: 6, sunColor, time: 'day'\|'sunset'\|'night' }` | Historical battles, nature, outdoor experiments |
| `KAZ.indoor(scene, opts)` | `{ wallColor, floorColor, width: 12, depth: 12, height: 7, window: true }` | Bedrooms (`dreams`), laboratories, offices, bunkers |
| `KAZ.space(scene, opts)` | `{ stars: 800, nebulaColor: 0x3a0ca3, sunPos: [20,10,-30] }` | "What If" astronomy (`two-moons`), physics, satellites |
| `KAZ.stage(scene, opts)` | `{ color: 0x0f1117, grid: true, pedestal: true, spotColor: 0xffffff }` | Clean abstract comparisons, probability (`luck-demo`), stats |
| `KAZ.mapScene(scene, opts)` | `{ countries: ['DE','FR','PL','GB','SU'], height: 0.35, waterColor }` — returns `{ map, tint(code, hex, t), raise(code, h, t), pin(code), center(code) }` | Geopolitics, wars (`road-to-ww2`), empire expansion |

### B. Low-Poly Characters & Animations

```javascript
// Spawn a blocky low-poly character:
const guy = KAZ.person({
  shirt: KAZ.PAL.blue,
  pants: KAZ.PAL.dark,
  skin: KAZ.PAL.skin1,
  hair: KAZ.PAL.wood,
  scale: 1.0,
  hat: 'crown' | 'helmet' | 'cap' | null,
  held: 'sword' | 'flag' | 'phone' | 'torch' | null,
});
scene.add(guy);

// Spawn a crowd of N people automatically scattered:
const crowd = KAZ.crowd(24, { radius: 6, colors: [KAZ.PAL.red, KAZ.PAL.blue, KAZ.PAL.gold] });
scene.add(crowd);

// Inside update(t, u):
KAZ.walk(guy, t, { speed: 1.4, stride: 0.6 }); // Swings arms + legs + body bob
KAZ.idle(guy, t);                               // Subtle breathing + head turn
KAZ.sit(guy);                                   // Poses legs at 90 degrees for chairs/beds
KAZ.wave(guy, t);                               // Raises right arm and waves
```

### C. Props, Architecture & Space Primitives
- **Nature & City**: `KAZ.tree(opts)`, `KAZ.pine(opts)`, `KAZ.rock(opts)`, `KAZ.mountain(opts)`, `KAZ.cloud(opts)`, `KAZ.building({ w, h, d, floors, color })`, `KAZ.house(opts)`, `KAZ.car({ color })`, `KAZ.road(from, to, width)`.
- **Space**: `KAZ.planet({ radius, color, bands, rings, clouds, atmosphere })`, `KAZ.blackHole({ radius, diskColor })`, `KAZ.orbitRing(radius, color)`.
- **Data & Diagrams**: `KAZ.arrow(from, to, { color, headSize })`, `KAZ.arcArrow(from, to, { height, color })`, `KAZ.bar3d({ value, max, label, color })`, `KAZ.label3d(text, { pos, color, size })`, `KAZ.burst(pos, { count, color })`.

### D. Camera & Spring Entrance Helpers (Mandatory in Every `update(t, u)`)
```javascript
// Inside return (t, u) => { ... } where t = seconds in shot, u = 0..1 progress:
KAZ.orbit(camera, u, { center: [0, 1.5, 0], radius: 9, height: 4.5, fromAngle: -0.4, toAngle: 0.5 });
KAZ.dolly(camera, u, { from: [0, 3, 12], to: [0, 2, 6], lookAt: [0, 1.5, 0] });
KAZ.pan(camera, u, { from: [-4, 3, 8], to: [4, 3, 8], lookAt: [0, 1.2, 0] });
KAZ.flyThrough(camera, u, waypointsArray);

// Spring pop-in for props/bars (staggered by delay in seconds):
KAZ.enter(mesh, t, { delay: 0.25, duration: 0.45, from: 'scale' | 'below' | 'above' });
```

---

## 2. The Responsive Telemetry HUD (`hud` Object)

Every shot in `window.SHOTS` includes a `hud` configuration that drives the HTML/CSS glass overlay (`--u = calc(100vw / 540)`):

```javascript
{
  duration: 4.2,
  hud: {
    tl: { label: "DREAM MEMORY RETAINED", value: "5%", sub: "5 mins post-wake", accent: "#e63946" },
    tr: { status: "NOREPINEPHRINE: OFF", dot: "#2ec4b6" },
    cap: "Within five minutes of opening your eyes, <em>ninety-five percent</em> of the dream is erased.",
    cards: [
      { label: "Prefrontal Cortex", value: "Offline", color: "#f4a261" },
      { label: "Hippocampus Save Rate", value: "0.05x", color: "#e63946" }
    ]
  },
  build({ scene, camera }) {
    // 3D setup + return (t, u) => { ... }
  }
}
```

---

## 3. End-to-End Production Commands

```powershell
# 1. Align script beats to voiceover pauses via Dynamic Programming:
python studio/tools/timing.py voiceover.mp3 `
  "Five minutes after you wake up, 95% of your dream is gone." `
  "While you sleep, your brain replays memories at twenty times normal speed." `
  --json > timing.json

# 2. Preview a single shot (e.g. shot 0) fast at 540x960:
node studio/render.js --shots ./shots.js --only 0 --width 540 --height 960 --out preview_0.mp4

# 3. Render full 1080x1920 @ 30fps master with voiceover muxed:
node studio/render.js --shots ./shots.js --audio ./voiceover.mp3 --out final_lowpoly.mp4
```
