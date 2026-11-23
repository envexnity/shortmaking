---
title: Three.js + Blender 5.3 Live Parity & Asset Handoff
tags: [threejs, blender, parity, glb, agx, materials, camera, handoff]
updated: 2026-11-20
---

# Three.js + Blender 5.3 Live Parity & Asset Handoff

How to make a **Blender 5.3** scene look **visually identical** inside **Three.js / WebGPU** with zero lighting surprises, broken shaders, or shifted cameras.

---

## 1. Exact Mathematical Parity Table

| Property | Blender 5.3 Source | Three.js r187 Exact Equivalent |
|---|---|---|
| **Color Management** | `AgX` (`AgX - Medium High Contrast`) | `renderer.toneMapping = THREE.AgXToneMapping` + `THREE.SRGBColorSpace` |
| **Camera Vertical FOV** | Focal length `f` (mm), sensor height `h` (`24 mm` full-frame vertical / `sensor_fit='VERTICAL'`) | `fov_deg = 2 * atan(h / (2 * f)) * (180 / Math.PI)` (`50 mm` ≈ `27.0°`, `35 mm` ≈ `37.8°`, `24 mm` ≈ `53.1°`) |
| **Coordinate Axes** | `+Z` Up, `-Y` Forward | Export glTF with **`export_yup=True`** → `+Y` Up, `+Z` Forward automatically |
| **Principled BSDF** | `Base Color`, `Metallic`, `Roughness`, `IOR`, `Normal`, `Coat`, `Transmission`, `Sheen`, `Thin Film` | `THREE.MeshPhysicalMaterial` (maps 1:1 via `KHR_materials_clearcoat`, `KHR_materials_transmission`, `KHR_materials_iridescence`, `KHR_materials_sheen`, `KHR_materials_dispersion`!) |
| **Emissive Glow** | `Emission Strength > 1.0` | `KHR_materials_emissive_strength` → triggers `UnrealBloomPass` cleanly |
| **NLA Animations** | Separate NLA Tracks per action (`Idle`, `Walk`, `Open`) | `gltf.animations` array → `THREE.AnimationMixer` |
| **Shadow Bias** | Cycles raytraced (no acne) | `light.shadow.bias = -0.0004`, `light.shadow.normalBias = 0.02`, `PCFSoftShadowMap` |

---

## 2. What Does NOT Export from Blender → Three.js (and How to Fix)

| Blender Feature | Why It Fails in GLB | Exact Fix |
|---|---|---|
| Procedural `Noise` / `Voronoi` / `ColorRamp` shader nodes | glTF only encodes image textures + scalar factors | Author in **MaterialCraft** → **TextureCraft** (`mesh_export` `.glb`) OR bake Blender shader maps to 2K PNGs before GLB export |
| `Geometry Nodes` un-realized instances | Instanced geometry may drop on export | Add **`Realize Instances`** node before `Group Output` (or export positions as JSON for `THREE.InstancedMesh`!) |
| `EEVEE Shader to RGB` cel ramps | Blender-internal node | Rebuild in Three.js using `THREE.MeshToonMaterial` + 3-px `NearestFilter` `gradientMap` OR Shortmaking's `onBeforeCompile` `shade()` hook ([[Three.js 2D-in-3D Toon, InkPass & Low-Poly Shorts Engine]]) |
| `Area` light physical decay | Three.js `RectAreaLight` does not cast shadows natively | Replace with `SpotLight` / `DirectionalLight` (for shadows) + `RoomEnvironment` / HDRI (for softbox reflections!) |

---

## 3. Automated Blender → Three.js Verification Loop

1. Export `.glb` from Blender 5.3 (`export_yup=True`, `export_apply=True`, `export_image_format='WEBP'`).
2. Run **`python "80 Tools & MCPs/gate/mesh_qa.py" hero.glb --profile web-hero`** — verify `< 50k` tris, `< 8 MB`, valid UVs, zero negative scale.
3. Drop into **`90 Templates/Three.js Studio Viewer Starter (Single-File r187).html`** (or live dev server).
4. Inspect live via **`threejs-devtools` MCP** (`scene_tree`, `material_details`, `draw_call_breakdown`, `take_screenshot`) and compare side-by-side against your Blender Cycles hero render!
5. Need React Three Fiber JSX? Call `threejs-devtools` MCP **`gltf_to_r3f`**!

## Related Notes
- [[Three.js Complete Master Guide — Scenes, Loaders, Post-Processing & MCP]]
- [[glTF - GLB & USD Export Pipeline (Zero-Defect Rules)]]
- [[Blender 5.3 API & Headless Scripting Reference]]
- [[GitHub 3D Modeling Skills Index]] (`blender-web-3d-skill`, `holo-card-studio-blender-threejs`)
