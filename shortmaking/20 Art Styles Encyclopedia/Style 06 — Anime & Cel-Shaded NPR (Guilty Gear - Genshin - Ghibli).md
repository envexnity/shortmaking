---
title: Style 06 — Anime & Cel-Shaded NPR (Guilty Gear - Genshin - Ghibli)
style_id: "06"
style_family: NPR & Anime
pbr_or_npr: Cel-Shaded NPR
primary_engines: [Blender EEVEE, Unity URP, Unreal Engine 5, Godot, Three.js]
artcraft_tools: [TextureCraft, VectorCraft, EffectCraft]
poly_budget: "15k–60k tris (Custom Edited Face Normals)"
texel_density: "10.24 px/cm (2K Albedo + ILM + SDF Face Map)"
lighting_key: "Hard 2-Band / 3-Band Cel + Rim + Warm Shadow Edge"
tags: [art-style, anime, cel-shaded, npr, guilty-gear, genshin, ghibli]
updated: 2026-11-20
---

# Style 06 — Anime & Cel-Shaded NPR (Guilty Gear / Genshin / Ghibli)

**Visual Benchmark:** *Guilty Gear Strive* (Arc System Works), *Genshin Impact*, *Hi-Fi Rush*, *Zelda: Breath of the Wild*, Studio Ghibli 3D adaptations.

---

## 1. The Secret That Makes Anime 3D Look Like 2D (Face Normals & SDFs)
> [!CAUTION]
> **Raw 3D face geometry produces horrifying nose/cheek shadows under cel shading!** Every pro anime studio fixes face shading using one of two techniques:
> 1. **Normal Transfer:** Transfer smooth normals from a simplified ellipsoid/sphere onto the character's face (`Data Transfer` modifier → `Custom Normals`) so shadows sweep cleanly across the cheek in a pure 2D arc!
> 2. **Face Shadow SDF Map (Genshin / Honkai method):** Bake or author a grayscale radial Signed Distance Field texture for the face; compare `dot(faceRight, lightDir)` against the SDF threshold for crisp, zero-artifact anime nose & cheek shadows at EVERY angle!

## 2. Geometry & Outline Rules
- **Hair:** Sculpted flowing tapered ribbons with crisp silhouette spikes; add **angel-ring anisotropic highlight band** painted/mapped horizontally across the crown UV!
- **Outlines (Inverted Hull Method):**
  - Add `Solidify` modifier (`thickness = -0.002 m to -0.005 m`, `use_flip_normals = True`, `material_offset = 1`).
  - Drive thickness with a **Vertex Group** (thin `0.2` on eyes/nose/lips, thicker `1.0` on outer cloak/boots/hair silhouette).
  - **Tint outlines dark colored** (deep maroon on skin, navy on white shirt — NEVER harsh `#000000` everywhere!).
- **Inner Line Details (`ILM` / Vertex Colors):** Follow the *Guilty Gear* method — paint crisp 2D inner crease lines directly on straightened UVs with zero antialiasing blur.

## 3. Blender 5.3 EEVEE Shader & Color Management
- **View Transform:** `Standard` (NOT AgX, unless specifically targeting soft cinematic anime — `Standard` preserves vivid anime palette hex codes!).
- **3-Tone Cel Ramp + Subsurface Termination Band:**
  - `Diffuse BSDF` → `Shader to RGB` → `ColorRamp (CONSTANT)`:
    - `0.00–0.46`: Hue-shifted cool shadow color
    - `0.46–0.50`: **Warm saturated orange/red terminator sliver** (simulates skin SSS along the shadow edge — instant anime polish!)
    - `0.50–1.00`: Clean lit base albedo
- **Crisp Rim Light:** Fresnel (`IOR 1.05`) masked by `N·L > 0` → `ColorRamp (CONSTANT)` → add bright sky/key rim edge!

## 4. Style Anti-Patterns
- Leaving raw unedited face normals under a hard cel ramp (creates jagged triangle nose shadows).
- Thick uniform black wireframe outlines choking delicate facial features.
- Default gray shadows instead of vivid hue-shifted shadow ramps.

## Related Notes
- [[Blender 5.3 Shader Nodes & NPR Shading Recipes]]
- [[Style 07 — 2D-in-3D Grease Pencil & Comic Ink (Ligne Claire - Manga)]]
- [[Style 19 — Botanical, Nature, Terrain & Biomes (Foliage - Water - Clouds)]]
- [[GLSL, WGSL & Three.js TSL Custom Shaders]]
