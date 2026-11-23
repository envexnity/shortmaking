---
title: Anti-Patterns — What Screams AI-Generated 3D Slop
tags: [qa, anti-patterns, craft, critique, slop]
updated: 2026-11-20
---

# Anti-Patterns — What Screams "AI-Generated 3D Slop"

Read this before every final visual review. If you spot even ONE of these tells, fix it before shipping!

---

## Geometry & Placement Tells
1. **The Floating Gap / Floor Sinking:** Legs hover `2 cm` off the floor or tires sink `5 cm` into asphalt because placement was guessed instead of computed from `bound_box` (`min_z`).
2. **Primitive Kitbash Soup:** Unbeveled raw cylinders, UV spheres, and boxes jammed through each other with zero connecting flanges, weld seams, collars, or brackets.
3. **Razor-Sharp 90° Infinite Edges:** Zero bevels on machined metal, wood furniture, or architecture — real objects ALWAYS have a tiny radius catching specular light.
4. **Inverted / Inside-Out Faces & Z-Fighting:** Coplanar overlapping faces flickering wildly, or negative-scaled mirrored parts rendering inside-out in Three.js/Unity/Roblox.
5. **Melted AI-Gen Blob Details:** Raw Tripo/Meshy/Hunyuan meshes shipped straight to production with lumpy asymmetric screws, melted typography, and chaotic 150k-triangle soup.

## Material & Texture Tells
6. **The `Roughness = 0.5` Plastic Curse:** Every object in the scene shares uniform default Principled BSDF `Roughness 0.5` with zero variation map — looks like cheap melted candle wax.
7. **Baked AI Shadows in Albedo:** Dark static lighting stains painted onto Base Color fighting dynamic scene lights.
8. **Pure `#000000` Void / `#FFFFFF` Radioactive White:** Violates PBR energy conservation and destroys shadow readability.
9. **Stretched / Checker-Distorted UVs & Black Seams:** Auto-projected UVs with `0.0` margin and unapplied object scale.
10. **Gibberish AI Text on Signs & Decals:** Always replace smeared AI signage with razor-sharp **VectorCraft** / **FigCraft** / **TextureCraft `resource.text`** decals!

## Lighting & Camera Tells
11. **Default Gray Blender World (`#0D0D0D` / `#393939`) + Single Point Light:** Lifeless gray mud with zero color contrast or rim separation.
12. **Cyberpunk Magenta-Cyan Vomit:** Flooding every dark scene uniformly with blinding pink & blue lights instead of controlled pools of light against dark shadow.
13. **Extreme Fish-Eye Product Lens (`24 mm` close-up):** Distorts product/character geometry unnaturally — use `65–100 mm` for products & busts!
14. **Blind Shipping:** Declaring "Done!" after running a script without rendering and looking at 3 camera angles.

## Related Notes
- [[Craft Floor — Non-Negotiable 3D Quality Gates]]
- [[The Visual Critic & Cook Loop for 3D Assets]]
- [[AGENTS]]
