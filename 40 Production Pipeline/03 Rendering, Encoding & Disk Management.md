---
title: 03 Rendering, Encoding & Disk Management
tags:
  - pipeline
  - rendering
  - remotion
  - playwright
  - ffmpeg
  - disk-space
area: pipeline
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-20
summary: Production rendering handbook covering 2K vertical upscaling (1440x2560), preventing the 60-110GB Remotion webpack temp disk trap, headless Chromium GPU flags, Blender 5.3 Cycles OptiX / EEVEE PNG sequence rendering, and FFmpeg stream muxing with bt709 color tags.
---

# 03 Rendering, Encoding & Disk Management

> [!WARNING] The 110 GB Remotion Temp Bundle Trap
> During the Bridge short build ([[Video 2 Teardown - Viral 2D-in-3D Shorts Workflow (Mr omi)]]), 4 parallel agents running Remotion stills and test renders silently wrote **`1.9 GB` per invocation** into `$TMPDIR/remotion-webpack-bundle-*`, consuming **110 GB of disk space** and crashing the final render mid-way (causing 8 seconds of frozen frame). **Always redirect and purge `TMPDIR` before rendering!**

---

## 1. Disk-Safe Remotion Rendering (`cartoon-3d-short`)

Always run this PowerShell wrapper when rendering Remotion projects:

```powershell
# 1. Redirect TMPDIR / TEMP to a dedicated scratch folder and purge stale bundles
$ScratchTmp = "C:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\scratch_tmp"
New-Item -ItemType Directory -Force -Path $ScratchTmp | Out-Null
Remove-Item -Recurse -Force "$ScratchTmp\remotion-*" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\Temp\remotion-*" -ErrorAction SilentlyContinue
$env:TMPDIR = $ScratchTmp
$env:TEMP = $ScratchTmp
$env:TMP = $ScratchTmp

# 2. Fast Stills Pass for Visual Critics (1080x1920 PNGs at shot midpoints)
node scripts/bridge-stills.mjs

# 3. Final 2K Vertical Master Render (1440x2560 @ 30fps via --scale=1.3333)
npx remotion render Bridge out/bridge_2k_silent.mp4 `
  --scale=1.3333 `
  --codec=h264 `
  --crf=16 `
  --pixel-format=yuv420p `
  --gl=angle

# 4. Clean up temp bundle immediately after render
Remove-Item -Recurse -Force "$ScratchTmp\remotion-*" -ErrorAction SilentlyContinue
```

### Why Render at `--scale=1.3333` (`1440×2560` 2K Vertical)?
YouTube Shorts, TikTok, and Instagram Reels re-encode uploaded `1080×1920` files aggressively, softening thin `3px` `InkPass` outlines. Rendering at `1440×2560` (`--scale=1.3333`) forces higher-bitrate VP9/AV1 transcoding tiers and keeps screen-space ink edges razor-sharp.

---

## 2. Playwright Headless Chromium Rendering (`cartoon-audio-short` & `make-3d-video`)

Both `tools/render.mjs` and `studio/render.js` step a browser clock deterministically (`window.__step(f)` or `window.__renderFrame(t)`) and pipe frames straight into `ffmpeg`:

```powershell
# Track 2: Standalone 2D-in-3D Toon (cartoon-audio-short)
node tools/render.mjs engine/index.html out/video.mp4 48.5

# Track 3: Low-Poly 3D Studio (make-3d-video)
node studio/render.js --shots ./shots.js --audio ./voiceover.mp3 --width 1080 --height 1920 --fps 30 --out ./final.mp4
```

### GPU vs. SwiftShader CPU Fallback
- If your machine has a dedicated NVIDIA/AMD GPU, pass `--use-gl=angle --use-angle=d3d11` (Windows) for `~40–60 fps` faster-than-realtime rendering.
- If running inside a headless container or when WebGL context creation fails, `tools/render.mjs` automatically uses `--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader` so WebGL2 shaders (`InkPass`, `LensBlurEffect`, `GradeEffect`) compile identically on CPU.

---

## 3. Blender 5.3 Headless Animation Rendering (Cycles OptiX & EEVEE 5.3)

Always render Blender animations via **Blender 5.3.0** (`C:\Program Files\Blender Foundation\Blender 5.3\blender.exe`) as **crash-resumable PNG frame sequences** (`frames/f_####.png`), NEVER straight to an MP4 container. See [[Blender 5.3 Cinematic Rendering & Animation Mastery Bible]] and `90 Templates & Starter Kits/blender-cinema-kit/blender_cinema_lib.py`:

- **Cycles GPU (Track 4 Realistic/Volumetric)**: Enable RTX 2050 `OPTIX` + GPU `OPENIMAGEDENOISE` (`RGB_ALBEDO_NORMAL`, `ACCURATE`), `use_adaptive_sampling = True`, `adaptive_threshold = 0.02`, `use_persistent_data = True` (keeps BVH & textures resident across frames), and bounded bounces (`max_bounces = 6`).
- **EEVEE 5.3 (`BLENDER_EEVEE`)**: Use `raytracing=True`, `fast_gi=True` for stylized PBR / Roblox R6-R15, or `filter_size=0.01`, `use_raytracing=False`, `taa_render_samples=8` for Track 7 Undershine pixel passes.
- **High-Speed Rendering & Post-Processing Optimizations (Mandatory for Multi-Pass & Blender Animations)**:
  1. **Zero PNG Zlib Compression on Scratch Passes (`compression = 0`)**: Set `scene.render.image_settings.compression = 0` and `fo.format.compression = 0` on all `CompositorNodeOutputFile` pass nodes (`img_`, `depth_`, `norm_`, `mist_`, `emit_`) so CPU cores don't waste 35–45% of frame time running zlib deflate on intermediate pass PNGs.
  2. **Multi-Worker Parallel Blender Chunks (`fast_blender_render.py`)**: Split long frame ranges across `2–3` parallel headless Blender 5.3.0 processes (`--range START END` with `--no-save` on workers) using `90 Templates & Starter Kits/undershine-blender-pixel-kit/fast_blender_render.py`.
  3. **8-Thread Post-Processing + Pre-Multiplied RGBA Sprite Caching (`pixel_postprocess.py`)**: Cache rendered subtitle pills (`_PILL_CACHE`), world title overlays (`_OVERLAY_CACHE`), and Bayer 4×4 dither matrices (`_BAYER_CACHE`), and load/process frames across an 8-worker `ThreadPoolExecutor` piping directly into `ffmpeg -preset veryfast -crf 16`.

```powershell
# 1. Parallel 3-Worker Headless Blender 5.3.0 Render (Track 4 / Track 5 / Track 7)
python "90 Templates & Starter Kits/undershine-blender-pixel-kit/fast_blender_render.py" --script build_scene.py --frames 1200 --workers 3

# 2. Encode PNG sequence + explicit audio mix with bt709 color tags (prevents browser/iOS gamma shift)
ffmpeg -y -framerate 30 -i out/frames/f_%04d.png -i out/mix.wav `
  -map 0:v:0 -map 1:a:0 `
  -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p `
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 `
  -af "loudnorm=I=-14:TP=-1.0:LRA=7" `
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest `
  out/final_master.mp4
```

---

## 4. Explicit FFmpeg Audio Muxing & Loudness Normalization

Because `render.mjs` and Remotion often output an MP4 container that already contains a silent audio track (`0:a:0`), running a naive `ffmpeg -i video.mp4 -i mix.wav out.mp4` **will ignore `mix.wav` and ship a silent video!**

Always use explicit `-map 0:v:0 -map 1:a:0`:

```powershell
ffmpeg -y `
  -i out/video.mp4 `
  -i out/mix.wav `
  -map 0:v:0 `
  -map 1:a:0 `
  -c:v copy `
  -af "loudnorm=I=-14:TP=-1.0:LRA=7" `
  -c:a aac -b:a 192k -ar 48000 `
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 `
  -movflags +faststart `
  -shortest `
  out/final_master.mp4
```
