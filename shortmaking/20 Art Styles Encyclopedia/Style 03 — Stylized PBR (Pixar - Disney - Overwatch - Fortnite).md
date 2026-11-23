---
title: Style 03 — Stylized PBR (Pixar - Disney - Overwatch - Fortnite)
style_id: "03"
style_family: Stylized PBR
pbr_or_npr: Stylized PBR
primary_engines: [Blender, Unreal Engine 5, Unity, Godot, Three.js]
artcraft_tools: [MaterialCraft, TextureCraft, VectorCraft]
poly_budget: "10k–60k tris (Chunky Clean Silhouette)"
texel_density: "10.24 px/cm (2K maps)"
lighting_key: "Bouncy Warm/Cool Three-Point + Strong Rim + SSS"
tags: [art-style, stylized-pbr, pixar, overwatch, fortnite, characters]
updated: 2026-11-20
---

# Style 03 — Stylized PBR (Pixar / Disney / Overwatch / Fortnite)

**Visual Benchmark:** *Overwatch*, *Fortnite*, *Kena: Bridge of Spirits*, Pixar / DreamWorks features — **chunky exaggerated shapes paired with crisp, tactile PBR light response**.

---

## 1. Silhouette, Proportions & Geometry Rules
- **Chunky, readable bevels (`0.008 m–0.025 m`):** Edges are 3×–5× wider and softer than photoreal so they catch juicy specular highlights even from far camera distances!
- **Shape Language Discipline:**
  - **Circles / Curves** = Friendly, soft, approachable.
  - **Squares / Rectangles** = Sturdy, heroic, grounded.
  - **Triangles / Tapered Wedges** = Dynamic, fast, dangerous.
- **Taper & Rhythm:** Never use plain straight cylinders or boxes — add subtle `3%–8%` taper, flared cuffs, oversized rivets/buckles, and straight-against-curve silhouette contrast.
- **No noisy micro-geometry:** Omit realistic 1 mm pores/screws; keep detail frequency clean and intentional.

## 2. MaterialCraft & TextureCraft Recipe
- **MaterialCraft:** Build simplified, bold macro-pattern graphs (stylized wood planks with wide bevels, soft hammered metal, chunky woven cloth) — apply `blur` / `slopeBlur` to soften high-frequency noise into painterly sculptural forms.
- **TextureCraft:**
  1. Bake `AO`, `curvature`, `position`, `thickness`.
  2. **Baked Bottom-to-Top Value Gradient:** Add Fill Layer driven by `position` generator — darken bottom by `15–25%` (cooler hue), brighten top by `10–15%` (warmer hue). This single layer gives instant Overwatch/Fortnite readability!
  3. **Broad Stylized Edge Highlight:** `curvature` / `edgeWear` generator (`softness: 0.4`, `level: 0.55`) with brighter, slightly desaturated tint + lower roughness (`-0.12`).
  4. **Warm Cavity AO:** Never use pure black AO! Tint `ambientOcclusion` cavity multiply layer to warm burnt umber or deep indigo (`opacity 0.35–0.5`).
  5. **Soft Broad Roughness:** Keep roughness gradients broad and readable (leather `0.45`, stylized metal `0.25–0.38`, skin `0.42` + `Subsurface Weight 0.35`).

## 3. Blender 5.3 Lighting & Color Management
- **Color Management:** `AgX` (`Look = AgX - Punchy` or `Medium High Contrast`).
- **Lighting:** Soft warm key light (`4800K`) + vibrant cool sky fill (`8500K`) + **crisp bright rim light** (`1.5×–2.5×` key intensity on silhouette edges!) so characters pop off backgrounds effortlessly.
- **Eyes & Hair:** Separate outer cornea shell (`IOR 1.38`, `Roughness 0.02`) over recessed iris for lively catchlights; sculpt hair as bold sculpted ribbon clumps rather than realistic stray strands.

## 4. Style Anti-Patterns
- High-frequency photo-scanned grunge/rust overlaid onto chunky cartoon meshes (creates uncanny "dirty toy" clash).
- Pure black cavity shadows instead of saturated dark shadow hues.
- Thin razor-sharp 1 mm edges that vanish at game camera distance.

## Related Notes
- [[Organic Sculpting, Retopology & Anatomy]]
- [[TextureCraft Mastery — Baking, Smart Materials & 3D Painting]]
- [[Style 04 — Hand-Painted Diffuse (Arcane - Riot - World of Warcraft)]]
- [[Style 13 — Roblox Stylized, Stud & UGC Accessory Pipeline]]
