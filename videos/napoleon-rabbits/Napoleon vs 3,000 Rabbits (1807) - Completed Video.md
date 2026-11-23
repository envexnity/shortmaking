---
title: Napoleon vs. 3,000 Rabbits (1807) — Completed Video
tags:
  - completed-video
  - low-poly-3d
  - kaz-studio
  - history-short
  - elevenlabs
area: production
style: kaz-3d-studio
status: shipped
created: 2026-11-17
updated: 2026-11-17
summary: Completed 57.30s vertical 9:16 low-poly 3D explainer on Napoleon's 1807 defeat by 3,000 tame farm rabbits using kaz-3d-studio-kit, ElevenLabs Daniel narration, 8sb2R11FeVw black-pill subtitles, and original fife-and-strings score.
---

# Napoleon vs. 3,000 Rabbits (1807)

> [!INFO] Playable Video Embed
> ![[out/napoleon-rabbits.mp4]]

## Technical Specs
- **Output File**: `videos/napoleon-rabbits/out/napoleon-rabbits.mp4` (`44,624,691` bytes, `42.6 MB`)
- **Resolution & FPS**: `1080×1920` (9:16 Vertical Short), `30 fps` (`H.264`, `bt709`)
- **Duration**: `57.30 s` (`1,719` frames across `28` dynamic shots)
- **Voice System**: ElevenLabs (`eleven_turbo_v2_5`, voice `Daniel — Steady Broadcaster` `onwK4e9ZLuTAKqWW03F9`, `speed=1.12`) + `faster-whisper` word timestamps (`166` words across `15` beats)
- **Subtitles**: `8sb2R11FeVw` black-pill style (`58px` bold geometric sans, `#FFFFFF` + `#FFE600` active-word pop, `2–4` words per pill)
- **Audio & Loudness**: `AAC 48000 Hz`, `-14.2 LUFS` (`-1.0 dBFS` peak), original 1807 French fife-and-strings march + Foley SFX (`audio.py`)

## Production Files
- **Script & Historical Facts**: [[SCRIPT]] (`David Chandler`, `Baron Thiébault Memoirs`, `Treaties of Tilsit`)
- **Voice Generator**: `videos/napoleon-rabbits/make_voice.py` (ElevenLabs CLI) + `words.py` (`faster-whisper`)
- **3D Scene & Shots**: `videos/napoleon-rabbits/shots.js` (`28` shots)
- **Score & SFX**: `videos/napoleon-rabbits/audio.py`
- **Upload Package**: [[Upload Package - Napoleon vs 3,000 Rabbits (1807)]]
- **Engine**: [[Style 3 - Low-Poly Flat-Shaded 3D (Kaz Studio Kit)]]
