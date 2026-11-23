---
title: "{{title}}"
tags: [material-recipe, materialcraft, texturecraft, pbr]
material_category: ""
ior: 1.5
metallic: 0.0
roughness_range: "0.35–0.65"
updated: "{{date}}"
---

# Material Graph Recipe — {{title}}

## 1. Physical Surface Target
- **Base Color Range (sRGB / Linear):**
- **Metallic:** `0.0` / `1.0`
- **Roughness Range:**
- **IOR / SSS / Coat / Sheen:**

## 2. MaterialCraft Atomic Node Spine (`.sbs` → `.mcmat`)
1. **Primary Height (`fx_map` / `pixel_processor` / `svg`):**
2. **Warp & Breakup (`directional_warp` / `blend`):**
3. **Micro-Detail (`sharpen` / `blur` / `distance`):**
4. **Normal (`normal`) + Roughness (`levels`) + Base Color (`gradient_map` / `hsl`):**
5. **Exposed Inputs (`input_value` / `input_color`):**

## 3. TextureCraft Layer Integration
- **Projection:** `uv` / `triplanar`
- **Generators & Filters:** `edgeWear` / `dirt` / `curvature` / `slopeBlur`
- **Export Preset:** OpenGL (`+Y`) / DirectX (`-Y`) / OpenPBR `.mtlx`
