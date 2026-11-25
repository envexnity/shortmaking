---
title: Style 5 — Roblox Animated Shorts (Ropilot + ForgeGUI + Blender R6-R15)
tags:
  - engine
  - roblox
  - ropilot
  - forge-gui
  - blender
  - sfx
area: engines
style: roblox
status: evergreen
created: 2026-11-15
updated: 2026-11-21
summary: Complete production guide to Track 5 — building viral Roblox Animated Shorts (R6/R15 storytime, Noob-to-Pro edits, VFX showcases, and Studio playtest captures) using the pre-built 8-character Aeresei R6 IK+FK Marketplace cast, Ropilot MCP, ForgeGUI MCP, and Blender 5.3.
---

# Style 5 — Roblox Animated Shorts (`ropilot` + `forge-gui` + Blender R6/R15)

> [!TIP] ⭐ Prime Roblox Video Example in Vault (`Track 5 Benchmark`)
> Study [[Bun Town Burger Wrapper - Prime Roblox Video Example]] (`videos/roblox-reel-Df1kubCJ-o0-v2/out/final.mp4`, `98.033 s`, `1080×1920`, `-14.7 LUFS`) before building new Roblox storytime shorts. It demonstrates our verified **pure-`bmesh` Roblox Studio R15 Blocky Rig + 2-half `1024×1024` clothing UVs + matte anti-glare solid-oval Roblox eye ink + stylized textured sets (`BLENDER_EEVEE` RT/GI, `AgX - Punchy`) + 1st-person POV arm framing + synced MyInstants SFX & sidechain-ducked music**.

> [!TIP] Pre-Built 8-Character Rigged R6 Cast Ready to Animate
> Skip building boxy characters from scratch! Use our **8 fully rigged Roblox R6 storytime characters** (built on Aeresei's verified R6 IK+FK Rig V2.22 + 50 real Roblox Marketplace assets in Blender 5.3):
> - **Full Guide & Cast Roster**: [[Roblox R6 Story Cast & Marketplace Character Factory (Blender 5.3)]]
> - **Master Cast Stage**: `assets/roblox-r6-characters/Roblox_R6_Story_Cast.blend`
> - **Individual Rest-Pose Characters**: `assets/roblox-r6-characters/characters/01_Alex_Protagonist.blend` → `08_Chloe_Rival.blend` (*Alex, Noob, Rich Kid Dominus, Maya, Dad/Principal, Hacker, Admin Boss, Chloe*)

> [!NOTE] Installed MCPs & Skills for Track 5
> - **Ropilot MCP (`ropilot`)**: `ropilot_blender_import_rig`, `ropilot_blender_import_animation`, `ropilot_blender_import_model`, `ropilot_blender_run_python`, `ropilot_blender_render`, `ropilot_studio_screenshot`, `ropilot_vfx_capture`, `ropilot_test_start_playtest`, `ropilot_edit_ctx_run_command`
> - **ForgeGUI MCP (`forge-gui` / `forgegui`)**: `forge_plan_ui`, `forge_build_luau`, `forge_preview_interactive`, `forge_push_studio`
> - **Skills**: `.agents/skills/roblox-game-context/SKILL.md`, `.agents/skills/forge-gui/SKILL.md`, `.agents/skills/sfx-sound-design-director/SKILL.md`

Roblox Shorts are one of the highest-volume vertical animation categories on YouTube Shorts and TikTok (`10M–100M+` views on R6/R15 storytime, *"Noob vs. Pro vs. Hacker"*, and high-retention VFX/UI showcases). Because this machine has both **Ropilot MCP** (connecting Roblox Studio directly to Blender) and **ForgeGUI MCP**, you can automate the entire Roblox-to-Blender-to-Short pipeline.

---

## 1. The 3 Viral Roblox Short Sub-Formats

| Sub-Format | Visual Engine | Retention Hook Formula | Audio / SFX Signature |
| :--- | :--- | :--- | :--- |
| **1. R6/R15 Storytime & Comedy Skits** (*e.g., **Xenost** `@xenost-j3i` — `1.4M+` subs, `1.1M–5.4M+` views/Short*) | **Blender R6/R15 Rig** (`ropilot_blender_import_rig` + `ropilot_blender_run_python`) with glossy studs & rim lighting | Recurring POV cast (`Dad`, `Baby Sister`, `Karen`) + absurd 1-rule hook (*"My DAD came to my friend's birthday party!"* `77s`, *"In this world, every word costs a DOLLAR!"*) | Hyper-saturated Foley (`sfx-sound-design-director`): classic Roblox *Oof/Slap/Coil* + `2–4f` whoosh lead-ins |
| **2. "Noob → Pro → God" Progression / Dev Showcases** | **Roblox Studio Live Capture** (`ropilot_vfx_capture`, `ropilot_test_start_playtest`) + **ForgeGUI** custom popups | Top-screen escalating level/cash bar (`LVL 1 NOOB -> LVL 999 ADMIN`) | Accelerating pitch risers + bass drop on each tier upgrade (`-14 LUFS`) |
| **3. Satisfying Game UI & VFX Micro-Shorts** | **ForgeGUI MCP** (`forge_push_studio`) + Studio `TweenService` (`Back.Out` / `Elastic.Out`) | Tactile button squash-and-stretch (`-0.04` press → `+0.02` hover) + screen-shake | Crisp UI clicks (`2–5 kHz` transient) + chest sub-thud (`70 Hz`) |

---

## 2. Pipeline A: Blender R6/R15 Cinematic Shorts via `ropilot` MCP

Instead of screen-recording flat Roblox Studio lighting, top Roblox animators render R6/R15 rigs inside **Blender** using Ropilot's bridge tools:

1. **Import the R6 or R15 Rig & Map Assets into Blender**:
   - Call `ropilot_blender_import_rig` to bring a clean, pre-weight-painted R6 or R15 rig into Blender.
   - Call `ropilot_blender_import_model` to import props or map chunks from Roblox Studio.
2. **Keyframe Snappy "Stepped-to-Spline" Poses (`ropilot_blender_run_python`)**:
   - Roblox characters have rigid blocky limbs—they look best with **exaggerated anticipation (`3 frames` squash down), `1-frame` overshoot, and `Back.Out` settle**.
   - Camera FOV: Use **`28mm–35mm` wide lenses close to the character** (`1.8–2.5m` distance) for comedic exaggeration, and add a `7-frame` sign-flipping camera shake on every slap/explosion.
3. **Verify Poses & Physical Contacts Visually**:
   - Call `ropilot_blender_screenshot` or `ropilot_blender_render` to inspect **tight close-up contact stills** of every hand-prop interaction (glasses, cups, tools) and multi-character shot before rendering the 30/60fps vertical `1080×1920` sequence.
   - **Mandatory Prop & Anti-Clipping Rules**:
     - **Never hardcode world `(X, Y, Z)` for handheld props**: Use a **`CHILD_OF` bone constraint** on the hand/arm bone (Blender) or **`Motor6D` / `WeldConstraint`** (Roblox Studio), and **2-bone IK** for target-seeking actions (drinking, eating, punching).
     - **Zero Z-Fighting**: Offset decals/rugs/overlays by `≥ 0.003m`, butt-joint walls cleanly (`≥ 0.01m` inset), and keep `clip_start ≥ 0.05` / `clip_end ≤ 500`.
     - **Zero Character Clipping**: Keep R6/R15 rigs **`≥ 0.85m` apart** (idle) and **`≥ 1.25m` apart** (gesturing/arm-swinging).
4. **Blender 5.3 Look-Dev Upgrade for R6/R15 (Kill Plastic Viewport Renders)**:
   - See [[Blender 5.3 Cinematic Rendering & Animation Mastery Bible]] and `90 Templates & Starter Kits/blender-cinema-kit/blender_cinema_lib.py` (`BLENDER_EEVEE` with `use_raytracing=True` or Cycles `OPTIX` GPU).
   - Enable `AgX` (`AgX - Punchy`), add `add_cinema_bevel(...)` (`0.008m`) + subtle `Coat Weight` + procedural roughness breakup on R6/R15 plastic limbs/studs, wrap scenes in a Kelvin 3-point rim rig (`7600K` cool rim behind hero), enable `180°` motion blur (`motion_blur_shutter = 0.5`), and apply `BACK` / `ELASTIC` easing via `set_keyframe_easing(...)` (Blender 5.3 Slotted Actions).

---

## 3. Pipeline B: In-Studio Automated Acting, UI & VFX Capture

When shooting directly inside **Roblox Studio**:
1. **Inject Tactile UI & HUD Counters via ForgeGUI (`forge_push_studio`)**:
   - Follow the **Golden Laws of Roblox UI** (`UDim2.fromScale`, mandatory `UIAspectRatioConstraint`, `AnchorPoint = (0.5, 0.5)`, `Back.Out` `0.4s` modal pop-in).
2. **Script Automated Camera & NPC Choreography (`ropilot_edit_ctx_run_command` / `ropilot_test_run_client_lua`)**:
   - Lock `workspace.CurrentCamera.CameraType = Enum.CameraType.Scriptable`.
   - Drive the camera along smooth CFrame splines synced to your beat sheet, and trigger VFX emitters via `ropilot_vfx_capture`.

---

## 4. Pipeline C: Procedural Pure-`bmesh` Roblox Studio R15 Storytime (`Bun Town` Pattern)

When you want custom story casts with **exact Roblox Studio R15 blocky silhouettes** rendered inside **richly textured stylized Blender 5.3 worlds** (without external `.blend` import overhead):
1. **Pure-`bmesh` R15 Blocky Proportions (`char_factory.py`)**: Keep rectangular beveled Torso/Arms/Legs/Square Hands (`bevel_w = 0.016–0.020 m`), `0.032 m`-beveled Head, and `b.align_roll((0, 1, 0))` edit bones (`+X` swings forward `+Y`). Always `subdivide_edges(cuts=2)` *before* `BEVEL` and map front `+Y` clothing UVs right-reading (`0.5 - (vx - cx)/sx` -> `[0.02..0.48]`, back/sides -> `[0.52..0.98]`).
2. **Matte Anti-Glare Roblox Face Ink (`make_skin_face_mat`)**: Use solid glossy-black vertical-oval Roblox eyes (`draw_glossy_eye`) and gate `Roughness = 0.62`, `Specular IOR Level = 0.04`, `Coat Weight = 0.0` by decal `Alpha` so front `AREA` lights never wash eyes gray.
3. **POV Top-Down Framing (`set_pov_arms_only`)**: Hide torso/head/legs while angling blocky forearms inward (`Ry = ±26°..34°`) at `lens = 24 mm`.

---

## 5. High-Retention Sound Spotting for Roblox Shorts

Always load [[SFX Direction & The 2-4 Frame Lead-In Law]] (`.agents/skills/sfx-sound-design-director/SKILL.md`):
- **Every visual movement needs an acoustic weight**:
  - R6 footstep: short crisp plastic tap (`1.8 kHz`)
  - Head turn / surprise zoom: fast high-passed whip pan (`2–4 frames` *before* the zoom lands)
  - Punch / Ragdoll launch: `3-layer` hit (`2.5 kHz` slap transient + `300 Hz` blocky crunch + `65 Hz` sub-bass thud)
- Keep zero dead air (`<0.15s` between sentences) by overlapping J-cuts on voiceover lines.
