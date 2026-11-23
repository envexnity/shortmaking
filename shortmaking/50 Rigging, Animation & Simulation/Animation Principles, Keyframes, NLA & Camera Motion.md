---
title: Animation Principles, Keyframes, NLA & Camera Motion
tags: [animation, keyframes, nla, camera-motion, easing, blender]
updated: 2026-11-20
---

# Animation Principles, Keyframes, NLA & Camera Motion

---

## 1. The 6 Non-Negotiable Principles for AI-Driven 3D Motion
1. **Anticipation:** Before jumping, punching, or launching, pull back `10–20%` in the opposite direction (`3–6 frames`).
2. **Ease-In / Ease-Out (Never Default Linear on Organic Motion!):** Use `BEZIER` S-curves with crisp slow-out/fast-middle/slow-in timing — EXCEPT for constant-speed turntables (`LINEAR`) and mechanical conveyors!
3. **Overshoot & Settle:** Let moving parts travel `5–10%` past their target pose and spring back smoothly (`BACK` / `ELASTIC` feel).
4. **Follow-Through & Overlapping Action:** Offset secondary elements (hair, capes, antennas, tails, wrists) by **`2–5 frames`** behind the main torso/root motion.
5. **Arcs:** Natural joints swing on curved arcs, never straight robotic vectors.
6. **Stepped Cadence Option:** For Spider-Verse / Claymation / Anime styles, apply a **`STEPPED` F-Curve modifier (`frame_step = 2`)** on character bones while keeping camera sweeps smooth on 1s (`24 fps`)!

---

## 2. Seamless 360° Product Turntable (`bpy`)

```python
import bpy, math

def create_turntable(pivot_obj, start_frame=1, end_frame=120):
    scene = bpy.context.scene
    scene.frame_start = start_frame
    scene.frame_end = end_frame
    pivot_obj.rotation_euler = (0, 0, 0)
    pivot_obj.keyframe_insert(data_path="rotation_euler", index=2, frame=start_frame)
    # Stop 1 frame short of 360° on last frame (or put 360° on end_frame+1) for seamless loop!
    pivot_obj.rotation_euler = (0, 0, math.tau)
    pivot_obj.keyframe_insert(data_path="rotation_euler", index=2, frame=end_frame + 1)
    for fc in pivot_obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
```

---

## 3. NLA Tracks for Multi-Clip Game Exports (glTF / FBX)
When exporting multiple named animations (`Idle`, `Walk`, `Run`, `Attack`, `Jump`) in a single `.glb`:
- Push each Action down onto its own **NLA Track** (`obj.animation_data.nla_tracks.new()`), named cleanly without spaces.
- Enable **`export_nla_strips=True`** in Blender glTF export so Three.js `AnimationMixer`, Godot `AnimationPlayer`, and Unity receive every clip cleanly!

## Related Notes
- [[Character Rigging, Armatures & Weight Painting]]
- [[Camera Lenses, Framing, Turntables & Product Shots]]
- [[Style 05 — Painterly Brushstroke & Spider-Verse (Halftones - Stepped Anim)]]
- [[glTF - GLB & USD Export Pipeline (Zero-Defect Rules)]]
