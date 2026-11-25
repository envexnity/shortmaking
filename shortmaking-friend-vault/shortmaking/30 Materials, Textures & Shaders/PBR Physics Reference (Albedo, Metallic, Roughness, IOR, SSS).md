---
title: PBR Physics Reference (Albedo, Metallic, Roughness, IOR, SSS)
tags: [materials, pbr, physics, roughness, ior, sss, shader]
updated: 2026-11-20
---

# PBR Physics Reference (Albedo, Metallic, Roughness, IOR, SSS)

> [!IMPORTANT]
> **Energy conservation is the foundation of photorealism and believable stylized PBR.** A surface cannot reflect more light than hits it. Violating Albedo, Metallic, or Roughness physical bounds immediately produces "CG plastic."

---

## 1. The Metallic/Roughness Contract

### Base Color (Albedo)
- **For Dielectrics (`Metallic = 0.0`):** Base Color is **diffuse reflectance** (no baked lighting, no baked shadows!).
  - Strict physical range: **sRGB `30–240`** (`0.02–0.85` linear).
  - Never use `#000000` (even soot/charcoal is `#282828`–`#323232`).
  - Never use `#FFFFFF` (fresh snow is `#DCE0E5`; white printer paper is `#D9D9D7`).
- **For Metals (`Metallic = 1.0`):** Base Color is **F0 specular tint** (diffuse is automatically `0`).
  - Range: **sRGB `170–255`** (`0.40–0.98` linear). Dark oxidized metal isn't dark bare metal — it's an oxide dielectric layer (`Metallic = 0.0` or blended)!

### Metallic
- Almost always **binary (`0.0` or `1.0`)**.
- Only allow intermediate `0.2–0.8` values across sub-pixel anti-aliased boundaries, dust coatings, or rust transitions. Never set wood, stone, skin, or plastic to `Metallic = 0.3` to "make it shinier" — lower `Roughness` or add `Coat Weight` instead!

### Roughness (The Single Most Important Realism Channel)
- Roughness tells the entire history of an object (fingerprints, grease, micro-scratches, wear polish, matte dust in crevices).
- **Never ship a flat constant roughness!** Always layer:
  1. **Macro variation** (large low-frequency grunge/oil smudges: `±0.12`).
  2. **Edge/cavity shift** (exposed metal edges smoother `−0.15`; dust-filled crevices rougher `+0.20`).
  3. **Micro-grain** (high-frequency fine noise/pores: `±0.05`).

---

## 2. Measured Dielectric IOR & F0 Table

| Material | IOR | Blender `Specular IOR Level` (at default IOR 1.5) | Typical Roughness |
|---|---|---|---|
| Vacuum / Air | `1.000` | `0.00` | — |
| Water (20 °C) | `1.333` | `0.25` | `0.00–0.05` |
| Ice | `1.310` | `0.22` | `0.05–0.35` |
| Human Skin / Milk | `1.38–1.40` | `0.33` | `0.38–0.52` |
| Acrylic / Plastic (ABS/PVC) | `1.49–1.54` | `0.48–0.56` | `0.15–0.45` |
| Crown Glass | `1.520` | `0.53` | `0.01–0.05` |
| Quartz / Porcelain Glaze | `1.540` | `0.56` | `0.06–0.18` |
| Sapphire / Ruby | `1.770` | `0.95` | `0.01–0.04` |
| Diamond | `2.417` | (Use direct `IOR = 2.417`!) | `0.00–0.02` |

---

## 3. Subsurface Scattering (SSS), Clearcoat & Sheen

- **Subsurface Scattering (`Random Walk`):** Essential for skin, wax, jade, marble, milk, clay, vinyl toys, leaves, ears, and fruit.
  - Set `Subsurface Radius` to physically tinted scatter distances (skin: `(1.0, 0.35, 0.20)` so red penetrates deeper than blue; jade/foliage: `(0.2, 0.85, 0.3)`).
  - Always scale `Subsurface Scale` to **real-world meters** (`0.005–0.025 m` for skin; `0.01–0.05 m` for wax/clay).
- **Clearcoat (`Coat Weight` + `Coat Roughness`):** Use for lacquered wood, car paint, glazed ceramic, wet surfaces, polished carbon fiber, varnished eyeballs.
- **Sheen (`Sheen Weight` + `Sheen Roughness`):** Use `Microfiber` sheen for velvet, wool, peach fuzz, denim, plush toys, and moss.

## Related Notes
- [[MaterialCraft Mastery — Node Library & Procedural Graphs]]
- [[TextureCraft Mastery — Baking, Smart Materials & 3D Painting]]
- [[Blender 5.3 Shader Nodes & NPR Shading Recipes]]
- [[01 Quick Reference]]
