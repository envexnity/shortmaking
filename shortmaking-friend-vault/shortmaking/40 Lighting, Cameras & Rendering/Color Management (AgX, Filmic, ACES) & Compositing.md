---
title: Color Management (AgX, Filmic, ACES) & Compositing
tags: [color-management, agx, aces, compositing, effectcraft, rendering]
updated: 2026-11-20
---

# Color Management (AgX, Filmic, ACES) & Compositing

---

## 1. Choosing the Right View Transform (Blender 5.3)

| View Transform | When to Use | Look Presets |
|---|---|---|
| **`AgX`** *(Default Hero)* | Photoreal, Stylized PBR, Product, ArchViz, Claymation, Mecha, Dark Fantasy | `AgX - Medium High Contrast` or `AgX - Punchy` — highlights naturally desaturate toward white with zero neon hue-clipping! |
| **`Standard`** | Exact-hex Anime NPR, Grease Pencil Ligne Claire, Blueprint CAD, Pixel-Art 3D, UI sprites | `None` — preserves exact palette RGB hex values 1:1 |
| **`ACEScg` (OCIO)** | High-end VFX film plates, TextureCraft `colorSpace: "ACEScg"` EXR interchange | Industry cinema color pipeline |

---

## 2. Calibrating Exposure (Never Guess Brightness!)

- Check **`False Color`** view transform temporarily in Blender (or inspect histogram via Python PIL/NumPy):
  - **Mid-gray (`18%` reflectance)** should sit in Green/Grey (`~0.5`).
  - **Key skin/focal highlights** in Yellow (`0.7–0.85`).
  - **Specular glints / light sources ONLY** in Red (`> 0.95`).
  - If large faces glow Red, drop `scene.view_settings.exposure` by `-0.5` to `-1.5` EV!

---

## 3. Essential Multi-Pass EXR → EffectCraft Compositing Pipeline

Export **16-bit Half-Float Multi-Layer OpenEXR** (`DWAA` lossless/near-lossless compression) from Blender Cycles containing:
1. `Combined` (Beauty)
2. `Mist` (Depth fog & atmospheric aerial perspective in post without re-rendering!)
3. `CryptoObject` / `CryptoMaterial` (Pixel-perfect per-object color grading masks!)
4. `Emission` / `GlossyDirect` (Selective optical halation & bloom!)

Import into **EffectCraft** (`effectcraft` / `effectcraft-live` MCP) to apply:
- Subtle optical **Glare / Halation** (`threshold > 1.5`)
- Corner-only **Chromatic Aberration** (`0.3–0.6 px`)
- Subtle **35mm Film Grain** (`2–4%`) + gentle vignette (`-0.15 EV` edges)
- Kinetic typography title cards, callout annotations, and turntable wipes!

## Related Notes
- [[Lighting Design & Three-Point to Atmospheric Cinema]]
- [[ArtCraft Full Suite MCP Guide (MaterialCraft, TextureCraft, VectorCraft, EffectCraft, DesignCraft, FigCraft, SoundCraft, Craft Anything)]]
- [[The Visual Critic & Cook Loop for 3D Assets]]
