---
title: Craft Floor — Non-Negotiable 3D Quality Gates
tags: [qa, craft-floor, quality, checklist, ship-gate]
updated: 2026-11-20
---

# Craft Floor — Non-Negotiable 3D Quality Gates

> [!CAUTION]
> **Nothing ships below the Craft Floor.** If an asset fails ANY Tier-1 blocker below, fix it immediately before showing the user or exporting final deliverables.

---

## Tier 1 — Hard Geometric & Technical Blockers (Must Pass 100%)
- [ ] **Real-world metric scale:** Dimensions match physical reference (not 0.004 m or 48 m!).
- [ ] **Applied transforms:** Every mesh has `scale == (1.0, 1.0, 1.0)` (zero negative scale!).
- [ ] **Grounded pivot:** Seated cleanly at `Z = 0` (bottom-center for props/characters) with zero accidental air gap or floor sinking.
- [ ] **Zero floating or colliding sub-parts:** Every attachment physically contacts its parent with mathematically calculated contact coordinates.
- [ ] **Outward manifold normals:** Zero inside-out transparent faces, zero duplicate coplanar z-fighting planes.
- [ ] **Clean UVs:** Non-overlapping `[0,1]` islands (or intentional UDIM tiles) with margin padding (`≥ 8–16 px`), zero extreme stretch.
- [ ] **`mesh_qa.py` PASS:** Zero fatal errors for target profile (`web-hero`, `roblox-ugc`, `roblox-meshpart`, `game-prop`, `film-hero`, `3d-print`).

## Tier 2 — Material & Look-Dev Gates
- [ ] **Zero flat `Roughness = 0.5` plastic:** Every surface has multi-frequency roughness variation appropriate to its locked Art Style.
- [ ] **Physically calibrated Albedo / Metallic:** Dielectrics stay within `0.03–0.85` linear reflectance; metals are `Metallic = 1.0`.
- [ ] **Correct normal handedness & color spaces:** OpenGL vs DirectX verified; all data maps set to `Non-Color` / `Linear`.
- [ ] **Bevel light-catch discipline:** Hard edges catch subtle specular rims (unless explicitly flat-faceted retro style).

## Tier 3 — Lighting, Presentation & Style Fidelity Gates
- [ ] **Unmistakable Style Lock:** Silhouette, topology, shaders, lighting, and color management ALL match the chosen `Style XX` note in `20 Art Styles Encyclopedia/`.
- [ ] **3-Angle Visual Inspection Complete:** Hero 3/4 + Side/Rear Silhouette + Close-Up Material detail rendered and visually audited via [[The Visual Critic & Cook Loop for 3D Assets]].
- [ ] **Critic Score `≥ 8.5 / 10`:** Zero unresolved visual defects.

## Related Notes
- [[The Visual Critic & Cook Loop for 3D Assets]]
- [[Anti-Patterns — What Screams AI-Generated 3D Slop]]
- [[Automated Mesh & GLB QA Gate (mesh_qa.py)]]
- [[AGENTS]]
