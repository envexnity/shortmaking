---
title: Style 13 — Roblox Stylized, Stud & UGC Accessory Pipeline
style_id: "13"
style_family: Stylized PBR
pbr_or_npr: Roblox PBR (SurfaceAppearance)
primary_engines: [Roblox Studio, Blender 5.3]
artcraft_tools: [TextureCraft, MaterialCraft, VectorCraft, FigCraft]
poly_budget: "≤ 4,000 tris (UGC) / ≤ 10,000 tris (MeshPart)"
texel_density: "1024×1024 Max (Color, Metal, Normal, Rough)"
lighting_key: "Future Lighting + Atmosphere + Bloom + Vibrant Rim"
tags: [art-style, roblox, ugc, stud, ropilot, surfaceappearance]
updated: 2026-11-20
---

# Style 13 — Roblox Stylized, Stud & UGC Accessory Pipeline

**Visual Benchmark:** Front-page Roblox hits (*Doors*, *Adopt Me*, *Blox Fruits*, *BedWars*, *Dress to Impress*, classic-modern Stud aesthetics) built cleanly with **Blender 5.3 + TextureCraft + Ropilot MCP**.

---

## 1. Platform Hard Limits & Metric Conversion
- **Scale:** `1 Roblox stud = 0.28 meters` (an R15 character is ~`5.2 studs ≈ 1.46 m`). Always export `.fbx` / `.glb` with `Scale = 0.01` (or calibrated FBX meter-to-stud scale) and verify in Studio via `ropilot` MCP!
- **Triangle Caps (Non-Negotiable):**
  - **UGC Accessories:** Hard cap **`4,000 triangles`** (`1,200 verts` on some older cages; verify current Marketplace spec), single `1024×1024` texture!
  - **Standard `MeshPart`:** Safe universal cap **`10,000 triangles`** (new MeshPart uploader supports up to `20k`, but keep game props `500–4,000` tris for 60 fps mobile!).
  - **Collision:** Set `CollisionFidelity = Box` or `Hull` (NEVER `PreciseConvexDecomposition` on decorative foliage/clutter!).

## 2. Three Roblox Visual Registers
1. **Classic-Modern Stud Style:** Crisp tactile stud patterns authored in **MaterialCraft** (`fx_map` cylindrical stud array + bevel normal + slight satin plastic roughness `0.32`), bold vibrant saturated colors, clean chunky silhouettes.
2. **Simulator / Pet / Anime Stylized:** Bright chunky forms, baked top-down gradient + warm cavity AO from **TextureCraft** (`1024×1024`), soft plastic/gloss contrast, crisp silhouette read on tiny phone screens.
3. **High-Fidelity PBR (`SurfaceAppearance` + `Future` Lighting):** 4-map PBR (`ColorMap`, `MetalnessMap`, `NormalMap [OpenGL +Y]`, `RoughnessMap`) exported from **TextureCraft** at `1024×1024` (Roblox's max texture resolution!).

## 3. TextureCraft → Roblox Studio Export Rules
- Use `normalFormat: "openGl"` (`+Y` green channel).
- Export 4 separate PNGs at `1024×1024` (`Color`, `Roughness`, `Metalness`, `Normal`) — Roblox `SurfaceAppearance` does NOT use packed ORM!
- For UI icons & 3D shop thumbnails: Pair with **ForgeGUI** MCP and **FigCraft** MCP!

## 4. Style Anti-Patterns
- Uploading 50k-tri unoptimized AI meshes into Roblox (crashes mobile players and fails UGC limits).
- Leaving `Default` grey `Plastic` material on every part without custom `MaterialVariant` or `SurfaceAppearance`.
- Oversized 4K textures (Roblox automatically downscales everything to `1024×1024` max — author crisp at `1024` so UV details stay sharp!).

## Related Notes
- [[Roblox Studio 3D Pipeline (Ropilot + ForgeGUI + Blender)]]
- [[Roblox R6-R15, Mixamo & Game-Ready Skeletal Export]]
- [[Style 03 — Stylized PBR (Pixar - Disney - Overwatch - Fortnite)]]
- [[GitHub 3D Modeling Skills Index]] (`roblox-ai-skills`)
