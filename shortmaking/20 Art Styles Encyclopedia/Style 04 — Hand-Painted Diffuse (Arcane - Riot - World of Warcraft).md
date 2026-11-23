---
title: Style 04 — Hand-Painted Diffuse (Arcane - Riot - World of Warcraft)
style_id: "04"
style_family: Stylized
pbr_or_npr: Hand-Painted / Hybrid Diffuse
primary_engines: [Blender, Unity, Unreal Engine 5, Three.js]
artcraft_tools: [TextureCraft, VectorCraft, DesignCraft]
poly_budget: "3k–25k tris (Clean Planes for Brushwork)"
texel_density: "10.24 px/cm (1K–2K Diffuse)"
lighting_key: "Baked Top-Down Light + Directional Rim + Hue-Shifted Shadows"
tags: [art-style, hand-painted, arcane, riot, stylized, diffuse]
updated: 2026-11-20
---

# Style 04 — Hand-Painted Diffuse (Arcane / Riot / World of Warcraft)

**Visual Benchmark:** *Arcane* (Fortiche), *League of Legends*, *World of Warcraft*, *Ruined King*, *Darksiders* — **every surface looks like a museum gouache/oil concept painting wrapped cleanly around 3D planes**.

---

## 1. Silhouette, Proportions & Geometry Rules
- **Planar chiseled forms:** Favor deliberate planar breaks (cheekbones, armor bevels, wood notches, cloth folds) instead of soft pillowy Blinn blobs. Planes catch brushstrokes cleanly.
- **Silhouette dents & chips:** Carve major notches, cracks, and asymmetrical wear into the actual low-poly silhouette (`3k–25k` tris) so edges never look like clean primitives.
- **Straightened UVs:** Align cloth, wood beams, and blades vertically/horizontally on UV islands so directional brushstrokes flow naturally with zero stair-stepping.

## 2. TextureCraft Hand-Painted Layer Recipe (The Fortiche / Riot Stack)
1. **Bake `AO`, `curvature`, `position`, `worldNormal` (Top-Down `Z` mask).**
2. **Base Value & Hue-Shift Gradient:**
   - Bottom-to-top `position` gradient: **shift hue toward cool purple/teal in shadows** and **warm yellow/peach in highlights** (never just add black/white!).
3. **Baked Lighting Sculpt Layer:**
   - Multiply warm/colored `AO` (`opacity 0.55`).
   - Overlay top-down `worldNormal` directional light (`opacity 0.35`).
   - Screen crisp `curvature` edge highlights (`opacity 0.45`, bright warm tint).
4. **The Painterly Brushstroke Pass (`TextureCraft` Filters + Paint):**
   - Apply **`slopeBlur`** (`effect.add.filter { filter: "slopeBlur" }`) driven by a directional stroke/voronoi noise onto mask edges and color transitions — instantly turns mathematical CG gradients into organic gouache brush dabs!
   - Paint directional flat-bristle strokes (`brush.preset.apply` + `tool.brush { followPath: true, jitterAngle: 6 }`) manually along form contours, adding deliberate **chiseled specular dabs** right into Base Color!
5. **Two Modes of Output:**
   - **Classic Unlit / WoW Mode:** Diffuse-only (`Roughness = 0.85`, `Metallic = 0.0`, no Normal map) — 100% lighting baked into Albedo!
   - **Arcane Hybrid PBR Mode:** Painted Albedo + subtle sculpted Roughness (`0.35–0.75` brushed stroke variation) + soft Normal map (`Strength 0.4`) + dramatic rim lighting + SSS on skin!

## 3. Blender 5.3 Lighting & Compositor
- Use **hard dramatic key lights** + saturated colored bounce fills so shadows stay rich, painterly, and luminous (never muddy brown).
- Optional subtle Kuwahara / Oil-Paint compositor filter (`CompositorNodeKuwahara`, `size = 3–5`, `variation = 'ANISOTROPIC'` in Blender 5.3!) on backgrounds only while keeping character faces crisp.

## 4. Style Anti-Patterns
- Using desaturated grey/black for shadows (kills the painterly color richness immediately!).
- Relying on noisy photographic normal maps that fight painted brushstrokes.
- Smooth uniform gradients without planar brush breaks.

## Related Notes
- [[TextureCraft Mastery — Baking, Smart Materials & 3D Painting]]
- [[Style 05 — Painterly Brushstroke & Spider-Verse (Halftones - Stepped Anim)]]
- [[Style 03 — Stylized PBR (Pixar - Disney - Overwatch - Fortnite)]]
