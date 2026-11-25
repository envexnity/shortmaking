---
title: Post-Completion Visual QA — What, How & Why to Fix
tags:
  - qa
  - visual-inspection
  - look-dev
  - anti-slop
  - troubleshooting
  - post-render
area: multi-agent
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-20
summary: Mandatory post-completion visual inspection protocol for every rendered short across all 7 engines—how to extract inspection frames, every visual defect to check for (including Blender 5.3 PBR/look-dev anti-slop), how to fix each one, and why each fix protects viewer retention and look-dev quality.
---

# Post-Completion Visual QA — What, How & Why to Fix

> [!CAUTION] Mandatory Final Gate (All 5 Styles)
> **Every single rendered `.mp4` MUST be inspected VISUALLY after completion before shipping or uploading.**
> Numeric scripts like [[Automated Frame & Audio QA (short_qa.py)|`short_qa.py`]] only catch signal errors (black frames, white flashes, frozen pixel spans, missing audio). A video can pass `short_qa.py` with a `100% PASS` while characters are bisected by railings, captions are hidden behind the TikTok UI, transparent planes have black boxes, or faces stare deadpan with zero blinks.

---

## 1. How to Inspect Every Completed Video Visually

Never rely on *"the code looked right"* or *"it rendered without errors"*. Always inspect the actual pixels from the **final muxed `.mp4`** (`final_master.mp4`), not an intermediate silent render.

### Step A: Generate 2-Second Contact Sheets + High-Res Inspection Stills
1. **Run `short_qa.py` (produces `sheet_XXXX.jpg` grids with burned-in frame numbers + `report.md`)**:
   ```powershell
   python "90 Templates & Starter Kits/cartoon-3d-short-kit/scripts/short_qa.py" out/final_master.mp4 out/qa_visual
   ```
   This writes 2-second (`60-frame`) contact sheets (`out/qa_visual/sheet_0000.jpg`, `sheet_0060.jpg`, ...) for scanning motion continuity, cut timing, blinks, and frame-level pops across the whole timeline.
2. **Extract Full-Detail Midpoint & Boundary Stills (for checking thin ink lines, eyes, text, & clipping)**:
   `short_qa.py` thumbnails are `108×192`—too small to inspect `3px` plum outlines, eye lids, or small HUD text. Always extract high-res (`540×960` or full `1080×1920`) frames at:
   - **Frame `0`** (`t = 0.00s` — the hook / shelf thumbnail frame)
   - **`1 frame` before and `1 frame` after every cut** (catches stray transition frames & jump cuts)
   - **Every shot midpoint** (`1 frame` per second or via `bridge-stills.mjs` / `tools/sheet.py`)
   - **The final frame** (verifies clean ending / loop seam)
   ```powershell
   # Extract 1 frame per second + Frame 0 at readable 540x960 resolution and tile into a review sheet:
   New-Item -ItemType Directory -Force -Path out/qa_stills | Out-Null
   ffmpeg -y -i out/final_master.mp4 -vf "fps=1,scale=540:960" out/qa_stills/sec_%03d.jpg
   ffmpeg -y -i out/final_master.mp4 -vf "select='eq(n,0)'" -vframes 1 out/qa_stills/frame_0000.jpg
   ```
3. **Inspect with Zero-Context Eyes**:
   Use multimodal vision (`read_file` on the PNG/JPG stills and `sheet_*.jpg` grids, `blender` MCP `look`, or a fresh zero-context critic subagent as in [[The Cook Loop for Autonomous Visual Polish]]). **Never skip inspecting Frame 0 and the 1fps stills.**

---

## 2. Master Visual Defect Guide: What to Fix, How to Fix, and Why

Use the tables below while scanning your contact sheets and high-res stills.

### A. Framing, 9:16 Safe Zones & Camera Grammar

| What to Look For (Symptom) | How to Fix It (Exact Action) | Why Fix It (Impact & Principle) |
| :--- | :--- | :--- |
| **1. Captions, HUD, or Hero Faces Covered by Platform UI** (inside top `0–220px`, bottom `1420–1920px`, or right `920–1080px` at `1080×1920`) | Move burned-in captions (`remotion-captions` / `KAZ` `hud.cap`) to **`y = 1280–1400px` (`66%–73%` height)**. Keep hero heads inside `x = 160–880px`, `y ≥ 220px`, and KAZ top HUD cards at `y ≥ 140px`. | YouTube Shorts, TikTok, and Reels overlay search icons, channel names, and Like/Share buttons on these margins. Covered faces or text immediately trigger swipes. |
| **2. Foreground Props Blocking the Subject** (tree, pillar, wall, or leaf crossing the hero's face or action) | Enforce a **`2.0m` cylinder clearance** along the ray from `camera.position` to `hero.position`. Push framing props (branches, barrels) into the **outer 18% left/right margins** (`story.ts`, `world.ts`, or Blender cam). | If a viewer cannot read the character's eyes or prop in `<0.3s`, comprehension breaks and retention drops sharply on mobile screens. |
| **3. Railings or Horizontal Bars Slicing Through Faces/Mouths** | Lower bridge/balcony railings to **`y ≤ 0.85–0.95m`** (chest/waist height on a `2.15m` card) and raise camera height to `cam.y ≥ 1.65m`. | Horizontal geometry across eyes or mouths destroys character expression readability and reads as amateur placement. |
| **4. Weak or Blank Frame 0** (black fade-in, empty sky, distant wide with no clear focal anomaly) | Start Frame `0` at full brightness directly on a high-contrast visual hook (subject close-up, mid-collapse prop, or bold KAZ HUD anomaly). Never start with a fade from black. | The `0–3s` **Viewed vs. Swiped Away** gate (`>78%` target) is decided in the first `0.5s`—and Browse/Search shelves often display Frame 0. |
| **5. Jump-Cut Pop Between Similar Angles** (camera snaps slightly sideways/closer on a cut) | Apply the **30° / 40% Rule**: every hard cut must change azimuth by `≥ 30°` OR distance by `≥ 40%`. If closer, replace the cut with a `18–40f` `smootherstep` `glide()`. | Cuts between cameras `<1.5m` and `<15°` apart look like a rendering glitch or dropped frame rather than an intentional edit. |
| **6. Static / Frozen Hold Frames** (character or camera sits completely still for `≥ 4–12f`) | Add mandatory `push(camera, shot.cam, u, 0.0025)` hold creep + `4f` blinks every `~1.2s` (Toon), or pair `KAZ.orbit`/`dolly` with continuous object bob/rotation (`make-3d-video`). | Static frames feel like buffering on TikTok/Shorts, spiking instant swipe-aways and failing `short_qa.py`'s `≥12f` frozen-span check. |

---

### B. 3D Geometry, Physics & Spatial Grounding

| What to Look For (Symptom) | How to Fix It (Exact Action) | Why Fix It (Impact & Principle) |
| :--- | :--- | :--- |
| **7. Floating or Sunken Characters, Props & Wheels** (gap under shoes/tires, or half-buried wheels/legs) | Align character card soles (`y = 975` on `600×1000` canvas) to ground `y = terrainHeight(x, z)`. Place a multiply-blended contact shadow blob (`0.7×1.1m`) at `y + 0.01`. Set wheel centers to `y = wheelRadius`. | Without ground contact and a contact shadow blob, 2D cards and 3D props look "pasted on" and weightless rather than physically present in the scene. |
| **8. Hanging / Swinging Prop "Neck-Hanging" Bug** (swing seat, rope, or lantern rotating around its bottom center) | Set the `Group` pivot at the **top attachment anchor (`y = branchY`)**, keep the beam/branch visible in frame, and model **two ropes (`x = ±0.42m`)** straddling the character's shoulders down to a seat board. | Single-rope or bottom-pivoted swings visually read as a noose or broken physics and break audience immersion immediately. |
| **9. Mesh Clipping & Z-Fighting Flicker** (arm passing through table, two coplanar faces shimmering, Blender cutaway fighting interior mesh) | Offset coplanar planes by `≥ 0.005–0.02m` (`polygonOffset` or physical gap). Adjust character `z` / prop offsets. In Blender booleans (`EXACT` solver), verify cutter bounds don't graze parallel faces. | Z-fighting creates distracting strobe artifacts under H.264 compression, and limb clipping screams "AI slop" to viewers. |
| **10. Sideways Vehicles & Historical / Prop Hallucinations** (carriage facing perpendicular to road, wrong period flag/helmet) | Align vehicles using `Math.atan2(dx, dz)` along road tangents. Audit flags, uniforms, and props on the 1fps stills against historical era (e.g., 1880s Britain = Union Jack + Home Service helmet, not St. George's Cross). | Historical and logic inaccuracies trigger negative distraction in comments or make the visual story nonsensical. |

---

### C. Outlines, Shaders, Lighting & Color Grade

| What to Look For (Symptom) | How to Fix It (Exact Action) | Why Fix It (Impact & Principle) |
| :--- | :--- | :--- |
| **11. Black Rectangular Boxes Around Characters, Smoke, Clouds, or Water** | Call `enableNoInk(mesh)` (`mesh.layers.enable(3)`) on every alpha-mapped card, sky dome, cloud, smoke puff, water sheet, and painted sign face. | `InkPass` detects depth/normal discontinuities on the quad geometry edges unless the `NOINK = 3` layer mask tells it to skip transparent cards. |
| **12. Glowing "Neon" Characters or Blown-Out White Shirts** | Remove `emissiveMap` from character cards. Use `cardShade(texture)` (`V ≥ 0.86` floor) and keep `BloomEffect` `luminanceThreshold ≥ 1.0`. | `emissiveMap` pushes whites above `1.0`, triggering `BloomEffect` halo bleed that washes out facial ink lines and looks synthetic. |
| **13. Blurry / Blocky World Outlines or Out-of-Focus Crisp Lines** | Verify `EffectComposer` order in `Bridge.tsx` / `main.js`: `RenderPass` → `InkPass` (standalone `Pass`) → `EffectPass(LensBlurEffect, BloomEffect, ToneMappingEffect, GradeEffect)`. Render final Toon master at `--scale=1.3333` (`1440×2560`). | If `InkPass` runs *after* `LensBlurEffect`, distant blurred trees get razor-sharp ink rings over bokeh. Rendering at 2K vertical prevents YouTube/TikTok compression from chewing up `3px` ink lines. |
| **14. Dark, Unreadable Painted Signs or Crushed Muddy Shadows** | Keep sign frames in `shade()`, but set the **painted sign face to `MeshBasicMaterial` + `enableNoInk()`** (`#241726` ink on `#f5ebd6` cream). In golden-hour shots, set explicit violet-blue shadow tint (`#5b5173`, `B/R 1.35–3.0×`) instead of muddy grey/black. | Directional `shade()` drops backlit sign faces to `0.50×` brightness, making critical comedic/story text illegible on mobile phones. |
| **15. Flat / Unseparated Subject Silhouette (Blender / Roblox / KAZ)** | Add a cool/warm **rim light** behind the hero (`7600K` `AREA` light with narrow `spread` in Blender 5.3 / Roblox) to separate hair/shoulders from dark backgrounds, and verify `bt709` color space tags on FFmpeg export (`-colorspace bt709 -color_primaries bt709 -color_trc bt709`). | Without rim separation or `bt709` color tags, subjects blend into dark sets and macOS/iOS devices show washed-out gamma shifts. |
| **15b. Plastic CG Look, Flat Grey World, or Blown-Out `Standard` PBR (Blender 5.3)** | Switch `view_transform` to **`AgX` (`AgX - Punchy`)**, replace default grey world with `setup_dark_studio_world` or `MULTIPLE_SCATTERING` sky, run `add_cinema_bevel` (`0.008–0.02m` + `WEIGHTED_NORMAL`), and use `make_pbr_material` (procedural roughness breakup + bump + albedo weathering + `Diffuse Roughness`). | Razor-sharp edges, uniform scalar `Roughness = 0.5`, grey ambient shadows, and clipped highlights instantly read as low-effort AI/2005 CG. |
| **15c. Cycles Fireflies / Denoiser Blotches or Corrupted Track 7 Depth/Normal Passes** | In Cycles, enable GPU `OPENIMAGEDENOISE` (`RGB_ALBEDO_NORMAL`, `ACCURATE`), set `sample_clamp_indirect = 8.0`, and raise low-sample drafts to `32–48 spp`. On Track 7 `OutputFile` passes, verify `save_as_render = False` on `depth_` / `norm_` so `AgX`/`sRGB` doesn't distort linear data. | Under-sampled Cycles smears details into watercolor blotches, and color-managed depth/normal maps create broken `t3ssel8r` ink lines. |

---

### D. Character Acting, Expressions & Lip-Sync

| What to Look For (Symptom) | How to Fix It (Exact Action) | Why Fix It (Impact & Principle) |
| :--- | :--- | :--- |
| **16. Uncanny "Dead Stare" or Late Facial Reactions** | Add deterministic **`4-frame` blinks** (`[0.5, 1, 1, 0.5]`) every `0.5–2.3s` + on every expression swap. Trigger brow/eye changes (`brows='v'`, `mouth='o'`) **`2 frames` (`~67ms`) BEFORE** the spoken punch word in `words.json`. | Human perception registers an expression that happens *after* a word as laggy/robotic; a `2f` anticipation lead makes 2D cards feel alive. |
| **17. Talking Mouth During Silence (or Frozen Mouth During Dialogue)** | Gate mouth shapes (`open`/`o` vs. `line`/`smirk`) strictly by `words.json` active-word intervals or RMS voice envelope (`amp > threshold`) at `10 Hz`. | Mouth flap during narration gaps breaks illusion immediately. |
| **18. Unwanted Blush Ovals, Eye Catchlights, or Pure Black `#000000` Character Ink** | In `toon.ts` / `roman.js`, enforce `#241726` warm plum ink (`3:1` thick/thin ratio), default `lidded` eyes, zero cheek blush ovals, and zero white specular eye dots. | Generic AI anime/cartoon defaults (blush + specular dots + `#000` ink) clash with the cohesive painted 3D world palette. |
| **19. Robotic / Linear Motion Curves or Missing Motion Blur (KAZ, Blender 5.3, EffectCraft, Roblox)** | Replace linear interpolation with `smootherstep(u)` (`motion.js`), `KAZ.enter()` spring entrances + `walk`/`idle` cycles (`kit.js`), `set_keyframe_easing` (`BEZIER`/`BACK`/`EXPO` on Blender 5.3 Slotted Actions) + `use_motion_blur = True` (`shutter = 0.5`), `75–85%` Bezier ease (`effectcraft`), or `Back.Out` + `3f` anticipation (`ropilot` / ForgeGUI). | Linear starts/stops and frozen zero-blur fast swings feel mechanical and kill kinetic satisfaction. |

---

### E. Captions, HUD Telemetry & End-of-Video Artifacts

| What to Look For (Symptom) | How to Fix It (Exact Action) | Why Fix It (Impact & Principle) |
| :--- | :--- | :--- |
| **20. Illegible, Overlapping, or Stale HUD / Captions** | Cap `hud.cap` / captions to `≤ 2 lines`, use high-contrast fill + dark stroke/pill (`remotion-captions`), verify escalating counters actually increment per beat, and check `cards` don't overlap `tl`/`tr` badges on `1080×1920`. | Viewers rely on captions/HUD to lock onto fast `2.6–3.7 wps` narration; overlapping or clipped text breaks trust and comprehension. |
| **21. Stray Single-Frame Pops at Cut Boundaries or Mid-Shot** | Inspect `POPS` in `out/qa_visual/report.md` and check `f_cut - 1` and `f_cut + 1` in `sheet_*.jpg`. Fix off-by-one `SHOTS` boundaries (`f >= s && f < e`), late camera state resets, or `1f` visibility toggles. | A 1-frame flash of the previous camera or unpositioned rig reads as a glitch. |
| **22. Dead Silent Tail or Abrupt Audio Cut-Off at the End** | Trim the final video frame to **`≤ 0.08s` after the final spoken syllable**, verify `-map 0:v:0 -map 1:a:0 -shortest` in FFmpeg, and match ending lighting/horizon to Frame 0 if looping. | Even `0.5–1.5s` of dead air at the end gives viewers time to swipe before the loop restarts, tanking Average Percentage Viewed (`APV`). |

---

## 3. The Post-Completion Fix & Re-Verify Loop

When visual inspection catches one or more defects:

1. **Log Exact Frame Numbers & Coordinates**: Record `[f_start..f_end]` from `sheet_*.jpg` and the exact defect category (e.g., *"f342–f410: right-side tree at x=1.2, z=2.5 clips soldier's hat"*).
2. **Route to the Single Owning Module** (never rewrite the whole project):
   - Camera / framing / cut timing → `story.ts` (`sb-cam`) / `shots.js` / Blender camera
   - 3D props / railings / pivots / ground height → `world.ts` (`sb-world`) / `shots.js` / Blender scene
   - Lighting / shadows / sign readability / `NOINK` → `shade.ts`, `cardshade.ts`, `lights.ts` (`sb-mat`)
   - Character ink / proportions / blinks / mouth sync → `toon.ts`, `cast.ts` (`sb-char`) / `roman.js`
   - Composer / DOF / grade / captions / FFmpeg color tags → `Bridge.tsx`, `ink.ts`, `lensblur.ts`, `grade.ts`, or FFmpeg export
3. **Re-Render & Re-Inspect**:
   - Render the updated `.mp4` (cleaning `$env:TMPDIR\remotion-*` first if using Remotion).
   - Re-run `short_qa.py` AND re-extract stills for every modified shot to verify the fix introduced **zero regressions**.

---

## 4. Go / No-Go Visual Sign-Off Checklist (Run Before Delivery)

- [ ] **Frame 0 Hook**: Bright, high-contrast, unobstructed subject/anomaly on the very first frame.
- [ ] **9:16 Safe Zones**: All faces, captions, and HUD elements clear of top `220px`, bottom `500px`, and right `160px` UI zones.
- [ ] **Zero Occlusion & Clipping**: No props blocking faces (`>2m` ray clearance), no chest-above railings bisecting heads, no limb/mesh clipping or z-fighting.
- [ ] **Grounding & Physics**: Feet/wheels sit flush on terrain with contact shadows; hanging props pivot at overhead anchor with visible support.
- [ ] **Clean Outlines & Lighting**: No `NOINK` black boxes around cards/smoke/clouds; no `emissiveMap` neon glow; signs readable; `InkPass` before DOF.
- [ ] **Alive Acting & Motion**: Every shot moves (`push()`, `glide()`, `orbit`/`dolly`); characters blink (`4f`), react `2f` early, and lip-sync cleanly.
- [ ] **Technical & Audio Clean**: `short_qa.py` reports `0` black frames, `0` unplanned white flashes, `0` frozen spans `≥12f`, `0` unplanned pops, `-14 LUFS` audio present, and clean `<0.08s` ending.
