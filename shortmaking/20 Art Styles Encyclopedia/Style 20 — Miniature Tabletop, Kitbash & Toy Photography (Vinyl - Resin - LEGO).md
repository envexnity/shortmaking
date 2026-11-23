---
title: Style 20 — Miniature Tabletop, Kitbash & Toy Photography (Vinyl - Resin - LEGO)
style_id: "20"
style_family: Tactile & Macro
pbr_or_npr: Macro Toy PBR + SSS
primary_engines: [Blender Cycles, Unreal Engine 5, Three.js]
artcraft_tools: [MaterialCraft, TextureCraft, VectorCraft]
poly_budget: "20k–150k tris (Injection-Mold Precision)"
texel_density: "20.48 px/cm (Macro Micro-Scratches & Decals)"
lighting_key: "Macro Studio Softbox + Extreme Shallow DoF (f/1.8–f/2.8)"
tags: [art-style, toy, miniature, vinyl, lego, tabletop, macro, kitbash]
updated: 2026-11-20
---

# Style 20 — Miniature Tabletop, Kitbash & Toy Photography (Vinyl / Resin / LEGO)

**Visual Benchmark:** *The LEGO Movie* (Animal Logic), Funko / Kidrobot / Superplastic designer vinyl toys, Warhammer 40K painted tabletop miniatures, Bandai Gunpla kits — **hyper-real macro physics applied to tiny crafted collectibles**.

---

## 1. The Micro-Physical Imperfections That Sell "Real Toy"
- **Injection-Mold Parting Lines:** Tiny `0.15 mm` hairline mold seam running along cylinder/torso midlines + subtle rounded bevels (`0.3–0.6 mm`) on every LEGO/ABS edge!
- **Micro-Scratches & Fingerprints (MaterialCraft + TextureCraft):** Real ABS plastic and designer vinyl collect faint wispy hair-line scuffs (`Roughness 0.14–0.28`, subtle micro-bump normal `0.03`) and slight oil smudges!
- **Real Toy Scale (`4 cm – 18 cm` tall):** Model at actual physical centimeter height (`0.04 m` for a minifigure, `0.15 m` for a vinyl collectible) so Cycles lens depth of field (`100 mm` macro lens, `f/2.0–f/2.8`) naturally dissolves background props into creamy real optical bokeh!

## 2. Sub-Style Material Recipes
- **Designer Vinyl / Soft PVC:** `IOR = 1.49`, `Roughness = 0.25–0.38`, **`Subsurface Weight = 0.15–0.25`**, `Subsurface Scale = 0.005 m` — that waxy light bleed around ears and edges screams real collectible vinyl!
- **ABS Brick / LEGO:** `IOR = 1.54`, `Roughness = 0.12–0.20`, subtle `Subsurface Weight = 0.06`, embossed top stud logo via normal/displacement map, crisp micro-scratches on flat top faces.
- **Hand-Painted Warhammer Tabletop Mini:** Painted matte acrylic base (`Roughness 0.65`) + **dry-brushed sharp bright edge highlights** (`curvature` + `edgeWear` in TextureCraft!) + dark oily Nuln-Oil ink wash pooling in crevices (`ambientOcclusion` multiply with slightly lower `Roughness = 0.35` glossy wash!) + textured flocking/tuft round display base!

## 3. Macro Photography Lighting
- Overhead soft diffused tent light + warm/cool accent rims + real tabletop surface (wood grain desk, cutting mat with VectorCraft millimeter grid, or dark velvet display plinth).

## 4. Style Anti-Patterns
- Modeling a "miniature" at 2-meter human scale (ruins macro DoF and SSS light transmission!).
- Zero micro-scratches or mold seams (reads as lifeless CG render, not photographed toy).

## Related Notes
- [[Style 09 — Claymation, Stop-Motion & Plasticine (Thumbprints - SSS)]]
- [[Style 08 — Isometric Diorama & Cozy Miniature (Tilt-Shift - Clay)]]
- [[Camera Lenses, Framing, Turntables & Product Shots]]
- [[MaterialCraft Mastery — Node Library & Procedural Graphs]]
