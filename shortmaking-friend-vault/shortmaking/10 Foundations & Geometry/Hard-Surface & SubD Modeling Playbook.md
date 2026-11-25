---
title: Hard-Surface & SubD Modeling Playbook
tags: [foundations, hard-surface, subd, booleans, vectorcraft, blender]
updated: 2026-11-20
---

# Hard-Surface & SubD Modeling Playbook

Production workflows for weapons, vehicles, robots, architecture, gadgets, industrial machinery, and consumer products.

---

## 1. Choose the Right Hard-Surface Strategy

| Technique | Best For | Pros | Watch Out For |
|---|---|---|---|
| **Mid-Poly + Bevel + Weighted Normals** | Game props, sci-fi corridors, electronics, Three.js | Fast, clean shading, no normal-map bake needed for flat panels | Requires `Keep Sharp` + sufficient bevel segments (`1–2`) |
| **SubD (Catmull-Clark)** | Cars, ergonomic gadgets, film hero props, curved armor | Silky smooth curvature, infinite LOD subdivision | Requires all-quad topology + carefully routed holding edges |
| **Boolean + Remesh/Retopo** | Complex mechanical silhouettes, firearms, concept kits | Ultra-fast iteration on complex cutouts | Always use `EXACT` solver, avoid coplanar faces, clean up ngons |
| **VectorCraft SVG → Blender Extrude** | Logos, architectural moldings, emblem relief, mechanical brackets | Mathematically exact Bezier profiles | Convert Curve → Mesh, Limited Dissolve coplanar verts, add Bevel |

---

## 2. The Non-Destructive Modifier Stack Order (Blender 5.3)

Order matters! Always stack modifiers top-to-bottom in this exact sequence:
1. **`Mirror`** (with `use_clip = True`, `use_bisect_axis = True`)
2. **`Solidify`** (for thin armor plates/shells, `even_thickness = True`)
3. **`Boolean`** (`solver = 'EXACT'`, clean cutters hidden in render)
4. **`Bevel`** (`limit_method = 'WEIGHT'` or `'ANGLE'`, `segments = 2` or `3`, `miter_outer = 'MITER_ARC'`, `harden_normals = False` if using Weighted Normal below)
5. **`Subdivision Surface`** (only for SubD assets; remove for mid-poly)
6. **`Weighted Normal`** (`mode = 'FACE_AREA'`, `weight = 50`, `keep_sharp = True`) — eliminates flat-panel shading gradients across beveled edges!

---

## 3. VectorCraft → Blender 5.3 Precision Profile Pipeline

Use **VectorCraft** (`vectorcraft` MCP) whenever a 3D silhouette, panel engraving, gear tooth profile, stencil, or typographic badge needs razor-sharp 2D curves:
1. Author clean closed Bezier paths in VectorCraft (`draw_path`, `draw_shape`, Pathfinder booleans) and export `.svg` (`--outline-text --decimals 4`).
2. Import into Blender via `bpy.ops.import_curve.svg(filepath=...)`.
3. Normalize scale (SVG imports at ~`1/1000` scale depending on DPI), extrude (`curve.extrude`), add curve bevel (`curve.bevel_depth`), convert to mesh (`bpy.ops.object.convert(target='MESH')`), remesh or quad-cap planar faces, and apply transforms.

---

## 4. Visual Realism Details That Separate Pro From Amateur

- **Panel seams (0.5 mm–3 mm recessed gaps):** Never paint panel lines onto a flat cube if the camera gets close — inset + extrude inward OR sculpt/bake real recessed seams in TextureCraft.
- **Fasteners & micro-silhouettes:** Hex bolts, Phillips screws, chamfered vents, rubber feet, cable strain reliefs, recessed ports, and serial-number decals (`TextureCraft` `layer.add.decal` or `resource.text`).
- **Primary / Secondary / Tertiary form ratio (70 / 20 / 10):**
  - **70% Primary:** Large unmistakable silhouette + rest areas (blank panels give the eye room to breathe!).
  - **20% Secondary:** Functional sub-assemblies (handles, vents, hinges, screens).
  - **10% Tertiary:** Bolts, weld beads, bevel chamfers, micro-scratches.

## Related Notes
- [[Topology & Edge Flow Mastery]]
- [[Style 15 — Brutalist, Industrial Hard-Surface & Mecha]]
- [[Style 01 — Photorealistic Physically-Based (ArchViz & Product)]]
- [[Parametric CAD & 3D Printing (OpenSCAD, CadQuery, SolidCraft)]]
