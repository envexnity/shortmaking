---
title: Style 24 — Pixel-Art 3D (Dithered Orthographic Sprites & 2.5D HD-2D)
style_id: "24"
style_family: Retro & Minimal
pbr_or_npr: Orthographic Pixel / HD-2D Hybrid
primary_engines: [Blender EEVEE, Three.js, Godot, Unity]
artcraft_tools: [TextureCraft, VectorCraft, EffectCraft]
poly_budget: "Low/Mid-Poly Rendered at Pixel Grid"
texel_density: "1:1 Pixel-Locked Ortho or 16 px/unit Sprites"
lighting_key: "Quantized Toon + Bayer Dither OR HD-2D Tilt-Shift Bloom"
tags: [art-style, pixel-art-3d, hd-2d, orthographic, dither, sprites, retro]
updated: 2026-11-20
---

# Style 24 — Pixel-Art 3D (Dithered Orthographic Sprites & 2.5D HD-2D)

**Visual Benchmark:** *A Short Hike*, *Dead Cells* (3D-to-2D normal-mapped sprites), *Octopath Traveler* (HD-2D), *Signalis*, *t3ssel8r* pixel-3D renders — **crisp hand-crafted pixel art backed by genuine 3D lighting, rotation, and parallax**.

---

## 1. Two Master Approaches (Pick One!)

### Approach A: Pure Pixelated 3D (*A Short Hike* / *t3ssel8r* / *Dead Cells*)
- **Camera:** **Orthographic** (`camera.data.type = 'ORTHO'`) at exact `30°` or `35.264°` isometric angle, rendered at native low resolution (`320×180`, `480×270`, or `640×360`) with **Filter Size = `0.01 px`** (turns off anti-aliasing completely in Blender Render → Film → Filter Size!).
- **Anti-Shimmer Secret (Texel Snapping):** Snap the orthographic camera position in world space to exact **pixel-grid increments** (`snap(pos, ortho_scale / res_y)`) so static geometry NEVER shimmers or crawls as the camera pans!
- **Edge Highlight & Silhouette Outline Pass:** Run a depth + normal discontinuity post-pass in shader/compositor to draw crisp 1-pixel lighter bevel highlights on convex creases and 1-pixel dark outlines on silhouette depth jumps!
- **Color Quantization:** Lock output to a curated **16–64 color Lospec palette** using ordered **Bayer 4×4 dithering** (snippet in [[GLSL, WGSL & Three.js TSL Custom Shaders]]).

### Approach B: 2.5D HD-2D (*Octopath Traveler* / *Triangle Strategy* / *Star Ocean 2 R*)
- **2D Pixel-Art Sprites (`NearestFilter`, billboarded toward camera)** standing inside a **3D PBR diorama world** with real-time dynamic shadows, water reflections, volumetric sun shafts, glowing particle fireflies, and **extreme shallow tilt-shift Depth of Field**!
- Author crisp pixel-art sprite sheets & foliage cards (`TextureCraft` / `VectorCraft` pixel grid) with matching **16-px/meter low-res pixel textures** on the 3D brick/wood/cobblestone geometry so 2D characters and 3D world share identical texel scale!

## 2. Blender 5.3 Pixel-Sprite Render Settings
- `scene.render.engine = 'BLENDER_EEVEE'`
- `scene.render.resolution_x = 320`, `resolution_y = 180` (upscale `4×` or `6×` with `Nearest` in **EffectCraft** / FFmpeg!)
- `scene.render.filter_size = 0.01` (zero AA blur!)
- `scene.view_settings.view_transform = 'Standard'`
- Step animation on `12 fps` or `8 fps` (`Stepped Interpolation`) for authentic sprite cadence!

## 3. Style Anti-Patterns
- Smooth anti-aliased 3D edges colliding with jagged pixel sprites.
- Sub-pixel camera shimmer (always snap orthographic camera to texel grid!).
- Uncapped 16-million-color gradients on a 320×180 pixel render (always quantize palette or use stepped cel bands!).

## Related Notes
- [[Style 11 — PS1 - PS2 - N64 Retro & Vertex-Snapped Lo-Fi]]
- [[Style 12 — Voxel, Blocky & Minecraft - Blockbench Style]]
- [[GLSL, WGSL & Three.js TSL Custom Shaders]]
- [[Style 08 — Isometric Diorama & Cozy Miniature (Tilt-Shift - Clay)]]
