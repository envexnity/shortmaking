---
title: Template — Frame-Accurate SFX & Music Spotting Sheet
tags:
  - template
  - audio
  - sfx
  - spotting
area: templates
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Frame-accurate audio cue sheet template enforcing the 2-4 frame pre-cut whoosh lead-in law, 4-layer impacts, and -6 dB gated RMS mixing.
---

# Frame-Accurate SFX & Music Spotting Sheet (`cues.md`)

Use this template before writing `audio/timeline.py` or `audio.py` to spot every transition whoosh (`2–4 frames` before cut), physical Foley loop, and 4-layer climax impact.

---

## 1. Musical Score Stems (`music.py`)
| Act | Frame Span (`s..e`) | Tempo & Key | Instrumentation (`instruments.py`) | Ducking Rule Under VO |
| :--- | :--- | :--- | :--- | :--- |
| **Act 1 (Setup & March)** | `0 .. 480` | `118 BPM`, G Major | Jaunty fife + pizzicato strings + crisp military snare | `0.35×` under speech, `1.0×` in gaps |
| **Act 2 (Tension & Collapse)** | `480 .. 630` | `118 BPM` → silence at `f=576` | Low brass drone + accelerating snare roll → **8-frame vacuum drop before `f=584`** | Drop to `-28 dB` at `f=576..584` |
| **Act 3 ('You see,' Pivot & Payoff)** | `630 .. 1350` | `108 BPM`, E Minor → G Major button | Warm celesta/pluck + upright bass walking line + final comedic button stinger | `0.35×` under speech |

---

## 2. Frame-Accurate SFX Cue Table (`timeline.py`)

| Cue ID | Visual Event Frame (`f0`) | Audio Trigger Frame (`f_trig`) | Lead-In Offset | 4-Layer Synth Recipe (`sfx_gen.py`) | Peak Gain (`dBFS`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SFX_01` | Cut 1 (`f = 114`) | **`f = 110`** | **`-4 frames`** (`-0.13s`) | `synth_whoosh(dur=0.18, f_start=320, f_peak=1650)` + soft `80Hz` thud on `f=114` | `-9.0 dB` |
| `SFX_02` | Regiment Marching (`f = 114..480`) | `f = 114` (loop @ `118 BPM`) | `0f` | `synth_regiment_step()` (95Hz boot thud + 1.4kHz timber scuff, 12-man micro-jitter) | `-12.0 dB` |
| `SFX_03` | Bridge Sway Creak (`f = 490`) | `f = 486` | `-4 frames` | `synth_wood_creak()` (stick-slip impulse train `180–640 Hz` bandpass) | `-8.0 dB` |
| `SFX_04` | **Hero Iron Bolt Snap (`f = 584`)** | **`f = 579`** (groan) → **`f = 584`** (snap) | **`-5 frames`** | **4-Layer Stack**: (1) `5f` metallic groan riser + (2) `2ms` `4.5kHz` crack + (3) 6-mode metallic ring + (4) `62Hz` sub drop | **`-3.5 dB`** |
| `SFX_05` | River Splash (`f = 626`) | `f = 624` | `-2 frames` | `synth_splash()` (low-end water cavity thump `110Hz` + `1.2s` filtered white-noise spray tail) | `-5.0 dB` |
| `SFX_06` | Final Punchline Button (`f = 1340`) | `f = 1340` | `0f` | Dry pizzicato double-pluck + rimshot tick | `-6.0 dB` |
