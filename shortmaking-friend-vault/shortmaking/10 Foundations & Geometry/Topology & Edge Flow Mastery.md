---
title: Topology & Edge Flow Mastery
tags: [foundations, topology, modeling, subd, retopology]
updated: 2026-11-20
---

# Topology & Edge Flow Mastery

> [!IMPORTANT]
> Good topology is not about making wireframes look pretty — it is about **predictable subdivision, clean silhouette shading, zero baking artifacts, and crease-free skeletal deformation**.

---

## 1. The Four Polygon Rules

| Element | Where Allowed | Where Forbidden |
|---|---|---|
| **Quads (4-sided)** | Everywhere — especially SubD cages, deforming character meshes, curved surfaces | Never forbidden |
| **Triangles (3-sided)** | Flat hard-surface caps, final game-engine triangulated exports, hidden termination areas | High-curvature SubD poles, bending joints (elbows, knees, eyelids, mouth) |
| **N-gons (5+ sides)** | Completely planar hard-surface areas surrounded by a perimeter holding bevel (before triangulation) | Any curved surface, any deforming mesh, any SubD cage without perimeter loop |
| **Poles (3-edge or 5-edge vertices)** | Redirecting edge flow on low-curvature surfaces | Direct crease lines, high-curvature bends, silhouette ridges |

---

## 2. Hard-Surface vs. Deforming Topology

### Hard-Surface / SubD Support Loops
- **Holding edges (proximity loops):** Place two loops tightly flanking a 90° corner (`0.002 m–0.01 m` offset) OR use a non-destructive **Bevel Modifier** (`limit_method = 'ANGLE'`, `angle_limit = math.radians(30)`, `segments = 2`, `harden_normals = True`) + **Weighted Normal Modifier** (`keep_sharp = True`).
- **Cylinder intersections:** Match segment counts mathematically before boolean/bridging. A cylinder penetrating a curved surface needs at least `16–32` segments on the host cylinder so shading does not pinch.
- **Avoid 6+ edge star poles** on reflective surfaces — they create "pinch stars" under specular highlights.

### Organic / Deforming Joint Loops
- Every hinged joint (elbow, knee, finger, ankle) requires **at least 3 concentric edge loops** around the bend axis:
  - Inner crease: compressed loops (`collapse` side)
  - Outer stretch: wider spaced loops (`expand` side) — diamond/kite quad redirection works best.
- Facial animation mandates **concentric ring topology**:
  - `O-loops` around both eyes (goggles mask)
  - `O-loops` around mouth + nasolabial fold loop wrapping nose-to-chin
  - Zero triangles inside the smile/eyelid deformation zones.

---

## 3. Blender 5.3 Headless Topology Audit (`bmesh`)

```python
import bpy, bmesh

def audit_topology(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    tris = sum(1 for f in bm.faces if len(f.verts) == 3)
    quads = sum(1 for f in bm.faces if len(f.verts) == 4)
    ngons = sum(1 for f in bm.faces if len(f.verts) > 4)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    loose_verts = sum(1 for v in bm.verts if not v.link_edges)
    zero_area = sum(1 for f in bm.faces if f.calc_area() < 1e-8)

    bm.free()
    return {
        "verts": len(obj.data.vertices),
        "tris": tris, "quads": quads, "ngons": ngons,
        "non_manifold_edges": non_manifold,
        "loose_verts": loose_verts,
        "zero_area_faces": zero_area,
    }
```

### Mandatory Pre-Export Cleanup Pass
1. `bpy.ops.mesh.select_all(action='SELECT')`
2. `bpy.ops.mesh.remove_doubles(threshold=0.0001)` (merge coincident vertices)
3. `bpy.ops.mesh.delete_loose()` (strip stray vertices/edges)
4. `bpy.ops.mesh.normals_make_consistent(inside=False)` (fix flipped normals)
5. Verify via [[Automated Mesh & GLB QA Gate (mesh_qa.py)]].

---

## Related Notes
- [[Hard-Surface & SubD Modeling Playbook]]
- [[Organic Sculpting, Retopology & Anatomy]]
- [[UV Unwrapping, Texel Density & UDIMs]]
- [[Craft Floor — Non-Negotiable 3D Quality Gates]]
