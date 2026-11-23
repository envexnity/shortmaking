---
title: Readability Traps & Anti-Slop Rules
tags:
  - look-bible
  - qa
  - anti-slop
  - geometry
  - readability
area: look-bible
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: The 12 real-world geometric, shader, and staging traps discovered during the Bridge, Napoleon, and Roman Soldier builds—and the exact rules to prevent them.
---

# Readability Traps & Anti-Slop Rules (Field-Tested Fixes)

> [!CAUTION] Mandatory Pre-Render Checklist
> Every single bug below actually occurred during the reference builds (`OtbLL6OBNE4` and `zGVQt4xoZAM`) before the visual critic agents caught them. Check your contact sheet (`stills.jpg` / `sbs_sheet.png`) against all 12 rules before final export.

---

## 1. The 12 Classic 3D/2D-in-3D Failure Modes & Fixes

### Trap 1: The Swing / Hanging Prop "Neck-Hanging" Illusion
- **What goes wrong**: When an agent builds a park swing, pendulum, or hanging cage, it often sets the pivot at the seat/character (`y = 1.0m`) and draws a single vertical line behind the character's head. When rotated, the rope swings wildly in the air and the child looks like they are hanging by their neck.
- **Mandatory Fix**:
  1. Set the `Group` pivot at the **overhead tree branch or crossbar (`y = 3.55m`)**—and keep that branch **visible inside the camera frame**.
  2. Build **two ropes (`x = ±0.42m`)** straddling the character's shoulders down to a visible wooden seat board under the character.
  3. Rotate the top pivot group (`swingGroup.rotation.z = Math.sin(t * 2.8) * 0.32`) so the entire assembly arcs physically around the branch.

### Trap 2: Bridge & Balcony Railings Slicing Across Character Faces
- **What goes wrong**: Building a `1.4m` tall railing next to a `2.15m` character card puts the top horizontal beam directly across the characters' mouths and eyes in medium shots.
- **Mandatory Fix**: Keep railings at **`y ≤ 0.85–0.95m` (chest/waist height)** and angle the camera slightly above the railing plane (`cam.y ≥ 1.65m`).

### Trap 3: Foreground Props Blocking the Hero's Face (`<2m` Clearance Violation)
- **What goes wrong**: In the Napoleon Free/Pro test (`zGVQt4xoZAM`), a pine tree placed at `(x = -0.5, z = 3.0)` sat directly between the camera `(0, 1.8, 6.0)` and Napoleon `(0, 0, 0)`, covering half his face.
- **Mandatory Fix**: Enforce a **strict `2.0m` cylinder clearance** along the ray from `camera.position` to `hero.position`. Purposeful foreground framing props (barrels, leaves) must sit in the **outer 18% left/right screen margins**.

### Trap 4: Black Boxes Around Characters, Clouds, or Smoke (Forgot `NOINK = 3`)
- **What goes wrong**: `InkPass` reads the depth buffer of a transparent `PlaneGeometry` and draws a thick black rectangle around the card.
- **Mandatory Fix**: Call `enableNoInk(mesh)` (`mesh.layers.enable(3)`) on every alpha-mapped plane, sky dome, cloud, water overlay, and particle puff.

### Trap 5: Glowing Neon Characters (Used `emissiveMap` Instead of `cardShade`)
- **What goes wrong**: Putting the character texture in `emissiveMap` triggers `BloomEffect`, turning white eyes and shirts into radioactive blurs.
- **Mandatory Fix**: Always use `cardShade(texture)` (`V ≥ 0.86` floor, unlit below bloom threshold `1.0`).

### Trap 6: Dark, Unreadable Painted Signs in Shadow
- **What goes wrong**: Applying directional `shade()` to a painted signboard (`"BREAK STEP BY ORDER"`) puts the text in the `0.50×` shadow band when backlit, making it unreadable.
- **Mandatory Fix**: Signboard *frames/posts* use `shade()`, but the **painted sign face MUST use `MeshBasicMaterial` + `enableNoInk(signFace)`** with bold `#241726` lettering on warm cream `#f5ebd6`.

### Trap 7: Historical Flag & Costume Hallucinations
- **What goes wrong**: Drawing a red-and-white St. George's Cross for an `1880s` British Army barracks instead of the **Union Jack** (with diagonal St. Patrick's + St. Andrew's saltires).
- **Mandatory Fix**: Verify period flags, helmets (e.g., 1880s British Home Service helmet / shako vs. WWII Brodie helmet), and vehicle orientations on the contact sheet.

### Trap 8: Sideways Vehicles & Floating Wheels
- **What goes wrong**: In `zGVQt4xoZAM`, the Free tier built a carriage aligned along `+X` while the road ran along `+Z`, and placed wheel centers at `y = 0` (sinking half the wheel underground).
- **Mandatory Fix**: Always set wheel center height to `y = wheelRadius`, and align vehicle forward vectors with `Math.atan2(dx, dz)` along the road path.

### Trap 9: Jump-Cut Camera Pops Between Similar Angles
- **What goes wrong**: Cutting between two cameras that are only `0.8m` and `8°` apart looks like a rendering glitch rather than a deliberate edit.
- **Mandatory Fix**: Follow the **30-Degree / 2-Meter Rule**: every hard cut must change camera angle by **`≥ 30°`** OR focal distance by **`≥ 40%`** (e.g., Wide `8m` → Medium Close-Up `3.5m`). Otherwise, use a smootherstep `glide()`.

### Trap 10: Frozen Camera Holds (`≥12 Frames` Identical)
- **What goes wrong**: Holding a static camera after a character stops talking makes the video look paused and tanks viewer retention.
- **Mandatory Fix**: Every single shot applies `push(camera, shot.cam, u, 0.0025)` + character `4f` blinks every `1.2s`.

### Trap 11: Silent Video Track Masking the Mixed Audio in FFmpeg
- **What goes wrong**: `ffmpeg -i video.mp4 -i mix.wav final.mp4` keeps the silent audio track from `video.mp4` and drops `mix.wav`!
- **Mandatory Fix**: Always pass **`-map 0:v:0 -map 1:a:0`**.

### Trap 12: Remotion 110 GB Temp Bundle Disk Exhaustion
- **What goes wrong**: Running multiple Remotion renders writes `1.9 GB` per invocation to `$TMPDIR/remotion-webpack-bundle-*`, filling the C: drive and causing truncated/frozen renders.
- **Mandatory Fix**: Set `$env:TMPDIR` to a local scratch folder and delete `remotion-*` before and after every render.
