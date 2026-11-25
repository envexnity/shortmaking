---
title: Style 01 — Photorealistic Physically-Based (ArchViz & Product)
style_id: "01"
style_family: Photoreal
pbr_or_npr: Physically-Based (PBR)
primary_engines: [Blender Cycles, Unreal Engine 5, Three.js]
artcraft_tools: [MaterialCraft, TextureCraft, VectorCraft]
poly_budget: "50k–500k+ tris (SubD / High-Poly)"
texel_density: "20.48 px/cm (2K–4K maps)"
lighting_key: "Physical HDRI + Softbox Area Lights (AgX)"
tags: [art-style, photoreal, archviz, product, pbr, cycles]
updated: 2026-11-20
---

# Style 01 — Photorealistic Physically-Based (ArchViz & Product)

**Visual Benchmark:** Dieter Rams / Apple product photography, Architectural Digest interiors, Behance studio commercial renders.

---

## 1. Silhouette, Proportions & Geometry Rules
- **100% real-world metric accuracy** (`1 u = 1 m`) — look up exact millimeter specs for screws, glass thicknesses (`6 mm`), moldings, chamfers (`0.5–2 mm`).
- **Zero razor-sharp 90° edges:** Every manufactured or architectural corner MUST have a micro-bevel (`0.0005 m–0.003 m`, 2–3 segments) to catch specular highlight lines!
- **Real physical gaps:** Doors have `2–3 mm` reveal gaps around frames; product housings have `0.3–0.8 mm` parting lines; books/pillows never sit mathematically aligned (`±0.5°–2°` organic rotation break).
- **SubD for curved housings** + **Weighted Normals** for planar brushed/anodized panels.

## 2. MaterialCraft & TextureCraft Recipe
- **MaterialCraft:** Author seamless 16-bit procedural fabrics, wood veneers, brushed aluminum (`directional_blur` + `pixel_processor` fine anisotropy), terrazzo, honed travertine, concrete. Export `.mcmat` + 16-bit EXR/PNG.
- **TextureCraft:** Bake `AO` + `curvature` → add ultra-subtle fingerprint/oil roughness smudges (`opacity 0.06–0.12`, roughness offset `±0.08`) on glossy screens/glass/metal; micro-dust in tight crevices (`dirt` generator at `0.05` opacity).
- **VectorCraft:** Export crisp product typography, CE/regulatory markings, speaker grille perforations, and knurling bump patterns as SVG/PNG decals (`layer.add.decal`).

## 3. Blender 5.3 Lighting, Camera & Color Management
- **Engine:** Cycles GPU/CPU, `AgX`, `Look = AgX - Medium High Contrast` or `AgX - Punchy`, `OpenImageDenoise (Albedo + Normal)`.
- **Studio Product Rig:** Curved infinite cyclorama backdrop + large overhead softbox (`Area`, `spread = 90°`) + warm/cool edge rim strips (`Rectangle` area lights positioned to trace sleek specular lines along bevels) + dark negative-fill black cards to carve crisp contrast!
- **ArchViz Rig:** Physical `Nishita Sky` sun (`sun_elevation = 18°–32°`) + `Light Portal` area lights in every window + warm practical interior lamps (`2700K–3000K`).
- **Camera:** `50 mm–85 mm` for product (zero wide-angle distortion), `24 mm–35 mm` with vertical shift (`camera.shift_y`, tilt-free verticals!) for ArchViz; subtle DoF (`f/4.0–f/8.0`).

## 4. Style Anti-Patterns (Instant Rejection)
- Flat uniform `Roughness` without micro-variation.
- Razor-sharp un-beveled 90° cube corners.
- Pure `#000000` black shadows or `#FFFFFF` blown-out walls.
- Tilted vertical wall lines in ArchViz (always keep camera pitch at `90°` and use `shift_y`!).
- Missing shadow contact / floating furniture.

## Related Notes
- [[PBR Physics Reference (Albedo, Metallic, Roughness, IOR, SSS)]]
- [[Hard-Surface & SubD Modeling Playbook]]
- [[Camera Lenses, Framing, Turntables & Product Shots]]
- [[GitHub 3D Modeling Skills Index]] (`kevinbadi-blender-product-skills`, `el4cteo-blender-53-skills`)
