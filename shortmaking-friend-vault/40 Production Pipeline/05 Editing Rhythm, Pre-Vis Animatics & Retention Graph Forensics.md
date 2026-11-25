---
title: 05 Editing Rhythm, Pre-Vis Animatics & Retention Graph Forensics
tags:
  - pipeline
  - editing
  - pacing
  - animatic
  - pre-vis
  - retention
  - analytics
  - cuts
area: pipeline
style: all
status: evergreen
created: 2026-11-21
updated: 2026-11-21
summary: Complete non-3D editing, pacing, and retention forensics bible — the 2-minute Radio-Cut & Pre-Vis Animatic gate, Walter Murch's Rule of Six re-weighted for <45s vertical video, 10 exact pattern-interrupt cut mechanics, and diagnostic repair playbooks for real retention curves.
---

# 05 Editing Rhythm, Pre-Vis Animatics & Retention Graph Forensics

> [!IMPORTANT] Great Shorts Are Won in the Edit Before Rendering Starts
> Most creators spend 4 hours polishing visuals on a video whose pacing died at `t = 4.2 s`. **Never render final frames until the Radio-Cut + Animatic passes the boredom test.** A tight `<45 s` story with zero dead air, crisp pattern interrupts every `1.0–1.8 s`, and a delayed curiosity payoff beats Hollywood visuals on a slow script every single time.

---

## 1. The 2-Minute Radio-Cut & Pre-Vis Animatic Gate

Before animating scenes (whether 2D vector, 8-bit pixel, Roblox, or Blender), lock the entire video's rhythm in **two 2-minute gates**:

### Gate 1: The Eyes-Closed Radio-Cut (`voice_master.wav` Only)
Play ONLY the processed voiceover (`voice_master.wav`) from `0.00 s` to end with your eyes closed:
- **Duration Check**: Is total runtime strictly **`< 45.0 s`** (`28–42 s` sweet spot)? If it's `47 s`, cut words ruthlessly—never speed up voiceover past `+10%` to hide a bloated script!
- **The 3-Second Hook Gate**: If you heard only `0.0–3.0 s`, would you *physically stop scrolling* to hear how it resolves?
- **Zero Dead-Air Check**: Does any unintended pause exceed **`0.20 s`**? Trim breaths and inter-sentence gaps immediately.
- **Clarity Without Visuals**: Does the `"Luckily... / Unluckily..."` reversal and the `"You see,"` analogy make instant sense via audio alone?

### Gate 2: The Rough Storyboard Animatic (Static Beat Stills + `voice_master.wav`)
Lay `8–14` rough frames (simple sketches, color blocks, or single preview stills) onto `voice_master.wav` using [[storyboard-beat-sheet]]:
- Verify **every single `1.5–2.0 s` window** contains at least ONE visual state change (new shot, zoom punch-in, expression flip, prop reveal, or diagram step).
- Verify the **visual story works on mute**: turn volume to `0%`—can a viewer still follow the escalation from the expressions, props, and `2–4` word black-pill captions?

---

## 2. Walter Murch's Rule of Six — Re-Weighted for `< 45 s` Vertical Shorts

Classic cinema editor Walter Murch ranked why a cut works (`Emotion 51% → Story 23% → Rhythm 10% → Eye-Trace 7% → 2D Plane 5% → 3D Space 4%`). In modern vertical short-form (`9:16`, `<45 s`), re-weight every cut decision by these **6 priorities**:

| Priority | Weight | Short-Form Editing Rule | Concrete Execution |
| :---: | :---: | :--- | :--- |
| **1. Curiosity & Emotional Hook** | **40%** | Never close the main question early; open micro-loops before closing the previous one. | Cut *just* as an action begins or a reaction lands—delay the explanation until the `"You see,"` beat (`55–65%`). |
| **2. Verbal-Visual Rhythm** | **25%** | Cut **on stressed nouns, comedic reversals, and audio transients**—never halfway through a weak preposition. | Pair every major cut with a `2–4f` pre-cut whoosh lead-in (`[[SFX Direction & The 2-4 Frame Lead-In Law]]`). |
| **3. Eye-Trace Continuity** | **15%** | Keep the viewer's eyes locked in one vertical sweet spot (`y = 35%–45%` from top) across rapid cuts. | Place Character A's eyes in Shot 1 at the exact screen Y-height as Character B's eyes or the hero prop in Shot 2 (Ben Kaluza Law). |
| **4. 9:16 Safe-Zone Clarity** | **10%** | Never cut to a frame whose focal point hides behind YouTube/TikTok UI chrome. | Keep focal action inside `x: 100–900 px`, `y: 230–1260 px` and captions cleanly at `y: 1280–1420 px`. |
| **5. Visual Contrast (Shot Size Jump)** | **6%** | Every hard cut must change **shot scale OR angle ≥ 30°** (Wide → Medium → Extreme Close-Up). | Never cut from a Medium Shot to a slightly-zoomed Medium Shot—that causes an amateur jump-cut pop (Law 13). |
| **6. Spatial Continuity** | **4%** | Keep left-to-right screen direction consistent during chases/dialogues (180° rule), unless deliberately breaking it for fever-dream chaos. | Protagonist faces right (`+X`) when looking toward conflict/goal; antagonist faces left (`-X`). |

---

## 3. The 10 High-Retention Cut & Pattern-Interrupt Mechanics

Cycle through these 10 techniques so the viewer's brain never adapts to a predictable cadence (**average reset every `0.9–1.6 s`**):

| # | Technique | Exact Frame Spec (`30 fps`) | When to Use | Paired Audio Cue |
| :- | :--- | :--- | :--- | :--- |
| **1** | **Blurred Hook Punch-Out** | `Scale 130% → 100%`, `Blur 3px → 0px` over `8–10f` (`Cubic.Out`) | **Frame 0** opening snap | Crisp transient pop + immediate Word 1 |
| **2** | **J-Cut (Audio Pre-Lap)** | Next shot's VO/SFX begins **`2–4f` BEFORE** the visual cut | Every dialogue reply & beat transition | Eliminates "slideshow" stop-start feel |
| **3** | **L-Cut (Audio Carry-Over)** | Previous shot's impact tail or ambience bleeds **`4–8f` INTO** the new shot | Cutting from disaster to stunned reaction face | Glues two different locations seamlessly |
| **4** | **Emphasis Punch-In** | Instant `100% → 116%` (normal) or `100% → 135%` (shock) over `4–6f` (`Back.Out`) | Numbers, twists, deadpan stares | Short sharp `swosh-08` (`2f` early) |
| **5** | **Match-Action Cut** | Cut mid-motion (e.g., hand raising, door swinging, object falling) so motion completes in the new angle | Connecting setup → consequence smoothly | Continuous motion whoosh bridging cut |
| **6** | **Match-Shape / Graphic Cut** | Circle/window/eye in Shot A occupies the exact center pixel as a planet/coin/wheel in Shot B | `"You see,"` everyday-analogy transitions! | Subtle chime or tonal sweep |
| **7** | **Micro-Stutter / Comic Hold** | Hold shocked expression for `4f` with slow `0.5%/f` creep + tiny `±4°` Dutch tilt | Deadpan `"Unluckily..."` punchline | `8f` music silence drop → dry `bonk` |
| **8** | **Whip-Pan / Directional Blur** | Fast `5–7f` horizontal/vertical smear sweep linking two scenes | High-energy chases, escalation ladders | High-passed whip swish peaking at frame 3 |
| **9** | **7-Frame Impact Kick + CA** | Deterministic alternating-sign decay `(1-u)` over `7f` (`±16 px`, `±2.5°` roll) + `4f` RGB split | Bass drops, explosions, slaps, stat slams | 4-layer sub-thud (`65 Hz`) + crunch |
| **10** | **Seamless Loop Cut** | Cut final frame **`< 0.08 s`** after last syllable; match final horizon & lighting to Frame 0 | Final frame of every `<45 s` Short | `25 ms` micro-fade on music bed, zero silent tail |

---

## 4. Retention Graph Forensics — Diagnosing & Fixing Real Curves

After every upload hits `1,000+` views, open YouTube Studio / TikTok Analytics and match its retention graph to one of these **5 diagnostic patterns** (record findings in [[retention-postmortem-template]]):

| Retention Graph Shape | Where Viewers Left | Root Cause Diagnosis | Exact Fix for Next Video |
| :--- | :--- | :--- | :--- |
| **1. The `0–3 s` Cliff** *(Viewed vs. Swiped `< 70%`)* | First `2.5 s` | Slow intro (*"In 1880..."*, *"Did you know..."*), silent Frame 0 breath, static blurry wide shot, or unclear visual focal point. | Start mid-paradox on Frame 0 (`0.00 s` speech), add `130%→100%` punch-out + `3–5` word glowing hook headline + clear face/prop anomaly. |
| **2. The `5–10 s` Second-Hook Slump** *(Sharp dip after good 3s start)* | Beat 2 (`5–10 s`) | Viewer stayed for the hook, then hit a boring exposition dump (*"First, let's understand the background..."*). | Immediately escalate the stakes in Beat 2 instead of explaining history; cut every word that doesn't add tension or irony. |
| **3. The Mid-Video Ski Slope** *(Steady downward bleed from `12 s → 30 s`)* | Beats 3–4 | Predictable visuals (same shot held `>3.5 s`), flat vocal cadence, or missing `"Luckily.../Unluckily..."` reversal + `"You see,"` pivot. | Force visual reset every `1.0–1.6 s`, vary shot sizes (`Wide → CU → Diagram → Reaction`), add `"You see,"` visual analogy at 58%. |
| **4. The Premature Drop-Off** *(Steep plunge at `82–90%`)* | Last `5 s` | You gave away the climax too early, added an outro (*"So that's why..."*, *"Like and subscribe"*), or left a `1.5 s` silent tail. | Delay the primary answer until the **final 3 seconds**, end immediately on the callback twist, and cut `<0.08 s` after the final word! |
| **5. The Flat Plateau + Replay Spike** *(APV `> 100%`)* | Entire video + `0–3 s` spike | **WINNER!** High information density, fast comedic/visual clues worth rewatching, or seamless grammatical loop + active comments. | **Clone the exact structural skeleton** (hook rhythm, visual cadence, word rate, topic family) into a 5-part series! |

---

## 5. Pre-Export Editing QA Checklist
- [ ] Total duration is strictly **`< 45.0 s`** (`28–42 s` target).
- [ ] Audio starts on **Frame 0 (`≤ 0.05 s` lead)** and ends **`≤ 0.08 s`** before the final video frame.
- [ ] Longest uninterrupted visual hold without a cut, zoom punch, or animation state change is **`≤ 2.2 s`**.
- [ ] Every hard cut jumps shot scale or angle cleanly (zero accidental jump-cut pops).
- [ ] Verified visually via `short_qa.py` (`0` black frames, `0` frozen spans `≥12f`) and [[Post-Completion Visual QA — What, How & Why to Fix]].

## Related Vault Guides
- [[02 Shot Planning & Camera Grammar]]
- [[04 Next-Generation Retention, Subtitles & Audio Spec]]
- [[Deep Research - Animation Layout, Staging & Visual Composition]]
- [[storyboard-beat-sheet]]
- [[retention-postmortem-template]]
