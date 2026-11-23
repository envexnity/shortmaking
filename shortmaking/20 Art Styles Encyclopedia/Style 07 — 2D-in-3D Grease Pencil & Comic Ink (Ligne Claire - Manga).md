---
title: Style 07 — 2D-in-3D Grease Pencil & Comic Ink (Ligne Claire - Manga)
style_id: "07"
style_family: NPR & Comic
pbr_or_npr: Ink & Flat NPR
primary_engines: [Blender Grease Pencil + EEVEE, Three.js]
artcraft_tools: [VectorCraft, DesignCraft, EffectCraft]
poly_budget: "5k–40k tris + Grease Pencil Line Art"
texel_density: "Flat / Paper Grain Overlay"
lighting_key: "Flat Ligne Claire or Stark High-Contrast Ink Shadows"
tags: [art-style, grease-pencil, comic, manga, ligne-claire, npr]
updated: 2026-11-20
---

# Style 07 — 2D-in-3D Grease Pencil & Comic Ink (Ligne Claire / Manga)

**Visual Benchmark:** Moebius, Hergé (*Tintin* Ligne Claire), *Sable*, *Borderlands*, *MadWorld*, modern Blender Grease Pencil 3.0 shorts.

---

## 1. Geometry & Grease Pencil Line Art Rules
- **Clean simplified silhouettes:** Avoid noisy micro-chamfers that generate chaotic jittery ink lines; instead mark intentional **Freestyle / Crease Edges** (`edge.use_freestyle_mark = True`) for interior mechanical panel lines and garment folds.
- **Blender 5.3 Grease Pencil v3 (`GPENCIL` → `GREASEPENCIL`):**
  - Add a Grease Pencil object with **`Line Art` Modifier** targeting the scene collection (`use_contour=True`, `use_crease=True`, `crease_threshold=math.radians(135)`, `use_material=True`, `use_intersection=True`).
  - Stack a subtle **`Noise` Modifier** (`position=0.002`, `thickness=0.25`, `step=2`) on the Grease Pencil strokes so lines breathe with organic hand-drawn nib pressure!
- **Tapered Ink Weight:** Thicker ink (`4–7 px`) on foreground hero silhouettes; crisp hairline (`1.5–2.5 px`) on background architecture (aerial line-weight perspective!).

## 2. VectorCraft + MaterialCraft + TextureCraft Recipe
- **VectorCraft:** Design clean graphic posters, signage, manga speed-lines, screentone dot sheets, and flat comic textures → export SVG/PNG.
- **MaterialCraft:** Generate a subtle warm watercolor/Bristol paper tooth overlay (high-frequency organic fiber noise) to multiply over the entire viewport!
- **Color Palette (Moebius / Sable):** Restrict scenes to **3–5 harmonious pastel or stark monochrome ink + 1 accent hue** (e.g., cream `#F3EAD8`, terracotta `#C96A4B`, cerulean sky `#6BA6C7`, deep espresso ink `#1D171A`).

## 3. Blender 5.3 Lighting & Shader Setup
- **View Transform:** `Standard` (exact flat color preservation).
- **2-Step Flat Shader:** Zero specular shine (`Specular IOR Level = 0.0`, `Roughness = 1.0`), sharp `Constant` ColorRamp shadow (or pure flat `Emission` for Ligne Claire + baked crisp cast shadows!).
- **Manga Black/White Mode:** Pure `#FAFAFA` paper base + `#111111` ink shadow + screen-space screentone dots in mid-shadows (`0.3–0.6` luminance).

## 4. Style Anti-Patterns
- Glossy PBR reflections fighting flat hand-drawn ink lines.
- Uniform sterile computer-straight 1 px black outlines with zero thickness variation.
- Cluttered micro-geometry turning Line Art into a tangled black blob.

## Related Notes
- [[Style 05 — Painterly Brushstroke & Spider-Verse (Halftones - Stepped Anim)]]
- [[Style 06 — Anime & Cel-Shaded NPR (Guilty Gear - Genshin - Ghibli)]]
- [[Blender 5.3 Shader Nodes & NPR Shading Recipes]]
