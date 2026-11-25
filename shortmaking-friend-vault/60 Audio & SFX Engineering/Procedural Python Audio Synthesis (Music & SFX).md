---
title: Procedural Python Audio Synthesis (Music & SFX)
tags:
  - audio
  - sfx
  - python
  - synthesis
  - dsp
area: audio
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete engineering guide to synthesizing custom background music and frame-accurate Foley/SFX purely in Python & NumPy (dsp.py, instruments.py, sfx_gen.py, music.py, mix.py).
---

# Procedural Python Audio Synthesis (Music & SFX in Pure Python)

> [!IMPORTANT] Vendored Audio Engine
> - **Full Multi-Module Synth**: `90 Templates & Starter Kits/cartoon-3d-short-kit/audio/` (`dsp.py`, `instruments.py`, `music.py`, `sfx.py`, `sfx_gen.py`, `mix.py`, `timeline.py`, `cues.md`)
> - **Single-File Synth Example**: `90 Templates & Starter Kits/cartoon-audio-short-kit/example/soldier/audio.py`

One of the biggest secrets revealed in the 4 reference videos is **zero reliance on external royalty-free SFX libraries**. Instead of searching Freesound for a "19th-century iron suspension bridge bolt groan", the agent writes a **deterministic Python + NumPy/SciPy DSP synthesizer** that generates every footstep, creak, snap, sword clash, splash, whoosh, and background musical score at `44.1 kHz` or `48 kHz`, locked to the exact millisecond from `words.json`.

---

## 1. Architecture of the `cartoon-3d-short-kit/audio/` Engine

| Module | Role | Key Primitives |
| :--- | :--- | :--- |
| **`dsp.py`** | Core waveform & filter primitives | `adsr()`, `biquad_lp()`, `biquad_hp()`, `biquad_bp()`, `soft_clip()`, `reverb_schroeder()`, `stereo_pan()`, `pitch_sweep()` |
| **`instruments.py`** | Physical-modeling & additive instruments | Plucked string (Karplus-Strong), brass horn, woodwind/fife, military snare drum (body membrane + wire rattle), bass drum, pizzicato strings |
| **`music.py`** | Multi-mood procedural score generator | Generates mood-locked stems synced to story acts (e.g., *Jaunty British March 118 BPM* → *Tense Dissonant Drone* → *Comedic Pluck Payoff*) |
| **`sfx_gen.py` & `sfx.py`** | Physical Foley & impact synthesizers | Boot march (`60 soldiers` micro-staggered), wood creak, iron bolt groan + metallic snap, timber crack, river splash, horse whinny + splash, transition whooshes |
| **`mix.py` & `timeline.py`** | Envelope ducking & `-6 dB` gated-RMS master mixer | Places every cue at its exact frame (`t = f / 30`), ducks music/SFX under spoken words, and outputs `mix.wav` |

---

## 2. Procedural Foley Recipes (Copy-Paste Python/NumPy)

### A. Transition Whoosh (`2–4 Frame` Pre-Cut Lead-In)
Band-pass filtered pink/white noise whose center frequency sweeps exponentially from `280 Hz → 1,800 Hz → 400 Hz` over `0.18s`:
```python
def synth_whoosh(sr=44100, dur=0.18, f_start=320, f_peak=1650):
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    # Asymmetric envelope peaking at 65% (right before the visual cut)
    env = np.sin(np.pi * (t / dur) ** 0.7) ** 1.8
    noise = np.random.randn(n)
    # Time-varying bandpass via 8 overlapping slices
    out = sweep_bandpass(noise, sr, f_start, f_peak, Q=2.8) * env
    return out * 0.45
```

### B. Metallic Bolt Snap / Sword Clang (`f = 584` Bridge Collapse)
Combines a `2ms` broadband click transient with 6 inharmonic metallic modal resonators (`f = [820, 1340, 2190, 3110, 4420, 5890] Hz`) decaying exponentially:
```python
def synth_metal_snap(sr=44100, dur=0.35):
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    click = np.random.randn(n) * np.exp(-t * 450.0) * 0.9
    modes = sum(
        amp * np.sin(2 * np.pi * freq * t) * np.exp(-t * decay)
        for freq, amp, decay in [
            (840, 0.5, 18), (1380, 0.4, 24), (2240, 0.35, 30),
            (3410, 0.25, 42), (4890, 0.15, 55)
        ]
    )
    return np.tanh((click + modes) * 1.4)
```

### C. Crowd / Regiment Marching Boots (`60 Soldiers` in Step)
Synthesizes one heavy leather-on-timber impact (`95 Hz` thump + `1.4 kHz` sole scuff) and convolves it with 12 micro-jittered impulses (`σ = 8ms` normal jitter) per beat at `118 BPM`:
```python
def synth_regiment_step(sr=44100):
    # Single boot: 95Hz sub thud + 1.4kHz gravel/wood transient
    # Summed across 12 micro-staggered offsets (+/- 8ms) for 60-man weight
```

---

## 3. The `-6 dB` Gated-RMS Voiceover Mixer (`mix.py`)

Never guess audio levels by ear or hardcode arbitrary multipliers without measuring RMS against the voiceover:
1. Measure the **speech-gated RMS** of `voice.mp3` (frames where `|v| > 10%` of peak).
2. Duck the background music + ambient bed to **`35%` gain whenever the narrator is speaking**, smoothly releasing (`120ms` attack/release) during breath pauses and impact beats.
3. Scale the combined `(music + sfx)` bus so its speech-gated RMS sits at **`-6.0 dB` (`0.28×` linear amplitude)** relative to the voiceover, then run FFmpeg `loudnorm=I=-14:TP=-1.0:LRA=7`.
