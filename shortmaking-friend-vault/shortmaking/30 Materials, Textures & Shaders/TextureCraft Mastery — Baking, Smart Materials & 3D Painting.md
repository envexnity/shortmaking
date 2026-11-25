---
title: TextureCraft Mastery — Baking, Smart Materials & 3D Painting
tags: [materials, texturecraft, artcraft, mcp, baking, painting, openpbr, materialx]
updated: 2026-11-20
---

# TextureCraft Mastery — Baking, Smart Materials & 3D Painting

**TextureCraft v0.6.1** (`storytold/texturecraft`, pure Rust) is your agent-native 3D texture painter and GPU/CPU mesh map baker (clean-room Substance Painter equivalent). It natively imports `.glb .gltf .fbx .dae .usd .usda .usdc .usdz .abc .obj .ply .stl`, supports **UDIMs**, **MaterialCraft `.mcmat` live links**, **MaterialX / OpenPBR**, **3D Decals**, **Particle Brushes**, and **path-traced viewport rendering**.

---

## 1. Registered MCP Servers & Paths

- **Binary:** `C:\Program Files\TextureCraft\texturecraft-cli.exe` (GUI: `texturecraft.exe`)
- **Headless MCP:** `texturecraft` (`--read-root C:\Users\AFADAZIO --write-root C:\Users\AFADAZIO`)
- **Live Bridge MCP:** `texturecraft-live` (`--bridge 7879` → launch GUI with `texturecraft.exe --control 7879`)
- **Full machine-readable dumps in vault:**
  - `80 Tools & MCPs/artcraft-catalog/texturecraft-mcp-tools.json` (22 MCP tools)
  - `80 Tools & MCPs/artcraft-catalog/texturecraft-commands.json` (all 177 engine commands!)

---

## 2. All 22 Live MCP Tools (Verified)

| Stage | Tools |
|---|---|
| **Project & Mesh I/O** | `project_new` (builtins: `material_ball`, `sphere`, `cube`, `rounded_cube`, `cylinder`, `torus`, `plane`, `crate`, `udim_plane`), `project_open`, `project_save`, `mesh_import`, `mesh_reimport` (`preserveStrokes: true`!), `mesh_export` (`.glb`, `.usda`, `.usdc`, `.usdz`, `.obj`) |
| **Mesh Map Baking** | `bake_mesh_add` (high-poly mesh or `cage: true`), `bake` (`normal`, `ambientOcclusion`, `curvature`, `thickness`, `bentNormal`, `position`, `worldNormal`, `id`, `height`) |
| **Smart Materials & Resources** | `material_load` (`.tcmat`, `.mcmat`, `.mcraft`!), `material_save` (`.tcmat`), `resource_import` |
| **3D Painting & Batch Ops** | `paint_stroke`, `command_list`, `command_run`, `command_batch`, `session_inspect` |
| **Export & Live Bridge** | `textures_export`, `ui_inspect`, `ui_menu_invoke`, `ui_screenshot`, `viewport_render` |

---

## 3. High-Impact Engine Commands (`command_run` / `command_batch`)

### Non-Destructive Layer & Mask Stack
- `layer.add.fill` (`color`, `roughness`, `metallic`) + `layer.fill.projection` (`uv` | `triplanar` | `planar` | `spherical` | `cylindrical`, `sharpness: 1..64`) — **use `triplanar` to erase UV seam discontinuities effortlessly!**
- `mask.add.black` / `mask.add.white` / `mask.add.colorSelection` (ID map masking!)
- `layer.set` (`heightMask: { enabled: true, contrast: 8, offset: 0.0 }`, `geometryMask: ["submesh_name"]`)
- `effect.add.generator` — ALL 7 built-in procedural mask generators:
  - `edgeWear` · `dirt` · `thinAreas` · `curvature` · `ambientOcclusion` · `position` · `direction`
- `effect.add.filter` — Key filters for style mastery:
  - **Wear & Painterly:** `slopeBlur`, `warp`, `blurDirectional`, `histogramScan`, `histogramRange`
  - **Stylized / NPR:** `gradientMap`, `posterize`, `hsl`, `colorBalance`, `contrastLuminosity`
  - **Industrial Metal Finishes:** `matFinishGrind`, `matFinishRaw`, `matFinishSanded`, `matFinishHammered`
- `effect.add.anchor` — Reference a painted height/paint layer (e.g., bolts, panel lines, scratches) inside an upper mask generator so edge wear wraps around painted stamps automatically!

### Precision 3D Decals, Text & Paths
- `resource.text` — Rasterize crisp vector typography (serial numbers, warning labels, stencils) into an alpha resource.
- `layer.add.decal` / `layer.decal.set` — Project VectorCraft/FigCraft logos, warning graphics, or grime decals directly onto surface normal/position without UV distortion!
- `tool.path` — Paint stitch seams, weld beads, panel trim, or neon piping along editable 3D Bezier paths on the mesh surface!
- `tool.brush` — Full radial symmetry (`symmetryRadial: 0..32`), mirror (`symmetryX/Y/Z`), lazy mouse, and **particle brushes** (`particles: { enabled: true, count: 8, gravity: 1.0 }` for rain streaks, rust drips, blood/oil leaks!).

### MaterialCraft Live Link
- `material.load { "path": "rusty_steel.mcmat" }` — Loads procedural MaterialCraft graph directly as a live fill layer!
- `material.link.set { "id": "wear_amount", "value": 0.65, "cook": true }` — Tweaks exposed MaterialCraft parameters right inside TextureCraft and re-cooks using the mesh's baked maps!

---

## 4. Standard Agent Texturing Recipe (Batch JSON)

1. **`mesh_import`** low-poly UV'd `.glb` (`resolution: 2048`).
2. **`bake`** all maps (`normal`, `ambientOcclusion`, `curvature`, `thickness`, `position`, `bentNormal`, `antialiasing: 4`, `dilation: 16`).
3. **Base Material Layer:** `material.load` (from MaterialCraft `.mcmat`) OR `layer.add.fill` with `triplanar` projection + subtle macro roughness variation.
4. **Cavity Dirt / AO Layer:** `layer.add.fill` (darker desaturated color, higher roughness `+0.25`) → `mask.add.black` → `effect.add.generator { "generator": "dirt" }` → `effect.add.filter { "filter": "slopeBlur" }`.
5. **Edge Wear / Highlight Layer:** `layer.add.fill` (brighter/bare metal or stylized highlight, lower roughness) → `mask.add.black` → `effect.add.generator { "generator": "edgeWear" }`.
6. **Top-Down Gradient (Stylized / Grounding):** `layer.add.fill` (subtle top highlight / bottom shadow) → `effect.add.generator { "generator": "position" }` (`blend: multiply` or `overlay`, `opacity: 0.18`).
7. **Decals & Storytelling:** `resource_import` from VectorCraft/FigCraft → `layer.add.decal`.
8. **Verify Visually:** `display.set { "toneMapping": "aces", "aoIntensity": 0.6 }` → render 3 angles via `texturecraft-cli render ... --samples 64`.
9. **Export:** `textures_export` (with `normalFormat: "openGl"` for Blender/Three.js/Godot/Unity/Roblox OR `"directX"` for UE5; `padding: "dilation"`; `materialX: true` for OpenPBR!) or `mesh_export` to `.glb`/`.usdz`.

## Related Notes
- [[MaterialCraft Mastery — Node Library & Procedural Graphs]]
- [[MaterialCraft-to-TextureCraft-to-Blender-to-Engine Bridge]]
- [[UV Unwrapping, Texel Density & UDIMs]]
- [[ArtCraft Full Suite MCP Guide (MaterialCraft, TextureCraft, VectorCraft, EffectCraft, DesignCraft, FigCraft, SoundCraft, Craft Anything)]]
