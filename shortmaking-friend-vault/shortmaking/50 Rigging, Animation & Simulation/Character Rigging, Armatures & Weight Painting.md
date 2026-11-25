---
title: Character Rigging, Armatures & Weight Painting
tags: [rigging, armature, weights, characters, blender, deformation]
updated: 2026-11-20
---

# Character Rigging, Armatures & Weight Painting

---

## 1. Pre-Rigging Checklist (Skip ONE and the Rig Explodes!)
1. Character stands in clean **A-Pose** (preferred for shoulders!) or **T-Pose**, facing **`-Y`** (Blender front), feet planted cleanly at **`Z = 0`**, symmetrical across **`X = 0`**.
2. Scale = `(1, 1, 1)`, Rotation = `(0, 0, 0)`, Location = `(0, 0, 0)`.
3. Real-world height (`~1.75 m` realistic, `~1.45 m` Roblox R15).
4. Clean concentric edge loops at shoulders, elbows, wrists, hips, knees, ankles, neck, eyelids, mouth ([[Topology & Edge Flow Mastery]]).

---

## 2. Standard Game-Ready Skeleton Naming Convention

Use clean `.L` / `.R` symmetric suffixes so Blender X-Mirror and Unity/Unreal/Godot humanoid retargeters map bones automatically:
- `Root` (at `(0,0,0)` on floor — carries root motion!)
- `Hips` (Pelvis) → `Spine` → `Spine1` → `Chest` → `Neck` → `Head`
- `Shoulder.L` → `UpperArm.L` → `Forearm.L` → `Hand.L` → fingers (`Thumb/Index/Middle/Ring/Pinky_01..03.L`)
- `Thigh.L` → `Shin.L` → `Foot.L` → `Toe.L`

> [!TIP]
> **Engine Bone Limits:** Keep max **4 bone influences per vertex** (`bpy.ops.object.vertex_group_limit_total(limit=4)`) and **normalize all weights** (`bpy.ops.object.vertex_group_normalize_all()`) before exporting to glTF / Unity / Unreal / Roblox!

---

## 3. IK / FK & Deformation Rules
- **Legs:** Always default to **IK (Inverse Kinematics)** with a Pole Target knee controller placed `0.5 m` in front of the knee so feet stay planted firmly on the ground without sliding!
- **Arms:** Provide **FK/IK switch** (FK for swinging/gestures; IK for grabbing walls/weapons/steering wheels).
- **Rigid Armor / Hard Props on Skinned Characters:** Assign rigid plates **100% weight to a single bone** (zero soft blending!) so steel armor never bends like rubber!
- **Auto-Weighting Fallback:** If `ARMATURE_AUTO` ("Bone Heat Weighting: failed to find solution") triggers on intersecting meshes, temporarily scale mesh + rig `×10`, bind weights, then scale back `×0.1`, OR transfer weights from a clean voxel-remeshed proxy cage via `Data Transfer` modifier!

## Related Notes
- [[Animation Principles, Keyframes, NLA & Camera Motion]]
- [[Roblox R6-R15, Mixamo & Game-Ready Skeletal Export]]
- [[Topology & Edge Flow Mastery]]
- [[glTF - GLB & USD Export Pipeline (Zero-Defect Rules)]]
