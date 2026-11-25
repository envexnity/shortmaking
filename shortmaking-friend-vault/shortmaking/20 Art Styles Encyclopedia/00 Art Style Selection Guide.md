---
title: 00 Art Style Selection Guide
tags: [art-styles, moc, art-direction, 3d]
updated: 2026-11-20
---

# 00 Art Style Selection Guide — Choosing & Mixing Every 3D Style

> [!IMPORTANT]
> **Lock ONE primary art style before creating any geometry.** Every 3D asset fails when geometry says "low-poly indie," textures say "photoreal Substance scan," and lighting says "flat studio default." All four pillars — **Silhouette/Topology + Material/Texture + Lighting/Color + Camera/Post** — MUST agree.

Open [[Art Styles Matrix.base]] to filter all 24 styles interactively, or [[Art Styles & Engines Map.canvas]] to browse them visually.

---

## Complete 24-Style Master Router

| ID | Style | Family | Shading | Primary Tools |
|---|---|---|---|---|
| **01** | [[Style 01 — Photorealistic Physically-Based (ArchViz & Product)]] | Photoreal | PBR | Blender Cycles + MaterialCraft + TextureCraft |
| **02** | [[Style 02 — Cinematic VFX & Film Realism (ACES - AgX)]] | Photoreal | PBR (ACEScg) | Blender Cycles + TextureCraft UDIM + EffectCraft |
| **03** | [[Style 03 — Stylized PBR (Pixar - Disney - Overwatch - Fortnite)]] | Stylized PBR | Stylized PBR | Blender + MaterialCraft + TextureCraft |
| **04** | [[Style 04 — Hand-Painted Diffuse (Arcane - Riot - World of Warcraft)]] | Stylized | Unlit / Semi-Lit | Blender + TextureCraft Paint (`slopeBlur`, `position`) |
| **05** | [[Style 05 — Painterly Brushstroke & Spider-Verse (Halftones - Stepped Anim)]] | NPR / Painterly | Hybrid NPR | Blender EEVEE + TextureCraft + EffectCraft |
| **06** | [[Style 06 — Anime & Cel-Shaded NPR (Guilty Gear - Genshin - Ghibli)]] | NPR / Anime | Cel NPR | Blender EEVEE + Custom Normals + Inverted Hull |
| **07** | [[Style 07 — 2D-in-3D Grease Pencil & Comic Ink (Ligne Claire - Manga)]] | NPR / Comic | Ink NPR | Blender Grease Pencil + VectorCraft + EEVEE |
| **08** | [[Style 08 — Isometric Diorama & Cozy Miniature (Tilt-Shift - Clay)]] | Stylized / Cozy | Soft PBR | Blender Cycles/EEVEE + MaterialCraft + Three.js |
| **09** | [[Style 09 — Claymation, Stop-Motion & Plasticine (Thumbprints - SSS)]] | Tactile / Clay | Tactile PBR+SSS | Blender Cycles + MaterialCraft (`fx_map` / thumbprint) |
| **10** | [[Style 10 — Low-Poly Flat-Shaded & Faceted (Monument Valley - Firewatch)]] | Retro / Minimal | Flat / Vertex Color | Blender + Three.js + Paletted Gradients |
| **11** | [[Style 11 — PS1 - PS2 - N64 Retro & Vertex-Snapped Lo-Fi]] | Retro | Lo-Fi Unlit/Gouraud | Blender + Three.js GLSL Vertex Snap + Nearest Filter |
| **12** | [[Style 12 — Voxel, Blocky & Minecraft - Blockbench Style]] | Voxel / Blocky | Crisp Pixel PBR | Blender / Blockbench + MagicaVoxel + TextureCraft |
| **13** | [[Style 13 — Roblox Stylized, Stud & UGC Accessory Pipeline]] | Stylized / Game | Roblox PBR | Blender + TextureCraft + Ropilot + ForgeGUI |
| **14** | [[Style 14 — Cyberpunk, Neon Noir & Holographic Sci-Fi]] | Genre World | Wet PBR + Emissive | Blender + TextureCraft + FigCraft HUDs + EffectCraft |
| **15** | [[Style 15 — Brutalist, Industrial Hard-Surface & Mecha]] | Genre World | Hard-Surface PBR | Blender + VectorCraft Decals + MaterialCraft + TextureCraft |
| **16** | [[Style 16 — Dark Fantasy, Gothic & Soulsborne Atmospheric]] | Genre World | Gritty PBR | Blender Sculpt + TextureCraft (`dirt`/`edgeWear`) |
| **17** | [[Style 17 — Surreal, Liminal Space & Dreamcore]] | Genre World | Uncanny PBR | Blender Cycles + Volumetrics + EffectCraft VHS/Grain |
| **18** | [[Style 18 — Abstract Motion Graphics, Glassmorphism & Iridescent (Cinema4D - Awwwards)]] | Motion / Web | Physical Glass/Iridescent | Blender GeoNodes + Three.js TSL/WebGPU + EffectCraft |
| **19** | [[Style 19 — Botanical, Nature, Terrain & Biomes (Foliage - Water - Clouds)]] | Photoreal / Nature | Translucency PBR | Blender GeoNodes + MaterialCraft + Alpha Cards |
| **20** | [[Style 20 — Miniature Tabletop, Kitbash & Toy Photography (Vinyl - Resin - LEGO)]] | Tactile / Macro | Macro PBR + DoF | Blender Cycles + TextureCraft + Shallow DoF |
| **21** | [[Style 21 — Technical Blueprint, Wireframe, X-Ray & Exploded CAD]] | Technical / CAD | NPR / Fresnel | CadQuery / OpenSCAD + Blender + VectorCraft + Three.js |
| **22** | [[Style 22 — Plush, Fabric, Knitwear & Woolly Tactile 3D]] | Tactile / Soft | Sheen + Hair/Fuzz | Blender Hair Curves + MaterialCraft Weave + Cycles |
| **23** | [[Style 23 — Ceramic, Glass, Jewelry & Caustics Macro]] | Photoreal / Macro | Transmission + Caustics | Blender Cycles (Manifold Caustics) + Dispersion |
| **24** | [[Style 24 — Pixel-Art 3D (Dithered Orthographic Sprites & 2.5D HD-2D)]] | Retro / NPR | Orthographic Pixel | Blender Ortho Nearest + GLSL Bayer Dither + Three.js |

---

## Safe Cross-Style Hybrids (High-Craft Combinations)

- **Arcane-Style Cinematic:** [[Style 04 — Hand-Painted Diffuse (Arcane - Riot - World of Warcraft)]] brush-painted albedo + [[Style 02 — Cinematic VFX & Film Realism (ACES - AgX)]] lighting & subsurface scattering!
- **Studio Ghibli Real-Time:** [[Style 06 — Anime & Cel-Shaded NPR (Guilty Gear - Genshin - Ghibli)]] characters + [[Style 19 — Botanical, Nature, Terrain & Biomes (Foliage - Water - Clouds)]] painterly billboard foliage + soft volumetric skies.
- **Awwwards Luxury Tech Hero:** [[Style 18 — Abstract Motion Graphics, Glassmorphism & Iridescent (Cinema4D - Awwwards)]] + [[Style 23 — Ceramic, Glass, Jewelry & Caustics Macro]] + [[Style 21 — Technical Blueprint, Wireframe, X-Ray & Exploded CAD]] exploded view transitions.
- **Cozy Tactical Diorama:** [[Style 08 — Isometric Diorama & Cozy Miniature (Tilt-Shift - Clay)]] + [[Style 09 — Claymation, Stop-Motion & Plasticine (Thumbprints - SSS)]] micro-imperfections.
