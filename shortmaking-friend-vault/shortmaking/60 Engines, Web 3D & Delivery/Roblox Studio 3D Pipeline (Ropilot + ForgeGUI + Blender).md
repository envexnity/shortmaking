---
title: Roblox Studio 3D Pipeline (Ropilot + ForgeGUI + Blender)
tags: [roblox, ropilot, forgegui, blender, texturecraft, ugc, meshpart]
updated: 2026-11-20
---

# Roblox Studio 3D Pipeline (Ropilot + ForgeGUI + Blender)

Leverages your installed **`ropilot` MCP**, **`Roblox_Studio` MCP**, **`forgegui` MCP**, **`blender` MCP**, and **`texturecraft` MCP**!

---

## 1. End-to-End Roblox 3D Asset Pipeline

1. **Model & UV in Blender 5.3:**
   - Keep `MeshPart` triangle count `≤ 10,000` tris (`≤ 4,000` for UGC Accessories).
   - Scale to Roblox proportions (`1 stud ≈ 0.28 m`; standard door `7.5 studs ≈ 2.1 m`, avatar `~5.2 studs ≈ 1.46 m`).
   - Apply transforms (`scale = 1,1,1`), outward normals, single UV map inside `[0,1]`.
2. **Texture in TextureCraft (1024×1024 Max):**
   - Bake `AO`, `curvature`, `position` → apply stylized or PBR stack.
   - Export 4 separate `1024×1024` PNG maps (`ColorMap`, `MetalnessMap`, `NormalMap [openGl]`, `RoughnessMap`).
3. **Import & Wire in Roblox Studio (`ropilot` MCP):**
   - Import `.fbx` / `.glb` via Studio 3D Importer (`ropilot_blender_import_model` / `ropilot_blender_import_rig` / `ropilot_blender_import_animation`).
   - Attach **`SurfaceAppearance`** (`AlphaMode = Overlay` or `Transparency`) referencing the 4 PBR maps, OR use **`MaterialVariant`** for reusable tiled MaterialCraft textures across `BaseParts`!
   - Set `CollisionFidelity`: `Box` / `Hull` for props; `Default` only for walkable architecture.
4. **3D Viewport Icons & Shop UI:**
   - Use **`forgegui` MCP** (`forge_plan_ui`, `forge_build_luau`) + Blender transparent PNG renders for crisp zero-lag inventory icons!
5. **Verify Live in Studio:**
   - Capture live verification screenshot with `ropilot_studio_screenshot` and playtest with `ropilot_test_start_playtest`!

---

## 2. Vendored Roblox 3D Skills
- `80 Tools & MCPs/skills/roblox-ai-skills/` (`SyphoDev-yt/roblox-ai-skills`, 11 `SKILL.md` files covering Roblox 3D models, maps, VFX, SFX, UI, animation).
- Also cross-reference your sister vault: `Roblox-UI-Vault` (`obsidian` MCP id: `roblox-ui`)!

## Related Notes
- **⭐ Prime Roblox Video Example**: [[Bun Town Burger Wrapper - Prime Roblox Video Example]] (`videos/roblox-reel-Df1kubCJ-o0-v2/out/final.mp4`)
- [[Style 13 — Roblox Stylized, Stud & UGC Accessory Pipeline]]
- [[Roblox R6-R15, Mixamo & Game-Ready Skeletal Export]]
- [[3D MCP Ecosystem & Setup Guide (Blender, CAD, Game Engines, AI Gen, Assets)]]
