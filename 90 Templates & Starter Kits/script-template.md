---
title: Template — 60s Beat-by-Beat Script & Word-Timing Table
tags:
  - template
  - script
  - timing
  - storyboarding
area: templates
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Beat-by-beat script, camera, acting, and frame-timing template synced to 3.7 words/sec (or 2.6 words/sec).
---

# Beat-by-Beat Script & Shot Timing Template

Use this table to map every sentence of your script to exact `words.json` frame numbers (`f = Math.round(t * 30)`), camera primitives (`cut`, `glide`, `push`, `kick`), and character expressions (`2f` lead before spoken punch word).

---

| Beat # | Frame Range (`s..e`) | Spoken Narration (`3.7 wps`) | Zone & Camera (`p`, `l`, `fov`) | Motion (`push` / `glide` / `kick`) | Character Pose (`2f` lead on punch word) | Light & DOF (`focusDist`, `maxCoc`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01 (Hook)** | `0 .. 114` (`0.0–3.8s`) | *"In [YEAR], a [NOUN] [IMPOSSIBLE OUTCOME] because [ABSURD REASON]."* | Zone A Wide `[0, 2.2, 8.5]` | `push(0.0025)` | Hero `'lidded'`, walk cycle | `day`, `[8.5, 4]` |
| **02 (Setting)** | `114 .. 228` (`3.8–7.6s`) | *"[CONCRETE NUMBERS] are [PRESENT TENSE ACTION]..."* | Zone A MCU `[-1.4, 1.6, 3.6]` | `glide(24f)` → `push` | Brows `'raised'` at `f=142` | `day`, `[3.6, 14]` |
| **03 (Joke 1)** | `228 .. 345` (`7.6–11.5s`) | *"'[IN-CHARACTER QUOTE]' — which goes about as well as you'd expect."* | Zone B Two-Shot `[1.8, 1.7, 4.8]` | Hard cut + `push` | Foil `'smirk'` → `'o'` | `day`, `[4.8, 11]` |
| **04 (Luckily / Unluckily)** | `345 .. 480` (`11.5–16.0s`) | *"Luckily, [GOOD NEWS]. Unluckily, [WORSE NEWS]."* | Zone B CU `[0.2, 1.55, 2.9]` | `kick(f=412)` on *"Unluckily"* | Eyes `'wide'` at `f=410` | `tense`, `[2.9, 15]` |
| **05 (Climax / Snap)** | `480 .. 630` (`16.0–21.0s`) | *"Until suddenly—[PHYSICAL DISASTER]."* | Hero Insert `[0.0, 1.2, 2.4]` | `kick(f=584, ampY=0.18)` | Eyes `'dead'` / prop breaks | `tense`, `[2.4, 16]` |
| **06 (Mystery)** | `630 .. 735` (`21.0–24.5s`) | *"Wait—how did [SMALL CAUSE] destroy [GIANT TARGET]?"* | Zone A Aftermath `[0, 2.5, 9.0]` | Slow pull-back `push(-0.002)` | Hero `'frown'`, head tilt | `day`, `[9.0, 4]` |
| **07 ('You see,' Pivot)** | `735 .. 930` (`24.5–31.0s`) | *"You see, every [OBJECT] has a [MECHANISM], like [EVERYDAY ANALOGY]."* | Zone C Analogy Set `[-80, 1.8, 5.2]` | `glide(30f)` synced to arc | Analogy prop oscillating | `golden`, `[5.2, 12]` |
| **08 (Escalation 2)** | `930 .. 1140` (`31.0–38.0s`) | *"Each time [ACTION REPEATS], the force multiplies..."* | Zone A Close `[0.5, 1.4, 3.2]` | Accelerating `push(0.004)` | Urgent speech (`10 Hz`) | `golden`, `[3.2, 14]` |
| **09 (Callback Twist)** | `1140 .. 1350` (`38.0–45.0s`) | *"And to this day, [IRONIC REAL-WORLD RULE]."* | Zone D Payoff `[0, 1.75, 4.5]` | `push(0.0025)` + cut `<0.08s` after last word | Deadpan `'line'` + `4f` blink | `day`, `[4.5, 12]` |
