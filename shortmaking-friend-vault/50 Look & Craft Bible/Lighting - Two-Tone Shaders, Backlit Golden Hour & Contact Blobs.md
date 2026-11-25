---
title: Lighting — Two-Tone Shaders, Backlit Golden Hour & Contact Blobs
tags:
  - look-bible
  - lighting
  - shaders
  - glsl
area: look-bible
style: 2d-in-3d-toon
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Exact GLSL two-tone shade() hook, day vs. backlit golden-hour palettes (violet-blue shadow shift), cardShade() brightness floor, and ground contact shadow blobs.
---

# Lighting — Two-Tone Shaders, Backlit Golden Hour & Contact Blobs (`shade.ts`, `lights.ts`, `cardshade.ts`)

> [!IMPORTANT] Source Code & Measured Report
> - **Implementation**: `90 Templates & Starter Kits/cartoon-3d-short-kit/bridge/shade.ts`, `lights.ts`, `cardshade.ts`
> - **Full Raw Report**: `.agents/skills/cartoon-3d-short/references/reports/lighting.md`

Standard Three.js `MeshStandardMaterial` produces muddy grey half-lambert shading that clashes with flat 2D characters. The reference shorts use a **custom two-tone cel-shaded material (`shade.ts`)** where every surface explicitly specifies its **lit colour (`uLitCol`)** and its **shadow colour (`uShadeCol`)**.

---

## 1. How `shade()` Captures Shadow Maps via `onBeforeCompile`

Instead of letting Three.js compute physically based direct + indirect lighting, `shade(mat, litHex, shadeHex)` hooks into `MeshStandardMaterial.onBeforeCompile`:
1. In `<lights_fragment_begin>`, it captures the directional sun's `NdotL` and hardware shadow-map visibility (`directLight.visible` / `getShadow()`).
2. It computes a smooth two-tone band (`sunVis = smoothstep(-0.05, 0.18, NdotL) * shadowMask`).
3. It multiplies the procedural Canvas2D texture (`diffuseColor.rgb`) by `mix(uShadeCol, uLitCol, sunVis)` plus a subtle normal-map rim relief.

---

## 2. The 4 Measured Atmosphere Presets (`lights.ts`)

| Preset | Sun Azimuth / Elevation | Sky Zenith → Horizon | Ground Lit → Shadow | Key Aesthetic Discovery |
| :--- | :--- | :--- | :--- | :--- |
| **`day` (Crisp Morning)** | `az = 135°, el = 42°` (3/4 front-side key) | `#36a3eb` → `#9ed4f0` | Grass `#6cb851` → `#38692c` (`Y_shade / Y_lit ≈ 0.50`) | Shadows preserve the exact surface hue at half luminance (`~50% Y`), never grey/black. |
| **`golden` (Backlit Sunset)** | **`az = 6–15°, el = 7–9°` (Directly ahead / backlit!)** | `#d96b27` → `#ffd27d` | Ground `#db9044` → **`#5b5173` (Violet-Blue!)** | **Crucial Law**: In golden hour, shadows are NOT dark brown—they shift strongly toward **cool violet-blue (`B/R ratio 1.35–3.0×` lit)** with warm gold rim-light on edges. |
| **`tense` (Storm / Danger)** | `az = 110°, el = 28°` | `#3d4e63` → `#7a8c9e` | Timber `#8c6d53` → `#473c4f` | Desaturated slate sky + cool purple-grey shadows before the collapse beat. |
| **`splash` (Aftermath)** | `az = 140°, el = 45°` | `#42a7eb` → `#a8dcf2` | Water `#3aa6b8` → `#1e6275` | High-contrast daylight return for the comedic punchline. |

---

## 3. Character Card Shading (`cardshade.ts`) & Contact Blobs

### A. Why Character Cards Need `cardShade()` (Never `emissiveMap`!)
- If you put a 2D character texture into `MeshStandardMaterial`, side-angled sun turns the card dark grey.
- If you put it into `emissiveMap` to keep it bright, `BloomEffect` makes the character's white eyes and shirt glow like a neon sign!
- **The Measured Solution (`cardShade.ts`)**:
  - Uses an unlit/custom shader with a **hard brightness floor (`V ≥ 0.86`)** so characters always pop against the 3D background.
  - Applies a subtle `8%` horizontal warm-to-cool gradient across the card (`vUv.x`) toward the sun's screen-space side.

### B. Ground Contact Shadow Blobs (`cast.ts`)
Because 2D vertical cards only cast thin line shadows when the sun is overhead, every character has a **multiply-blended radial gradient disc (`0.7m × 1.1m`, `#1e1924` at `alpha = 0.38`)** hovering at `y = 0.015m` directly beneath their feet (`enableNoInk` enabled). When a character jumps or falls, scaling the blob down (`scale = Math.max(0, 1 - y * 0.4)`) sells their height above the ground immediately.
