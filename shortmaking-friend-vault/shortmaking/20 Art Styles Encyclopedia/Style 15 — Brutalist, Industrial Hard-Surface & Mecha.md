---
title: Style 15 — Brutalist, Industrial Hard-Surface & Mecha
style_id: "15"
style_family: Genre World
pbr_or_npr: Hard-Surface PBR
primary_engines: [Blender Cycles, Unreal Engine 5, Unity, Three.js]
artcraft_tools: [MaterialCraft, TextureCraft, VectorCraft, DesignCraft]
poly_budget: "30k–250k tris (Beveled Armor + Mechanical Internals)"
texel_density: "10.24–20.48 px/cm (2K–4K Decals + Wear)"
lighting_key: "Monumental Directional Hard Sun + Cold Industrial Rim"
tags: [art-style, mecha, brutalist, industrial, hard-surface, sci-fi]
updated: 2026-11-20
---

# Style 15 — Brutalist, Industrial Hard-Surface & Mecha

**Visual Benchmark:** *Armored Core VI*, *Titanfall 2*, *Metal Gear*, *Control* (Oldest House brutalism), Vitaly Bulgarov / Simon Stålenhag — **massive engineering weight, crisp chamfered armor, and unmistakable industrial function**.

---

## 1. Geometry & Mechanical Believability Rules
- **Functional Engineering Anatomy:** Every joint needs a clear **pivot axis, hydraulic actuator, shock absorber, or cable conduit** — armor plates sit *over* an exposed dark mechanical inner frame (`Metallic 1.0`, `Roughness 0.35`) so gaps reveal intricate engineering depth!
- **45° Industrial Chamfers:** Use crisp 1-segment or 2-segment `45°` machined chamfers (`0.005 m–0.02 m`) rather than soft pillowy fillets; pair with **Weighted Normals** so large flat armor slabs reflect light cleanly with zero shading wobble.
- **Scale Cue Micro-Details (The Giant-Scale Secret):** On a 12-meter mecha or monumental concrete brutalist monolith, **human-scale anchors** sell scale instantly: tiny `1.1 m` safety handrails, yellow warning stencils, service hatches, bolted access ladders, and tiny amber beacon lights!

## 2. MaterialCraft, TextureCraft & VectorCraft Recipe
- **MaterialCraft:** Author board-formed brutalist concrete (wood plank formwork grain + tie-rod holes via `fx_map`), cast-iron sand-blasted armor, carbon fiber weave, and ribbed rubber gaskets.
- **VectorCraft:** Generate high-contrast military/industrial technical stencils (`CAUTION — HIGH PRESSURE`, `NO STEP`, unit numbers `04-B`, hazard chevrons, panel serials) → export transparent PNGs for **TextureCraft `layer.add.decal`**.
- **TextureCraft:**
  - Base painted military coat (`olive drab`, `matte chalk grey`, `hazard safety orange`, `Roughness 0.45–0.62`).
  - `matFinishRaw` / `matFinishGrind` filter on bare exposed alloy sub-layers.
  - Sharp metallic `edgeWear` chipping along chamfered armor ridges (`Metallic 1.0`, `Roughness 0.22`), oil/grease leaks around hydraulic joints (`dirt` + gravity streaks), and heat-blued exhaust nozzles.

## 3. Lighting & Camera Framing
- **Low-Angle Hero Camera:** Place camera at human eye height (`1.65 m` above ground!) tilted upward (`28 mm–35 mm` lens) to make brutalist structures and mechs feel overwhelmingly colossal.
- **Hard Monumental Lighting:** Crisp high-contrast sunlight (`angle = 0.6°–1.5°`) raking across angled bevels + subtle ground-level dust/smoke volumetric sheet.

## 4. Style Anti-Patterns
- Random decorative greebles covering 100% of every surface with zero rest space (violates the 70/20/10 primary/secondary/tertiary ratio!).
- Soft bouncy marshmallow bevels on heavy military armor.
- Floating limbs with impossible zero-clearance mechanical joints.

## Related Notes
- [[Hard-Surface & SubD Modeling Playbook]]
- [[Style 14 — Cyberpunk, Neon Noir & Holographic Sci-Fi]]
- [[Style 21 — Technical Blueprint, Wireframe, X-Ray & Exploded CAD]]
- [[TextureCraft Mastery — Baking, Smart Materials & 3D Painting]]
