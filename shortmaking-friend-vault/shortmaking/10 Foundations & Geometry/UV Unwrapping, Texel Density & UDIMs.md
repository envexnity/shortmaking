---
title: UV Unwrapping, Texel Density & UDIMs
tags: [foundations, uv, texel-density, udim, texturecraft, baking]
updated: 2026-11-20
---

# UV Unwrapping, Texel Density & UDIMs

> [!IMPORTANT]
> Bad UVs ruin the best sculpture and the best material graph. **Every hard shading split (sharp edge ≥ 70°) MUST also be a UV seam** when baking normal maps — otherwise black edge seams appear on every bevel.

---

## 1. Golden Rules of UV Layout

1. **Hide seams where cameras rarely look:** undersides, inner arms, cloth stitches, mechanical panel gaps, material boundaries.
2. **Hard Edge = UV Seam Rule:** Whenever an edge is marked Sharp (split normal) on a low-poly bake target, split its UV seam too so tangent-space normal rays don't fight across shared UV pixels.
3. **Straighten rectangular strips:** Cylindrical tubes, cables, trim sheets, and straps should be straightened (`Follow Active Quads` / UV rectifying) so horizontal/vertical textures and edge-wear generators align cleanly without stair-step aliasing.
4. **Texel density consistency:** Keep pixels-per-meter uniform across an asset (exceptions: give character faces +1.5×–2× density; shrink unseen bottoms/interiors to 0.5×).
5. **Apply object scale BEFORE unwrapping!** Unwrapping with non-uniform scale `(1, 1, 4)` stretches UVs by 400%.

---

## 2. Padding & Mipmap Bleeding Table

Mipmaps halve texture resolution repeatedly (`2048 → 1024 → 512 → 256 → 128...`). Without island margin + dilation padding, background pixels bleed across seams at distance.

| Texture Resolution | Minimum UV Island Margin | TextureCraft Export Padding Mode |
|---|---|---|
| `512 × 512` | `4 px` (`margin=0.008`) | `dilation` (`4–8 px`) or `infinite` |
| `1024 × 1024` | `8 px` (`margin=0.008`) | `dilation` (`8–16 px`) or `infinite` |
| `2048 × 2048` | `16 px` (`margin=0.008`) | `dilation` (`16–32 px`) or `infinite` |
| `4096 × 4096` | `32 px` (`margin=0.008`) | `dilation` (`32+ px`) or `infinite` |

---

## 3. UDIM Workflows (Hero Film, VFX & Multi-Tile TextureCraft)

UDIM numbering starts at **`1001`** (`U ∈ [0,1], V ∈ [0,1]`), incrementing horizontally (`1002`, `1003`... up to `1010`), then next row (`1011`...).
- **Use UDIMs when:** A single hero asset needs extreme close-up resolution across head (`1001`), torso (`1002`), arms (`1003`), legs (`1004`), gear (`1005`) without splitting into 5 separate materials.
- **TextureCraft native UDIM support:**
  - `file.new { "mesh": "hero.glb", "uvTiles": true }` automatically enables UDIM mode when UVs extend past tile `1001`.
  - Override per-tile resolution with `textureSet.tile.resolution { "tile": 1001, "resolution": 4096 }` (4K face, 2K body!).
  - Toggle baking per tile with `bake.tile.set { "tile": 1002, "enabled": true }`.
- **Warning for Web/Three.js & Roblox:** WebGL/glTF 2.0 and Roblox do **NOT** natively support UDIM tiles! For web/Roblox, split by **Material Slots / Texture Sets** (every UV stays inside `[0, 1]`).

---

## 4. Blender 5.3 Headless Smart UV + Packing Script

```python
import bpy, math

def unwrap_and_pack(obj, angle_deg=66.0, margin=0.015):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(
        angle_limit=math.radians(angle_deg),
        island_margin=margin,
        area_weight=0.0,
        correct_aspect=True,
        scale_to_bounds=False
    )
    bpy.ops.uv.pack_islands(margin=margin, rotate=True)
    bpy.ops.object.mode_set(mode='OBJECT')
```

---

## 5. UV Inspection in TextureCraft

Before painting, inspect the UV report via `texturecraft-cli info asset.glb` or MCP `session_inspect`, and visually verify checker distortion with:
```json
{ "id": "viewport.view", "params": { "mode": "uvChecker" } }
```

## Related Notes
- [[TextureCraft Mastery — Baking, Smart Materials & 3D Painting]]
- [[Topology & Edge Flow Mastery]]
- [[glTF - GLB & USD Export Pipeline (Zero-Defect Rules)]]
