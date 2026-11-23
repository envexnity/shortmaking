---
title: Style 05 — Painterly Brushstroke & Spider-Verse (Halftones - Stepped Anim)
style_id: "05"
style_family: NPR & Painterly
pbr_or_npr: Hybrid NPR + Graphic Print
primary_engines: [Blender EEVEE, Unreal Engine 5, Three.js]
artcraft_tools: [TextureCraft, VectorCraft, EffectCraft]
poly_budget: "15k–80k tris (+ Brush/Ink Cards)"
texel_density: "10.24 px/cm (2K Painted + Screen Halftones)"
lighting_key: "Graphic Split-Tone + CMYK Halftones + Crosshatch Shadows"
tags: [art-style, spider-verse, painterly, halftone, npr, stepped-animation]
updated: 2026-11-20
---

# Style 05 — Painterly Brushstroke & Spider-Verse (Halftones / Stepped Anim)

**Visual Benchmark:** *Spider-Man: Into/Across the Spider-Verse*, *Puss in Boots: The Last Wish*, *Teenage Mutant Ninja Turtles: Mutant Mayhem* — **living comic book print meets 3D cinema**.

---

## 1. The 5 Signature Technical Pillars
1. **Halftone Dots in Highlights & Shadows:** Replace smooth shadow falloff with camera/screen-space Ben-Day dot grids (`Voronoi` / `Checker` dot mask modulated by `Shader to RGB` luminance).
2. **Hatching / Ink Lines in Deep Shadows:** Drive angled parallel ink line textures (`Wave Texture`) exclusively where `N·L < 0.35`, fading out cleanly in midtones.
3. **Stepped Animation ("On Twos"):** Animate character motion on **12 fps (`Stepped Interpolation` modifier, `step_size = 2`)** inside a **24 fps** camera move! Use multi-frame **smear frames** and comic motion lines instead of smooth CG motion blur.
4. **CMYK Misregistration / Chromatic Split:** Instead of soft Gaussian depth-of-field blur, offset Red/Cyan/Yellow channels slightly in out-of-focus areas (Blender Compositor `Lens Distortion` + `Mist` mask or **EffectCraft** RGB split!).
5. **Hand-Drawn Ink Accents:** Add **Grease Pencil Line Art** modifier on silhouette creases + interior brow/jaw/collar expression lines.

## 2. MaterialCraft & TextureCraft Recipe
- **TextureCraft:** Paint bold graphic color blocks + `posterize` + `slopeBlur` filters to create visible dried-acrylic brush edges; stamp VectorCraft halftone/hatch patterns directly into highlight/shadow masks.
- **VectorCraft:** Generate sharp comic speech effects, halftone dot matrices, speed-line overlays, and bold typographic impact graphics for **EffectCraft** compositing!

## 3. Blender 5.3 EEVEE Next Node Recipe
- `Diffuse BSDF` → `Shader to RGB` → split into 3 luminance masks:
  - **Shadow (`< 0.35`):** Multiply angled crosshatch lines + deep chromatic shadow hue.
  - **Midtone (`0.35–0.78`):** Clean painterly TextureCraft Albedo.
  - **Highlight (`> 0.78`):** Screen-space halftone dots (`Texture Coordinate → Window` → scaled dot grid `< luminance`).
- **Disable Motion Blur!** Replace with smeared geometry/duplicate ghost frames.

## 4. Style Anti-Patterns
- Smooth 60 fps interpolated character motion (breaks the comic book spell instantly!).
- Applying halftone dots uniformly across the entire surface (dots MUST respond to light & shadow!).
- Muddy photorealistic motion blur or soft depth-of-field without graphic print breakup.

## Related Notes
- [[Blender 5.3 Shader Nodes & NPR Shading Recipes]]
- [[Style 04 — Hand-Painted Diffuse (Arcane - Riot - World of Warcraft)]]
- [[Style 07 — 2D-in-3D Grease Pencil & Comic Ink (Ligne Claire - Manga)]]
- [[Animation Principles, Keyframes, NLA & Camera Motion]]
