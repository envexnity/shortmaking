---
title: Procedural Noise, Grunges & Weathering Patterns
tags: [materials, procedural, weathering, noise, materialcraft, texturecraft]
updated: 2026-11-20
---

# Procedural Noise, Grunges & Weathering Patterns

How to make every surface feel lived-in, physically grounded, and immune to sterile "default CG" uniformity.

---

## 1. The 3-Frequency Surface Rule

Every believable surface (photoreal OR stylized) combines three spatial frequencies:

| Frequency | Wavelength | Purpose | Tooling |
|---|---|---|---|
| **Low (Macro)** | `0.5 m – 5.0 m` | Ambient gradients, water leaks, sun bleaching, top-to-bottom value ramp, large wear zones | MaterialCraft `fx_map` / TextureCraft `position` & `ambientOcclusion` generators |
| **Medium (Meso)** | `2 cm – 30 cm` | Scratches, dents, paint chips, brick mortar, fabric weave, wood knots | MaterialCraft `distance` + `directional_warp` / TextureCraft `edgeWear` & `dirt` + `slopeBlur` |
| **High (Micro)** | `0.2 mm – 5 mm` | Pores, brushed metal grain, dust specks, clay thumbprints, leather pebble | MaterialCraft `pixel_processor` / TextureCraft `matFinishSanded` / `matFinishGrind` |

---

## 2. Weathering Logic (Tell a Physical Story)

Never sprinkle random noise everywhere! Ask *where does physical interaction happen?*
- **Gravity & Rain (`direction` + `position`):** Rust streaks, moss, lime buildup, and grime drip **downward** from protruding bolts, ledges, and sills.
- **Human Touch (`curvature` + `edgeWear`):** Handles, triggers, railings, and stair treads get **polished smoother** (lower roughness, exposed metal/wood) while surrounding corners stay dusty and matte.
- **Ground Contact (`position` Z-gradient):** Bottom `0–25 cm` gathers mud splashes, dark moisture (lower roughness where wet, higher roughness where dry dust), and scuffs.
- **Heat & Friction:** Exhaust pipes and gun barrels exhibit iridescent blue/straw/purple **heat temper oxidation** bands near the source, transitioning to matte carbon soot at the muzzle.

## Related Notes
- [[PBR Physics Reference (Albedo, Metallic, Roughness, IOR, SSS)]]
- [[MaterialCraft Mastery — Node Library & Procedural Graphs]]
- [[TextureCraft Mastery — Baking, Smart Materials & 3D Painting]]
- [[Anti-Patterns — What Screams AI-Generated 3D Slop]]
