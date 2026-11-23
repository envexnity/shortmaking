---
title: Depth & Post — Thin-Lens DOF, Sky Gradients & Mipmap Bloom
tags:
  - look-bible
  - dof
  - bloom
  - postprocessing
  - shaders
area: look-bible
style: 2d-in-3d-toon
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Exact measured parameters for LensBlurEffect (32-tap Poisson thin-lens DOF), sky dome vertical gradients, atmospheric fog, and mipmap bloom.
---

# Depth & Post — Thin-Lens DOF, Sky Gradients & Mipmap Bloom (`lensblur.ts`)

> [!IMPORTANT] Source Code & Measured Report
> - **Implementation**: `90 Templates & Starter Kits/cartoon-3d-short-kit/bridge/lensblur.ts`
> - **Full Raw Report**: `.agents/skills/cartoon-3d-short/references/reports/depth.md`

Depth separation is what makes the 2D character card feel like a miniature toy standing inside a cinematic 3D film set rather than a sticker pasted on a flat wallpaper.

---

## 1. Thin-Lens Circle-of-Confusion (`LensBlurEffect` in `lensblur.ts`)

Default Three.js `BokehPass` produces harsh ringing artifacts around 2D alpha-cutout character cards. `lensblur.ts` implements a custom **32-tap golden-angle spiral Poisson disc gather** with bilateral foreground bleed:

$$\text{CoC}(z) = c_{\infty} \cdot \text{clamp}\left(\frac{|z - d_{\text{focus}}| - r_{\text{focus}}}{d_{\text{span}}},\ 0,\ 1\right)$$

### Measured DOF Settings by Shot Type (at 1080p)

| Shot Framing | Focus Distance (`focusDist`) | In-Focus Span (`focusRange`) | Max Blur Radius (`cInf` / `maxCoc`) | Visual Effect |
| :--- | :--- | :--- | :--- | :--- |
| **Establishing Wide (`WS`)** | `18.0 – 35.0 m` | `25.0 m` | **`0.0 – 2.0 px`** | Everything crisp so the viewer reads the geography/bridge scale. |
| **Medium Two-Shot (`MS`)** | `4.5 – 7.5 m` (on speaker) | `2.2 m` | **`10.0 – 13.0 px`** | Background buildings & trees melt into soft painted shapes; `InkPass` lines blur softly. |
| **Hero Close-Up / Insert (`CU`)** | **`2.2 – 3.8 m` (locked to eyes/prop)** | **`1.1 m`** | **`14.0 – 16.0 px`** | Strong miniature tilt-shift feel; foreground framing props (`1.5m` away) also blur softly. |

---

## 2. Sky Dome, Fluffy 3D Clouds & Horizon Fog

1. **Painted Sky Dome (`skyTex` in `paint.ts`, `NOINK = 3`, `fog: false`)**:
   - Uses a power-curve vertical gradient (`pow(t, 0.65)`) from zenith `#36a3eb` to horizon `#9ed4f0` so the bottom third behind the silhouettes is bright and airy.
2. **Horizon-Matched Linear Fog (`THREE.Fog`)**:
   - `scene.fog = new THREE.Fog(horizonHex, 25, 300)` (day) or `new THREE.Fog(0xffb86c, 18, 220)` (golden hour).
   - **Rule**: The fog colour MUST match the sky dome's horizon colour (`vUv.y ≈ 0.52`), erasing the hard seam where the ground plane ends.
3. **Puffy Cloud Cards (`cloudHD` in `paint.ts`, `NOINK = 3`)**:
   - Flat-bottomed, cream-lit (`#ffffff`) with warm lavender-grey bellies (`#c8d4e3` day / `#d9825b` sunset), placed at `y = 28–55m, z = -90..-160m`.

---

## 3. Mipmap Bloom & Neutral Tone Mapping

- **Bloom (`BloomEffect`)**: `luminanceThreshold = 1.0`, `luminanceSmoothing = 0.25`, `intensity = 0.5`, `mipmapBlur = true`, `levels = 6`, `radius = 0.6`. Because `threshold = 1.0`, only true HDR highlights (the sun disc, water specular glints, lantern flames, and golden-hour rim edges) bloom—never character faces.
- **Tone Mapping (`ToneMappingMode.NEUTRAL`)**: Always set `renderer.toneMapping = THREE.NoToneMapping` and let the postprocessing `ToneMappingEffect({ mode: ToneMappingMode.NEUTRAL })` handle HDR roll-off directly before `GradeEffect`.
