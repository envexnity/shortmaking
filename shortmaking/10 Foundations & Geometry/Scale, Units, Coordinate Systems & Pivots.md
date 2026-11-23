---
title: Scale, Units, Coordinate Systems & Pivots
tags: [foundations, scale, coordinates, pivots, math, export]
updated: 2026-11-20
---

# Scale, Units, Coordinate Systems & Pivots

> [!CAUTION]
> Wrong scale breaks **cycles depth-of-field, subsurface scattering radius, physics gravity, bevel widths, ambient occlusion ray distance, and engine collision hulls** simultaneously.

---

## 1. Real-World Metric Reference Table

| Object Category | Real-World Metric Dimension | Blender Units (`1 u = 1 m`) |
|---|---|---|
| Coffee mug | `9.5 cm` tall × `8 cm` dia | `0.095 × 0.08` |
| Smartphone | `15 cm × 7.2 cm × 0.8 cm` | `0.15 × 0.072 × 0.008` |
| Chair seat height | `45 cm` | `0.45` |
| Desk / table height | `75 cm` | `0.75` |
| Standard interior door | `2.05 m × 0.90 m × 0.045 m` | `2.05 × 0.90 × 0.045` |
| Average adult human | `1.75 m` tall | `1.75` |
| Sedan car | `4.6 m L × 1.85 m W × 1.45 m H` | `4.6 × 1.85 × 1.45` |
| Story / ceiling height | `2.7 m–3.2 m` | `3.0` |
| Roblox Avatar (R15) | ~`5.0–5.5 studs` (`1 stud ≈ 0.28 m`) | `~1.5 m` in Blender |

---

## 2. Cross-Engine Coordinate Matrix

| Software / Format | Handedness | Up Axis | Forward Axis | Base Unit |
|---|---|---|---|---|
| **Blender 5.3** | Right-Handed | `+Z` | `-Y` (faces camera at `-Y`) | `1 meter` |
| **glTF 2.0 / GLB / Three.js** | Right-Handed | `+Y` | `+Z` (front) | `1 meter` |
| **Godot 4** | Right-Handed | `+Y` | `-Z` | `1 meter` |
| **USD / OpenUSD** | Right-Handed | `+Y` (default) or `+Z` | `-Z` | `1 cm` or `1 m` (`metersPerUnit`) |
| **Maya / Substance / TextureCraft** | Right-Handed | `+Y` | `+Z` | `1 cm` / `1 m` |
| **Unity** | Left-Handed | `+Y` | `+Z` | `1 meter` |
| **Unreal Engine 5** | Left-Handed | `+Z` | `+X` | `1 centimeter` |
| **Roblox Studio** | Right-Handed | `+Y` | `-Z` | `1 stud` (`≈ 0.28 m`) |
| **STL / 3D Print Slicers** | Right-Handed | `+Z` | `-Y` | `1 millimeter` |

---

## 3. Pivot & Origin Placement Contract

| Asset Type | Required Origin (`(0, 0, 0)`) | Why |
|---|---|---|
| **Characters & Creatures** | Ground center between feet (`Z = 0`) | Drops flush onto terrain/navmesh |
| **Furniture & Grounded Props** | Bottom-center footprint (`Z = min_z`) | Snaps cleanly onto floors & tables |
| **Doors, Hinges, Turrets, Wheels** | Exact mechanical rotation axis | Enables 1-line rotation animation |
| **Modular Wall / Floor Tiles** | Bottom-left grid corner on `0.5 m` or `1.0 m` grid | Snaps seamlessly in level editors |
| **Floating Collectibles / UI Icons** | Geometric center of mass | Clean turntable spin |

---

## 4. Exact Grounding & Transform Freeze Helper (`bpy`)

```python
import bpy
from mathutils import Vector

def ground_and_freeze(obj):
    """Seat object cleanly on Z=0 with bottom-center origin and scale=(1,1,1)."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    cx = 0.5 * (min(v.x for v in bbox) + max(v.x for v in bbox))
    cy = 0.5 * (min(v.y for v in bbox) + max(v.y for v in bbox))
    min_z = min(v.z for v in bbox)

    obj.location.x -= cx
    obj.location.y -= cy
    obj.location.z -= min_z
    bpy.context.view_layer.update()

    # Set origin to world (0,0,0)
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
```

## Related Notes
- [[AGENTS]]
- [[glTF - GLB & USD Export Pipeline (Zero-Defect Rules)]]
- [[Automated Mesh & GLB QA Gate (mesh_qa.py)]]
