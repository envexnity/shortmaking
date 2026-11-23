---
title: SFX Direction & The 2-4 Frame Lead-In Law
tags:
  - audio
  - sfx
  - sound-design
  - retention
  - mixing
area: audio
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Psychoacoustic sound design rules from the sfx-sound-design-director skill—the 2-4 frame pre-cut lead-in law, 4-layer impact stacking, frequency carving (2-4kHz VO pocket), and -14 LUFS mastering.
---

# SFX Direction & The 2–4 Frame Lead-In Law

> [!NOTE] Vendored Skill
> - **Skill Path**: `.agents/skills/sfx-sound-design-director/SKILL.md`
> - **Cue Sheet Template**: [[sfx-cue-sheet]]

In high-retention short-form animation, **sound is 50% of perceived visual quality**. A flat 2D card or low-poly block feels heavy and tactile the moment it is paired with multi-layered acoustic weight.

---

## 1. The 4 Golden Psychoacoustic Laws of Short-Form Audio

### Law 1: The 2–4 Frame Pre-Cut Lead-In (`66ms – 133ms` @ 30fps)
The human brain processes auditory transients faster than visual scene changes, and anticipates motion through rising air pressure:
- **Never start a transition whoosh or riser on the frame of the cut.**
- Start the whoosh **`4–6 frames` before the cut**, let its amplitude and bandpass frequency peak **`2 frames` before the cut**, and land a low-end impact thud (`60–85 Hz`) on **Frame 0** of the new shot. This makes hard camera cuts feel invisible and magnetic.

### Law 2: 4-Layer Impact Stacking (Never Use a Single Thin Sound)
Every major physical event in your short (the bridge snapping, Napoleon's cage bursting, a Roblox character getting slapped, a HUD stat slamming onto screen) requires **4 distinct frequency layers**:

| Layer | Frequency Band | Timing Relative to Impact Frame `f0` | Acoustic Role |
| :--- | :--- | :--- | :--- |
| **1. Lead-In / Anticipation** | `300 Hz – 2.5 kHz` sweep | `f0 - 5f` to `f0` | Builds tension (creak, inhale, pitch riser, whip whoosh) |
| **2. Transient Snap** | `2.5 kHz – 8.0 kHz` (`5–15ms`) | Exact `f0` | Crisp definition (wood crack, metal click, slap transient) |
| **3. Body / Material Texture** | `200 Hz – 1.8 kHz` (`80–250ms`) | `f0` to `f0 + 6f` | Tells the ear *what* broke (splintering oak, splashing water, crumbling stone) |
| **4. Sub Weight & Tail** | `50 Hz – 110 Hz` + reverb tail | `f0` to `f0 + 18f` | Physical chest punch + spatial environment decay |

### Law 3: Carve the `1.5 kHz – 4.0 kHz` Pocket for the Narrator
At `3.7 words/sec`, the narrator rarely stops speaking. If your background music or continuous SFX (marching boots, rain, crowd murmur) has heavy energy at `2.5 kHz`, it masks consonant clarity and causes viewers to swipe away:
- Apply a **biquad peaking cut (`-4.5 dB` at `2.4 kHz`, `Q = 1.2`)** or low-pass filter (`fc = 1,800 Hz`) on continuous background beds whenever the voiceover envelope is active.

### Law 4: Contrast via the `8-Frame` Pre-Climax Drop
Before the biggest disaster beat in your short (e.g., `8 frames` before the suspension bridge snaps at `f = 584`), **drop the background music and marching loop to `-28 dB` (near-total silence)** while the narrator says *"Wait—"* or right before the bolt cracks. The sudden vacuum makes the subsequent impact hit `3×` harder without clipping `0 dBFS`.
