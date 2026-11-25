---
title: Style 10 — Low-Poly Flat-Shaded & Faceted (Monument Valley - Firewatch)
style_id: "10"
style_family: Retro & Minimal
pbr_or_npr: Flat-Shaded / Palette Gradient
primary_engines: [Blender, Three.js, Unity, Godot, Roblox]
artcraft_tools: [DesignCraft, VectorCraft, EffectCraft]
poly_budget: "150–4,000 tris (Deliberate Facets)"
texel_density: "Vertex Colors or 64×64 Palette Atlas"
lighting_key: "Atmospheric Gradient Fog + Hard Sun + Soft Bounce"
tags: [art-style, low-poly, flat-shaded, faceted, monument-valley, firewatch]
updated: 2026-11-20
---

# Style 10 — Low-Poly Flat-Shaded & Faceted (Monument Valley / Firewatch)

**Visual Benchmark:** *Monument Valley*, *Firewatch*, *Ashen*, *Tunic*, *Lonely Mountains: Downhill*, Grow With Kaz low-poly explainers — **maximum emotional beauty with minimal geometric economy**.

---

## 1. Geometry & Facet Economy Rules
- **Every single triangle earns its silhouette:** Deliberately triangulate organic forms (rocks, trees, terrain, clouds) and call `bpy.ops.object.shade_flat()` (NEVER smooth shading on faceted low-poly!).
- **Irregular artistic triangulation:** Use `Decimate (Collapse / Planar)` + tiny organic vertex jitter so triangles have pleasing varied scale rather than sterile robotic quads.
- **Color-Palette UV Trick (1 Draw Call for Entire Scene!):**
  - Pack a `256×256` palette texture (or vertical linear gradient swatches per color!) and scale each face's UVs down to a tiny dot inside its color swatch — an entire forest + town renders in **1 single material draw call** in Three.js / Unity / Godot!
- **Monument Valley Variant:** Razor-clean architectural geometry (`shade_flat()`), isometric orthographic projection, impossible Escher connections, and vibrant soft pastel gradients across vertical faces.

## 2. Material & Shader Setup
- **Zero noisy photo textures!** Surfaces are pure solid/gradient color with matte roughness (`0.70–0.88`), `Specular IOR Level = 0.25`, optional gentle height-based vertical gradient (`Generated Z` → `ColorRamp`) so trees and mountains darken gracefully at their bases.
- **Water:** Translucent flat-triangulated plane with subtle animated vertex ripples + crisp white foam line (`Ambient Occlusion` / depth intersection mask) where terrain meets water!

## 3. Lighting & Atmospheric Color (The Firewatch Secret)
> [!TIP]
> **Low-poly lives or dies by atmospheric depth fog and color harmony.** Without distance mist and warm/cool light separation, flat triangles look like a 1996 tech demo!
- Use **3-Band Color Depth:**
  - **Foreground:** Deep rich saturated shadow silhouettes (pine green / warm mahogany).
  - **Midground:** Clear sunlit local colors (amber, coral, sage).
  - **Background:** Soft atmospheric mist fading cleanly into sky horizon (lavender, peach, golden haze).
- Use **one crisp directional Sun** (`angle = 1.5°–4°`) casting bold geometric shadows + soft pastel sky hemisphere bounce.

## 4. Style Anti-Patterns
- Accidentally leaving Smooth Shading on low-poly meshes (produces muddy balloon shading).
- Mixing high-res photorealistic bark/grass textures onto 300-triangle rocks.
- Flat white lighting with no atmospheric distance fog or color palette discipline.

## Related Notes
- [[Three.js, React Three Fiber & WebGPU Production]]
- [[Style 11 — PS1 - PS2 - N64 Retro & Vertex-Snapped Lo-Fi]]
- [[Style 08 — Isometric Diorama & Cozy Miniature (Tilt-Shift - Clay)]]
- [[Lighting Design & Three-Point to Atmospheric Cinema]]
