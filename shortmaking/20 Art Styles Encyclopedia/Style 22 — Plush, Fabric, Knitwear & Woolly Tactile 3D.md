---
title: Style 22 — Plush, Fabric, Knitwear & Woolly Tactile 3D
style_id: "22"
style_family: Tactile & Macro
pbr_or_npr: Fabric Sheen PBR + Micro-Fuzz Hair
primary_engines: [Blender Cycles, Unreal Engine 5, Three.js]
artcraft_tools: [MaterialCraft, TextureCraft]
poly_budget: "15k–80k tris + Procedural Hair Curves / Fuzz"
texel_density: "20.48 px/cm (2K–4K Weave Normal + Height)"
lighting_key: "Strong Warm Rim Backlight (Lights Up Peach Fuzz!)"
tags: [art-style, plush, fabric, wool, knitwear, felt, tactile, hair]
updated: 2026-11-20
---

# Style 22 — Plush, Fabric, Knitwear & Woolly Tactile 3D

**Visual Benchmark:** *Yoshi's Crafted World*, *Unravel*, *Sackboy: A Big Adventure*, Jellycat plushies, luxury fashion cloth renders — **soft, cozy, huggable materiality driven by weave displacement, grazing sheen, and backlit silhouette fuzz**.

---

## 1. Geometry, Seams & Silhouette Fuzz
- **Real Stitched Seams:** Model recessed pinch creases along pattern seams (`Bevel` → inset → push inward `2–4 mm`) and run a Geometry Nodes stitch loop (`Curve to Mesh` thread loops every `4 mm`) along every join!
- **Stuffing Tension Wrinkles:** Slightly puff convex sections and add subtle radial pull creases around button eyes, limb joints, and stitched seams (using Blender Cloth Pressure simulation or sculpting!).
- **The Silhouette Fuzz Layer (CRITICAL):** Real wool, felt, and plush have **thousands of stray 1–4 mm fibers catching backlight** along the silhouette!
  - In **Blender 5.3:** Add Hair Curves (`Geometry Nodes` surface scatter of `50k–250k` ultra-thin `0.15 mm` curled micro-strands, length `2–6 mm`, `Principled Hair BSDF` or translucent `Principled BSDF` matching base dye).
  - For **Real-Time / Three.js:** Fake silhouette fuzz using **2–4 nested shell layers** (extruded outward by `1–3 mm` with alpha-tested high-frequency fiber noise!) + strong Fresnel `Sheen`!

## 2. MaterialCraft Weave & Knit Graphs
Author crisp tileable textile patterns in **MaterialCraft**:
- **Chunky Cable Knit / Crochet:** Interlocking braided V-loops via `fx_map` + `directional_warp` + 16-bit Height/Displacement + fine stray fiber micro-bump.
- **Pressed Felt / Fleece:** Multi-layered overlapping random bent hair strokes (`fx_map`) + soft organic mottling.
- **Corduroy / Velvet:** Parallel ribbed height waves + **Blender 5.3 `Sheen` section (`Sheen Weight = 0.8–1.0`, `Sheen Roughness = 0.45–0.65`, `Sheen Tint = slightly brighter pastel`)** — grazing-angle microfiber sheen is non-negotiable for real fabric!
- **Roughness:** Always high (`0.82–0.98`) with `Metallic = 0.0` (except metallic embroidery thread!).

## 3. Lighting the Fuzz
- **Back/Rim Light is Everything:** Place a warm or crisp daylight rim light at `135°–160°` behind the plushie so grazing sheen and stray hair fibers glow softly around the entire silhouette!

## 4. Style Anti-Patterns
- Smooth glossy plastic shading (`Roughness 0.4`) on cloth with zero `Sheen Weight`.
- Clean hard geometric silhouettes with zero stray fibers or recessed stitch seams.
- Flat un-creased spheres instead of soft stuffed-cloth volume tension.

## Related Notes
- [[PBR Physics Reference (Albedo, Metallic, Roughness, IOR, SSS)]]
- [[Physics Simulations (Cloth, Rigid Body, Hair, Fluid, Smoke)]]
- [[Style 09 — Claymation, Stop-Motion & Plasticine (Thumbprints - SSS)]]
- [[MaterialCraft Mastery — Node Library & Procedural Graphs]]
