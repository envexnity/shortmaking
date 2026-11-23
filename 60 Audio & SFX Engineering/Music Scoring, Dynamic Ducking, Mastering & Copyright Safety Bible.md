---
title: Music Scoring, Dynamic Ducking, Mastering & Copyright Safety Bible
tags:
  - audio
  - music
  - scoring
  - ducking
  - mastering
  - copyright
  - lufs
  - soundcraft
area: audio
style: all
status: evergreen
created: 2026-11-21
updated: 2026-11-21
summary: Complete music & audio mastering engineering bible for short-form animation — genre BPM/key scoring matrix, beat-locked stem drops, FFmpeg sidechain ducking & 2.4kHz vocal pocket carving, 5-bus mastering architecture (-14 LUFS / -1.0 dBTP), and YouTube/TikTok/IG copyright safety rules.
---

# Music Scoring, Dynamic Ducking, Mastering & Copyright Safety Bible

> [!IMPORTANT] Music Sets the Emotional Contract in 0.5 Seconds
> Before the viewer finishes reading Sentence 1, your music bed tells their brain whether this video is **deadpan comedy, cosmic dread, tragic heartbreak, or fever-dream chaos**. Use music **only when it fits the tone** (Law 29)—never slap loud generic phonk over a thoughtful history or horror story.

---

## 1. Genre & Emotional Scoring Matrix (BPM, Harmony & Texture)

| Story Genre / Vibe | Ideal Tempo (BPM) | Harmonic Mode & Instrumentation | Curated Pool / Synthesis Starting Point | When to Cut / Drop Music |
| :--- | :---: | :--- | :--- | :--- |
| **Deadpan History & Bizarre Facts** *(Nutshell / Mr Omi)* | `95–118 BPM` | Pizzicato strings, quirky marimba, upright bass, light brush snare (Major / Mixolydian) | Procedural Python `music.py` pizzicato bed, Kevin MacLeod quirky cues | Hard-drop `8 frames` before the disaster/collapse beat |
| **Atmospheric Mystery / Cosmic Dread** *(Space / Undershine / Storytelling)* | `65–88 BPM` | Slowed + reverb synth pads, minor 9th chords, sub-drone (Dorian / Aeolian) | `Snowfall (Slowed+Reverb)`, `Apathy (Slowed+Reverb)`, `Resonance (Slowed+Reverb)`, `Private Reflection` | Swell pad right into `"You see,"` pivot; mute on revelation |
| **Roblox Storytime / Fever-Dream Comedy** *(Xenost / In This World)* | `115–138 BPM` | Bouncy chiptune/lofi plucks, upbeat indie synth, quick trap hi-hats on escalation | `Numbers — TEMPOREX`, `Fallen Down (Reprise)`, `Dream Playground`, quirky marimba loop | Record-scratch or full vacuum drop on `"Unluckily..."` reversal |
| **Analog / ASCII / Unexplained Horror** | `0` (Drone) or `55–70 BPM` | Sub-bass `45–60 Hz` drone, dissonant tritone strings, room-tone hum, vinyl hiss (Phrygian) | `Unseen Horrors`, `Controlled Chaos`, procedural Python low-passed sub-drone | **Total silence (`0.35–0.5s`)** immediately before a `2f` visual glitch/reveal |
| **Emotional / Heartwarming Twist** *(Hachiko / Kacaurus)* | `72–92 BPM` | Solo felt piano, soft warm cello swell, gentle rain ambience (Major 7th / Lydian) | `In This Shirt` (instrumental feel), procedural warm felt-piano arpeggio | Let piano solo bloom `+3 dB` for `0.6 s` during emotional payoff pause |
| **High-Energy Science / Data Explainer** *(Kurzgesagt / Kaz / Orbit)* | `108–124 BPM` | Pulsing analog synth bass, crisp electronic arps, clean kick/snap pulse | Procedural synthwave/ambient pulse, `playing with numbers` | Strip percussion during `"You see,"` analogy, bring drums back on climax |

---

## 2. The 3-Act Musical Arc Inside a `< 45 s` Short

Never loop a single flat static music track from `0.0 s` to `38.0 s` at constant volume—the brain tunes it out after 8 seconds. Shape energy across **3 musical phases**:

1. **Phase 1 — Hook Entry (`0.0–3.5 s`)**:
   - Either start music cleanly at `-18 dB` under the first word OR **delay music entry until the Scroll-Stop twist at `t = 1.8–2.5 s`** (dropping the beat on the exact bass-hit frame gives massive punch!).
2. **Phase 2 — Tension & Pivot (`3.5–28.0 s`)**:
   - Keep music tucked smoothly **`-6 dB` to `-10 dB` gated RMS below voice** (ducking `35%` under active speech).
   - At the **`"You see,"` pivot (~60%)**, apply a gentle low-pass filter (`fc = 1,400 Hz`) or strip percussive high-hats so the explanation sounds intimate and focused.
3. **Phase 3 — The `8-Frame` Vacuum Drop & Climax (`28.0–42.0 s`)**:
   - Drop music to **`-28 dB` (near silence)** for **`8 frames` (`0.27 s`)** right before the biggest twist/impact.
   - Slam the climax impact (`65 Hz` sub-thud + transient snap) + final musical sting, then **end music cleanly on the final frame** (no awkward mid-note click—add a `30 ms` micro-fade at the last frame!).

---

## 3. The 5-Bus Stem Mixing Architecture & Sidechain Ducking Math

Organize every video mix (in Python `audio_mix.py`, `soundcraft` MCP, or FFmpeg) into **5 independent buses** feeding 1 Master Bus:

| Bus | Contents | Target Relative Level | Mandatory EQ Carving |
| :--- | :--- | :--- | :--- |
| **Bus 1: Master VO** | Primary narrator (broadcast processed) | **Anchor (`-14 LUFS`)** | HPF `85 Hz`, dip `250 Hz`, boost `3.2 kHz` |
| **Bus 2: Character Dialogue** | Secondary character voices / yells | `-1 to 0 dB` vs. VO | Distinct formant/EQ pocket per speaker |
| **Bus 3: Hard Foley & Impacts** | Footsteps, slaps, explosions, UI clicks | `-3 to -1 dB` peak vs. VO | Keep `60–90 Hz` punch clean; don't stack two loud `3 kHz` transients over key words |
| **Bus 4: Transitions & Risers** | Pre-cut whooshes (`2–4f` lead-in), tension risers | `-6 to -4 dB` peak | HPF `220 Hz` on whooshes so they stay airy & never muddy bass |
| **Bus 5: Music Underscore** | Background score / ambient bed | **`-6 dB` gated RMS** (`~0.28×` linear gain under VO; ducks `35%`) | **Mandatory VO Pocket Cut**: `-4.5 dB` at `2,400 Hz` (`Q = 1.2`) + HPF `40 Hz` + LPF `12 kHz` |
| **Master Bus** | Final summed stereo mix | **`-14.0 LUFS` integrated, `-1.0 dBTP` true peak, `LRA 4–7 LU`** | Brickwall true-peak limiter (`-1.0 dBTP`); zero clipping (`0` samples ≥ `0 dBFS`) |

### Production FFmpeg Sidechain Ducking + Vocal-Pocket EQ Filtergraph
Use this exact one-pass FFmpeg mix when combining `voice_master.wav`, `sfx_bus.wav`, and `music_bed.wav`:
```powershell
ffmpeg -y -i voice_master.wav -i music_bed.wav -i sfx_bus.wav -filter_complex `
  "[0:a]asplit=2[vo_main][vo_sc]; `
   [1:a]highpass=f=45,equalizer=f=2400:t=q:w=1.2:g=-4.5,volume=0.34[mus_eq]; `
   [mus_eq][vo_sc]sidechaincompress=threshold=0.03:ratio=4:attack=15:release=180:makeup=1[mus_duck]; `
   [2:a]volume=0.80[sfx_lvl]; `
   [vo_main][mus_duck][sfx_lvl]amix=inputs=3:duration=first:dropout_transition=0:normalize=0, `
   loudnorm=I=-14:TP=-1.0:LRA=6" `
  -ar 48000 -ac 2 mix_master.wav
```
> **Why `normalize=0` on `amix`?** By default FFmpeg's `amix` divides every input by `1/N` (`1/3`), crushing your voiceover `-9.5 dB`! Always pass `normalize=0` and let `loudnorm=I=-14:TP=-1.0` set final broadcast loudness cleanly.

---

## 4. Copyright, Content ID & Monetization Safety Matrix

Nothing kills a viral short's revenue or cross-platform reach faster than a muted audio track or Content ID claim. Follow this **4-Tier Rights Safety Hierarchy**:

| Safety Tier | Audio Source | YouTube Shorts Monetization | TikTok (Personal vs. Business) | Instagram Reels | Rules & Gotchas |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **Tier A — 100% Bulletproof** | **Procedural Python Synthesis** (`music.py`, `sfx_gen.py`), **Openverse CC0**, **`earshot` / `real-sound` CC0** | `100%` Creator Revenue, zero claims | `100%` safe on Personal & Business accounts | `100%` safe on all account types | Best default for monetized multi-platform channels & future long-form compilations! |
| **Tier B — Attribution Safe** | **CC-BY 4.0** (e.g., Kevin MacLeod / Incompetech: *Controlled Chaos*, *Private Reflection*, *Unseen Horrors*) | `100%` Creator Revenue (credit in description) | Safe when credited | Safe when credited | Always include exact credit line (`"Music: [Track] by Kevin MacLeod (incompetech.com) — CC BY 4.0"`) in `upload.md` & description. |
| **Tier C — Platform-Native Only** | Trending commercial tracks (`Snowfall`, `Numbers`, `Cry`, `Levels`) | Shorts Audio Pool revenue-share split (works on Shorts, **claimed on 16:9 Long-Form!**) | Personal/Creator accounts OK (`<60 s` often); **blocked on Business accounts** | Personal/Creator OK; **blocked on Business accounts** | If using a viral commercial track in a Short, **keep a clean stem-less `vo_sfx_only.wav` backup** so you can swap to a Tier A/B bed when compiling Shorts into monetized 8-minute YouTube compilations! |
| **Tier D — Avoid** | Unlicensed movie scores, ripped anime OSTs, unverified "No Copyright" reuploads | High risk of worldwide block or demonetization | Frequent silent muting | Audio stripped automatically | Never use unverified YouTube "copyright free" reuploads—claims often appear 6 months later after a video goes viral. |

---

## 5. Pre-Mux Audio QA Checklist
- [ ] Integrated loudness verified at **`-14.0 LUFS ± 0.5 LU`** and True Peak **`≤ -1.0 dBTP`** (`ffmpeg -i mix_master.wav -af ebur128=peak=true -f null -`).
- [ ] Phone-speaker mono test: collapse stereo to mono mentally or via `-ac 1`—does every single spoken consonant remain crystal clear?
- [ ] Zero clicks/pops at `t = 0.00 s` or the final frame (`20–30 ms` micro fade-in/out on music & ambient beds).
- [ ] Explicit FFmpeg stream mapping used on final mux (`-map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest` — Law 23).

## Related Vault Guides
- [[Voice Acting, Expressive TTS Direction & Vocal Processing Bible]]
- [[SFX Direction & The 2-4 Frame Lead-In Law]]
- [[Procedural Python Audio Synthesis (Music & SFX)]]
- [[Openverse API, Real-Sound & Earshot MCP Pipeline]]
- [[Reference Video Music & Audio Catalog]]
