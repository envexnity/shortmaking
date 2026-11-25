---
title: Outlines — Screen-Space Depth & Normal InkPass
tags:
  - look-bible
  - shaders
  - outlines
  - glsl
  - postprocessing
area: look-bible
style: 2d-in-3d-toon
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete GLSL architecture for InkPass (ink.ts) — Sobel log-depth + view-normal edge detection, distance-scaled stroke widths (5.1px to 2.2px), and the mandatory NOINK=3 layer mask.
---

# Outlines — Screen-Space Depth & Normal `InkPass` (`ink.ts`)

> [!IMPORTANT] Source Code & Measured Report
> - **Implementation**: `90 Templates & Starter Kits/cartoon-3d-short-kit/bridge/ink.ts`
> - **Full Raw Report**: `.agents/skills/cartoon-3d-short/references/reports/outlines.md`

To make a 3D Three.js world look hand-drawn in the same universe as the 2D character cards, every 3D building, bridge timber, crate, and cliff edge receives a **screen-space ink outline** whose thickness tapers smoothly with camera distance.

---

## 1. Measured World Outline Widths at 1080p

| Camera Distance (`z_view`) | Measured Stroke Width (`1080×1920`) | Visual Role |
| :--- | :--- | :--- |
| **Foreground (`3–6 m`)** | **`3.4 – 5.1 px`** | Hero props, bridge railings, foreground framing barrels |
| **Midground (`12–25 m`)** | **`2.8 – 3.8 px`** | Buildings, towers, trees, riverbanks |
| **Background (`50–90 m`)** | **`2.2 – 3.3 px`** (softened further by DOF) | Distant hills, horizon structures |

- **Ink Colour**: `#030303` to `#0b0a0c` at `inkStr = 0.88` opacity, blended in **display gamma** (`mix(sceneCol, inkCol, edge * inkStr)`).

---

## 2. The Two Non-Negotiable Architecture Rules

### Rule 1: `InkPass` MUST Be a Standalone `Pass` Before `LensBlurEffect`
If you implement outlines as a `postprocessing` `Effect` merged into the same `EffectPass` as `LensBlurEffect`, the DOF blur runs *before* or *simultaneously with* the outline shader, either erasing edges or drawing razor-sharp black lines over blurry background bokeh.
- **Fix**: `InkPass` extends `Pass`, renders an internal Normal+Depth target (`normalPass`), applies the Sobel edge shader to `inputBuffer → outputBuffer`, and hands that inked image to `EffectPass(lensBlur, bloom, toneMapping, grade)`.

### Rule 2: The `NOINK = 3` Layer Mask
2D character billboards are rectangular `PlaneGeometry` meshes with transparent alpha around the character. If the depth-edge pass sees the rectangle, it draws a giant black box around every character!
- **Fix**: Every non-outlined object calls `enableNoInk(obj)` (which enables Three.js layer `NOINK = 3` recursively). Before `InkPass` renders its internal depth/normal buffer, it traverses the scene and temporarily sets `obj.visible = false` for any mesh on layer `NOINK = 3` (character cards, sky dome, clouds, water ripple sheets, smoke puffs, and painted sign faces).

```typescript
export const NOINK = 3;
export function enableNoInk(root: THREE.Object3D) {
  root.traverse((o) => o.layers.enable(NOINK));
}
```

---

## 3. Core GLSL Edge Detector (`ink.ts`)

`InkPass` combines **grazing-angle-compensated log-depth Sobel** (for silhouette edges) with **view-space normal Sobel** (for interior creases like plank steps and stone corners):

```glsl
// Distance-scaled sample radius (in texels):
float d0 = viewZ(vUv); // linear view depth in meters
float distScale = clamp(1.45 - 0.55 * smoothstep(5.0, 75.0, d0), 0.72, 1.45);
vec2 stepUv = (uTexel * 1.35 * distScale);

// 3x3 Sobel on log(depth), weighted by N.V so flat ground planes don't self-ink at grazing angles:
float grazing = clamp(abs(n0.z), 0.18, 1.0);
float depthEdge = smoothstep(0.022 / grazing, 0.058 / grazing, gradDepth);

// 3x3 Sobel on view-space normals (creases between faces > ~38 degrees):
float normEdge = smoothstep(0.55, 0.95, gradNormal) * smoothstep(70.0, 15.0, d0);

float edge = max(depthEdge, normEdge * 0.78);
gl_FragColor = vec4(mix(base.rgb, uInkCol, edge * uInkStr), base.a);
```
