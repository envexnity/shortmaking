---
title: Style 02 — Cinematic VFX & Film Realism (ACES - AgX)
style_id: "02"
style_family: Photoreal
pbr_or_npr: Physically-Based (PBR)
primary_engines: [Blender Cycles, Unreal Engine 5, Houdini/USD]
artcraft_tools: [MaterialCraft, TextureCraft, EffectCraft, SoundCraft]
poly_budget: "100k–2M+ tris (UDIM + Displacement)"
texel_density: "20.48–40.96 px/cm (4K UDIMs)"
lighting_key: "High-Contrast Chiaroscuro + Volumetrics + Anamorphic"
tags: [art-style, vfx, film, cinema, aces, udim, photoreal]
updated: 2026-11-20
---

# Style 02 — Cinematic VFX & Film Realism (ACES / AgX)

**Visual Benchmark:** ILM / Weta FX / Denis Villeneuve (*Dune*, *Blade Runner 2049*), ROGUE ONE industrial grit, live-action plate integration.

---

## 1. Silhouette, Proportions & Geometry Rules
- **True geometric displacement + micro-silhouette fidelity:** Use 32-bit EXR displacement maps (`Adaptive Subdivision` in Cycles) for rock strata, weathered metal armor plates, skin pores, and architectural stonework.
- **Real mechanical assembly:** Every visible hinge, cable clamp, rivet, weld bead, and hydraulic piston is physically modeled — never faked with a flat texture if it enters mid-shot.
- **Multi-tile UDIM layout (`1001–1010+`):** Give hero face/cockpit/weapon breech 4K tiles; secondary body panels 2K tiles.

## 2. MaterialCraft & TextureCraft Recipe
- **MaterialCraft:** Build layered procedural weathering graphs (chipped primer → oxidized metal → oil streak → dust crust) exporting 16/32-bit EXR Height + `.mcmat`.
- **TextureCraft:** Enable `uvTiles: true` (UDIM mode), bake high-to-low `normal`, `AO`, `curvature`, `thickness`, `bentNormal` at 4K (`antialiasing: 4`). Layer `dirt` + `edgeWear` + particle gravity streaks (`tool.brush { particles: { enabled: true, gravity: 1.2 } }`). Export in **`ACEScg`** color space (`file.exportTextures { colorSpace: "ACEScg", materialX: true }`)!

## 3. Blender 5.3 Lighting, Volumetrics & EffectCraft Post
- **Atmospheric Depth:** Add bounded `Principled Volume` cube (`Density 0.002–0.015`, `Anisotropy 0.65`) for light shafts and aerial perspective — never let distant elements match foreground black levels!
- **Color Separation:** Warm tungsten/amber key (`3200K`) vs cool twilight/cyan sky fill (`7500K–9000K`).
- **Optical Imperfections:** Render multi-layer EXR (Beauty, Mist, Cryptomatte, GlossyDirect, Emit) → composite in **EffectCraft** (`effectcraft` MCP) with subtle anamorphic oval bokeh/flare, `0.4 px` chromatic aberration at frame corners, halation around highlights, and 35mm fine film grain.
- **Audio:** Pair turntable/shot in **SoundCraft** (`soundcraft` MCP) with sub-bass rumble + room tone (`-14 LUFS`).

## 4. Style Anti-Patterns
- Clean showroom surfaces in a lived-in world (zero grime/oil/wear history).
- Over-saturated neon colors clipping under sRGB (always use `AgX` or `ACEScg`).
- Heavy artificial bloom/lens flare masking weak lighting composition.

## Related Notes
- [[Color Management (AgX, Filmic, ACES) & Compositing]]
- [[UV Unwrapping, Texel Density & UDIMs]]
- [[Lighting Design & Three-Point to Atmospheric Cinema]]
- [[ArtCraft Full Suite MCP Guide (MaterialCraft, TextureCraft, VectorCraft, EffectCraft, DesignCraft, FigCraft, SoundCraft, Craft Anything)]]
