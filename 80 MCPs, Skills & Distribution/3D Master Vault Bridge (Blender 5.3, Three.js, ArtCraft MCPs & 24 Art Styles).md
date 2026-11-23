---
title: 3D Master Vault Bridge (Blender 5.3, Three.js, ArtCraft MCPs & 24 Art Styles)
tags:
  - bridge
  - 3d-master
  - blender
  - threejs
  - artcraft
  - mcp
  - cross-vault
area: tools
style: all
status: evergreen
created: 2026-11-20
updated: 2026-11-20
summary: Live cross-vault bridge connecting Shortmaking Tracks 1-7 directly to 3D-Master-Vault (obsidian MCP id 3d-master), threejs-devtools MCP (69 tools), all 10 live ArtCraft MCP servers, 24 3D art styles, and 580+ vendored GitHub 3D/Three.js modeling skills.
---

# 3D Master Vault Bridge — Blender 5.3, Three.js, ArtCraft MCPs & 24 Art Styles

> [!IMPORTANT] Cross-Vault Live Connection
> Your **`obsidian` MCP** now connects **`shortmaking`** (`C:\Users\AFADAZIO\OneDrive\Desktop\shortmaking`) directly to **`3d-master`** (`C:\Users\AFADAZIO\Obsidian\3D-Master-Vault`), **`roblox-ui`**, **`awwwards`**, and **`master`**!
> Whenever a viral short needs bespoke 3D models, procedural PBR materials, custom 3D painted textures, non-standard art styles, or Three.js live scene inspection, query `obsidian` MCP with `vault: "3d-master"`.

---

## 1. Newly Wired Live MCP Servers Available to Shortmaking Agents

| MCP Server | Live Verified Tools | How It Upgrades Shortmaking |
|---|---|---|
| **`threejs-devtools`** (`threejs-devtools-mcp` v0.5.0) | **69 tools** (`scene_tree`, `set_camera`, `set_light`, `set_uniform`, `layer_details`, `draw_call_breakdown`, `take_screenshot`, `annotated_screenshot`, `capture_frames`, `gltf_to_r3f`) | Live-inspect & tweak Track 1/2/3 Three.js shorts (`NOINK = 3` layers, `InkPass` uniforms, KAZ cameras, frame capture) without full Remotion re-renders! |
| **`materialcraft`** + **`materialcraft-live`** (`:7878`) | **20 tools** + 29 atomic nodes | Author custom procedural `.sbs` / `.mcmat` PBR textures (cobblestone, stylized wood, claymation thumbprints, wet asphalt, knitted wool) for Tracks 3, 4, 5 & 7! |
| **`texturecraft`** + **`texturecraft-live`** (`:7879`) | **22 tools** + 177 commands | Bake high-to-low `AO`, `curvature`, `normal`, `position` maps & paint smart materials / decals directly onto `.glb` hero props before Blender/Three.js rendering! |
| **`vectorcraft`** + **`vectorcraft-live`** (`:7979`) | **33 tools** | Crisp vector character emblems, historical flags, signs, comic speed-lines, and SVG profiles for Blender extrusion! |
| **`designcraft`** / **`figcraft`** / **`soundcraft`** | **26 / 19 / 17 tools** | Turnaround sheets, diegetic HUD overlays for Track 3/6 explainers, and `-14 LUFS` spatial audio mixing! |
| **`craft-anything`** | **39 core tools** | Instant **Tripo P1** GLB 3D prop generation (`assets_model_generate`) & **Nano Banana Pro** concept textures (`assets_image_generate`)! |

---

## 2. How Each Shortmaking Track Maps Into `3D-Master-Vault` (`vault: "3d-master"`)

| Shortmaking Track | Read in `vault: "3d-master"` | Vendored Skills (`3D-Master-Vault/80 Tools & MCPs/skills/`) |
|---|---|---|
| **Track 1 & 2 (2D-in-3D Toon)** | `Three.js 2D-in-3D Toon, InkPass & Low-Poly Shorts Engine`, `Style 07 — 2D-in-3D Grease Pencil & Comic Ink`, `Style 05 — Painterly Brushstroke & Spider-Verse` | `cloudai-threejs-skills` (★4,311), `open-3d-skills` (★437), `threejs-awesome-graphics` (★1,018) |
| **Track 3 (Low-Poly KAZ)** | `Style 10 — Low-Poly Flat-Shaded & Faceted`, `Three.js Complete Master Guide`, `Three.js + Blender 5.3 Live Parity & Asset Handoff` | `threejs-game-skills` (★2,863), `blender-web-3d-skill`, `threejs-architecture-effects` |
| **Track 4 (Blender 5.3 Cinema)** | `20 Art Styles Encyclopedia/` (all 24 styles: Photoreal, Arcane Hand-Painted, Claymation, Dark Fantasy, Cyberpunk, Mecha, Plush, Ceramic/Glass), `MaterialCraft Mastery`, `TextureCraft Mastery` | `el4cteo-blender-53-skills` (★2,491), `arjun988-blender-skills` (★4,440), `dream-loop-blender-critic` (★2,450), `capybala-bpy-skill` |
| **Track 5 (Roblox Shorts)** | `Style 13 — Roblox Stylized, Stud & UGC Accessory Pipeline`, `Roblox Studio 3D Pipeline`, `Roblox R6-R15, Mixamo & Game-Ready Skeletal Export` | `roblox-ai-skills` (★198), `scenario-labs-3d-skills` (★3,929) |
| **Track 7 (Undershine 3D Pixel Art)** | `Style 24 — Pixel-Art 3D (Dithered Orthographic Sprites & 2.5D HD-2D)`, `Style 11 — PS1 - PS2 - N64 Retro`, `Style 06 — Anime & Cel-Shaded NPR` | `el4cteo-blender-53-skills`, `cc-blender-5x-skill` |

---

## 3. Shared QA Gates
- Before importing any Blender/AI `.glb` into a Shortmaking Three.js or Blender scene, validate it with:
  ```powershell
  python "C:\Users\AFADAZIO\Obsidian\3D-Master-Vault\80 Tools & MCPs\gate\mesh_qa.py" prop.glb --profile web-prop
  ```
- Preview any `.glb` interactively in 1 click using:
  `C:\Users\AFADAZIO\Obsidian\3D-Master-Vault\90 Templates\Three.js Studio Viewer Starter (Single-File r187).html`
