---
title: 01 Quick Reference
tags: [reference, cheatsheet, blender, pbr, artcraft, gltf]
updated: 2026-11-20
---

# 01 Quick Reference — 3D Engineering Cheat Sheet

Everything you need to copy-paste in 10 seconds without digging through sub-notes. For full rules see [[AGENTS]].

---

## 1. Real-World PBR Values (Physically Measured)

| Material | Albedo (Linear / sRGB Hex) | Metallic | Roughness | IOR | Notes |
|---|---|---|---|---|---|
| **Charcoal / Matte Rubber** | `#2E2E30` (0.03) | `0.0` | `0.78–0.92` | `1.52` | Never pure `#000000` |
| **Fresh Snow** | `#DCDFE3` (0.75–0.82) | `0.0` | `0.45–0.65` | `1.31` | Add SSS (`Scale 0.03`) |
| **Brushed Aluminum** | `#D2D6DA` | `1.0` | `0.22–0.38` | — | Anisotropic `0.5` |
| **Polished Gold** | `#F6C868` | `1.0` | `0.08–0.18` | — | Warm specular tint from albedo |
| **Aged Copper / Bronze** | `#C87A56` | `1.0` | `0.30–0.55` | — | Verdigris mask = `Metallic 0.0`, `Rough 0.85` |
| **Raw Steel / Iron** | `#8E9296` | `1.0` | `0.28–0.48` | — | Add curvature edge wear (`Rough 0.18`) |
| **Car Clearcoat Paint** | Base color | `0.0–0.4` | `0.25–0.35` | `1.50` | `Coat Weight 1.0`, `Coat Roughness 0.03` |
| **Matte Painted Wood** | `#6B5344` | `0.0` | `0.55–0.75` | `1.50` | Wood grain drives roughness `±0.12` |
| **Clear Glass / Water** | `#FFFFFF` | `0.0` | `0.01–0.06` | `1.52` / `1.333` | `Transmission Weight 1.0`, thin-walled vs solid |
| **Human Skin** | `#C68B6B` | `0.0` | `0.38–0.52` | `1.40` | `Subsurface Weight 0.25–0.4`, Radius `(1.0, 0.35, 0.2)` |
| **Soft Plastic / Vinyl Toy** | Saturated hex | `0.0` | `0.22–0.42` | `1.49` | Subtle SSS (`0.08`) prevents harsh CG look |
| **Clay / Plasticine** | Earthy/pastel | `0.0` | `0.55–0.72` | `1.45` | Thumbprint bump + micro-fuzz roughness |
| **Porcelain / Ceramic** | `#ECE8E1` | `0.0` | `0.06–0.15` | `1.54` | `Coat Weight 0.8`, subtle glaze bump |
| **Woven Fabric / Wool** | Desaturated | `0.0` | `0.85–0.98` | `1.50` | `Sheen Weight 0.6–1.0`, `Sheen Roughness 0.5` |

---

## 2. Target Engine Budgets & Conventions

| Target | Up Axis | Scale | Normal Map | Hero Poly Budget | Prop Budget | Texture Packing |
|---|---|---|---|---|---|---|
| **Blender 5.3** | `+Z` (RH) | `1 u = 1 m` | OpenGL (`+Y`) | Unlimited (Cycles) | 5k–50k | Separate / Packed `.blend` |
| **Three.js / WebGPU** | `+Y` (RH) | `1 u = 1 m` | OpenGL (`+Y`) | 15k–50k tris | 500–5k tris | glTF ORM (`R=AO, G=Rough, B=Metal`), KTX2/WebP |
| **Unreal Engine 5** | `+Z` (LH) | `1 u = 1 cm` | DirectX (`-Y`) | Nanite / 100k+ | 2k–15k | ORM (`R=AO, G=Rough, B=Metal`), Linear |
| **Unity (URP/HDRP)** | `+Y` (LH) | `1 u = 1 m` | OpenGL (`+Y`) | 20k–60k tris | 1k–8k | MaskMap (`R=Metal, G=AO, B=Detail, A=Smoothness`) |
| **Godot 4** | `+Y` (RH) | `1 u = 1 m` | OpenGL (`+Y`) | 20k–50k tris | 1k–8k | glTF ORM (`R=AO, G=Rough, B=Metal`) |
| **Roblox Studio** | `+Y` (RH) | `1 stud ≈ 0.28 m` | OpenGL (`+Y`) | ≤ 10,000 tris/MeshPart | 300–4k | SurfaceAppearance (Color, Metal, Normal, Rough) |
| **3D Printing (FDM)** | `+Z` (RH) | `1 u = 1 mm` | N/A | Watertight high-res | Wall ≥ 1.2 mm | `.stl` / `.3mf` / `.step` |

---

## 3. UV Padding & Texel Density Rules

| Map Resolution | Min UV Island Padding | Typical Hero Texel Density (1st-person) | Typical Prop Texel Density (3rd-person) |
|---|---|---|---|
| `512 × 512` | `4 px` | — | `2.56 px/cm` |
| `1024 × 1024` | `8 px` | `5.12 px/cm` | `5.12 px/cm` |
| `2048 × 2048` | `16 px` | `10.24 px/cm` | `5.12–10.24 px/cm` |
| `4096 × 4096` | `32 px` | `20.48 px/cm` (film/closeup) | `10.24 px/cm` |

---

## 4. Essential CLI One-Liners (Verified on This Machine)

### Headless Blender 5.3
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe" -b --factory-startup -P scene.py
```

### MaterialCraft Headless Cook, Render & Export
```powershell
# Create new PBR package, cook, render HQ preview ball, export 2K PNG maps
& "C:\Program Files\MaterialCraft\materialcraft-cli.exe" new pbr brick.sbs --size 2048 --name brick
& "C:\Program Files\MaterialCraft\materialcraft-cli.exe" render brick.sbs preview.png --size 1024x1024 --scene material_ball --hq
& "C:\Program Files\MaterialCraft\materialcraft-cli.exe" export brick.sbs ./maps --format png --depth 16 --size 2048
```

### TextureCraft Headless Bake, Paint & Export
```powershell
# New project from GLB, bake 2K mesh maps, render path-traced preview, export textures
& "C:\Program Files\TextureCraft\texturecraft-cli.exe" new asset.glb asset.tcraft --resolution 2048 --sample
& "C:\Program Files\TextureCraft\texturecraft-cli.exe" bake asset.tcraft --resolution 2048 --maps normal,ambientOcclusion,curvature,thickness,position
& "C:\Program Files\TextureCraft\texturecraft-cli.exe" render asset.tcraft preview.png --size 1280x720 --samples 64
& "C:\Program Files\TextureCraft\texturecraft-cli.exe" export asset.tcraft ./textures --format png --size 2048
```

### Launch Live-Bridge ArtCraft Apps (for `*-live` MCPs)
```powershell
Start-Process "C:\Program Files\MaterialCraft\materialcraft.exe" -ArgumentList "--control","7878"
Start-Process "C:\Program Files\TextureCraft\texturecraft.exe" -ArgumentList "--control","7879"
Start-Process "C:\Program Files\ArtCraft\VectorCraft\vectorcraft.exe" -ArgumentList "--control","7979"
Start-Process "C:\Users\AFADAZIO\AppData\Local\Programs\EffectCraft\effectcraft.exe" -ArgumentList "--control","9877"
```

### Automated Mesh & GLB QA Gate
```powershell
python "C:\Users\AFADAZIO\Obsidian\3D-Master-Vault\80 Tools & MCPs\gate\mesh_qa.py" asset.glb --profile web-hero
```

---

## 5. Blender 5.3 `bpy` Critical Gotchas

- **Principled BSDF socket names (Blender 4.0–5.3):**
  - `Base Color`, `Metallic`, `Roughness`, `IOR`, `Alpha`, `Normal`
  - `Specular IOR Level` (NOT `Specular`)
  - `Subsurface Weight`, `Subsurface Radius`, `Subsurface Scale` (NOT `Subsurface`)
  - `Coat Weight`, `Coat Roughness`, `Coat IOR` (NOT `Clearcoat`)
  - `Transmission Weight` (NOT `Transmission`)
  - `Sheen Weight`, `Sheen Roughness`, `Sheen Tint` (NOT `Sheen`)
  - `Emission Color`, `Emission Strength` (NOT `Emission`)
- **Smooth shading (4.1–5.3):** `mesh.use_auto_smooth` does NOT exist! Use `bpy.ops.object.shade_smooth()` + `NODES` "Smooth by Angle" modifier or weighted normals + sharp edges.
- **Color management:** Always set `scene.view_settings.view_transform = 'AgX'` and `scene.view_settings.look = 'AgX - Punchy'` (or `'None'` for linear/NPR).
- **glTF export:** Always pass `export_yup=True`, `export_apply=True`, `export_texcoords=True`, `export_normals=True`, `export_tangents=False` (unless engine requires precomputed MikkTSpace).
