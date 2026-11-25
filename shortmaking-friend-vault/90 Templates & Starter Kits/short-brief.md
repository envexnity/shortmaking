---
title: Template — Short Production Brief
tags:
  - template
  - brief
  - production
area: templates
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Pre-flight production brief template for starting any new viral animated short across all 5 art style tracks.
---

# Short Production Brief Template

Copy this brief into your new project folder (`BRIEF.md`) before writing code or running agents.

---

## 1. Project Identity & Track Selection
- **Working Title (`≤52 chars`)**: 
- **Art Style Track**: `[ ] Track 1: 2D-in-3D Toon (Remotion)` | `[ ] Track 2: 2D-in-3D Standalone (Playwright)` | `[ ] Track 3: Low-Poly 3D (Kaz)` | `[ ] Track 4: Realistic Blender 3D` | `[ ] Track 5: Roblox R6/R15`
- **Target Duration**: `45.0s` (`1350 frames @ 30fps`)
- **Speaking Rate Target**: `3.7 wps` (`~165 words` total) or `2.6 wps` (Low-Poly HUD)

---

## 2. The 6-Part Narrative Spine
1. **Sentence 1 Paradox Hook (`10–16 words`)**:
   > *""*
2. **Setting & Concrete Numbers (`1–2 sentences`, present tense)**:
   > *""*
3. **Escalation & `"Luckily... / Unluckily..."` Reversal**:
   > *"Luckily, ... Unluckily, ..."*
4. **Mystery Question (`"Wait — how did ...?"`)**:
   > *""*
5. **The `"You see,"` Pivot + Everyday Physical Analogy**:
   > *"You see, ..."*
6. **Callback Twist Ending (Final 1–2 sentences, zero outro)**:
   > *""*

---

## 3. World Zones & Cast List
- **Zone A (`z = 0`)**: 
- **Zone B (`x = +80`)**: 
- **Zone C (`x = -80`)**: 
- **Cast**:
  - `Hero`: Shirt `#`, Hat `''`, Prop `''`
  - `Foil / Crowd`: Count `N`, Shirt `#`

---

## 4. Quality Gates Before Shipping
- [ ] `words.json` / `timing.json` generated from actual `voice.mp3`
- [ ] Contact sheet (`stills.jpg` / `sbs_sheet.png`) inspected via `read_file` against all 12 rules in [[Readability Traps & Anti-Slop Rules]]
- [ ] Procedural audio + SFX mixed at `-6 dB` gated RMS and normalized to `-14 LUFS`
- [ ] `short_qa.py` passed (`0` black frames, `0` white flashes, `0` frozen spans `≥12f`)
