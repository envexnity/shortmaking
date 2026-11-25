---
title: Style 11 — PS1 - PS2 - N64 Retro & Vertex-Snapped Lo-Fi
style_id: "11"
style_family: Retro & Minimal
pbr_or_npr: Lo-Fi Unlit / Gouraud / Nearest
primary_engines: [Three.js, Godot, Unity, Blender EEVEE]
artcraft_tools: [TextureCraft, VectorCraft, EffectCraft, SoundCraft]
poly_budget: "100–1,500 tris (PS1) / 2k–6k (PS2)"
texel_density: "64×64 to 256×256 Nearest-Neighbor + Dither"
lighting_key: "Vertex-Lit Gouraud + Distance Fog + 15-bit Color Dither"
tags: [art-style, ps1, ps2, n64, retro, lo-fi, shader, vertex-snap]
updated: 2026-11-20
---

# Style 11 — PS1 / PS2 / N64 Retro & Vertex-Snapped Lo-Fi

**Visual Benchmark:** *Silent Hill 1*, *Metal Gear Solid*, *Signalis*, *Crow Country*, *Mouthwashing*, *Dread Delusion* — **authentic 32-bit/64-bit hardware quirks recreated with precision**.

---

## 1. Authentic Hardware Signatures (Choose Era)

| Feature | PS1 (1995) | N64 (1996) | PS2 (2001) |
|---|---|---|---|
| **Resolution** | `320 × 240` (`4:3`) | `320 × 240` | `640 × 448` interlaced |
| **Texture Filtering** | **Nearest-Neighbor (crisp pixels!)** | 3-Point Bilinear blurry | Bilinear + mipmaps |
| **Texture Size** | `64×64` – `128×128` (indexed 16/256 colors) | `32×32` – `64×64` | `256×256` – `512×512` |
| **Geometry Quirk** | **Integer screen-space vertex jitter** + affine texture warping | Clean float vertices + heavy distance fog | Smooth skinned limbs + moody bloom |
| **Lighting** | Per-vertex Gouraud color + baked shadow planes | Vertex colors + rich fog | Lightmaps + soft real-time point lights + heavy bloom |

## 2. Modeling & TextureCraft Lo-Fi Recipe
- **Geometry:** Strict budget (`300–900` tris for a PS1 character!). Keep quads subdivided somewhat evenly so affine texture warping doesn't explode wildly on giant single-quad walls. Paint shadows and ambient occlusion directly into **Vertex Colors** (`Col` attribute)!
- **TextureCraft / Photobash Lo-Fi:** Paint or bake at `512×512`, then downsample with `Nearest` + `posterize` filter (`16–32` color levels) down to `128×128` (`Nearest` interpolation in Blender `Image Texture` node and `THREE.NearestFilter` in Three.js!).
- **No Normal Maps or Roughness Maps on PS1!** Bake highlights, grime, and specular streaks directly into the low-res Albedo texture.

## 3. Shader & Post-Processing Stack
- **Vertex Snapping (GLSL / Blender Geometry Nodes):** Quantize clip-space `xy` coordinates to a `160×120` or `240×180` screen grid (exact snippet in [[GLSL, WGSL & Three.js TSL Custom Shaders]]!).
- **15-bit Color Depth + Ordered Bayer 4×4 Dither:** Quantize final RGB to `32` steps per channel (`5 bits/channel`) with Bayer dithering for authentic PS1 banding!
- **Post (EffectCraft / Three.js):** Render at `320×240`, upscale with nearest-neighbor, optionally layer subtle CRT scanlines, phosphor curvature, and heavy atmospheric distance fog (`linear fog` starting at `6 m–18 m`).

## 4. Style Anti-Patterns
- Putting 2K PBR normal/roughness maps onto a 400-tri mesh (looks broken, not retro).
- Rendering at crisp 4K 60fps with TAA anti-aliasing instead of pixelated `320×240` nearest upscale.
- Overdoing vertex jitter until text and faces become unreadable vomit.

## Related Notes
- [[GLSL, WGSL & Three.js TSL Custom Shaders]]
- [[Style 24 — Pixel-Art 3D (Dithered Orthographic Sprites & 2.5D HD-2D)]]
- [[Style 17 — Surreal, Liminal Space & Dreamcore]]
- [[Style 10 — Low-Poly Flat-Shaded & Faceted (Monument Valley - Firewatch)]]
