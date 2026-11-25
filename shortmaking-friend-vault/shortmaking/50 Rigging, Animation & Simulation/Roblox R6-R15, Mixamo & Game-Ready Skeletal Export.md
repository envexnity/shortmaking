---
title: Roblox R6-R15, Mixamo & Game-Ready Skeletal Export
tags: [rigging, roblox, mixamo, fbx, glb, skeletal, animation]
updated: 2026-11-20
---

# Roblox R6/R15, Mixamo & Game-Ready Skeletal Export

---

## 1. Roblox R15 & Skinned Mesh (`MeshPart` + `Bone`) Rules
- **R15 Rig Scale:** Standard Roblox R15 avatar height ≈ `5.2 studs` (`~1.46 m` in Blender). Keep exact R15 attachment/joint names (`HumanoidRootPart`, `LowerTorso`, `UpperTorso`, `Head`, `LeftUpperArm`, `LeftLowerArm`, `LeftHand`, etc.) when exporting custom avatar bodies or layered clothing!
- **Layered Clothing / UGC Cage Rules:** Inner & outer cage meshes MUST match Roblox's exact canonical vertex count & UV layout; wrap asset cleanly between cages with zero poke-through.
- **Custom Creatures (Skinned Mesh):** Export `.fbx` with:
  - `scale_unit = 0.01` (or calibrated stud import via Roblox Studio 3D Importer!)
  - `add_leaf_bones = False` (CRITICAL — removes useless `_end` bones!)
  - `bake_anim = True`, `bake_anim_simplify_factor = 0.0`
  - Max `4` bone weights per vertex, normalized!

---

## 2. Mixamo Auto-Rigging & Retargeting Pipeline
1. Export clean, grounded, symmetrical A/T-pose `.fbx` (or `.obj`) with zero armature from Blender.
2. Upload to Mixamo → place chin/wrist/elbow/knee/groin markers → download `T-Pose (With Skin)` + animation clips (`Without Skin`, `30 fps` or `60 fps`, `In Place` checked for locomotion!).
3. Import into Blender → push all actions onto NLA strips → export single clean multi-clip `.glb` for Three.js / Godot / Unity / Unreal!

---

## 3. Common Skeletal Export Bugs (and Instant Fixes)
- **Spaghetti / exploded limbs on import:** Unapplied object scale/rotation on either Mesh OR Armature before parenting! Always freeze both to `Scale = (1,1,1)` and `Rot = (0,0,0)` BEFORE binding!
- **Character sinks halfway into floor:** Origin/Root bone placed at Hips instead of `(0,0,0)` between feet.
- **Giant 100× character in Roblox/UE5:** FBX centimeter vs meter unit mismatch — verify `apply_unit_scale=True` and check real bounding box upon import via `ropilot` MCP!

## Related Notes
- [[Character Rigging, Armatures & Weight Painting]]
- [[Roblox Studio 3D Pipeline (Ropilot + ForgeGUI + Blender)]]
- [[Style 13 — Roblox Stylized, Stud & UGC Accessory Pipeline]]
- [[glTF - GLB & USD Export Pipeline (Zero-Defect Rules)]]
