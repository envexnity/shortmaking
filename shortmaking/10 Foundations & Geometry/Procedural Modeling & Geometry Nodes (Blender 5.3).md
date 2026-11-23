---
title: Procedural Modeling & Geometry Nodes (Blender 5.3)
tags: [foundations, geometry-nodes, procedural, blender, scattering]
updated: 2026-11-20
---

# Procedural Modeling & Geometry Nodes (Blender 5.3)

Geometry Nodes turn static meshes into **parametric generators** — ideal for AI agents because every parameter (count, seed, width, density, wear) stays editable without regenerating geometry from scratch.

---

## 1. Core Procedural Patterns for Agents

| Pattern | Node Graph Spine | Best Use Cases |
|---|---|---|
| **Surface Scatter (Poisson Disk)** | `Distribute Points on Faces (POISSON)` → `Align Rotation to Vector` → `Random Value (Scale/Rot)` → `Instance on Points` | Foliage, pebbles, rivets, moss, debris, crowds |
| **Curve-to-Tube / Cable / Rope** | `Curve` → `Resample Curve` → `Set Curve Radius` (with noise/taper) → `Curve to Mesh (Curve Circle)` | Cables, pipes, vines, hair strands, stylized outlines |
| **Parametric Architectural Array** | `Grid` / `Mesh Line` → `Instance on Points` + `Switch` by index (corners vs walls vs windows) → `Realize Instances` → `Merge by Distance` | Buildings, fences, bridges, sci-fi corridors, stairs |
| **SDF / Volume Remesh** | `Mesh to Volume` → `Volume to Mesh` (voxel size + adaptivity) → `Set Shade Smooth` | Melting wax, stylized clouds, organic welds, clay blobs |
| **Proximity / Ambient Wear Mask** | `Geometry Proximity` → `Map Range` → `Store Named Attribute ("wear_mask")` | Drive Blender shaders with distance-to-floor or contact dirt! |

---

## 2. Blender 5.3 `bpy` Geometry Nodes Builder Snippet

```python
import bpy

def add_scatter_geonodes(emitter_obj, instance_col, density=12.0, min_dist=0.15, seed=42):
    mod = emitter_obj.modifiers.new(name="ProceduralScatter", type='NODES')
    ng = bpy.data.node_groups.new(name="ScatterTree", type='GeometryNodeTree')
    mod.node_group = ng

    # Blender 4.0+ / 5.3 interface API (NOT ng.inputs / ng.outputs!)
    ng.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    n_in = ng.nodes.new('NodeGroupInput')
    n_out = ng.nodes.new('NodeGroupOutput')
    n_dist = ng.nodes.new('GeometryNodeDistributePointsOnFaces')
    n_dist.distribute_method = 'POISSON'
    n_dist.inputs['Distance Min'].default_value = min_dist
    n_dist.inputs['Density Max'].default_value = density
    n_dist.inputs['Seed'].default_value = seed

    n_col = ng.nodes.new('GeometryNodeCollectionInfo')
    n_col.inputs['Collection'].default_value = instance_col
    n_col.inputs['Separate Children'].default_value = True
    n_col.inputs['Reset Children'].default_value = True

    n_inst = ng.nodes.new('GeometryNodeInstanceOnPoints')
    n_inst.inputs['Pick Instance'].default_value = True

    n_join = ng.nodes.new('GeometryNodeJoinGeometry')

    ng.links.new(n_in.outputs['Geometry'], n_dist.inputs['Mesh'])
    ng.links.new(n_dist.outputs['Points'], n_inst.inputs['Points'])
    ng.links.new(n_col.outputs['Instances'], n_inst.inputs['Instance'])
    ng.links.new(n_in.outputs['Geometry'], n_join.inputs['Geometry'])
    ng.links.new(n_inst.outputs['Instances'], n_join.inputs['Geometry'])
    ng.links.new(n_join.outputs['Geometry'], n_out.inputs['Geometry'])
    return ng
```

> [!WARNING]
> **Blender 4.0–5.3 API Change:** `node_group.inputs.new(...)` was removed! Always use `node_group.interface.new_socket(name=..., in_out='INPUT'|'OUTPUT', socket_type=...)`.

---

## 3. Exporting Geometry Nodes to GLB / TextureCraft

Before exporting to glTF/GLB or importing into TextureCraft:
- Add a **`Realize Instances`** node before `Group Output` (or check `Apply Modifiers` on export) — otherwise un-realized instances may vanish or lose UV attributes in downstream tools.
- Store custom procedural attributes as **UVMap** or **Color Attributes** (`Byte Color` / `Float Color`) so Three.js & TextureCraft can read them!

## Related Notes
- [[Blender 5.3 API & Headless Scripting Reference]]
- [[Style 19 — Botanical, Nature, Terrain & Biomes (Foliage - Water - Clouds)]]
- [[Style 18 — Abstract Motion Graphics, Glassmorphism & Iridescent (Cinema4D - Awwwards)]]
- [[GitHub 3D Modeling Skills Index]] (`XliuXjianX/blender-production-skills`)
