---
title: Style 23 — Ceramic, Glass, Jewelry & Caustics Macro
style_id: "23"
style_family: Photoreal
pbr_or_npr: Optical Transmission, Dispersion & Caustics
primary_engines: [Blender Cycles, Three.js WebGPU, Unreal Engine 5]
artcraft_tools: [MaterialCraft, TextureCraft, EffectCraft]
poly_budget: "30k–250k tris (True Wall Thickness + Exact Facets)"
texel_density: "20.48 px/cm (Micro Glaze & Precious Metal)"
lighting_key: "Focused Point/Spot Caustic Sources + Studio Strip Softboxes"
tags: [art-style, glass, ceramic, jewelry, caustics, macro, optical, dispersion]
updated: 2026-11-20
---

# Style 23 — Ceramic, Glass, Jewelry & Caustics Macro

**Visual Benchmark:** Tiffany & Co. / Cartier jewelry macro stills, luxury perfume bottles, Japanese artisanal ceramics, glassblowing studies — **breathtaking refractive physics, spectral rainbow fire, and tactile stoneware glaze**.

---

## 1. Optical Geometry Rules (Zero Physics Cheats!)
- **Glass MUST have real wall thickness (`2 mm–8 mm`):** A single-sided hollow glass cup refracts like a solid crystal block! Use `Solidify` with consistent outward normals on the exterior and inward normals on the interior cavity.
- **Liquid-in-Glass Interface (The "Overlap Rule"):** For perfume, wine, or water inside a glass vessel, **extend the liquid mesh slightly (`0.1 mm`) *into* the inner glass wall**! Leaving an air gap creates ugly silver total-internal-reflection artifacts; slight overlap produces physically exact dark meniscus refraction!
- **Gemstones (Brilliant Cut / Emerald Cut):** Model mathematically exact facet angles (critical angle for Diamond `IOR 2.417` is `24.4°`) with razor-sharp flat facets (tiny `0.03 mm` edge catchlight micro-bevel only) and high Cycles light path bounces (`Transmission = 16`, `Glossy = 12`, `Total = 24`)!

## 2. Material Recipes (Blender 5.3 Cycles + MaterialCraft)
- **Dispersion Glass & Diamond:** Blend 3 `Glass BSDF` shaders (`Red IOR = 2.40`, `Green IOR = 2.42`, `Blue IOR = 2.45` for diamond fire; `1.51 / 1.52 / 1.53` for crystal glass) using `Add Shader`!
- **Manifold Shadow Caustics (Blender 5.3 Cycles):**
  - Enable `Shadow Caustics` on the focused Spot/Sun light (`light.use_shadow_caustics = True`), mark the glass vessel `Cast Shadow Caustics`, and mark the tabletop `Receive Shadow Caustics` for razor-sharp glowing refractive light patterns on the table!
- **Artisanal Glazed Ceramic (MaterialCraft):**
  - **Kiln Glaze Drip:** Thick glossy coat (`Coat Weight = 1.0`, `Coat Roughness = 0.04`, `IOR = 1.54`, subtle orange-peel micro-bump) dripping down via height mask to reveal raw matte unglazed terracotta/stoneware clay foot at the bottom (`Roughness = 0.78`, speckled mineral grit)!
  - **Kintsugi / Gold Vein:** Recessed crack mask filled with burnished 24K gold (`#F6C868`, `Metallic = 1.0`, `Roughness = 0.14`)!

## 3. Studio Lighting & Post
- **High-Contrast Reflections:** Glass is invisible without **bright white reflection cards AND dark black negative-fill cards** flanking its edges!
- **EffectCraft / Compositor:** Add subtle crisp star/glint glare (`Glare → STREAKS`, threshold `3.5`, mix `-0.8`) exclusively on pinpoint diamond/gold highlights.

## 4. Style Anti-Patterns
- Single-sided zero-thickness glass meshes.
- Default Cycles max transmission bounces (`4` is too low — gemstones turn black inside! Raise to `12–16`).
- Flat uniform white dome HDRI lighting (makes glass and chrome vanish into grey soup).

## Related Notes
- [[PBR Physics Reference (Albedo, Metallic, Roughness, IOR, SSS)]]
- [[Blender 5.3 Cycles vs EEVEE Next Optimization]]
- [[Style 18 — Abstract Motion Graphics, Glassmorphism & Iridescent (Cinema4D - Awwwards)]]
- [[Style 01 — Photorealistic Physically-Based (ArchViz & Product)]]
