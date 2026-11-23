---
title: Blender 5.3 Shader Nodes & NPR Shading Recipes
tags: [materials, shaders, blender, npr, toon, principled-bsdf]
updated: 2026-11-20
---

# Blender 5.3 Shader Nodes & NPR Shading Recipes

Production shader node graphs for Blender 5.3 (`Cycles` & `EEVEE Next`) covering PBR texture wiring, procedural wear, glass/caustics, anime cel shading, painterly strokes, and retro dithered shaders.

---

## 1. Canonical PBR Texture Wiring (`bpy` — Blender 5.3)

```python
import bpy

def build_pbr_material(name, base_color_path, normal_path, rough_path, metal_path=None, ao_path=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    def add_tex(path, colorspace="Non-Color"):
        tex = nt.nodes.new("ShaderNodeTexImage")
        img = bpy.data.images.load(path, check_existing=True)
        img.colorspace_settings.name = colorspace
        tex.image = img
        return tex

    c_tex = add_tex(base_color_path, "sRGB")
    if ao_path:
        ao_tex = add_tex(ao_path, "Non-Color")
        mix_ao = nt.nodes.new("ShaderNodeMix")
        mix_ao.data_type = 'RGBA'
        mix_ao.blend_type = 'MULTIPLY'
        mix_ao.inputs['Factor'].default_value = 0.65
        nt.links.new(c_tex.outputs["Color"], mix_ao.inputs[6])
        nt.links.new(ao_tex.outputs["Color"], mix_ao.inputs[7])
        nt.links.new(mix_ao.outputs[2], bsdf.inputs["Base Color"])
    else:
        nt.links.new(c_tex.outputs["Color"], bsdf.inputs["Base Color"])

    r_tex = add_tex(rough_path, "Non-Color")
    nt.links.new(r_tex.outputs["Color"], bsdf.inputs["Roughness"])

    if metal_path:
        m_tex = add_tex(metal_path, "Non-Color")
        nt.links.new(m_tex.outputs["Color"], bsdf.inputs["Metallic"])

    n_tex = add_tex(normal_path, "Non-Color")
    n_map = nt.nodes.new("ShaderNodeNormalMap")
    n_map.inputs["Strength"].default_value = 1.0
    nt.links.new(n_tex.outputs["Color"], n_map.inputs["Color"])
    nt.links.new(n_map.outputs["Normal"], bsdf.inputs["Normal"])
    return mat
```

---

## 2. EEVEE Next NPR / Anime Cel Shader Recipe

> [!NOTE]
> `Shader to RGB` works exclusively in **EEVEE Next** (not Cycles). For Cycles NPR, drive a `ColorRamp` using `Normal · LightDirection` via a `Vector Math (Dot Product)` node!

### EEVEE Cel Spine
1. `Diffuse BSDF` (white) → **`Shader to RGB`** → `ColorRamp (Interpolation: CONSTANT)` with 2–3 stops:
   - `0.00–0.42`: Cool/hue-shifted Shadow Color (never muddy grey — shift hue `+15°` toward blue/purple!)
   - `0.42–0.85`: Base Albedo
   - `0.85–1.00`: Warm Rim / Specular Accent
2. Multiply `ColorRamp` output with Hand-Painted Albedo / Ink Line map → feed directly into `Emission` (or `Material Output`) with `View Transform = Standard` so exact palette hex colors stay crisp!
3. **Inverted Hull Outline:** Add `Solidify` modifier (`thickness = -0.004 m`, `use_flip_normals = True`, `material_offset = 1`) assigned to an unlit dark ink material with `use_backface_culling = True`.

---

## 3. Spider-Verse Halftone / Crosshatch Shader Pattern

- Split light response (`Shader to RGB` → `RGB to BW`).
- In **Shadow zone** (`< 0.45`): blend screen-space / camera-mapped **Voronoi Dot Grid** (`Window` or `Camera` texture coords scaled `60–120`) using `Math (Less Than)` for Ben-Day comic halftone dots!
- In **Highlight zone** (`> 0.78`): blend rotated `Wave Texture (Bands)` for crisp specular cross-hatching!
- Quantize animation F-curves with a **`Stepped Interpolation` modifier (`step_size = 2`)** to animate on 2s (`12 fps` inside a `24 fps` timeline).

---

## 4. Physical Architectural Glass & Caustics Trick (Cycles)

Pure glass creates heavy noise in Cycles interior renders. Mix `Glass BSDF` with `Transparent BSDF` driven by `Light Path → Is Shadow Ray` so sunlight enters windows cleanly while reflections remain physically accurate!

## Related Notes
- [[PBR Physics Reference (Albedo, Metallic, Roughness, IOR, SSS)]]
- [[GLSL, WGSL & Three.js TSL Custom Shaders]]
- [[Style 06 — Anime & Cel-Shaded NPR (Guilty Gear - Genshin - Ghibli)]]
- [[Style 05 — Painterly Brushstroke & Spider-Verse (Halftones - Stepped Anim)]]
