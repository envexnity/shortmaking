---
title: Unreal Engine 5, Unity & Godot 4 Import Specs
tags: [engines, unreal, unity, godot, fbx, glb, usd, pbr]
updated: 2026-11-20
---

# Unreal Engine 5, Unity & Godot 4 Import Specs

---

## 1. Engine-by-Engine Master Import Matrix

| Spec | Unreal Engine 5 | Unity (URP / HDRP) | Godot 4 |
|---|---|---|---|
| **Best Mesh Format** | `.fbx` / `.usd` / `.glb` | `.fbx` / `.glb` | **`.glb` (native first-class!)** |
| **Normal Map Format** | **DirectX (`-Y` Green)** | OpenGL (`+Y` Green) | OpenGL (`+Y` Green) |
| **Packed Map Layout** | **ORM** (`R=AO, G=Rough, B=Metal`, sRGB OFF!) | **MaskMap** (`R=Metal, G=AO, B=Detail, A=Smoothness [1-Rough]`) | **ORM** (auto-mapped from glTF!) |
| **Scale / Axis** | `+Z` Up, Left-Handed, `cm` | `+Y` Up, Left-Handed, `m` | `+Y` Up, Right-Handed, `m` |
| **High-Poly / LODs** | **Nanite** (disable on foliage cards / translucent glass!) | 3-tier LODGroup (`100% / 50% / 20%`) | Auto-LOD on glTF import |
| **Lighting GI** | Lumen Hardware/Software RT | Baked Lightmaps / APV | SDFGI / VoxelGI / LightmapGI |

---

## 2. TextureCraft Export Preset Routing

- **For UE5:** `file.exportTextures { "normalFormat": "directX", "padding": "dilation", "colorSpace": "sRGB" }` + pack ORM (ensure `sRGB` checkbox is **OFF** in UE5 Texture Editor for ORM & Normal!).
- **For Unity HDRP/URP:** Invert Roughness → Smoothness (`1 - Roughness`) in the Alpha channel of MaskMap (`openGl` normals).
- **For Godot 4:** Export directly as `.glb` via TextureCraft `mesh_export` or Blender `export_scene.gltf` — Godot 4 parses every PBR channel, ORM map, emission, animation NLA track, and collision suffix (`-col`, `-colonly`) automatically!

---

## 3. Collision Naming Suffixes (Zero Manual Setup!)
- **Unreal Engine 5:** `UCX_<MeshName>_01` (convex hull), `UBX_<MeshName>_01` (box), `USP_<MeshName>_01` (sphere).
- **Godot 4:** Append `-col` (static trimesh), `-convcol` (convex hull), `-colonly` (invisible collider mesh) directly to Blender object names!

## Related Notes
- [[Scale, Units, Coordinate Systems & Pivots]]
- [[glTF - GLB & USD Export Pipeline (Zero-Defect Rules)]]
- [[3D MCP Ecosystem & Setup Guide (Blender, CAD, Game Engines, AI Gen, Assets)]]
