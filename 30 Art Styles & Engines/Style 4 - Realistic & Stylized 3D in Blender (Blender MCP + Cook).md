---
title: Style 4 — Realistic & Stylized 3D in Blender (Blender MCP + Cook)
tags:
  - engine
  - blender
  - mcp
  - cook
  - realistic-3d
area: engines
style: realistic-3d
status: evergreen
created: 2026-11-15
updated: 2026-11-20
summary: Complete guide to Track 4 — building Zack D. Films / Fern style realistic & stylized 3D animated shorts in Blender 5.3.0 (Cycles OptiX GPU + EEVEE 5.3 RT + blender_cinema_lib.py) using the Blender MCP server and the Cook autonomous visual loop.
---

# Style 4 — Realistic & Stylized 3D in Blender 5.3 (`blender_cinema_lib` + `blender` MCP + `cook`)

> [!IMPORTANT] Mandatory Blender 5.3 Bible & Starter Kit
> - **Look-Dev & API Mastery Bible**: [[Blender 5.3 Cinematic Rendering & Animation Mastery Bible]]
> - **Reusable Cinema Library**: `90 Templates & Starter Kits/blender-cinema-kit/blender_cinema_lib.py`
> - **Primary Executable**: `C:\Program Files\Blender Foundation\Blender 5.3\blender.exe` (RTX 2050 `OPTIX` + GPU `OPENIMAGEDENOISE`)
> - **Active MCP Server**: `blender` (`execute_blender_code`, `get_scene_info`, `look`, `search_assets`, `import_asset`, `generate_3d`, `generate_gaussian_world`, `record_trajectory_feedback`) — *(if running live GUI MCP in 5.3, ensure `blender_mcp_addon` is installed/enabled in Blender 5.3's addons directory)*.
> - **Autonomous Polish Skill**: `.agents/skills/cook/SKILL.md`

When creating **Zack D. Films** (medical/mechanical cross-sections, anatomical simulations), **Fern / Hoog** (forensic crime/historical reconstructions with volumetric lighting), or **Stylized Clay/Diorama 3D** shorts, Three.js primitives aren't enough—you need **Blender 5.3's boolean cross-sections, skeletal rigs, cloth/fluid physics, bounded `Principled Volume` shafts, `AgX` tone mapping, and Cycles OptiX / EEVEE 5.3 raytraced shaders** orchestrated via headless `Blender 5.3\blender.exe` or `blender` MCP.

---

## 1. The `blender` MCP Tool Suite

Read the tool schemas in `<appDataDir>/mcp/blender/` before invoking via `call_mcp_tool`:

| Tool Name | Purpose in Short-Form Production |
| :--- | :--- |
| `get_addon_status` / `get_scene_info` | Inspect active objects, materials, armatures, cameras, frame range (`frame_start`, `frame_end`), and render settings. |
| `search_assets` / `import_asset` | Search PolyHaven / Sketchfab / Hyper3D / Hunyuan3D assets (PBR textures, HDRIs, 3D models) and import them straight into the Blender scene. |
| `generate_3d` | Generate custom 3D hero props or anatomical/mechanical meshes from text or reference images when no library asset matches. |
| `generate_gaussian_world` | Generate background 3D Gaussian Splatting / world environments for establishing shots. |
| `execute_blender_code` | Run arbitrary `bpy` Python scripts inside Blender 5.3 to build geometry, animate Slotted Actions, set up boolean cutaways, configure Cycles OptiX / EEVEE 5.3, and render stills. |
| `look` | Capture a viewport or rendered camera frame and inspect it visually with multimodal vision. |

---

## 2. The "Zack D. Films" Cross-Section & Camera Recipe (`bpy`)

The signature Zack D. Films look relies on **three specific Blender techniques** that you can script via `execute_blender_code`:

### A. Animated Boolean Cross-Section Cutaway (With Dark-Red/Metal Cap Material)
To slice open a human skull, jet engine, or submarine mid-shot:
1. Create a `CUBE` cutter object (`Cutter_Box`), set ` cutter.display_type = 'WIRE'`, and disable its camera ray visibility (`cutter.visible_camera = False`).
2. Add a **Solidify** or **Boolean (`DIFFERENCE`, Solver = `EXACT`)** modifier to the target anatomy/machine mesh, assigning slot 2 of the target's material list to a **Cross-Section Cap Material** (matte dark crimson `#6b1414` for biological tissue, or brushed dark steel `#22262b` for machines).
3. Keyframe `cutter.location.x` across `18 frames` (`Bezier` interpolation) while the camera dollies into the exposed interior.

### B. Blender 5.3.0 Cinematic Setup (`blender_cinema_lib.py` — Cycles OptiX / EEVEE 5.3 RT)
```python
import sys
sys.path.append(r"C:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\90 Templates & Starter Kits\blender-cinema-kit")
import blender_cinema_lib as bcl
import bpy

bcl.clear_scene()
scene = bpy.context.scene

# Option A: Hero Realism / Medical / Volumetric Shafts (RTX 2050 OptiX + GPU OIDN)
bcl.configure_cycles_optix(scene, res_x=1080, res_y=1920, fps=30, samples=48, view_transform="AgX", look="AgX - Punchy")

# Option B: Fast Stylized Diorama / High-Speed Iteration (Blender 5.3 EEVEE Raytracing)
# bcl.configure_eevee_cinema(scene, res_x=1080, res_y=1920, fps=30, samples=32, raytracing=True, fast_gi=True)

# Kill flat default grey world + add Kelvin 3-point rim separation + subtle compositor polish:
bcl.setup_dark_studio_world(scene, hex_col="#0c101a", strength=0.12)
bcl.add_studio_3point_rig(target_loc=(0.0, 0.0, 1.0), key_energy=900.0, rim_energy=1400.0, key_temp=4400.0, rim_temp=7600.0)
bcl.setup_cinema_compositor(scene, glare_strength=0.22, dispersion=0.005, vignette=0.18)
```

---

## 3. Headless Blender 5.3 Rendering, PNG Sequence & `bt709` Mux

1. **Always clear the 3-Gate Pre-Render Pipeline** from [[Blender 5.3 Cinematic Rendering & Animation Mastery Bible]]:
   - **Gate 1 (`540×960`, `16 spp`)**: Fast framing/shadow/safe-zone stills.
   - **Gate 2 (`1080×1920`, `32–48 spp`)**: Full material/compositor stills graded by a Cook critic.
   - **Gate 3 (Full Sequence)**: Render crash-resumable PNGs (`frames/f_####.png`) via headless CLI, then encode with `bt709` tags + explicit `-map` audio:
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe" --background --python build_scene.py

ffmpeg -y -framerate 30 -i out/frames/f_%04d.png -i out/mix.wav `
  -map 0:v:0 -map 1:a:0 `
  -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p `
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 `
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest out/final.mp4
```
2. **Optional 10× Speed Draft Trick** ([[Video 2 Teardown - Viral 2D-in-3D Shorts Workflow (Mr omi)]], `11:08`): For ultra-tight turnarounds, render EEVEE 5.3 (`raytracing=True`) or `24 spp` Cycles OptiX at `720×1280` and apply a fast FFmpeg CAS sharpening pass (`-vf scale=1080:1920:flags=lanczos,cas=0.35`).

---

## 4. Running the `.agents/skills/cook` Loop & Anti-Slop Look-Dev Checklist

Never write a 45-second Blender script in one shot and hope it works. Use the **Cook Loop** (`.agents/skills/cook/SKILL.md`):
1. **Create `cook/BRIEF.md` and `cook/SHOTS.md`**: Define the 8–12 shots, camera focal lengths (`28mm` wide, `50mm` hero, `85mm` macro cross-section), and reference stills.
2. **Render Stills at `t_start`, `t_mid`, `t_end` of Every Shot**: Use `blender` MCP `look` or headless `Blender 5.3\blender.exe` to build a contact sheet (`sbs_sheet.py`).
3. **Spawn a Zero-Context Visual Critic Subagent**: Have a fresh subagent score the contact sheet (`0–10`) on:
   - **Silhouette & Rim Separation**: Dark world or physical sky (no default grey), bright `7600K` rim catching beveled edges.
   - **Non-Plastic Shading**: `make_pbr_material` procedural roughness breakup, dual-frequency albedo weathering, micro-bump, `BEVEL` + `WEIGHTED_NORMAL`, and `AgX - Punchy` highlight roll-off.
   - **Cross-Section Readability**: Zero z-fighting or intersecting cutter meshes (`EXACT` solver).
   - **Physical Optics & Motion Curves**: Animated `focus_object` DOF, `180°` motion blur (`shutter = 0.5`), Slotted Actions non-linear easing (`set_keyframe_easing`), subtle handheld camera noise, and `7f` impact `KICKS`.
4. **Iterate Until Every Shot Scores `≥ 8.5/10`**, render the full `30fps` PNG sequence, encode with `bt709` + explicit `-map` audio, and run `short_qa.py` + [[Post-Completion Visual QA — What, How & Why to Fix]].
