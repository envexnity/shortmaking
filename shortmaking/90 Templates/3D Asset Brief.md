---
title: "{{title}}"
tags: [brief, asset, 3d]
style: ""
target_engine: ""
status: draft
updated: "{{date}}"
---

# 3D Asset Brief — {{title}}

## 1. Concept & Art Style Lock
- **Subject:**
- **Locked Art Style Note:** [[Style XX — ...]]
- **Reference Links / Attachments:**
- **Emotional Read (3 adjectives):**

## 2. Physical Scale & Technical Contract
- **Real-World Metric Bounding Box (`W × D × H` meters):**
- **Origin / Pivot Location:** Bottom-center `(0, 0, 0)` / Hinge axis / Center
- **Target Engine:** Blender Cycles / Three.js / UE5 / Unity / Godot / Roblox / 3D Print
- **Triangle Budget:**
- **Texture Resolution & Packing:** `2048×2048` / OpenGL or DirectX Normal / ORM or Separate
- **QA Gate Profile:** `web-hero` / `roblox-ugc` / `roblox-meshpart` / `game-hero` / `film-hero` / `3d-print`

## 3. Component & Material Breakdown (70 / 20 / 10 Rule)
| Part | MaterialCraft / TextureCraft Recipe | Metallic | Roughness Range | Special Notes |
|---|---|---|---|---|
| Primary Body (70%) | | | | |
| Secondary Assemblies (20%) | | | | |
| Tertiary Details & Decals (10%) | | | | |

## 4. Pipeline & Verification Checklist
- [ ] Geometry modeled cleanly in metric scale, transforms applied (`1,1,1`), outward normals
- [ ] Clean non-overlapping UVs with margin padding
- [ ] MaterialCraft `.mcmat` authored / TextureCraft mesh maps baked (`AO`, `Curvature`, `Normal`, `Position`)
- [ ] `mesh_qa.py` PASSED with zero fatal errors
- [ ] 3-Angle Renders inspected (`Hero 3/4`, `Side Silhouette`, `Material Close-Up`) — Critic Score `≥ 8.5 / 10`
