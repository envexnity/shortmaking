---
title: For $1,000, Would You Travel to the 100th Dimension? — Completed Video
tags:
  - completed-video
  - pixel-art
  - countryballs
  - 8bit
  - elevenlabs
area: production
style: pixel-8bit
status: shipped
created: 2026-11-18
updated: 2026-11-18
summary: Completed 49.63s vertical 9:16 8-bit pixel-art Countryball short on travelling to the 100th dimension inside a quantum toaster, rendered on a 180x320 native canvas (6x nearest-neighbor upscale to 1080x1920) with 5-character ElevenLabs voices, dimension-shifting 8-bit chiptune score, and 8sb2R11FeVw black-pill subtitles.
---

# For \$1,000, Would You Travel to the 100th Dimension?

> [!INFO] Playable Video Embed
> ![[out/dimension_100_short.mp4]]

## Technical Specs
- **Output File**: `videos/dimension-100-short/out/dimension_100_short.mp4`
- **Resolution & FPS**: `1080×1920` (`180×320` native pixel canvas upscaled `6×` nearest-neighbor), `30 fps` (`H.264`, `bt709`)
- **Duration**: `49.625 s` (`1,486` frames across `16` beats + mid-beat camera punch-ins)
- **Voice System**: ElevenLabs (`eleven_turbo_v2_5`, 5-character cast: `Liam`, `Adam`, `Will`, `Callum`, `Bill`) + `faster-whisper` word timestamps (`161` words across `16` beats)
- **Subtitles**: `8sb2R11FeVw` black-pill style (`58px` bold geometric sans, `#FFFFFF` + `#FFE600` active-word pop, `2–4` words per pill at `y = 1365`)
- **Audio & Loudness**: `AAC 48000 Hz`, `-14.3 LUFS` (`LRA 2.2 LU`, `-0.8 dBFS` peak), dimension-morphing 8-bit chiptune score (`3D C-major` → `2D arcade minor` → `4D whole-tone tesseract` → `11D string overdrive` → `100D 1-bit pocket calculator piezo beep`) + layered SFX (`audio.py`)
- **Automated & Visual QA**: `0` black frames, `0` unplanned white flashes, `0` frozen spans `≥12f`, `0` silences (`short_qa.py`)

## Production Files
- **Script**: [[SCRIPT]]
- **Voice & Word Timing Generator**: `videos/dimension-100-short/make_voice.py`
- **8-Bit Pixel Engine & 4D Tesseract Wireframe**: `videos/dimension-100-short/engine/pixel_engine.js`
- **Character & Dimensional Form Renderer**: `videos/dimension-100-short/engine/characters.js`
- **16-Beat Scene Choreography**: `videos/dimension-100-short/engine/scenes.js`
- **Chiptune Score & Foley Mixer**: `videos/dimension-100-short/audio.py`
- **Upload Package**: [[Upload Package - Dimension 100 8-Bit]]
