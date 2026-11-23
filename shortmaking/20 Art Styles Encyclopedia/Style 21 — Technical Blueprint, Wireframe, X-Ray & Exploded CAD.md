---
title: Style 21 — Technical Blueprint, Wireframe, X-Ray & Exploded CAD
style_id: "21"
style_family: Technical & CAD
pbr_or_npr: NPR / Fresnel X-Ray / CAD Vector
primary_engines: [Blender EEVEE/Cycles, Three.js, CadQuery/OpenSCAD]
artcraft_tools: [VectorCraft, DesignCraft, FigCraft, EffectCraft]
poly_budget: "Exact CAD Tessellation or Clean Quad Wireframe"
texel_density: "Procedural Grid + Vector Callouts"
lighting_key: "Unlit Cyan Blueprint / Luminous Fresnel X-Ray / Clean Clinical Studio"
tags: [art-style, blueprint, wireframe, xray, cad, exploded-view, technical]
updated: 2026-11-20
---

# Style 21 — Technical Blueprint, Wireframe, X-Ray & Exploded CAD

**Visual Benchmark:** Teenage Engineering exploded hardware manuals, Apple silicon X-ray teardowns, Iron Man Jarvis holograms, Swiss industrial patent drawings — **surgical engineering clarity where internal structure IS the hero**.

---

## 1. Four Sub-Style Recipes
1. **Classic Cyanotype Blueprint:** Deep Prussian blue paper background (`#0E3A66` with subtle grid lines) + crisp white silhouette/crease lines (**Grease Pencil Line Art** or Three.js `EdgesGeometry(geo, 20)`) + hidden interior dashed lines + **VectorCraft / DesignCraft** millimeter dimension callouts!
2. **Holographic X-Ray Glass:** Semi-transparent Fresnel shell (`Layer Weight → Facing^2.5` driving `Emission` cyan/ice-white `#4CE8FF` mixed with `Transparent BSDF`, zero shadows!) revealing glowing opaque internal circuit boards, gears, or skeleton!
3. **Exploded Mechanical Assembly:** Parent every sub-component cleanly around logical assembly vectors (`X`, `Y`, `Z`), animate radial explosion offsets (`0% → 100%` scroll-driven in Three.js via `Moh4696/open-3d-skills` exploded-view skill!), and connect separated bolts/parts with crisp dotted **axis guide lines**!
4. **Clay + Wireframe Overlay (Portfolio Breakdown):** Soft matte porcelain clay (`#DCD8D0`, `Roughness 0.55`, AO cavity) blended with crisp dark-grey quad topology wireframe (`Wireframe` modifier `thickness = 0.0008 m` or `ShaderNodeWireframe` / barycentric GLSL shader!).

## 2. ArtCraft Precision Integration
- **VectorCraft MCP:** Generate crisp technical callout leader lines, orthographic grid backdrops, ISO tolerance tables, and vector SVG logos.
- **DesignCraft MCP:** Assemble final technical spec sheets, multi-view orthographic pages (Front / Side / Top / Isometric), and bill-of-materials layouts into publication-grade PDF/PNG decks.
- **FigCraft MCP:** Build interactive inspection HUD overlays and parameter sliders for Three.js WebGL viewers.

## 3. Camera & Color Management
- Prefer **Orthographic** (`camera.data.type = 'ORTHO'`) or long telephoto (`100 mm–150 mm`) to minimize perspective foreshortening so parallel mechanical lines read cleanly.
- Use `Standard` view transform for pure blueprint hex accuracy; `AgX` for clinical white-studio hardware teardowns.

## 4. Style Anti-Patterns
- Messy triangulated boolean soup under a wireframe overlay (wireframe showcases demand immaculate quad topology or clean CAD edge extraction!).
- Overlapping unreadable callout leader lines.

## Related Notes
- [[Parametric CAD & 3D Printing (OpenSCAD, CadQuery, SolidCraft)]]
- [[Hard-Surface & SubD Modeling Playbook]]
- [[GitHub 3D Modeling Skills Index]] (`open-3d-skills`, `flowful-cadquery-skill`)
- [[Style 18 — Abstract Motion Graphics, Glassmorphism & Iridescent (Cinema4D - Awwwards)]]
