---
title: Complete Machine MCP & Skill Registry
tags:
  - mcp
  - skills
  - registry
  - tools
  - automation
area: tools
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-20
summary: Exhaustive catalog of every MCP server configured on this machine and all 32 skills vendored inside .agents/skills/ and ~/.gemini/config/skills/.
---

# Complete Machine MCP & Skill Registry

This note catalogs **every single Model Context Protocol (MCP) server and Agent Skill** installed on this machine and vendored into `.agents/skills/` inside this vault (`34 skills total`). For the complete 16-app open-source ArtCraft ecosystem (`AniCraft`, `EffectCraft`, `FilmCraft`, `SoundCraft`, `TextureCraft`, `MaterialCraft`, `VectorCraft`, etc.), see [[ArtCraft Suite & MCP Directory (All 16 Crafting Apps)]].

---

## 1. Active MCP Servers on This Machine (For Short-Form Animation)

| MCP Server Name | Key Lazy/Eager Tools | Role in Shortmaking Pipeline |
| :--- | :--- | :--- |
| **`blender`** | `execute_blender_code`, `get_scene_info`, `look`, `search_assets`, `import_asset`, `generate_3d`, `generate_gaussian_world`, `record_trajectory_feedback` | **Track 4 (Realistic/Stylized 3D), Track 5 (Roblox R6/R15) & Track 7 (Undershine)**: Runs against **Blender 5.3.0** (`C:\Program Files\Blender Foundation\Blender 5.3\blender.exe`, RTX 2050 `OPTIX` + `OPENIMAGEDENOISE` GPU) using `BLENDER_EEVEE` or `CYCLES`. *(Note: `blender_mcp_addon` currently lives in `%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\` and must be copied/enabled into `5.3\scripts\addons\` for live MCP sessions in Blender 5.3.)* |
| **`ropilot`** | `ropilot_blender_import_rig`, `ropilot_blender_import_animation`, `ropilot_blender_import_model`, `ropilot_blender_run_python`, `ropilot_blender_render`, `ropilot_studio_screenshot`, `ropilot_vfx_capture`, `ropilot_test_start_playtest`, `ropilot_edit_ctx_run_command`, `ropilot_generate_vfx_texture` | **Track 5 (Roblox Shorts)**: Connects Roblox Studio & Blender—imports R6/R15 rigs, captures Studio VFX, runs client/server Lua choreography, and renders in Blender. |
| **`forge-gui` / `forgegui`** | `forge_plan_ui`, `forge_build_luau`, `forge_preview_interactive`, `forge_export_rbxmx`, `forge_push_studio`, `forge_library_presets` | **Track 5 (Roblox Shorts)**: Generates juicy, scale-locked (`UDim2.fromScale`) Roblox HUDs, level-up banners, and interactive popups with `Back.Out` tweens. |
| **`effectcraft` & `effectcraft-live`** | `run_script`, `get_comp`, `get_layer`, `set_property`, `add_keyframe`, `add_effect`, `render_frame`, `command_batch`, `screenshot`, `ui_inspect` | **Bonus Track (ArtCraft Motion Graphics & Compositing)**: Automates EffectCraft (`effectcraft-cli.exe mcp` / `--bridge 9877`) for kinetic typography, speed-graph curves, and post-FX. *(Companion ArtCraft binaries also installed locally: `Craft Anything v0.6.1`, `DesignCraft v0.20.1`, `FigCraft v0.18.1`, `MaterialCraft v0.4.1`, `SoundCraft v0.20.1`, `TextureCraft v0.6.1`, `VectorCraft v0.24.1` — see [[ArtCraft Suite & MCP Directory (All 16 Crafting Apps)]] for `mcp_config.json` snippets & CLI usage).* |
| **`figma_figma`** | `get_design_context`, `get_screenshot`, `generate_image`, `generate_vector_illustration`, `create_shader`, `export_video` | **Asset & Vector Creation**: Generates clean SVG badges, HUD frames, custom GLSL shaders, and vector props for 2D/3D overlays. |
| **`obsidian`** | `obsidian_read_note`, `obsidian_create_note`, `obsidian_edit_note`, `obsidian_search_vault`, `obsidian_manage_tags` | **Vault Knowledge Management**: Reads and updates scripts, idea banks, and production logs in this vault. |
| **`windows-desktop`** | `list_windows`, `focus_window`, `screenshot`, `click`, `type_text`, `press_keys`, `scroll` | **Desktop GUI Automation**: Controls standalone desktop apps (ElevenLabs UI, Blender viewport, Roblox Studio, CapCut/Premiere) when CLI hooks aren't exposed. |

---

## 2. Vendored Core Animation Skills (`.agents/skills/` & Global Config)

All 32 skills below are installed locally in **both** `<Vault>/.agents/skills/` and `C:\Users\AFADAZIO\.gemini\config\skills\`:

### A. Primary Short-Form Animation Engines (Downloaded from Reference Videos)
| Skill Folder | Origin | What It Builds |
| :--- | :--- | :--- |
| **`cartoon-3d-short`** | **Mr omi** (`github.com/mromidev/claude-animated-shorts` — `youtu.be/OtbLL6OBNE4`) | **Track 1**: Remotion + Three.js 2D-in-3D Toon shorts with 8 measured look reports, 4-sandbox merge, `InkPass`, `LensBlurEffect`, `GradeEffect`, and Python synth audio. |
| **`cartoon-audio-short`** | **AI Playbook / mr miro** (`cartoon-short-kit` — `youtu.be/W3q1_MpWkok` & `zGVQt4xoZAM`) | **Track 2**: Zero-React standalone Playwright + Three.js 2D-in-3D Toon engine (`engine/main.js`, `roman.js`, `paint.js`, `motion.js`) + Whisper `timing.py`. |
| **`make-3d-video`** | **Grow With Kaz** (`3d-kaz.plugin` — `youtu.be/46C6qLvTjnU`) | **Track 3**: Low-Poly Flat-Shaded 3D explainer studio (`KAZ` global API, extruded 3D country maps, blocky characters, space/planets, and CSS `--u` glass HUD). |

### B. Polish, Audio, Motion & Research Skills
| Skill Folder | Role in Pipeline |
| :--- | :--- |
| **`earshot`** | (`github.com/Leonxlnx/earshot`) CPU-only audio intelligence & synthesis MCP + skill: `describe`, `find`, `realness`, `timeline`, visual `sheet` PNG sync checker, `critique`, `forge`, `fit`, and `252`-sound `kit`. |
| **`real-sound`** | (Bundled with `earshot`) Sound-supervisor skill sourcing verified Freesound/Mixkit/Openverse real recordings with licence audit (`CREDITS.md`), 5 critic subagents, and `-14 LUFS` mastering. |
| **`cook`** | Autonomous multi-hour visual polish loop (`BRIEF.md`, `SHOTS.md`, `ROUNDS.md`, `side-by-side.mjs`, zero-context critic subagents) targeting `≥ 8.5/10`. |
| **`sfx-sound-design-director`** | Psychoacoustic SFX spotting, `2–4 frame` pre-cut whoosh lead-ins, 4-layer impact stacking, `1.5–4 kHz` VO pocket carving, and `-14 LUFS` mastering. |
| **`after-effects-automation`** | Programmatic ExtendScript (JSX) and EffectCraft timeline automation, `75–85%` Bezier velocity curves, 3D camera null rigs, and kinetic typography. |
| **`deep-research-agent`** | 5-phase evidence-based deep research workflow used to mine outlier topics, curiosity gaps, and retention benchmarks. |
| **`roblox-game-context` & `forge-gui`** | Full Roblox Luau, R6/R15 rig hierarchy, `TweenService` spring physics, and scale-based UI rules for Track 5. |

### C. Remotion 13-Skill Suite (`.agents/skills/remotion-*`)
- `remotion-best-practices` — Core `<Sequence>`, `useCurrentFrame()`, `spring()`, `interpolate()`, and asset loading laws.
- `remotion-captions` — Word-by-word animated TikTok/Shorts subtitles via `@remotion/captions`.
- `remotion-maps` — Animated 2D/3D geographic map flyovers and glowing route lines.
- `remotion-multimedia` — Audio/video trimming, volume curves, and FFmpeg recipes inside Remotion.
- `remotion-render` — Headless rendering, `--scale`, codecs, and cloud rendering.
- `remotion-create`, `remotion-docs`, `remotion-interactivity`, `remotion-license`, `remotion-markup`, `remotion-saas`, `remotion-studio`, `remotion-upgrade`.

### D. GSAP 7-Skill Suite (`.agents/skills/gsap-*`)
- `gsap-core`, `gsap-timeline`, `gsap-plugins`, `gsap-react`, `gsap-frameworks`, `gsap-scrolltrigger`, `gsap-performance`, `gsap-utils`.

### E. Obsidian Vault Skills
- `obsidian-markdown`, `obsidian-bases`, `json-canvas`.
