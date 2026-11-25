---
title: glTF - GLB & USD Export Pipeline (Zero-Defect Rules)
tags: [export, gltf, glb, usd, usdz, draco, ktx2, blender]
updated: 2026-11-20
---

# glTF / GLB & USD Export Pipeline (Zero-Defect Rules)

**glTF 2.0 (`.glb`)** is the JPEG of real-time 3D (Web / Three.js / Godot / Unity / Roblox / TextureCraft). **OpenUSD (`.usd`, `.usda`, `.usdc`, `.usdz`)** is the universal scene interchange standard for VFX, Unreal Engine 5, Apple VisionOS/AR, and TextureCraft.

---

## 1. Blender 5.3 Canonical GLB Export (`bpy`)

```python
import bpy

def export_clean_glb(filepath, selected_only=True, draco=False):
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        use_selection=selected_only,
        export_yup=True,
        export_apply=True,             # Applies modifiers cleanly
        export_texcoords=True,
        export_normals=True,
        export_materials='EXPORT',
        export_image_format='WEBP',    # Or 'AUTO' / 'PNG' for lossless
        export_animations=True,
        export_nla_strips=True,
        export_draco_mesh_compression_enable=draco,
        export_draco_mesh_compression_level=6 if draco else 0,
    )
```

---

## 2. glTF Material Compatibility Rules (Avoid Broken Web Renders!)
- glTF 2.0 ONLY exports **Principled BSDF** (and basic Unlit `Background`/`Emission`)! Complex procedural Blender noise graphs (Perlin, Voronoi, ColorRamp) **DO NOT EXPORT** into GLB — you MUST either:
  1. Author materials in **MaterialCraft** → paint/bake in **TextureCraft** → export textures / GLB (`mesh_export`), OR
  2. Bake procedural Blender nodes to 2K PNG maps (`Base Color`, `Roughness`, `Metallic`, `Normal`, `AO`) before GLB export!
- **ORM Packing (`KHR_materials_*`):** glTF natively packs `R = Ambient Occlusion`, `G = Roughness`, `B = Metallic` into one texture!
- **Web Size Optimization:** Run `gltf-transform optimize in.glb out.glb --compress draco --texture-compress webp --texture-size 2048` (or KTX2 BasisU GPU-compressed textures) to shrink 40 MB raw GLBs down to **1.5–4 MB**!

---

## 3. OpenUSD / USDZ Export (VFX, Apple AR & UE5)
- TextureCraft natively exports `.usda`, `.usdc`, and `.usdz` via `file.exportMesh` AND OpenPBR `.mtlx` via `file.exportTextures { materialX: true }`!
- Blender 5.3 natively exports USD via `bpy.ops.wm.usd_export(filepath=..., export_materials=True, export_textures=True, generate_preview_surface=True)`.

## Related Notes
- [[Automated Mesh & GLB QA Gate (mesh_qa.py)]]
- [[Three.js, React Three Fiber & WebGPU Production]]
- [[MaterialCraft-to-TextureCraft-to-Blender-to-Engine Bridge]]
- [[Scale, Units, Coordinate Systems & Pivots]]
