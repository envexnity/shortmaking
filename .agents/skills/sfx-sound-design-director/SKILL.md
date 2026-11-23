---
name: sfx-sound-design-director
description: Expert sound engineering and SFX direction skill for video editing, pacing, Foley, audio spotting, and soundscape design for high-energy retention videos, gaming montages, and cinematic edits.
---

# SFX & Sound Design Director Skill

This skill guides the LLM to direct, map, layer, and engineer audio and sound effects (SFX) with millisecond precision to elevate video edits from amateur to dopamine-inducing professional content.

## 1. The Sound Design Hierarchy (Layering Rule)

Every impactful video moment requires a multi-frequency stack. Never use a single sound effect in isolation:
1. **The Transient / Click (Highs, 4kHz - 12kHz):**
   - Provides instant sharpness and clarity. Examples: Mechanical key click, camera shutter snap, glass ping, blade sheathe.
2. **The Body / Texture (Mids, 500Hz - 3kHz):**
   - Gives the sound recognizable real-world character. Examples: Sword slash swoosh, cartoon pop, fabric rustle, vinyl scuff.
3. **The Weight / Impact (Lows & Sub-bass, 30Hz - 150Hz):**
   - Hits the viewer physically in the chest. Examples: 808 sub boom, cinematic cinema thud, low brass hit, earthquake rumble.
4. **The Tail / Reverb (Space & Decay, 1s - 3s tail):**
   - Fades out smoothly into the ambient bed so the cut doesn't sound abruptly severed.

---

## 2. Micro-Timing & Lead-Ins (The 2-4 Frame Rule)

- **The Golden Lead-In Law:** High-velocity sound effects (whooshes, risers, whip pans) **MUST start 2 to 4 frames BEFORE the visual cut happens**.
  - If a cut happens at `00:03.500`, the whoosh riser must begin at `00:03.400` - `00:03.433` and peak exactly on the cut at `00:03.500`.
  - When whooshes hit after the cut, the edit feels sluggish and lagging.
- **Impacts & Booms:** The transient must hit on the exact frame of contact or text entry.
- **J-Cuts & L-Cuts:**
  - **J-Cut:** Audio of the incoming scene/sound effect begins 0.5s - 1.0s prior to the visual switch. Builds anticipation.
  - **L-Cut:** Audio of the previous sound or dialogue lingers across the cut into the new shot. Smoothes jarring cuts.

---

## 3. Gaming & "Noob to Pro" Sound Toolkit

In Roblox / Anime Last Stand / Gaming content:
| Event / Visual Trigger | Primary SFX Stack | Emotional Pacing |
| :--- | :--- | :--- |
| **Snap Zoom on Face/Reaction** | Short whip-whoosh + subtle camera shutter | Adds punch to witty commentary |
| **Shock / Failure / Bad Roll** | Vine Boom (808 distortion) + vinyl record scratch or Roblox "OOF" | Comedic timing |
| **Summon / Opening Pack** | Magical chime riser -> Tension stop (0.2s silence) -> Godly choir beam + golden ding | Climax / High dopamine |
| **Stat / Level Up (+10 Levels)** | Cash register cha-ching + Mario 1-up / arcade coin ding + bass pulse | Progress validation |
| **Damage / Critical Strike** | Heavy anime slash / laser discharge + sub boom | Action intensity |
| **Fast Forward / Grinding Montage** | Muffled tape rewind sound -> upbeat synthwave/chiptune track with sidechain ducking | Relieves boredom during grinds |

---

## 4. Audio Ducking & Volume Balancing

Always provide exact decibel (dB) balance recommendations:
- **Spoken Voiceover / Commentary:** `-6 dB` to `-3 dB` (crystal clear, top of mix).
- **Foreground SFX (Impacts, Booms, Risers):** `-8 dB` to `-5 dB` (must cut through).
- **Secondary Foley & UI Clicks (Subtitles, button pops):** `-14 dB` to `-18 dB` (tactile without overwhelming).
- **Background Music (BGM):**
  - During commentary: `-22 dB` to `-26 dB` (auto-ducked by -6dB whenever voice is active).
  - During action montage without speech: `-10 dB` to `-8 dB`.

---

## 5. Outputting Production-Ready SFX Cue Sheets

Always format SFX schedules into a machine-readable, time-stamped table:
```markdown
| Timecode (s) | Frame | Visual Action | SFX Category | Recommended Sound Asset | Volume (dB) | Notes |
|---|---|---|---|---|---|---|
| 00:01.850 | 111 | Zoom into Noob Avatar | Transition | Whip Whoosh Fast | -10 dB | Lead in by 3 frames |
| 00:02.000 | 120 | "NOOB" Text Slam | Impact | Heavy Thud + Cartoon Squeak | -6 dB | Sync with camera shake |
```
