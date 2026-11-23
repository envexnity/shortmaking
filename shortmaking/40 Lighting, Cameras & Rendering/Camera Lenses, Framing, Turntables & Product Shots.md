---
title: Camera Lenses, Framing, Turntables & Product Shots
tags: [camera, framing, turntable, lenses, dof, blender]
updated: 2026-11-20
---

# Camera Lenses, Framing, Turntables & Product Shots

---

## 1. Focal Length Psychology (35mm Full-Frame Sensor)

| Lens | Visual Effect | Best 3D Use Cases |
|---|---|---|
| **`18–24 mm`** | Dramatic forced perspective, monumental scale | Cathedrals, brutalist skyscrapers, cramped cyberpunk alleys |
| **`35 mm`** | Cinematic storytelling documentary feel | Environmental shots, character-in-world framing, ArchViz |
| **`50 mm`** | Natural human eye proportion | General asset hero shots, balanced character portraits |
| **`85–135 mm`** | Flattering compression, zero nose/edge distortion | Product renders, character busts, luxury watch/jewelry, toys |
| **`ORTHO`** | Zero perspective convergence | Isometric dioramas (`X=54.736°, Z=45°`), Pixel-Art 3D, Blueprint CAD |

---

## 2. Mandatory 3-Angle Visual QA Turntable Spec

Every AI agent MUST render at least these 3 inspection stills before finishing an asset (plus optional 360° turntable):
1. **`01_hero_3q.png`:** Front-right 3/4 view (`Yaw = 35°`, `Pitch = 18°`, `Lens = 65 mm`, object fills `70–75%` of frame height).
2. **`02_side_silhouette.png`:** Pure side/profile OR rear-left 3/4 view (exposes floating parts, back-face holes, and posture/proportion errors!).
3. **`03_closeup_material.png`:** Tight close-up (`85 mm`, `f/4.0`) focused on primary bevel/material junction (proves roughness breakup, micro-bevels, and UV sharpness!).

---

## 3. Exact Auto-Framing Camera Helper (`bpy`)

```python
import bpy, math
from mathutils import Vector

def frame_object_camera(cam, target_objs, yaw_deg=35.0, pitch_deg=18.0, lens_mm=65.0, fill=0.72):
    """Mathematically frame bounding sphere of target_objs with zero clipping."""
    coords = []
    for ob in target_objs:
        coords.extend([ob.matrix_world @ Vector(c) for c in ob.bound_box])
    bmin = Vector((min(v.x for v in coords), min(v.y for v in coords), min(v.z for v in coords)))
    bmax = Vector((max(v.x for v in coords), max(v.y for v in coords), max(v.z for v in coords)))
    center = 0.5 * (bmin + bmax)
    radius = max(0.01, (bmax - bmin).length * 0.5)

    cam.data.type = 'PERSP'
    cam.data.lens = lens_mm
    fov_v = cam.data.angle_y
    dist = (radius / math.sin(fov_v * 0.5)) / fill

    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    offset = Vector((
        dist * math.cos(pitch) * math.sin(yaw),
        -dist * math.cos(pitch) * math.cos(yaw),
        dist * math.sin(pitch)
    ))
    cam.location = center + offset
    cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
```

## Related Notes
- [[Lighting Design & Three-Point to Atmospheric Cinema]]
- [[The Visual Critic & Cook Loop for 3D Assets]]
- [[Style 01 — Photorealistic Physically-Based (ArchViz & Product)]]
- [[Style 08 — Isometric Diorama & Cozy Miniature (Tilt-Shift - Clay)]]
