---
title: ArtCraft Suite & MCP Directory (All 16 Crafting Apps)
tags:
  - mcp
  - artcraft
  - effectcraft
  - anicraft
  - filmcraft
  - soundcraft
  - texturecraft
  - vectorcraft
area: tools
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-20
summary: Complete engineering directory of the ArtCraft open-source Rust creative suite (getartcraft.com / github.com/storytold)—all Craft MCP-enabled apps, local Windows installations on this machine, live-bridge ports, implementation snippets, and animation workflows.
---

# ArtCraft Suite & MCP Directory (`getartcraft.com` / `github.com/storytold`)

**ArtCraft** is an open-source ecosystem of native creative applications written in pure **Rust** where every menu action, timeline operation, brush stroke, shader node, and export runs through one unified command registry exposed as:
1. A native desktop app (`<app>`)
2. A headless CLI (`<app>-cli run / commands / exec / render`)
3. A JSON-lines socket / live UI bridge (`--bridge PORT` or `--connect PORT`)
4. **A native Model Context Protocol (MCP) server (`<app>-cli mcp`)**

---

## 1. Installed ArtCraft Binaries & Active MCPs on This Machine

Check or launch the **ArtCraft Launcher** (`C:\Users\AFADAZIO\AppData\Local\Programs\ArtCraft\Launcher\artcraft-launcher.exe`) to install or update any app in the suite. **Eight Craft apps** are installed locally on this machine:

| App | Version | Local CLI Binary Path | Active in Antigravity? | Native MCP Launch Command |
| :--- | :--- | :--- | :--- | :--- |
| **EffectCraft** *(Motion Graphics & VFX)* | — | `C:\Users\AFADAZIO\AppData\Local\Programs\EffectCraft\effectcraft-cli.exe` | **YES (`effectcraft` & `effectcraft-live`)** | `effectcraft-cli.exe mcp` (headless) / `effectcraft-cli.exe mcp --bridge 9877` (live UI) |
| **Craft Anything** *(Reverse-Engineering & Rebuild)* | `v0.6.1` | `C:\Program Files\Craft Anything\craft-anything-cli.exe` | Ready to wire | `craft-anything-cli.exe mcp` (or `craft-anything-cli.exe setup` for auto-registration) |
| **DesignCraft** *(Page Layout & Publishing)* | `v0.20.1` | `C:\Program Files\ArtCraft\DesignCraft\designcraft-cli.exe` | Ready to wire | `designcraft-cli.exe mcp` / `--connect <PORT>` |
| **FigCraft** *(Interface Design & Prototyping)* | `v0.18.1` | `C:\Program Files\ArtCraft\FigCraft\figcraft-cli.exe` | Ready to wire | `figcraft-cli.exe mcp` / `--attach <PORT>` (`figcraft --control <PORT>`) |
| **MaterialCraft** *(Procedural Material Node Graphs)* | `v0.4.1` | `C:\Program Files\MaterialCraft\materialcraft-cli.exe` | Ready to wire | `materialcraft-cli.exe mcp` / `--bridge <PORT>` (`materialcraft --control <PORT>`) |
| **SoundCraft** *(Audio Recording, Editing & Mixing)* | `v0.20.1` | `C:\Program Files\ArtCraft\SoundCraft\soundcraft-cli.exe` | Ready to wire | `soundcraft-cli.exe mcp` / `--connect <PORT>` / `--demo` |
| **TextureCraft** *(3D PBR Texture Painting)* | `v0.6.1` | `C:\Program Files\TextureCraft\texturecraft-cli.exe` | Ready to wire | `texturecraft-cli.exe mcp` / `--bridge <PORT>` (`texturecraft --control <PORT>`) |
| **VectorCraft** *(Vector Illustration & SVGs)* | `v0.24.1` | `C:\Program Files\ArtCraft\VectorCraft\vectorcraft-cli.exe` | Ready to wire | `vectorcraft-cli.exe mcp` (defaults to `--connect 127.0.0.1:7979`, or `--headless`) |

---

## 2. Complete 16-App ArtCraft MCP Catalog (Organized by Production Role)

### A. Core Animation, Video, Motion Graphics & Audio MCPs
| ArtCraft App | Repo (`storytold/*`) | What It Replaces | MCP Command & Live Bridge Flag | Shortmaking Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **EffectCraft** | `storytold/effectcraft` | After Effects | `effectcraft-cli mcp` / `--bridge 9877` | Kinetic typography, ExtendScript `.jsx` comps, 3D camera rigs, expressions, Lottie & H.264/ProRes/EXR export (`37 MCP tools` exposed on this machine!). |
| **AniCraft** | `storytold/anicraft` | Adobe Animate / Flash | `anicraft-cli mcp` | **Pure 2D Vector Character Animation**: merge-drawing shapes, nested graphic symbols, frame-by-frame onion skinning, tweens, and spritesheet/GIF/video export. |
| **FilmCraft** | `storytold/filmcraft` | Premiere Pro / DaVinci Cut | `filmcraft-cli mcp` | Rust NLE timeline (650+ engine commands): multi-track cuts, 26 blend modes, parametric EQ, true-peak limiter, FCPXML 1.9–1.11, and vertical assembly. |
| **SoundCraft** | `storytold/soundcraft` | Pro Tools / Audition | `soundcraft-cli mcp` (`--demo` or `--automation-read-root`) | Native DAW: multi-track mixing, VCA masters, clip gain lines, comping lanes, crossfades, and mastering voiceover + SFX stems. |

### B. 3D Texturing, Material, Lighting & Raster Asset MCPs
| ArtCraft App | Repo (`storytold/*`) | What It Replaces | MCP Command & Live Bridge Flag | Shortmaking Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **TextureCraft** | `storytold/texturecraft` | Substance 3D Painter | `texturecraft-cli mcp` / `--bridge 7878` | GPU-accelerated 3D PBR texture painting & map baking (Albedo, Normal, Roughness, AO) for **Track 3/4 Blender & Three.js props**. |
| **MaterialCraft** | `storytold/materialcraft` | Substance 3D Designer | `materialcraft-cli mcp` / `--bridge 7878` | Node-based procedural material synthesis (`wood`, stone, stylized cel textures) with height displacement previews. |
| **PhotoCraft** | `storytold/photocraft` | Adobe Photoshop | `photocraft-cli mcp` | Layered `.psd/.psb` painting (500+ commands), clipping masks, adjustment layers, and thumbnail/background matte art. |
| **LightCraft** | `storytold/lightcraft` | Adobe Lightroom | `lightcraft-cli mcp` / `--connect 127.0.0.1:7980` | RAW colour grading, vibrance/skin-tone protection, and local SAM-3 object masking on rendered stills/thumbnails. |
| **VectorCraft** | `storytold/vectorcraft` | Adobe Illustrator | `vectorcraft-cli mcp` / `--connect 127.0.0.1:7979` | Pen paths, shape booleans, Outer Glows, and clean `.svg` character props, maps, flags, and icons. |

### C. UI, Layout, CAD & Documentation Companion MCPs
| ArtCraft App | Repo (`storytold/*`) | What It Replaces | MCP Command & Live Bridge Flag | Shortmaking Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **FigCraft** | `storytold/figcraft` | Figma | `figcraft-cli mcp` / `--attach 47800` | Designing HUD cards, glass telemetry overlays, thumbnail templates, and storyboards cleanly offline (supports `.fig`, `.penpot`, `.svg`). |
| **CADCraft** | `storytold/cadcraft` | AutoCAD (2D/3D) | `cadcraft-cli mcp` / `--connect 127.0.0.1:7979` | Precision architectural floorplans, cutaway blueprints, and mechanical diagrams for engineering/science explainers. |
| **DesignCraft** | `storytold/designcraft` | InDesign | `designcraft-cli mcp` / `--connect PORT` | Multi-page pitch decks, comic panels, and clean typographic overlays. |
| **DeckCraft** | `storytold/deckcraft` | Keynote / PowerPoint | `deckcraft-cli mcp` / `--connect 7990` | Clean slide visuals or rapid animated explainer card decks. |
| **WordCraft** | `storytold/wordcraft` | Word | `wordcraft-cli mcp` / `--connect 127.0.0.1:7981` | Formatted script booklets & production docs. |
| **GridCraft** | `storytold/gridcraft` | Excel | `gridcraft-cli mcp` / `--connect 7979` | Shot lists, budget trackers, and outlier metrics sheets. |
| **PdfCraft** | `storytold/pdfcraft` | Acrobat | `pdfcraft-cli mcp --root DIR` | Extracting reference diagrams/history illustrations from research PDFs. |
| **Craft Anything** | `storytold/craft-anything` | Reverse-engineering / App inspector | `craft-anything-cli mcp` / `--deep` / `--clean-room` | Inspecting how websites, desktop apps, or games work (`triage`, `report`, `rebuild`) to extract mechanics, UI patterns, or shaders for new shorts/tools. |

*(Companion Web/Library repos on `github.com/storytold`: **`spark`** — advanced 3D Gaussian Splatting renderer for Three.js, and **`craft-skills`** — agent skill definitions for the Craft ecosystem.)*

---

## 3. Ready-to-Use MCP Config Snippets (`mcp_config.json`)

Add any installed ArtCraft app to `C:\Users\AFADAZIO\.gemini\antigravity\mcp_config.json` (or Claude Code via `claude mcp add`). Note that **headless MCP sessions** should pass the vault path via `--automation-read-root` / `--automation-write-root` (or `--read-root` / `--write-root` for TextureCraft/MaterialCraft), because leaving out a root flag grants no file access in headless mode:

```json
{
  "mcpServers": {
    "effectcraft": {
      "command": "C:\\Users\\AFADAZIO\\AppData\\Local\\Programs\\EffectCraft\\effectcraft-cli.exe",
      "args": ["mcp"]
    },
    "effectcraft-live": {
      "command": "C:\\Users\\AFADAZIO\\AppData\\Local\\Programs\\EffectCraft\\effectcraft-cli.exe",
      "args": ["mcp", "--bridge", "9877"]
    },
    "craft-anything": {
      "command": "C:\\Program Files\\Craft Anything\\craft-anything-cli.exe",
      "args": ["mcp"]
    },
    "designcraft": {
      "command": "C:\\Program Files\\ArtCraft\\DesignCraft\\designcraft-cli.exe",
      "args": [
        "mcp",
        "--automation-read-root", "C:\\Users\\AFADAZIO\\OneDrive\\Desktop\\shortmaking",
        "--automation-write-root", "C:\\Users\\AFADAZIO\\OneDrive\\Desktop\\shortmaking"
      ]
    },
    "figcraft": {
      "command": "C:\\Program Files\\ArtCraft\\FigCraft\\figcraft-cli.exe",
      "args": [
        "mcp",
        "--automation-read-root", "C:\\Users\\AFADAZIO\\OneDrive\\Desktop\\shortmaking",
        "--automation-write-root", "C:\\Users\\AFADAZIO\\OneDrive\\Desktop\\shortmaking"
      ]
    },
    "materialcraft": {
      "command": "C:\\Program Files\\MaterialCraft\\materialcraft-cli.exe",
      "args": [
        "mcp",
        "--read-root", "C:\\Users\\AFADAZIO\\OneDrive\\Desktop\\shortmaking",
        "--write-root", "C:\\Users\\AFADAZIO\\OneDrive\\Desktop\\shortmaking"
      ]
    },
    "soundcraft": {
      "command": "C:\\Program Files\\ArtCraft\\SoundCraft\\soundcraft-cli.exe",
      "args": [
        "mcp",
        "--automation-read-root", "C:\\Users\\AFADAZIO\\OneDrive\\Desktop\\shortmaking",
        "--automation-write-root", "C:\\Users\\AFADAZIO\\OneDrive\\Desktop\\shortmaking"
      ]
    },
    "texturecraft": {
      "command": "C:\\Program Files\\TextureCraft\\texturecraft-cli.exe",
      "args": [
        "mcp",
        "--read-root", "C:\\Users\\AFADAZIO\\OneDrive\\Desktop\\shortmaking",
        "--write-root", "C:\\Users\\AFADAZIO\\OneDrive\\Desktop\\shortmaking"
      ]
    },
    "vectorcraft": {
      "command": "C:\\Program Files\\ArtCraft\\VectorCraft\\vectorcraft-cli.exe",
      "args": [
        "mcp",
        "--headless",
        "--automation-read-root", "C:\\Users\\AFADAZIO\\OneDrive\\Desktop\\shortmaking",
        "--automation-write-root", "C:\\Users\\AFADAZIO\\OneDrive\\Desktop\\shortmaking"
      ]
    }
  }
}
```

### Security Sandboxing Flags (Best Practice for Autonomous Agents)
When running any headless ArtCraft MCP on a client or production folder, lock file I/O to your active project directory so the agent cannot read/write outside it. Note that root flags **conflict with `--connect` / `--attach` / `--bridge`** (a running GUI app enforces its own roots when launched with `--control PORT`):
```powershell
vectorcraft-cli.exe mcp --headless `
  --automation-read-root "C:\Users\AFADAZIO\OneDrive\Desktop\shortmaking" `
  --automation-write-root "C:\Users\AFADAZIO\OneDrive\Desktop\shortmaking"
```

---

## 4. How to Use & Implement Each Installed Craft App MCP

### 1. Craft Anything (`v0.6.1` — `craft-anything-cli.exe`)
- **What it does:** Analyzes how any website, desktop app, or game works, logs evidence into a `*.cany` project folder, and helps rebuild it.
- **Quick Auto-Setup:** Run `craft-anything-cli.exe setup` to auto-register Craft Anything with coding-agent apps, and `craft-anything-cli.exe doctor` to verify engines/AI backends.
- **MCP Flags:**
  - `--project <DIR.cany>`: Persist evidence, memory, and investigation journal in a project folder.
  - `--deep` vs `--clean-room`: `--deep` lets tools read target code/files/page source; `--clean-room` forbids reading inside the target.
  - `--allow-run`: Allow tools that execute code or modify a device without prompting.
  - `--restricted` (with optional `--allow-web` / `--allow-capture`): Safe mode for shared hosts.
- **CLI Workflow:** `triage` (first look) → `report --html` (Markdown/HTML findings) → `rebuild` (reconstruct in a new folder).

### 2. DesignCraft (`v0.20.1` — `designcraft-cli.exe`)
- **What it does:** Page layout, typographic grids, comic panels, thumbnail sheets, and publishing (`.designcraft`).
- **MCP Modes:**
  - **Headless:** `designcraft-cli.exe mcp --automation-read-root <DIR> --automation-write-root <DIR>` (add `--sample` to start with a sample doc).
  - **Live GUI:** Launch `designcraft.exe` with control port, then `designcraft-cli.exe mcp --connect <PORT>`.
- **Implementation Tip:** Use for multi-card storyboard sheets, YouTube/TikTok cover art templates, and print-ready PDF/PNG exports.

### 3. FigCraft (`v0.18.1` — `figcraft-cli.exe`)
- **What it does:** Offline interface design, UI component libraries, and prototyping (`.figcraft`, `.fig`, `.penpot`, `.svg`).
- **MCP Modes:**
  - **Headless:** `figcraft-cli.exe mcp --automation-read-root <DIR> --automation-write-root <DIR>`.
  - **Live GUI:** Launch `figcraft.exe --control 47800`, then `figcraft-cli.exe mcp --attach 47800` (accepts `--timeout 1..600`, default `60s`).
  - **Deterministic Text:** Pass `--no-system-fonts` (or `FIGCRAFT_NO_SYSTEM_FONTS=1`) so renders use only FigCraft's built-in fonts and match identically across machines.
- **Implementation Tip:** Prototype Track 3 (`make-3d-video`) glass HUD cards, Roblox UI frames, and subtitle pill layouts before translating to CSS or Luau.

### 4. MaterialCraft (`v0.4.1` — `materialcraft-cli.exe`)
- **What it does:** Procedural PBR material synthesis via node graphs, saving native `.sbs` packages.
- **MCP Modes:**
  - **Headless:** `materialcraft-cli.exe mcp --read-root <DIR> --write-root <DIR>` (also accepts `--automation-read-root` / `--automation-write-root`).
  - **Live GUI:** Launch `materialcraft.exe --control <PORT>`, then `materialcraft-cli.exe mcp --bridge <PORT>`.
- **Headless CLI Pipeline (No GPU Needed):**
  - `materialcraft-cli.exe new pbr wood.sbs --size 1024` (templates: `empty`, `pbr`, `atomics`)
  - `materialcraft-cli.exe nodes` (inspect node library, ports, and parameters)
  - `materialcraft-cli.exe cook wood.sbs --set roughness=0.4 --full`
  - `materialcraft-cli.exe export wood.sbs out_tex/ --format png --depth 8 --size 1024` (supports `png, jpg, tga, tif, bmp, webp, exr, hdr`)
  - `materialcraft-cli.exe render wood.sbs preview.png --scene material_ball --hq` (CPU beauty render with height displacement + AO).

### 5. SoundCraft (`v0.20.1` — `soundcraft-cli.exe`)
- **What it does:** Native Rust DAW for multi-track recording, editing, plugin FX, and mixing (`.scraft` sessions).
- **MCP Modes:**
  - **Headless:** `soundcraft-cli.exe mcp --automation-read-root <DIR> --automation-write-root <DIR>` (or `--demo` for the built-in demo session).
  - **Live GUI:** `soundcraft-cli.exe mcp --connect <PORT>`.
- **Headless CLI Helpers:**
  - `soundcraft-cli.exe info <file.wav | session.scraft>` (JSON format/session summary)
  - `soundcraft-cli.exe convert <in> <out>` (resample, bit depth, normalize)
  - `soundcraft-cli.exe plugins` (list built-in audio plugins)
  - `soundcraft-cli.exe commands` / `describe <ID>` (discover all DAW engine commands).

### 6. TextureCraft (`v0.6.1` — `texturecraft-cli.exe`)
- **What it does:** 3D PBR texture painting, mesh map baking, and smart materials (`.tcraft`, `.glb/.gltf/.fbx/.obj/.usd/.stl`).
- **MCP Modes:**
  - **Headless:** `texturecraft-cli.exe mcp --read-root <DIR> --write-root <DIR>`.
  - **Live GUI:** Launch `texturecraft.exe --control <PORT>`, then `texturecraft-cli.exe mcp --bridge <PORT>`.
- **Headless CLI Pipeline:**
  - `texturecraft-cli.exe new prop.glb prop.tcraft --resolution 1024 --sample` (bakes mesh maps & applies a smart material; built-in meshes include `builtin:material_ball`, `crate`, `rounded_cube`, `udim_plane`)
  - `texturecraft-cli.exe bake prop.tcraft --resolution 1024`
  - `texturecraft-cli.exe export prop.tcraft out_maps/` (exports Document channels + Normal + AO)
  - `texturecraft-cli.exe render prop.tcraft view.png --samples 32 --cpu` (viewport or path-traced render).

### 7. VectorCraft (`v0.24.1` — `vectorcraft-cli.exe`)
- **What it does:** Vector illustration, Pen paths, shape booleans, and multi-format conversion (`.vectorcraft`, `.svg`, `.ai`, `.pdf`, `.psd`, `.png`).
- **MCP Modes:**
  - **Default (Live-first with Headless fallback):** `vectorcraft-cli.exe mcp` tries `127.0.0.1:7979` (`vectorcraft.exe --control 7979`) and falls back to headless if no GUI is running.
  - **Strict Headless:** `vectorcraft-cli.exe mcp --headless --automation-read-root <DIR> --automation-write-root <DIR>`.
  - **Safe Mode:** `vectorcraft-cli.exe --safe-mode mcp` (disables plug-ins).
- **Headless CLI Helpers:** `convert` (e.g. `.ai`/`.svg` → `.png` with `--ppi` / `--outline-text`), `run` (batch JSON commands), `commands` (full command catalogue).

---

## 5. How the ArtCraft Suite Fits Into the 5 Vault Tracks

- **Track 1 & 2 (2D-in-3D Toon)**: Use **`VectorCraft`** to craft crisp historical props/flags/signs as clean SVGs, **`EffectCraft`** (`effectcraft-live`) to composite 2D callout graphics or kinetic captions on top of your 3D render, and **`SoundCraft`** / **`earshot`** to mix & inspect VO + SFX stems.
- **Track 3 (Low-Poly 3D)**: Prototype HUD card geometry in **`FigCraft`** before translating into `studio/page.html` CSS `--u` overlays, and generate stylized tileable textures in **`MaterialCraft`**.
- **Track 4 (Realistic Blender 3D)**: Author procedural node-graph materials in **`MaterialCraft`** (`.sbs` → PBR maps), paint hero prop wear/grime in **`TextureCraft`** (`.tcraft` → Albedo/Normal/Roughness/AO), import into Blender via `blender` MCP, and assemble multi-clip edits + audio stems in **`FilmCraft`**.
- **2D Traditional / Serialized Storytime (`Kacaurus` Style)**: Animate frame-by-frame/symbol rigs natively inside **`AniCraft`**, composite camera zooms and grain inside **`EffectCraft`**, lay out comic/thumbnail sheets in **`DesignCraft`**, and spot whistle/footstep audio via **`SoundCraft`** + **`earshot`** + **`real-sound`**.
- **R&D / Tooling (`Craft Anything`)**: Inspect reference web tools, interactive explainers, or game UIs with **`Craft Anything`** (`triage` / `report` / `rebuild`) before building custom Three.js/Playwright kits.
