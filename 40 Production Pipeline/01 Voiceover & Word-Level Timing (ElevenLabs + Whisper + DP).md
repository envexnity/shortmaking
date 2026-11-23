---
title: 01 Voiceover & Word-Level Timing (ElevenLabs + Whisper + DP)
tags:
  - pipeline
  - voiceover
  - elevenlabs
  - whisper
  - timing
area: pipeline
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete engineering guide to generating high-retention narration in ElevenLabs and extracting frame-accurate word/beat timestamps using faster-whisper (words.json) and silence Dynamic Programming (timing.py).
---

# 01 Voiceover & Word-Level Timing (ElevenLabs + Whisper + DP)

> [!IMPORTANT] The Golden Law of Short-Form Sync
> **Never animate to estimated word counts.** A `0.3s` drift between a spoken punch word (*"SNAP!"*) and the visual bolt breaking destroys comedic timing. Always generate the voiceover **first**, extract exact timestamps, and lock every shot cut, facial expression, and sound effect to those numbers.

---

## 1. ElevenLabs Voiceover Settings for Viral Shorts

Across the 4 reference creators (`Mr omi`, `mr miro`, `Grow With Kaz`, `AI Playbook`), the highest-performing narration settings are:

| Setting | Target Value | Why It Works |
| :--- | :--- | :--- |
| **Model** | `Eleven Multilingual v2` or `Eleven Turbo v2.5` | Crisp consonant transients and natural deadpan inflection on `"Luckily / Unluckily"` reversals. |
| **Speed** | **`1.10× – 1.15×` (`3.7 words/sec` median)** | Standard `1.0×` TTS reads at `~2.9–3.1 wps`, which feels sluggish on Shorts. Pushing speed to `1.12×` hits the viral `3.7 wps` cadence. |
| **Stability** | `35% – 45%` | Lower stability gives expressive pitch swings on mystery beats (*"Wait—how did..."*) and punchlines. |
| **Similarity / Clarity** | `75% – 85%` | Keeps the voice forward in the `2–4 kHz` presence band above `-6 dB` music/SFX. |
| **Style Exaggeration** | `15% – 30%` | Adds storyteller energy without sounding clipped or robotic. |
| **Silence Trimming** | Trim pauses `>0.25s` down to `0.12–0.18s` | Total pauses `>0.25s` across a 45s short must be `<1.0s` combined. |

---

## 2. Method A: Word-Level Alignment via `faster-whisper` (`cartoon-audio-short`)

Located at `90 Templates & Starter Kits/cartoon-audio-short-kit/tools/timing.py`.
This script runs `faster-whisper` (`tiny.en`, `word_timestamps=True`) and uses Dynamic Programming to align the recognized tokens back to your exact script punctuation:

```powershell
python tools/timing.py voice.mp3 story.txt words.json
```

### Output Format (`words.json`) & Frame Conversion
```json
[
  { "word": "In", "start": 0.06, "end": 0.18 },
  { "word": "1880,", "start": 0.18, "end": 0.64 },
  { "word": "sixty", "start": 0.68, "end": 1.04 },
  { "word": "soldiers", "start": 1.04, "end": 1.52 }
]
```
- **Frame Conversion (`30 fps`)**: `frame = Math.round(word.start * 30)`
- **2-Frame Reaction Lead**: Trigger eyebrow/eye/mouth shock at `frame = Math.round(word.start * 30) - 2`
- **4-Frame SFX Whoosh Lead-In**: Trigger transition whoosh at `t_whoosh = word.start - 0.10`

---

## 3. Method B: Beat-Level Pause DP Alignment (`make-3d-video`)

Located at `90 Templates & Starter Kits/kaz-3d-studio-kit/tools/timing.py`.
When building Low-Poly 3D explainers where each shot corresponds to a full sentence/beat (`10–14 beats`), `studio/tools/timing.py` finds every natural breath pause in the audio and snaps beat transitions via Dynamic Programming:

```powershell
python studio/tools/timing.py voiceover.mp3 `
  "In 1914, a driver took one wrong turn in Sarajevo." `
  "That single mistake triggered a chain reaction across six empires." `
  "Within thirty days, seventy million soldiers were mobilized." `
  --json > timing.json
```

### Output Format (`timing.json`)
```json
{
  "total_duration": 44.2,
  "beats": [
    { "index": 0, "start": 0.0, "end": 3.84, "duration": 3.84, "text": "In 1914..." },
    { "index": 1, "start": 3.84, "end": 7.92, "duration": 4.08, "text": "That single..." }
  ]
}
```
Copy each beat's `duration` directly into `window.SHOTS[i].duration` in `shots.js` so every camera cut lands on the exact breath between sentences.
