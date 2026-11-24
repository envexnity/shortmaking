---
title: Video 7 Teardown — In This Town Roblox Stories (BlueStarLazer) & Why AI 3D Animation Breaks
tags:
  - teardown
  - roblox
  - animation
  - rigging
  - z-fighting
  - clipping
  - prop-attachment
area: teardowns
style: roblox
status: evergreen
created: 2026-11-24
updated: 2026-11-24
source: https://youtu.be/RKthzHzcZ_0
summary: Forensic teardown of why human-made Roblox animations (BlueStarLazer's "In This Town / In This World") look flawless while AI-generated Blender/Python shorts suffer from floating props, Z-fighting, and character clipping—plus the exact engineering fixes.
---

# Video 7 Teardown — *In This Town / In This World* Roblox Stories & Why AI 3D Breaks

- **Reference Video**: `https://youtu.be/RKthzHzcZ_0` (*In This Town / In This World Roblox Stories Compilation* by **BlueStarLazer**)
- **Internal Post-Mortem**: `videos/roblox-human-survival/render_scene.py`, `videos/roblox-bruise-town/build_scene.py`, `videos/roblox-theo-631/render_scene.py`

---

## 1. Why Human-Made Roblox Animations Look Effortless & Flawless

Watching `RKthzHzcZ_0` frame-by-frame reveals why human-made Roblox shorts never suffer from the "janky AI 3D" look:

1. **Hierarchical Rigging & Rigid Prop Welds (`Motor6D` / `WeldConstraint`)**:
   - In Roblox Studio (Moon Animator 2 / Animation Editor), a glass, mug, phone, or weapon is **welded directly to the hand bone (`RightHand` / `Right Arm`)** via a `Motor6D` or `WeldConstraint` with a fixed local grip offset (`C0`).
   - The animator never computes or guesses where the glass should be in world space—wherever the arm/hand swings, the prop follows with **0.000m drift**.
2. **Real Keyframe Interpolation & Secondary Motion**:
   - Instead of raw `math.sin(t)` loops on isolated joints, human animators use eased curves (`Cubic` / `Quad` / `Back`), torso counter-rotation, head follow-through, and eye/face swaps timed to syllables.
3. **Authored Studio Maps (No Coplanar Primitives)**:
   - Roblox Studio builds snap parts to studs (`0.25` / `0.5` / `1.0` stud grid) or offset decals/textures cleanly, and the Roblox engine's camera clipping (`NearPlaneZ ≈ 0.1`) avoids depth-buffer collapse.
4. **Live Viewport Feedback Before Export**:
   - Humans immediately see if two characters overlap or a cup misses a mouth in the viewport before hitting render.

---

## 2. Forensic Post-Mortem: Why Our Past AI Videos Broke

### Failure A: The Floating Water Pitcher / Glass (`roblox-human-survival/render_scene.py`)
Look at lines 712–716 of `videos/roblox-human-survival/render_scene.py`:
```python
gulp_tilt = -26.0 - 6.0 * math.sin(t * 10.0)
cf.pose_char(alex, head_rot=(gulp_tilt, 0, 0), arm_l=(110, -24, -10), forearm_l=(55, 0, 0), arm_r=(25, 0, -18))
cf.set_face(alex, "alex_gulp_o.png")
props["pitcher"].location = (0.28, 0.26, 1.78 + 0.02 * math.sin(t * 10.0))
props["water_stream"].location = (0.08, 0.25, 1.57)
```
- **Root Cause**: The script **guessed hardcoded world-space `(X, Y, Z)` coordinates** `(0.28, 0.26, 1.78)` for `props["pitcher"]` instead of parenting or constraining it to `alex`'s hand bone!
- Because `arm_l=(110, -24, -10)` and `forearm_l=(55, 0, 0)` rotate the limb in local bone space, the actual world-space position of the hand tip did **not** match `(0.28, 0.26, 1.78)`, leaving the pitcher floating in mid-air away from his hand.

### Failure B: Z-Fighting (Flickering / Shimmering Surfaces)
- **Root Cause 1 — Zero-Offset Coplanar Geometry**: Procedural `bpy` scripts frequently place rugs, puddles, road stripes, posters, or inner dark rooms (`S1_HDarkInside`, wall trims, layered clothing/decals) at the exact same plane (`0.000m` offset) as the floor or wall behind them.
- **Root Cause 2 — Extreme Camera Clip Ratio**: Setting `clip_start = 0.001` with `clip_end = 10000` in Blender EEVEE collapses 24-bit depth buffer precision, causing nearby coplanar faces to flicker.

### Failure C: People Clipping Into Each Other & Props
- **Root Cause 1 — Unchecked World Coordinates**: Characters are spawned with hardcoded `Vector((x, y, z))` positions without enforcing the R6/R15 bounding width (`~1.0m` shoulder-to-shoulder with arms, `~0.5m` deep).
- **Root Cause 2 — Unchecked Arm-Swing / Walk Arcs**: Rotating arms `±110°` or translating characters along paths without computing swept bounding boxes causes hands and torsos to pass straight through adjacent characters or furniture.

### Failure D: Blind Euler Guessing Without Close-Up Contact QA
- **Root Cause**: Rendering only wide overview stills hides hand-to-prop gaps, wrist twists, and subtle torso clipping until after a full 2,000+ frame render finishes.

---

## 3. Mandatory Engineering Fixes (The "Zero-Slop 3D" Contract)

1. **Never Hardcode World Coordinates for Handheld Props**:
   - **In Blender (`bpy`)**: Attach every handheld prop using a **`CHILD_OF` bone constraint** targeting the character's `Armature` + hand/arm bone (e.g., `LeftHand` / `RightHand` / `Left Arm`), or compute the exact hand socket via `arm_obj.matrix_world @ pose_bone.matrix @ local_grip_offset` after `bpy.context.view_layer.update()`.
   - **In Roblox Studio (`ropilot`)**: Use a **`Motor6D`** or **`WeldConstraint`** (`Part0 = RightHand`, `Part1 = Prop.Handle`).
2. **Use 2-Bone IK for Target-Seeking Actions (Drinking, Eating, Punching, High-Five)**:
   - Drive the hand toward a `Mouth_Target` or `Impact_Target` Empty rather than guessing `(rx, ry, rz)` Euler angles by trial and error.
3. **Z-Fighting Prevention**:
   - Enforce a **`≥ 0.003m` (`3 mm`) normal offset** on all decals, rugs, puddles, road lines, and layered plates.
   - Butt-joint walls instead of overlapping boxes on the same plane; inset inner wall linings by `≥ 0.01m`.
   - Keep camera `clip_start ≥ 0.05` and `clip_end ≤ 500` for indoor/town scenes.
4. **Pre-Render Collision & Prop-Contact Gate (Fail-Fast Python Assert)**:
   - Before rendering any animation range, run a fast frame-sweep check in `bpy` that asserts:
     - **Rig Separation**: Non-grappling character pairs maintain `dist_xy ≥ 0.85m` (idle) / `≥ 1.25m` (gesturing).
     - **Prop-to-Hand Distance**: Every active handheld prop's grip origin is `≤ 0.12m` from its target hand bone world position.
   - Render a **tight close-up contact still** of every hand-prop or character-contact beat before launching the full render.
