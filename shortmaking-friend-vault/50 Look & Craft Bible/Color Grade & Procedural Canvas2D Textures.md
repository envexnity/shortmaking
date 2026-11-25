---
title: Color Grade & Procedural Canvas2D Textures
tags:
  - look-bible
  - grade
  - textures
  - canvas2d
  - shaders
area: look-bible
style: 2d-in-3d-toon
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Exact 7-knot monotone Hermite tone curve (GradeEffect), 3-zone saturation/tint parameters, and procedural Canvas2D texture + bump generators (paint.ts).
---

# Color Grade & Procedural Canvas2D Textures (`grade.ts`, `paint.ts`)

> [!IMPORTANT] Source Code & Measured Reports
> - **Implementations**: `90 Templates & Starter Kits/cartoon-3d-short-kit/bridge/grade.ts` & `paint.ts`
> - **Full Raw Reports**: `.agents/skills/cartoon-3d-short/references/reports/grade.md` & `textures.md`

---

## 1. The 7-Knot Monotone Hermite Color Grade (`grade.ts`)

Raw WebGL output looks clinical and digital. Across the 20 reference shorts, the final image has a lifted matte black floor (`y0 = 0.025`), punchy midtone contrast, and a soft creamy highlight shoulder (`y6 = 0.985`).

### A. The 7 Measured Luma Curve Knots
| Knot Index | Input Luma (`x`) | Output Luma (`y`) | Visual Role |
| :--- | :--- | :--- | :--- |
| `0` | `0.00` | **`0.025`** | Lifts pure `#000000` shadows into warm charcoal/plum |
| `1` | `0.08` | **`0.072`** | Toe compression (deepens dark timber/stone crevices) |
| `2` | `0.22` | **`0.215`** | Lower-mid anchor |
| `3` | `0.50` | **`0.535`** | Midtone lift (`+3.5%` brightness on character skin & grass) |
| `4` | `0.75` | **`0.785`** | Upper-mid punch |
| `5` | `0.90` | **`0.915`** | Soft highlight knee |
| `6` | `1.00` | **`0.985`** | Creamy highlight roll-off (prevents clipped `#ffffff` whites) |

### B. 3-Zone Saturation & Split-Tone Cb/Cr Shift
- **Saturation Multipliers**: Shadows `1.08×`, **Midtones `1.26×`** (vibrant storybook colors), Highlights `0.96×` (clean warm whites).
- **Split-Tone Tint**: Shadows shift slightly toward cool plum/indigo (`Cb +0.012, Cr +0.004`), while highlights warm toward golden cream (`Cb -0.018, Cr +0.014`).
- **Vignette**: Subtle elliptical radial falloff (`0.09` corner darkening) that draws the eye to the center 9:16 safe zone.

---

## 2. Procedural `Canvas2D` Surface Painters (`paint.ts`)

Never use flat solid-color polygons on large 3D surfaces, and never import photorealistic Megascans textures that clash with 2D cartoon characters. `paint.ts` generates **hand-painted, tileable `512×512` / `1024×1024` Canvas2D diffuse + bump textures** at startup (`anisotropy = 8`, `RepeatWrapping`):

| Generator Function | Visual Construction | Where to Use |
| :--- | :--- | :--- |
| **`planksHD()`** | Staggered wood planks with dark `#241726` seam gaps (`3px`), curved Bezier wood-grain ribbons (`alpha = 0.08`), nail head dots at board ends, and matching height bump map. | Bridge decks, tavern floors, crates, wagons, signboards. |
| **`stoneHD()`** | Coursed ashlar / cobblestone blocks with rounded corners, per-block warm/cool hue jitter (`±6%`), mortar grooves, and subtle noise stipple. | Bridge towers, castle walls, cobblestone roads, quays. |
| **`grassHD()`** | Layered warm-green base with painted darker/lighter clover patches and short vertical blade strokes. | Hills, riverbanks, park lawns, battlefield meadows. |
| **`waterNear()` & `waterFar()`** | Stylized turquoise-blue water with hand-drawn creamy foam ribbons (`#e8f7fa`) and `NOINK = 3` animated UV scroll. | Rivers, moats, oceans (use high repeat near camera, low repeat in distance). |
| **`barkHD()` & `foliageHD()`** | Vertical ridged bark strokes for trunks; overlapping scalloped leaf clusters for canopy spheres. | Trees, bushes, forest backgrounds. |
