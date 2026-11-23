---
title: Parametric CAD & 3D Printing (OpenSCAD, CadQuery, SolidCraft)
tags: [foundations, cad, openscad, cadquery, solidcraft, 3d-printing]
updated: 2026-11-20
---

# Parametric CAD & 3D Printing (OpenSCAD, CadQuery, SolidCraft)

When a model must meet **exact millimeter tolerances, mechanical threads, enclosures, gears, brackets, or watertight FDM/SLA 3D printing**, code-driven B-Rep / CSG CAD beats polygon modeling every time.

---

## 1. Engine Selection Matrix

| Engine | Paradigm | Output Formats | Best For | Vendored Skill / MCP |
|---|---|---|---|---|
| **CadQuery / build123d (Python)** | B-Rep (OpenCASCADE) | `.step`, `.stl`, `.3mf`, `.dxf` | Engineering enclosures, exact fillets/chamfers, CNC, functional parts | `80 Tools & MCPs/skills/flowful-cadquery-skill/SKILL.md` |
| **OpenSCAD** | CSG scripting (`.scad`) | `.stl`, `.3mf`, `.off` | Parametric grids, organizers, rapid math-driven geometry | `RobertCoop/openscad-mcp`, `forge3d` |
| **SolidCraft** (`tangency-labs/solidcraft`) | Pure Rust Parametric CAD + MCP | `.step`, `.stl`, `.glb` | Agent-native interactive + headless parametric CAD | MCP server built-in |
| **Bambu Studio AI** | Slicer + MakerWorld/Printables QA | `.3mf`, `.gcode` | End-to-end slicing, overhang checks, AMS color mapping | `80 Tools & MCPs/skills/bambu-studio-3d-print-ai/SKILL.md` |

---

## 2. FDM 3D Printing Design Rules (Zero-Failure Specs)

| Rule | Standard 0.4 mm Nozzle Spec | Why |
|---|---|---|
| **Minimum wall thickness** | `≥ 1.2 mm` (3 perimeters; `≥ 1.6 mm` structural) | Prevents hollow gaps and brittle snaps |
| **Clearance (moving/mating parts)** | `0.20 mm` snug press-fit · `0.30–0.40 mm` sliding fit · `0.50 mm` print-in-place hinge | Compensates for thermal expansion & extrusion squish |
| **Maximum overhang angle** | `≤ 45°` from vertical (up to `55°` with good cooling) | Eliminates ugly support scarring |
| **Bridging span** | `≤ 15 mm` unsupported | Prevents sag |
| **Bottom chamfers over fillets** | Use `45°` chamfer on bed-touching edges (never round fillet!) | Bottom fillets start at 80° overhang and curl |
| **Horizontal hole teardrop** | Add `45°` roof peak on horizontal bolt holes | Prevents top sagging on circular holes |
| **Minimum embossed text** | Stroke width `≥ 0.6 mm`, depth/height `0.4–0.8 mm` | Crisp readability with 0.4 mm nozzle |

---

## 3. CadQuery Reference Pattern (Parametric Enclosure)

```python
import cadquery as cq

W, D, H = 80.0, 50.0, 28.0
WALL, FILLET = 2.0, 3.0

box = (
    cq.Workplane("XY")
    .box(W, D, H, centered=(True, True, False))
    .edges("|Z").fillet(FILLET)
    .faces(">Z").shell(-WALL)
    .edges("<Z").chamfer(0.8)  # 45° bed chamfer (no overhang curl!)
)
cq.exporters.export(box, "enclosure.step")
cq.exporters.export(box, "enclosure.stl", tolerance=0.01, angularTolerance=0.1)
```

---

## 4. Mesh Verification Before Slicing

Always check **watertightness** (`is_watertight == True`), **zero non-manifold edges**, **positive volume**, and **flat bed contact (`min_z == 0`)** using [[Automated Mesh & GLB QA Gate (mesh_qa.py)]] or the installed `3d-print-check` skill!

## Related Notes
- [[3D Printing & Fabrication Export (STL, 3MF, STEP)]]
- [[Hard-Surface & SubD Modeling Playbook]]
- [[3D MCP Ecosystem & Setup Guide (Blender, CAD, Game Engines, AI Gen, Assets)]]
