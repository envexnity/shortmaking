---
title: Physics Simulations (Cloth, Rigid Body, Hair, Fluid, Smoke)
tags: [simulation, physics, cloth, rigid-body, hair, fluid, blender]
updated: 2026-11-20
---

# Physics Simulations (Cloth, Rigid Body, Hair, Fluid, Smoke)

---

## 1. Cloth Simulation (Garments, Capes, Cushions, Pillows)
- **Topology requirement:** Evenly distributed medium-res quads (`1–3 cm` edge length) — long thin stretched triangles kink and explode!
- **Scale:** Always simulate at **1:1 real-world metric scale** (or temporarily `×5` for tiny delicate silk lace, then scale back after baking to shape keys / Alembic).
- **Inflatable Cushions / Plushies Trick:** Enable `Cloth → Pressure` (`uniform_pressure_force = 2.0–6.0`, `gravity = 0.0`) on a closed stitched pillow mesh → run 20 frames → **Apply as Shape Key or Mesh** for instant ultra-realistic stuffed seams!
- **Real-Time Export:** Game engines can't read Blender's live cloth modifier — bake simulated cloth to **Alembic (`.abc`)**, **MDD**, **Shape Keys**, or drive runtime spring bones!

---

## 2. Rigid Body Physics (Clutter Scattering, Piles, Destruction)
- **Natural Clutter Pile Recipe:** Drop coins, books, fruit, rocks, or rubble into a bowl/floor via `Rigid Body (ACTIVE)` + `Collision Margin = 0.002 m` → run 80 frames until settled → **`bpy.ops.object.visual_transform_apply()`** → remove Rigid Body physics! Instant physically grounded natural piles with zero floating or overlap!
- **Destruction:** Pre-fracture with **Cell Fracture** addon → set shards `Active` with `Deactivation → Start Deactivated` so walls stay rock-solid until struck!

---

## 3. Hair Curves & Mantaflow Smoke/Fire
- **Blender 5.3 Hair Curves:** Use the modern Geometry Nodes Hair system (`Surface Deform` + `Interpolate Hair Curves` + `Clump` + `Frizz` + `Set Hair Curve Profile`) — 10× faster, procedural, and non-destructive compared to legacy Particle Hair.
- **Mantaflow Smoke / Fire / Liquid:** Always set `Domain` bounding box tight around the action + enable `Adaptive Domain` + `Noise` (upres factor `2`) + bake cache to an external folder (`VDB` OpenVDB format) so renders are deterministic and re-usable in Cycles / UE5 / Houdini!

## Related Notes
- [[Procedural Modeling & Geometry Nodes (Blender 5.3)]]
- [[Style 22 — Plush, Fabric, Knitwear & Woolly Tactile 3D]]
- [[Style 19 — Botanical, Nature, Terrain & Biomes (Foliage - Water - Clouds)]]
