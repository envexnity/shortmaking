---
title: Bun Town Burger Wrapper — Prime Roblox Video Example (Blender 5.3 R15)
tags:
  - completed-video
  - prime-example
  - roblox
  - roblox-r15
  - blender-53
  - eevee
  - storytime
area: production
style: roblox
status: prime-benchmark
created: 2026-11-22
updated: 2026-11-22
video_file: "videos/roblox-reel-Df1kubCJ-o0-v2/out/final.mp4"
resolution: "1080x1920"
duration_sec: 98.033
loudness_lufs: -14.7
summary: Prime Track 5 Roblox Studio R15 benchmark short combining authentic beveled Roblox Studio R15 blocky characters and solid glossy-oval faces with stylized textured sets, Blender 5.3 EEVEE RT/GI lighting, single-voice Fish Audio narration, real MyInstants HUSS SFX, and sidechain-ducked TEMPOREX Numbers music.
---

# Bun Town Burger Wrapper — Prime Roblox Video Example (`Track 5 Benchmark`)

> [!IMPORTANT] Gold-Standard Reference for Future Roblox Shorts
> This production (`videos/roblox-reel-Df1kubCJ-o0-v2/`) is the **Prime Track 5 Roblox Video Example** in the vault. It solves the core visual failure mode of AI/Blender Roblox renders by fusing **authentic Roblox Studio R15 blocky proportions, stitched 2-half clothing UVs, UGC accessories, and glossy solid-black vertical-oval eyes** with **richly textured stylized sets, `AgX - Punchy` Kelvin lighting, high-detail hero props, and verified `-14.7 LUFS` comedy timing**.

> [!INFO] Playable Master Video
> ![[out/final.mp4]]

---

## 1. Visual Verification Stills (`frame_0000` + Full 1fps Contact Sheets)

![[out/qa_stills/frame_0000.png]]

![[out/qa_stills/final_sheet_01.png]]

![[out/qa_stills/final_sheet_02.png]]

![[out/qa_stills/final_sheet_03.png]]

---

## 2. Verified Technical & QA Specs (`short_qa.py` Passed — Exit `0`)

| Metric | Verified Output (`videos/roblox-reel-Df1kubCJ-o0-v2/out/final.mp4`) |
| :--- | :--- |
| **Resolution & FPS** | `1080×1920` (9:16 Vertical, Lanczos upscale from `720×1280` EEVEE `samples=12`), `30 fps` (`2,941` frames) |
| **Duration & File Size** | `98.033 s`, `125,888,966 bytes` (`h264`, `yuv420p`, `bt709` color tags) |
| **Audio & Loudness** | `AAC 48000 Hz` stereo · **`-14.7 LUFS`** (`LRA: 2.3 LU`, `Peak: -3.6 dBFS`) · **`SILENCES none`** |
| **Automated Frame Integrity** | Black frames: **`0`** · Unplanned white flashes: **`0`** · Frozen spans `>=12f`: **`0`** · Mean motion diff: **`4.58`** |
| **Voiceover (`make_voice.py`)** | Single consistent Fish Audio S2-Pro model (`eb4bcc6dbb634e9eaee239c94266935e`) across all spoken beats (`51` beats, `340` aligned words via `faster-whisper`) |
| **Signature SFX** | Real MyInstants 3-hit `"HUSS!"` burst (`audio/huss_sfx_clean.wav`, `0.620 s`, onsets `[0.043, 0.258, 0.445]`): 1× for `b17_huss_3`, 2× chained for the 6-hit beats |
| **Music Bed (`audio_mix.py`)** | `"Numbers"` — TEMPOREX (`audio/song_numbers.mp3`) with smooth `-7 dB` voice-envelope sidechain ducking and a `0.12×` ramped comedy dip on the rejection sequence (`b32`–`b37`) |
| **Subtitles (`post_and_mux.py`)** | Rule-27 black rounded pill (`rgba(8,8,10,0.91)`) at `y = 1340 px`, crisp `#FFFFFF` bold sans with `#FFE600` active-word pop (`HUSS!` always standalone `76 px`) |

---

## 3. Five Reusable Engineering Breakthroughs (Copy This Architecture)

### A. Authentic Roblox Studio R15 Blocky Proportions in Pure `bmesh` (`char_factory.py`)
- Built 100% procedurally via `bmesh` (`~1.75 m` height, ZERO `bpy.ops.mesh` scene-build stalls) so studio lighting and props fit exact true-SI meters:
  - **Armature**: `Root -> Pelvis -> Torso (0.70..1.32m) -> Head (1.34..1.75m)`, shoulders at `x = ±0.435`, hips at `x = ±0.150`. Every edit bone calls `b.align_roll(Vector((0, 1, 0)))` so `+X` pose rotation cleanly swings arms forward (`+Y`).
  - **Blocky Silhouette**: Rectangular beveled Torso `(0.59, 0.30, 0.62)` (`bevel=0.020m`), Legs `(0.282, 0.288, 0.676)` (`bevel=0.018m`) + thin sole plate, 2-segment Arms with **square Roblox R15 hands** `(0.242, 0.242, 0.112)` (`bevel=0.016m`), and Head `(0.43, 0.37, 0.41)` (`bevel=0.032m`, crisp blocky bevel instead of over-rounded vinyl spheres).
  - **Inward Wrapping Poses**: For blocky shoulders at `x = ±0.435`, use inward `Ry` (`arm_l=(52, -24, -10), forearm_l=(32, -12, 0)`) so forearms converge over table props instead of flaring outward.

### B. WYSIWYG 2-Half Clothing UV Atlases & Anti-Glare Face Ink (`textures_factory.py`, `scene_common.py`)
- **`subdivide_edges(cuts=2)` BEFORE `BEVEL`**: Prevents `BEVEL` from stretching UVs on Torso, Legs, and Head.
- **Right-Reading 2-Half Character UV (`[0.02..0.48]` Front / `[0.52..0.98]` Back & Sides)**: Maps front `+Y` faces with `u = 0.5 - (vx - cx) / sx` so chest graphics (white heart, lightning bolt, burgundy suit pocket square, lapels, denim pockets) render WYSIWYG without mirroring or leaking onto backs/armpits, while the bottom `16%` wraps around all 4 vertical leg faces for crisp Roblox sneakers/dress shoes (`textures/chars/`).
- **Matte Eye Ink Shader (`scene_common.py:make_skin_face_mat`)**: Sets `Coat Weight = 0.0` and uses decal `Alpha` to mix `Roughness = 0.62` and `Specular IOR Level = 0.04` on eye/mouth ink — eliminating milky gray light glare over solid-black vertical-oval Roblox eyes (`draw_glossy_eye`).

### C. Stylized Textured Worlds + High-Detail Hero Props (`props_factory.py`, `textures_factory.py`)
- Pairs blocky Roblox avatars with rich tactile world surfaces (`wood_planks_honey`, `wood_table_espresso`, `brick_blue_wainscot`, `tile_cream_diner`, `asphalt_speckled`, `sidewalk_pavers`, `wrapper_paper_yellow` + dedicated bump maps) and smooth subsurfaced/beveled props (sesame-seed hero burger, 4-flap animated wrap sheet, whiskered cat, clocks, cast-iron griddle, fried egg & bacon, 7-segment 3D LED `001 -> 400` scoreboard).

### D. 1st-Person POV Wrapping & Deterministic `HUSS!` Camera Kicks (`scene_common.py`)
- **`set_pov_arms_only(alex, True)` + `lens = 24mm`**: Hides head/torso/legs while angling blocky forearms inward (`Ry = ±26°..34°`) over `build_animated_wrap_sheet` so top-down POV wrapping frames match Roblox POV gameplay.
- **`kick_offset` in `set_camera_look`**: Default `-1` (so normal shots stay steady without accidental tilt), triggered to `f - last_huss_frame` (`0..6`) for deterministic 7-frame sign-flipping Z-lift & roll kicks synced directly to `huss_hit_times`.

### E. Crash-Resumable Multi-Set Pipeline (`scene_*.py`)
- Splits all 51 beats cleanly across 4 independent headless Blender 5.3 scene renders (`scene_exterior.py` -> `scene_town.py` -> `scene_room.py` -> `scene_buntown_interior.py` sequentially on RTX 2050 4GB VRAM) writing crash-resumable `frames/f_%04d.png`.

---

## 4. Production Files

| Component | Path / Vault Link | Role |
| :--- | :--- | :--- |
| **Voice & SFX Builder** | `videos/roblox-reel-Df1kubCJ-o0-v2/make_voice.py` | Single Fish Audio model (`eb4bcc6dbb634e9eaee239c94266935e`) + trimmed MyInstants HUSS bursts + `faster-whisper` word timestamps (`beats.json`, `words.json`, `shots.json`) |
| **Audio Mixer & Master** | `videos/roblox-reel-Df1kubCJ-o0-v2/audio_mix.py` | TEMPOREX `"Numbers"` bed, Foley spot SFX, rejection comedy dip, `-7 dB` sidechain ducking, `-14 LUFS` `loudnorm` -> `audio/mix.wav` |
| **Texture Generator** | `videos/roblox-reel-Df1kubCJ-o0-v2/textures_factory.py` | Environment, prop signage/dials, 36 2-half `1024×1024` Roblox clothing atlases (`textures/chars/`), and 30 Roblox face decals (`textures/faces/`) |
| **Shared Render / Look-Dev** | `videos/roblox-reel-Df1kubCJ-o0-v2/scene_common.py` | Blender 5.3 `BLENDER_EEVEE` RT+GI, `AgX - Punchy`, `make_textured_pbr`, anti-glare `make_skin_face_mat`, `set_camera_look`, `render_frame` |
| **R15 Character Factory** | `videos/roblox-reel-Df1kubCJ-o0-v2/char_factory.py` | Pure-`bmesh` Roblox Studio R15 blocky rig + 9 custom-dressed characters + blink/POV helpers |
| **Props Factory** | `videos/roblox-reel-Df1kubCJ-o0-v2/props_factory.py` | Pure-`bmesh` burgers, animated 4-flap wrap sheet, cat, clocks, breakfast, griddle, blocky blur arms, townhouses, trees |
| **4 Scene Renderers** | `scene_exterior.py`, `scene_town.py`, `scene_room.py`, `scene_buntown_interior.py` | 51 animated beats rendered to `frames/f_0001.png`–`f_2941.png` |
| **Captions & Mux** | `videos/roblox-reel-Df1kubCJ-o0-v2/post_and_mux.py` | `1080×1920` Lanczos upscale, synced Rule-27 black-pill captions, `bt709` H.264 + AAC mux |
| **QA & Upload Kit** | `out/qa_visual/report.md` · `upload.md` | Automated `short_qa.py` report + [[Upload Package - Bun Town Burger Wrapper (Roblox R15)]] |

## Related Vault Guides
- [[00 Completed Videos]]
- [[Style 5 - Roblox Animated Shorts (Ropilot + ForgeGUI + Blender R6-R15)]]
- [[Roblox R6 Story Cast & Marketplace Character Factory (Blender 5.3)]]
- [[Roblox Studio 3D Pipeline (Ropilot + ForgeGUI + Blender)]]
- [[Blender 5.3 Cinematic Rendering & Animation Mastery Bible]]
