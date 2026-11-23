---
title: Style 14 — Cyberpunk, Neon Noir & Holographic Sci-Fi
style_id: "14"
style_family: Genre World
pbr_or_npr: Wet PBR + Emissive + Volumetrics
primary_engines: [Blender Cycles/EEVEE, Unreal Engine 5, Three.js]
artcraft_tools: [MaterialCraft, TextureCraft, FigCraft, VectorCraft, EffectCraft]
poly_budget: "30k–300k tris (Layered Greebles & Cabling)"
texel_density: "10.24–20.48 px/cm (2K–4K + Emissive/Roughness)"
lighting_key: "Wet Specular Reflections + Neon Practicals + Rain Fog"
tags: [art-style, cyberpunk, sci-fi, neon, hologram, noir, volumetrics]
updated: 2026-11-20
---

# Style 14 — Cyberpunk, Neon Noir & Holographic Sci-Fi

**Visual Benchmark:** *Cyberpunk 2077*, *Blade Runner 2049*, *Akira*, *Ghost in the Shell*, *Stray* — **wet dark asphalt mirroring razor-sharp saturated signage through layered rain haze**.

---

## 1. Geometry & World-Building Rules
- **High-Low Tech Density ("Used Future"):** Layer utilitarian industrial hardware (AC units, corrugated vents, braided conduit cables via Geometry Nodes curves, bolted steel shutters, dripping pipes) underneath sleek corporate glass and holographic billboards.
- **Verticality & Framing:** Stack signage at multiple Z heights (`3 m`, `7 m`, `15 m`) with overhanging walkways and diagonal cable catenaries to create dense, claustrophobic leading lines.
- **Puddle Micro-Relief:** Model slight road crown & gutter depressions so rain pools naturally along curbs rather than uniform flat puddles everywhere.

## 2. Full ArtCraft Suite Integration (Where Every App Shines!)
- **FigCraft MCP:** Design crisp diegetic holographic UIs, kanji/cyrillic street kiosks, telemetry dashboards, and glowing vending machine screens → export transparent PNGs for **Emissive** maps!
- **VectorCraft MCP:** Design neon tube signs, corporate megacorp logos, hazard chevron stripes, and industrial stencils → extrude neon tubes in Blender OR apply as decals in TextureCraft!
- **MaterialCraft MCP:** Build procedural **Wet Asphalt with Puddles** (base asphalt `Roughness 0.72` blended via height mask into mirror puddle water `Roughness 0.02`, subtle ripple normal!).
- **TextureCraft MCP:** Bake grime + downward rain streak particles (`tool.brush { particles: { enabled: true, gravity: 1.5 } }`) + worn painted steel (`edgeWear` + `dirt`).
- **EffectCraft MCP:** Add optical halation/anamorphic horizontal flare streaks on neon sources + fine chromatic aberration + falling rain pass.

## 3. Lighting Discipline (Avoid "Purple-Cyan Slop"!)
> [!WARNING]
> **The #1 Cyberpunk cliché is flooding the entire frame evenly with blinding magenta + cyan.** Real neo-noir is **75% dark moody shadow** (`#0B0E14`) punctuated by **intentional pools of sodium-vapor amber (`#FF9E2C`), toxic jade (`#00E5A0`), crimson neon (`#FF2442`), and cold rainy steel blue (`#3A6EA5`)**!
- Use **volumetric fog** (`Principled Volume`, `Density 0.01–0.025`, `Anisotropy 0.7`) so every neon tube casts a soft luminous halo without washing out foreground blacks.
- Wet roughness contrast (`0.02` puddles vs `0.78` damp concrete) creates 90% of the visual richness!

## 4. Style Anti-Patterns
- Flooding every surface uniformly with neon pink & cyan (destroys contrast and focal hierarchy).
- Dry matte roads with zero specular reflection breakup.
- Generic gibberish AI text on billboards (always author real crisp typography in **FigCraft** / **VectorCraft**!).

## Related Notes
- [[Style 15 — Brutalist, Industrial Hard-Surface & Mecha]]
- [[Lighting Design & Three-Point to Atmospheric Cinema]]
- [[GLSL, WGSL & Three.js TSL Custom Shaders]]
- [[ArtCraft Full Suite MCP Guide (MaterialCraft, TextureCraft, VectorCraft, EffectCraft, DesignCraft, FigCraft, SoundCraft, Craft Anything)]]
