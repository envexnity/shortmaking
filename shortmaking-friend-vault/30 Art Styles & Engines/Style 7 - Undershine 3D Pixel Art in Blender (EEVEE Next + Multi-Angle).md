---
title: Style 7 — Undershine 3D Pixel Art in Blender (EEVEE Next + Multi-Angle)
tags:
  - engine
  - blender
  - eevee-next
  - pixel-art
  - undershine
  - multi-angle
  - shadows
area: engines
style: undershine-3d-pixel
status: evergreen
created: 2026-11-19
updated: 2026-11-20
summary: Production engine guide for Track 7 — building atmospheric, non-arcady @playundershine-style 3D-to-pixel-art vertical shorts in Blender 5.3 EEVEE (`BLENDER_EEVEE`) with real directional shadows, hue-shifted lighting, Ghibli foliage normals, t3ssel8r normal/depth edge post-processing, and 8-angle cinematic camera switching.
---

# Style 7 — Undershine 3D Pixel Art in Blender (5.3 `EEVEE` + Multi-Angle)

> [!IMPORTANT] Research Bible & Reusable Kit
> - **Deep Research Bible**: [[Deep Research - Undershine 3D Pixel Art, Atmospheric Shadows & Multi-Angle Blender Cinematography]]
> - **Blender 5.3 API & Look-Dev Reference**: [[Blender 5.3 Cinematic Rendering & Animation Mastery Bible]]
> - **Reusable Starter Kit**: `90 Templates & Starter Kits/undershine-blender-pixel-kit/`
>   - `blender_pixel_lib.py` — Blender 5.3 `BLENDER_EEVEE` shaders, Ghibli trees, water, lanterns, particles, multi-camera timeline markers & `compositor_effects` PNG pass exporter (with `save_as_render=False` on linear Depth/Normal passes)
>   - `pixel_postprocess.py` — Vectorized NumPy/OpenCV `t3ssel8r` Depth-Silhouette Ink (`#181326`), Normal Bevel Highlights, Atmospheric Mist, Emissive Glow, 4×4 Bayer Dither, `4×` Nearest-Neighbor Integer Upscale, and crisp `1080×1920` `8sb2R11FeVw` Black-BG Subtitle Pills
> - **Reference Showcase Video**: `videos/undershine-blender-demo/`

Use **Track 7** whenever you want **rich, atmospheric, non-arcady pixel art** like **`@playundershine`** (*UNDERSHINE*), ***A Short Hike***, ***Octopath Traveler* (HD-2D)**, or ***Eastward*** — with **real 3D geometry, crisp cast shadows, warm lanterns/campfires, fog-softened cliffs, and multi-angle 3D camera cuts** instead of flat single-angle 2D sprites.

---

## 1. Track 7 Core Production Spec

| Parameter | Exact Production Constant | Why |
| :--- | :--- | :--- |
| **3D Engine** | **Blender 5.3 `BLENDER_EEVEE`** (headless CLI) | Renders `270×480` frames in `~0.15–0.25 s/frame` with full real-time 3D shadows & `compositor_effects` passes |
| **Native Render Resolution** | **`270 × 480`** (default, `4×` scale) or **`360 × 640`** (`3×` scale) | Exact integer divisors of `1080×1920` — zero uneven pixel scaling |
| **Pixel Filter Size** | **`scene.render.filter_size = 0.01`** | Eliminates blurry AA edges; produces crisp pixel grid directly out of 3D |
| **Shadow Crispness** | `sun.data.angle = 0.018 rad`, `taa_render_samples = 12` | Razor-sharp graphic shadows across terrain, cliffs, bridges & water |
| **Color Management** | `Standard` view transform (`sRGB`) | Preserves exact hand-tuned hue-shifted color ramps without muddy desaturation |
| **Outline & Edge Ink** | **Depth silhouette** in `#181326` (deep plum, 55–65%) + **+12% Normal convex highlight** | Separates silhouettes cleanly without harsh `#000000` arcade outlines |
| **Atmosphere** | Blender **`Mist` pass** + **`Emit` pass glow** + subtle **`4×4` Bayer dither** | Melts horizon into warm/twilight haze and makes lanterns/fires feel alive |
| **Camera Grammar** | **6–8 distinct Blender cameras** bound to `scene.timeline_markers` | Ends single-angle monotony; every cut shifts ≥2 of `(Azimuth, Elevation, Lens)` |
| **Character Framerate** | **Stepped on twos (`15 fps`)** inside **`30 fps`** world/camera | Tactile indie-RPG charm while camera pans, water, wind & fireflies stay smooth |
| **Subtitles & Audio** | High-res `1080×1920` **`8sb2R11FeVw` black-bg pills** + `en-AU-WilliamNeural` (`+4%`) + `-14 LUFS` mix | Ultra-legible modern mobile packaging over lush retro 3D pixel art |

---

## 2. The 5-Step Track 7 Production Pipeline

### Step 1: Write the Script & Generate Word-Level Timing (`< 45s` Cap)
1. Write a tight **`< 45s` (`25–42s` sweet spot, `95–148 words`)** script obeying [[The 1-Sentence Paradox Hook Formula]] and [[Script Architecture - 3.7 WPS & The 'You See' Pivot]] (`3.2–3.8 wps`).
2. Generate voiceover with `edge-tts` (`en-AU-WilliamNeural`, `rate="+4%"`) and align exact word timestamps with `faster-whisper` → `voice/words.json`.

### Step 2: Plan the Multi-Angle Shot List (Minimum 6 Distinct Angles)
Never reuse the same angle back-to-back. Map every `1.5–3.2 s` beat to a distinct archetype from the **8-Camera Matrix**:
1. **3/4 Isometric Diorama (`110mm` / `ORTHO`, `34°` pitch)** — Establish world geography & cast shadows.
2. **Low-Angle Worm's-Eye (`26mm`, `z = 0.55m`)** — Ground-level grass/mushrooms looking UP at hero/monument.
3. **Side-Profile Parallax Track (`48mm`)** — Lateral truck behind dark silhouetted foreground trunks.
4. **High Bird's-Eye Top-Down (`55mm`, `76°` pitch)** — Reveal winding river, bridge & shadow geometry.
5. **Over-the-Shoulder (OTS) Follow (`35mm`)** — Behind hero shoulder aiming down path toward glowing objective.
6. **Tight Dutch-Angle Macro Close-Up (`72mm`, `+7°` roll)** — Flickering campfire/lantern/rune detail.
7. **Foreground-Framed Peek (`60mm`)** — Sliding reveal framed through stone arch or foliage.
8. **Dramatic Crane Orbit Reveal (`32mm`)** — Rising quarter-orbit across the whole lit twilight valley.

### Step 3: Build & Render the 3D World in Blender 5.3 (Headless)
Import `blender_pixel_lib.py` in your scene script (`build_scene.py`):
- Build real 3D terraced terrain, stepped stone bridges/stairs, fluffy Ghibli-normal-transferred trees (`make_foliage_tree`), wind-swaying grass, animated river/waterfall, flickering campfire/lanterns, glowing particles, and stepped hero character (`apply_stepped_on_twos` for Blender 5.3 Slotted Actions).
- Use `make_hue_shifted_toon_mat(...)` for every material (warm-shifted highlights, earthy midtones, cool indigo/plum shadows, snapped procedural grain).
- Bind every camera shot with `add_multi_angle_shot(...)` so Blender switches cameras automatically across `scene.timeline_markers`.
- Render natively at `270×480` using `setup_passes_compositor(...)` (Blender 5.3 `scene.compositor_effects`, `rl.outputs["Emission"]`, `file_name=""`, `media_type="IMAGE"`, `compression=0`, `use_persistent_data=True`, `taa_render_samples=8`, and `save_as_render=False` on linear 16-bit `depth_` and `norm_` passes), using `fast_blender_render.py` to shard across parallel Blender 5.3.0 workers:
```powershell
python "90 Templates & Starter Kits/undershine-blender-pixel-kit/fast_blender_render.py" --script build_scene.py --frames 1200 --workers 3
```

### Step 4: Run the `t3ssel8r` / *Undershine* Pixel Post-Processor & Subtitle Compositor
Run `pixel_postprocess.py` to apply:
- Relative depth silhouette darkening (`#181326`)
- Convex normal sunlit pixel bevels (`+12%`)
- Dynamic per-shot atmospheric mist color (golden hour → sunset → twilight)
- Warm emissive bloom halo on fires/lanterns/runes/fireflies
- Subtle 4×4 Bayer dither & palette cohesion
- Exact **4× Nearest-Neighbor integer upscale (`270×480` → `1080×1920`)**
- Crisp `1080×1920` **`8sb2R11FeVw` black-bg subtitle pills** with active-word `#FFE600` pop
- Pipe directly into `ffmpeg` (`libx264`, `-crf 17`, `-pix_fmt yuv420p`)!

### Step 5: Mix `-14 LUFS` Audio, Mux Explicitly & Run Visual QA
1. Mix voiceover + fitting atmospheric music (e.g. `Snowfall (Slowed + Reverb)` or `Resonance` at `-6 dB` gated RMS ducking) + `2–4f` pre-cut whooshes (`whoosh.wav` / `whoosh_low.wav`) + frame-0 impact (`riser_hit.wav`) + subtle water/fire ambience.
2. Mux explicitly (`-map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest`).
3. Run `python scripts/short_qa.py final.mp4 out/qa_visual` and **visually inspect stills from EVERY camera angle** per [[Post-Completion Visual QA — What, How & Why to Fix]].

---

## 3. Anti-Slop Checklist for Track 7 Shorts

- [ ] **Zero Pure `#000000` Outlines or Shadows**: Every dark shadow & silhouette ink is hue-shifted toward deep indigo/plum (`#181326`–`#26243d`).
- [ ] **Real 3D Cast Shadows Visible in Every Outdoor Shot**: Sun light sits at a flattering cross/golden-hour angle (`elevation 18°–32°`, `angle = 0.018 rad`) so trees, cliffs, bridges, and characters throw bold readable shadows.
- [ ] **At Least 6 Distinct Camera Angles**: Check the QA contact sheet — no two consecutive cuts share the same angle or elevation.
- [ ] **Zero Static Holds**: Every single camera shot moves (`push`, `truck`, `orbit`, or `crane`) and natural elements (water, grass, fire, fireflies, character) stay alive.
- [ ] **Warm vs. Cool Contrast**: Cool shadow zones are punctuated by warm glowing practicals (campfires, lanterns, torches, windows) or golden rim light.
- [ ] **Razor-Sharp Pixels + Crisp High-Res Subtitles**: Pixel grid is exact integer `4×` (or `3×`) nearest-neighbor; black-bg subtitle pills are rendered at full `1080×1920` inside the safe zone (`y = 1320–1400 px`).
