---
title: Automated Frame & Audio QA (short_qa.py)
tags:
  - qa
  - testing
  - python
  - ffmpeg
  - automation
area: multi-agent
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete documentation for scripts/short_qa.py—automated frame-by-frame inspection for black frames, white flashes, frozen spans (>=12f), cut verification, and audio stream checks.
---

# Automated Frame & Audio QA (`short_qa.py`)

> [!IMPORTANT] Vendored QA Script
> - **Script Path**: `90 Templates & Starter Kits/cartoon-3d-short-kit/scripts/short_qa.py`

Before presenting any rendered `.mp4` to the user or uploading to YouTube Shorts / TikTok, you **MUST** run `short_qa.py`. It decodes the entire video at `160×284` grayscale via `ffmpeg` and inspects every single frame and frame-to-frame transition in `<3 seconds`.

---

## 1. What `short_qa.py` Checks Automatically

| Check | Failure Threshold | What Causes It in Production |
| :--- | :--- | :--- |
| **1. Black Frames** | `mean_luma < 5.0` | Camera accidentally placed inside a mesh; renderer failed to initialize on frame 0; missing light preset key. |
| **2. White Flashes** | `mean_luma > 250.0` | Unclamped bloom explosion (`luminanceThreshold` too low); exposure spike during transition. |
| **3. Frozen Spans** | **`frame_to_frame_diff < 0.25` for `≥ 12 frames` (`0.4s`)** | **Forgot `push()` camera hold creep**; Remotion render crashed early due to full `$TMPDIR`; animation loop stopped before `DURATION`. |
| **4. Camera Cuts Detected** | `frame_to_frame_diff > 18.0` | Verifies that every planned shot boundary in `SHOTS` actually produced a clean visual cut at the expected frame index. |
| **5. Audio Stream Presence & Duration** | Missing `a:0` stream or `|dur_v - dur_a| > 0.25s` | Forgot `-map 0:v:0 -map 1:a:0` in FFmpeg mux, or rendered silent video without mixing `mix.wav`. |

---

## 2. Running `short_qa.py`

```powershell
python "90 Templates & Starter Kits/cartoon-3d-short-kit/scripts/short_qa.py" out/final_master.mp4 out/qa_visual
```

`short_qa.py` outputs:
- `out/qa_visual/report.md` (specs, EBU R128 loudness, silences, black/white/frozen/pop frame lists, per-shot luma & saturation medians)
- `out/qa_visual/sheet_0000.jpg`, `sheet_0060.jpg`, ... (`2s` contact sheets of `10×6` frames at `108×192` with burned-in frame numbers)
- `out/qa_visual/perframe.npz` (raw per-frame metrics)

### Example Passing Output
```text
SPECS 1440x2560 30/1 fps, 1365 frames, 45.500 s; audio: aac 48000 Hz 2ch
LOUDNESS I: -14.0 LUFS | LRA: 2.4 LU | Peak: -1.0 dBFS
SILENCES none
FRAMES 1365; black []; unplanned white []; frozen spans >=12f []
POPS (unplanned frame-diff spikes > 3x local median): []
MOTION mean diff 4.18; frames with diff<0.3 (held): 0 (0%)
```

> [!CAUTION] Hard Gate Rule — Numeric + Visual
> 1. If `short_qa.py` reports **even 1 black frame, 1 unplanned white flash, or 1 frozen span `≥ 12f`**, the build is **REJECTED**. Fix the offending shot range `[f_start..f_end]` and re-render before shipping.
> 2. Passing `short_qa.py` is **not enough on its own**—after running it, you **MUST** also complete [[Post-Completion Visual QA — What, How & Why to Fix]] on the generated contact sheets and high-res stills (`540×960`+) to catch clipping, 9:16 UI occlusion, `NOINK` boxes, and dead acting.
