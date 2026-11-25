---
title: 3D Printing & Fabrication Export (STL, 3MF, STEP)
tags: [3d-printing, stl, 3mf, step, fabrication, cad, watertight]
updated: 2026-11-20
---

# 3D Printing & Fabrication Export (STL, 3MF, STEP)

---

## 1. Format Selection

| Format | Best For | Key Advantage |
|---|---|---|
| **`.step` (AP214/AP203)** | CNC machining, CAD interchange, Bambu Studio / PrusaSlicer high-precision curves | Exact mathematical NURBS curves — zero polygon faceting! |
| **`.3mf`** | Multi-color AMS/MMU printing, modern slicers | Embeds millimeter units, multi-material color groups, print orientation, and metadata |
| **`.stl` (Binary)** | Universal fallback for every slicer | Simple triangle soup — always specify **millimeters** on export! |

---

## 2. Mandatory Pre-Print Watertightness Checklist
1. **Manifold & Closed:** Zero open boundary edges, zero internal stray faces, zero non-manifold edges (`non_manifold == 0`).
2. **Consistent Outward Normals:** Positive enclosed volume (`volume > 0`).
3. **Flat Bed Contact:** Base sits cleanly at `Z = 0` with a `45°` bottom chamfer (`0.4–0.8 mm`) to prevent elephant's foot & overhang curling.
4. **Wall Thickness & Overhangs:** Walls `≥ 1.2 mm` (FDM 0.4 mm nozzle) or `≥ 1.0 mm` (SLA resin + drain holes for hollow prints!); overhangs `≤ 45°`.
5. **Blender Millimeter Export Setup:** Set `unit_settings.scale_length = 0.001` (`MILLIMETERS`) OR set `global_scale = 1000.0` in `bpy.ops.wm.stl_export` when modeling in meters!

---

## 3. Vendored CAD & 3D Printing Skills
- `80 Tools & MCPs/skills/flowful-cadquery-skill/SKILL.md` (★734 — parametric CadQuery generation)
- `80 Tools & MCPs/skills/bambu-studio-3d-print-ai/SKILL.md` (★282 — Bambu Lab AMS & printability)
- Built-in `3d-print-check` skill (`cq-viewer` overhang, bed contact, thin-wall audit)

## Related Notes
- [[Parametric CAD & 3D Printing (OpenSCAD, CadQuery, SolidCraft)]]
- [[Automated Mesh & GLB QA Gate (mesh_qa.py)]]
- [[Style 21 — Technical Blueprint, Wireframe, X-Ray & Exploded CAD]]
