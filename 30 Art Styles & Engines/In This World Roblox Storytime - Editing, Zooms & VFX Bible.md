---
title: In This World Roblox Storytime — Editing, Zooms & VFX Bible
tags:
  - engine
  - roblox
  - storytime
  - editing
  - zooms
  - vfx
  - subtitles
  - sfx
area: engines
style: roblox
status: evergreen
created: 2026-11-16
updated: 2026-11-16
summary: Complete production, editing, camera, VFX, kinetic subtitle, and SFX engineering bible for "In This World" Roblox Storytime Shorts (Xenost-style), synthesized from 8 YouTube reference teardowns (Videos 9–16), Ropilot/ForgeGUI/Blender R6-R15 workflows, and the 25 Non-Negotiable Shortmaking Laws.
---

# "In This World" Roblox Storytime — Editing, Zooms & VFX Bible

> [!IMPORTANT] Scope & Synthesis
> This bible codifies the exact editing, camera grammar, VFX stack, kinetic typography, and audio engineering required to produce `1M–10M+` view **"In This World..." Roblox Storytime Shorts** (*Xenost* `@xenost-j3i` style). It synthesizes:
> - **8 Reference Teardowns**: [[Video 9 Teardown - How to Make Shorts That Go Viral Every Time (Logan Smith)|Logan Smith (HPC)]], [[Video 10 Teardown - How to Create Irresistible Hooks (Kallaway)|Kallaway (3-Step Hook)]], [[Video 11 Teardown - I Studied 100+ Hooks, This Strategy Will Make You Go Viral (Jade Beason)|Jade Beason (Hook Moment)]], [[Video 12 Teardown - Give Me 15 Mins, and I'll Make Your Hooks Impossible to Skip (Kallaway)|Kallaway (4 Hook Mistakes)]], [[Video 13 Teardown - How to Make Viral YouTube Shorts Captions in One Click (Thomas Creates)|Thomas Creates (1-Click Captions)]], [[Video 14 Teardown - 10 Must-Know Tips for Short-Form Content Creators (Ben Kaluza)|Ben Kaluza (Eye-Level Continuity)]], [[Video 15 Teardown - The Ultimate Guide to Editing Short-Form Content in 2026 (Joseph | Video Editing)|Joseph (7-Phase Premiere Pipeline)]], and [[Video 16 Teardown - The Most Popular Sound Effects for Editing 1240+ (Render Queue)|Render Queue (5-Bucket SFX)]].
> - **Workspace Engines**: [[Style 5 - Roblox Animated Shorts (Ropilot + ForgeGUI + Blender R6-R15)]], [[SFX Direction & The 2-4 Frame Lead-In Law]], [[04 Next-Generation Retention, Subtitles & Audio Spec]], and [[AGENTS]].

---

## 1. The Exact `"In This World..."` Hook & Narrative Structure (`< 45s` Cap)

Every high-retention Roblox storytime Short runs on a tight **`< 45 s` (`28–42 s` sweet spot)** arc (`3.8–4.3 words/sec`, `~115–158 words max`) with **zero dead air** (`<0.15 s` gaps) and a **strictly delayed payoff** ([[Video 9 Teardown - How to Make Shorts That Go Viral Every Time (Logan Smith)|Logan Smith HPC]]).

### 1.1 The `0–3.5 s` Hook Formula (3-Step + 3-Element Moment)
Combine **Kallaway's 3-Step Hook** with **Jade Beason's 3-Element Moment** (*Words + Visuals + Pacing* simultaneously on Frame 0):

| Beat | Timing | Verbal Formula (6th-Grade Active Voice, Staccato) | Simultaneous Visual & Audio Trigger |
| :--- | :--- | :--- | :--- |
| **1. Context Lean** | `0.0–1.5 s` | *"In this world, [universal absurd rule with a number]."*<br>*(e.g., "In this world, every word you speak costs one dollar.")* | **Blurred Zoom-Out** (`130% → 100%` + `Blur 3 → 0`) + **3–5 Word Stacked Hook Title** (`WORDS COST $1`) + glowing floating HUD counter. Zero Millennial Pause. |
| **2. Scroll-Stop Interjection** | `1.5–2.5 s` | Contrasting pivot word (`But`, `Except`, `However`):<br>*"Everyone else was careful. Except me."* | Hard cut or **115% Punch-In** on protagonist R6/R15 face + **2–4f lead-in whoosh** + subtle vignette pulse. |
| **3. Contrarian Snapback** | `2.5–3.5 s` | Implied or Stated **A vs. B Contrast**:<br>*"I woke up already ten thousand dollars in debt."* | **Chromatic aberration (`4f`)** + **7-frame impact shake** + `65 Hz` bass drop + red `#FF3344` emphasis caption (`-$10,000`). |

### 1.2 The 6-Beat Narrative Spine (HPC + Escalation Ladder, `< 45s`)
1. **Beat 1 — Hook (`0–3.5 s`)**: State the world rule + protagonist's impossible anomaly (opens 2–3 curiosity loops).
2. **Beat 2 — Normal Baseline (`3.5–9 s`)**: Show how normal people/family/classmates survive the rule (wide/medium shot, quirky rhythmic music).
3. **Beat 3 — First Complication (`9–17 s`)**: Protagonist enters a high-pressure social setting (school, store, birthday party, principal's office).
4. **Beat 4 — `"Luckily... / Unluckily..."` Reversal (`17–25 s`)**: Mandatory deadpan double-beat where a temporary win immediately backfires worse.
5. **Beat 5 — Fever-Dream Escalation (`25–35 s`)**: Stakes multiply exponentially (police, judge, giant avatar, world-ending consequence). Scene cuts accelerate to every **`1.0–1.6 s`**.
6. **Beat 6 — Delayed Climax & Loop Callback (`35–42 s`, strict `< 45 s` ceiling)**: Resolve the primary curiosity loop **only in the final 3 seconds** with an abrupt deadpan twist or ironic callback—**zero outro, zero "subscribe"**, cutting cleanly so viewers loop the opening frame.

---

## 2. Camera Grammar (Zooms, Tilts, Shakes & Tweening)

**Golden Rule**: **No camera hold is ever static (`≥4 frames`).** Even during dialogue, the camera must drift (`0.15–0.35%/frame` push) and visual framing must reset every **`1.5–3.0 s`**.

| Camera Move | Exact Keyframe / Math Spec | When to Use | Easing / Curve |
| :--- | :--- | :--- | :--- |
| **Opening Blurred Punch-Out** | `Scale: 130% → 100%` over `8–12f`; `Gaussian Blur: 3.0 → 0.0` | **Frame 0** of every Short to snap viewer attention | Fast-start, slow-settle (`Cubic.Out`) |
| **Punch-In Zoom-In** | `Scale: 100% → 115%` (normal emphasis) or `100% → 138%` (shock/punchline) over `5–8f` | On highlighted nouns, sudden realizations, or eyebrow/mouth swaps | `Back.Out` (slight `2%` overshoot) or `Quart.Out` |
| **Dramatic Zoom-Out** | `Scale: 145% → 100%` (2D) or Blender/Studio `28mm` dolly-back `1.8m → 6.5m` over `12–18f` | Revealing crowd staring, giant character, or chaotic aftermath | `Expo.Out` |
| **Dutch Tilt (Z-Roll)** | `Rotation: 0° → ±6° to ±12°` (`±15°` max on fever-dream climax) | Suspicion, rule-breaking, *"Wait what?"* beats, villain entrance | `Quint.Out` snap + slow `0.05°/f` creep |
| **Micro-Drift (Anti-Freeze)** | Continuous `Scale +0.15% to +0.35%/f` (or `0.6%/f` on punch words) | Every dialogue hold so `short_qa.py` never flags frozen frames | Linear / subtle S-curve |
| **7-Frame Impact `KICKS`** | Deterministic alternating-sign decay `(1 - u)` over `7 frames` on `dy` (`±18px → 0`) + roll `da` (`±2.5° → 0`); or AE `wiggle(15, 30)` for `6–10f` | Slaps, Roblox *Oof* ragdolls, bass drops, door slams, gavel hits | Linear decay `(1 - u)` |
| **Orbital Pan & Tweening** | `18–40f` smootherstep glide (`≤25 px/f` at 720p); Roblox `TweenService` on `Scriptable` `CFrame` | Establishing 3D Roblox map/room or circling a stunned character | `Smootherstep` / `Quad.InOut` |

### Eye-Level Cut Continuity (Ben Kaluza Rule)
Across rapid `1–3 s` scene cuts, keep the speaking R6/R15 avatar's **eyes anchored within `y = 35%–42%`** from the top of the `9:16` frame. The viewer's eye stays locked in one spot while the world changes behind them.

---

## 3. VFX Stack (Glow, Vignette, Chromatic Aberration, Particles & Grading)

| Layer | Exact Parameters | Trigger & Purpose |
| :--- | :--- | :--- |
| **1. Glow / Bloom** | **Premiere**: Glow (`Threshold: low`, `Radius: 97`, `Brightness: 132`) on hero hook text & neon props.<br>**Blender/3D**: `BloomEffect` (`threshold > 0.85`, `intensity: 0.35–0.6`). | Separates key hook nouns, glowing eyes, laser/magic VFX, and Roblox neon parts from the background. |
| **2. Vignette Pulses** | Resting radial vignette at **`15–20%` opacity**; pulse to **`38–45%` opacity** (dark plum/black) synced to riser swells or dread beats. | Narrows viewer tunnel vision toward the center character face during tension. |
| **3. Chromatic Aberration** | **3–6 frame RGB split** (`4–10 px` radial red/cyan offset) peaking on Frame 0 of impact and decaying to `0 px`. | Triggers visceral "screen-hit" sensation on bass drops, shocks, glitches, and plot twists. |
| **4. Speed Lines** | Radial anime/manga speed-line overlay (`Screen` blend, `15–30%` opacity, `12–15 fps` jitter). | Sprints, chases, sudden camera whip-ins, and panicked internal monologue. |
| **5. Particle Bursts** | Roblox `ParticleEmitter` / 2D PNG bursts: floating `$` bills, broken hearts, sweat drops, cartoon smoke puffs, sparks. | Visualizes abstract rules (*"$1 per word"*, *"100 hugs"*) directly in 3D space. |
| **6. Lighting & Color Grade** | **Blender R6/R15**: Warm key light + **cool cyan/violet rim light** (`28–35mm` lens at `1.8–2.5m`) to pop blocky silhouettes off the map.<br>**B-Roll/Text Contrast**: Adjustment layer under stacked text dropping **Brightness (`-25%`)** & **Saturation (`-30%`)** ([[Video 15 Teardown - The Ultimate Guide to Editing Short-Form Content in 2026 (Joseph | Video Editing)|Joseph Phase 5]]). | Prevents flat Roblox Studio lighting; ensures captions remain `100%` legible over busy maps. |

---

## 4. Subtitle Styling & Kinetic Typography

People **read faster than they hear** ([[Video 10 Teardown - How to Create Irresistible Hooks (Kallaway)|Kallaway]]). Captions are a primary retention engine, not an accessibility afterthought.

### 4.1 Two-Mode Caption Architecture
1. **Hook Mode (`0.0–3.5 s`) — Stacked Accumulating Title**:
   - Display `3–5` punchy words stacked in the upper-center/center zone, accumulating word-by-word so the full rule stays readable on screen.
   - Bold geometric sans (**Metropolis Bold**, **Montserrat Black**, or **Burbank Big Condensed**). Highlight the hero rule noun in **Orange/Yellow** with **Glow (`R=97, B=132`)**.
2. **Story Mode (`3.5 s–End`) — Rapid 1-Word (or 1–2 Word) Pop Captions**:
   - Transcribe and align to exact millisecond timestamps (`faster-whisper` → `words.json`, or Vizard/Premiere `max chars = 7`, `single line`).
   - **Pop-Up Fade-In + Bounce Curve**:
     - `f = 0`: `Opacity = 0%`, `Scale = 85%`, `Y = restY + 14px`
     - `f = 2`: `Opacity = 100%`, `Scale = 112%`, `Y = restY - 2px` *(overshoot)*
     - `f = 4`: `Opacity = 100%`, `Scale = 100%`, `Y = restY` *(settle)*

### 4.2 Emphasis Color Palette & Outline
- **Base Text**: Pure White `#FFFFFF` with thick `#000000` (or `#241726` plum) outline (`6–8 px` at `1080×1920`) + soft drop shadow (`blur 12px`, `opacity 65%`).
- **Yellow `#FFE600`**: Rule nouns, numbers, time limits, quantities (`100`, `DOLLAR`, `SECRET`).
- **Red `#FF3344`**: Danger, debt, negative twists, bans, deaths (`DEBT`, `ZERO`, `FIRED`).
- **Green `#22EE66`**: Wins, money gained, `"Luckily..."` beats (`RICH`, `SAVED`, `$1,000,000`).

### 4.3 `9:16` Platform Safe Zones (`1080×1920` / `1440×2560`)
Keep **all** captions and HUD counters inside the collision-free zone across YouTube Shorts, TikTok, and Reels:
- **Top Dead Zone (`0–220 px` / top `11.5%`)**: Covered by Shorts/TikTok search & following tabs.
- **Bottom Dead Zone (`1500–1920 px` / bottom `22%`)**: Covered by channel handle, description, and progress bar.
- **Right Rail (`920–1080 px` / right `15%`)**: Covered by Like/Comment/Share/Remix icons.
- **Optimal Caption Anchor**: Center-horizontal (`x = 540 px`), **`y = 1150–1320 px` (`60–69%` down)** for Story Mode; **`y = 860–1020 px` (`45–53%` down)** for Hook Title Mode.

---

## 5. SFX & Audio Layering Architecture

Every visual cut, zoom, and Roblox expression swap **must** have acoustic weight ([[Video 16 Teardown - The Most Popular Sound Effects for Editing 1240+ (Render Queue)|Render Queue]], [[SFX Direction & The 2-4 Frame Lead-In Law]]).

### 5.1 The 5-Layer Timeline Mix
1. **Voiceover (Anchor Layer — `-14 LUFS`, `TP = -1.0 dBTP`)**:
   - Crisp, deadpan-energetic narration (`en-AU-WilliamNeural` @ `+4%` or ElevenLabs).
   - **Zero dead air**: Trim every breath/silence `>0.15 s`; use **J-cuts** (`2–4` frames audio lead) across scene cuts.
2. **Transitions & Whooshes (`2–4 Frame Lead-In Law`)**:
   - Place high-passed whooshes/swishes **`2–4 frames` (`0.067–0.133 s`) BEFORE** the visual cut or zoom-in so the peak transient lands on Frame 0 of the new shot.
3. **Risers & Sub-Bass Impacts**:
   - **Riser**: `0.5–1.5 s` upward pitch/noise sweep leading into the `"Unluckily..."` or climax beat, cutting dead on impact.
   - **Bass Hit**: `60–80 Hz` sub-thud on Frame 0 of the twist/reveal (paired with 7-frame shake + 4-frame chromatic aberration).
4. **Roblox & Cartoon Foley**:
   - R6 plastic footsteps (`1.8 kHz` tap), classic Roblox *Oof* / *Gravity Coil* / *Slap* (`2.5 kHz` transient + `300 Hz` blocky crunch + `65 Hz` sub), UI pop (`2–5 kHz`) synced to every word/HUD counter tick, cartoon *boing/bonk/record-scratch* on absurd punchlines.
5. **Underscore Music Bed (`-6 dB` Gated RMS)**:
   - Quirky/marimba/suspenseful rhythmic loop mixed **`-6 dB` below voiceover** (`~0.28×` linear gain, sidechain-ducking `35%` whenever speech is active).
   - **Explicit FFmpeg Mux**: Always merge with `-map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest`.

---

## 6. Pre-Render QA Checklist (Before Shipping)
- [ ] **Frame 0 Audit**: Does Frame 0 have motion (blurred zoom-out), 3–5 word bold hook text, and immediate speech (`0.0 s` delay)?
- [ ] **Reset Cadence**: Does *something* change visually (cut, zoom, angle, particle, B-roll) every **`1.5–3.0 s`**?
- [ ] **Eye-Level Lock**: Are protagonist eyes anchored in `y = 35–42%` across cuts?
- [ ] **Safe-Zone Check**: Are all captions and HUD counters inside `x: 60–920 px`, `y: 220–1500 px`?
- [ ] **Audio Sync & Loudness**: Are whooshes leading cuts by `2–4 frames`? Is integrated loudness `-14 LUFS` with zero clipping?
- [ ] **Automated QA**: Run `python scripts/short_qa.py final.mp4 out/qa_visual` (`0` black frames, `0` white flashes, `0` frozen spans `≥12f`) and visually inspect cut midpoints.
