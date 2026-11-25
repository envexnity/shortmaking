---
title: Style 08 — Isometric Diorama & Cozy Miniature (Tilt-Shift - Clay)
style_id: "08"
style_family: Stylized PBR
pbr_or_npr: Soft Stylized PBR
primary_engines: [Blender Cycles, Blender EEVEE, Three.js, Unity]
artcraft_tools: [MaterialCraft, TextureCraft, FigCraft]
poly_budget: "15k–80k tris (Full Room/Island Diorama)"
texel_density: "5.12–10.24 px/cm (1K–2K Soft Maps)"
lighting_key: "Orthographic 35.264° + Warm Practical Glow + Cool Window Sun"
tags: [art-style, isometric, diorama, cozy, miniature, stylized]
updated: 2026-11-20
---

# Style 08 — Isometric Diorama & Cozy Miniature (Tilt-Shift / Clay)

**Visual Benchmark:** *Animal Crossing*, *Unpacking*, *Monument Valley* interiors, Dribbble / Behance isometric cutaway rooms & floating islands.

---

## 1. Camera & Cutaway Composition Rules
- **True Isometric Camera Math (Blender 5.3):**
  - `camera.data.type = 'ORTHO'` (or telephoto `85 mm–135 mm` perspective with subtle tilt-shift DoF `f/2.8`!).
  - Rotation: **`X = 54.736°`** (`atan(sqrt(2))`, i.e., `35.264°` pitch down), **`Y = 0°`**, **`Z = 45°`**!
- **Thick Cutaway Shell (`0.12 m–0.22 m` slab thickness):** Never leave paper-thin single-sided walls! Give the cutaway floor slab and two back walls chunky beveled thickness with a dark/neutral cutaway cross-section color so it reads like a tactile museum diorama block.
- **Clutter Storytelling:** Group cozy micro-props in **clusters of 3 and 5** (stacked books, steaming mug, potted trailing plant, warm desk lamp, rug corner slightly curled, cat sleeping on cushion) while preserving an open walkable center!

## 2. Geometry & MaterialCraft / TextureCraft Recipe
- **Chunky Rounded Bevels (`0.01 m–0.03 m`, 3 segments):** Everything looks touchable, pillowy, and warm — zero sharp edges anywhere.
- **MaterialCraft:** Soft matte plaster (`Roughness 0.72–0.85`), warm honey oak wood planks, woven knit rug (`fx_map` loops), frosted glass lamp shade.
- **TextureCraft:** Soft top-down `position` gradient + subtle warm `AO` darkening in corners (`opacity 0.25`) + tiny color variation per tile/book spine.
- **Tactile Softness:** Add subtle `Subsurface Weight = 0.08–0.15` to cushions, foliage, lampshades, and food props!

## 3. Lighting Recipe (The "Cozy Glow" Formula)
- **Color Contrast:** Cool twilight/morning sky blue (`7500K–9000K`) streaming through the window at `45°` **against** warm amber practical lamps/candles/monitors (`2400K–3000K`) inside the room!
- **Backdrop:** Soft desaturated radial studio gradient slightly darker than the diorama's sunlit top so the floating cube silhouette pops immediately.
- **Color Management:** `AgX` (`Look = AgX - Medium High Contrast` or `Punchy`), gentle compositor `Glare (FOG_GLOW, threshold = 1.4)` on lamps and fairy lights.

## 4. Style Anti-Patterns
- Paper-thin cutaway walls (breaks the miniature toy illusion).
- Cold harsh white fluorescent lighting with no warm practical light pools.
- Empty barren floors or evenly spaced grid-aligned props with zero cozy storytelling.

## Related Notes
- [[Style 09 — Claymation, Stop-Motion & Plasticine (Thumbprints - SSS)]]
- [[Style 20 — Miniature Tabletop, Kitbash & Toy Photography (Vinyl - Resin - LEGO)]]
- [[Style 03 — Stylized PBR (Pixar - Disney - Overwatch - Fortnite)]]
- [[Camera Lenses, Framing, Turntables & Product Shots]]
