---
title: Style 09 — Claymation, Stop-Motion & Plasticine (Thumbprints - SSS)
style_id: "09"
style_family: Tactile & Clay
pbr_or_npr: Tactile PBR + SSS
primary_engines: [Blender Cycles, Unreal Engine 5, Three.js]
artcraft_tools: [MaterialCraft, TextureCraft, EffectCraft]
poly_budget: "20k–150k tris (Displaced Sculpted Forms)"
texel_density: "20.48 px/cm (2K–4K Micro-Bump)"
lighting_key: "Macro Tabletop Softbox + Shallow DoF (f/2.0) + Stepped 12fps"
tags: [art-style, claymation, stop-motion, plasticine, sss, tactile]
updated: 2026-11-20
---

# Style 09 — Claymation, Stop-Motion & Plasticine (Thumbprints / SSS)

**Visual Benchmark:** Aardman (*Wallace & Gromit*, *Shaun the Sheep*), Laika (*Coraline*, *Kubo*), *The Midnight Gospel* clay shorts, *Harold Halibut* — **hand-squeezed tactile charm where every thumbprint catches warm studio light**.

---

## 1. Geometry & Imperfection Rules
- **Zero mathematical straight lines:** Subdivide every shape and pass it through a low-frequency `Displace` modifier (`Clouds` / `Perlin`, strength `0.002–0.006 m`) so cylinders and boxes look hand-rolled!
- **Pinch-joined seams:** Where limbs, eyes, or props meet, sculpt a tiny pinched fillet / clay crease instead of sharp Boolean intersections.
- **Miniature physical scale:** Build at real stop-motion puppet scale (`15 cm–25 cm` tall puppet!) so Cycles camera Depth of Field (`85 mm`, `f/2.0–f/2.8`) naturally produces authentic miniature bokeh!
- **Stepped animation ("On Twos" + Random Micro-Shift):** Animate on `12 fps` (`step_size = 2`) AND shift the fingerprint UV/object-space noise seed every 2 frames so the clay subtly "boils" like real re-sculpted frames!

## 2. MaterialCraft Fingerprint & Plasticine Graph
Build this dedicated `.mcmat` in **MaterialCraft**:
1. **Macro lumps:** Low-frequency `pixel_processor` Perlin noise (`scale 4–8`).
2. **Thumbprint ridges:** `fx_map` / `pixel_processor` concentric warped sine rings (`directional_warp` + subtle `blur`) scattered across randomized rotated stamps!
3. **Lint & dust specks:** High-frequency sparse `fx_map` tiny bright hair/fiber specks (`opacity 0.04`).
4. **Surface response:**
   - `Roughness`: `0.50–0.68` (slightly oilier/shinier `0.42` on raised thumbprint ridges, dustier `0.72` in crevices!).
   - `Subsurface Weight`: `0.25–0.45` (`Random Walk`, `Subsurface Scale = 0.008 m`, warm tint) — plasticine waxiness dies without SSS!
   - `Coat Weight`: `0.15`, `Coat Roughness = 0.35` (subtle waxy finger-oil sheen).

## 3. Blender 5.3 Lighting & Macro Camera
- **Practical miniature tabletop set:** Warm tungsten key (`3800K`) + soft bounce cards + **shallow depth of field** (`focus_distance` locked tightly to character eyes, `aperture_fstop = 2.0`).
- **Felt / Cardboard / Wood Set Props:** Contrast plasticine characters with fuzzy felt fabric ([[Style 22 — Plush, Fabric, Knitwear & Woolly Tactile 3D]]) and corrugated cardboard/balsa wood props!

## 4. Style Anti-Patterns
- Perfect mathematical spheres/cylinders with uniform smooth clay shader (reads as cheap rubber, not stop-motion).
- Missing SSS (makes clay look like painted concrete).
- Deep infinite focus instead of miniature macro DoF.

## Related Notes
- [[MaterialCraft Mastery — Node Library & Procedural Graphs]]
- [[Style 08 — Isometric Diorama & Cozy Miniature (Tilt-Shift - Clay)]]
- [[Style 22 — Plush, Fabric, Knitwear & Woolly Tactile 3D]]
- [[Style 20 — Miniature Tabletop, Kitbash & Toy Photography (Vinyl - Resin - LEGO)]]
