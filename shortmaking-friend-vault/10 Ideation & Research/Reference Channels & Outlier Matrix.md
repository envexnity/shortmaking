---
title: Reference Channels & Outlier Matrix
tags:
  - ideation
  - references
  - channels
  - analysis
area: ideation
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Breakdown of the top viral animated short channels across all 5 art styles—their exact visual engines, pacing numbers, hook archetypes, and how to replicate them with this vault.
---

# Reference Channels & Outlier Matrix

This matrix maps the **top-performing short-form animation channels on YouTube Shorts & TikTok** directly to the 5 production engines and look-bible specs in this vault.

---

## 1. Master Channel-to-Vault Mapping

| Channel / Creator | Primary Art Style | Typical Views / Outlier | Speaking Rate (WPS) | Signature Visual & Narrative Hook | Vault Track to Replicate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Nutshell Animations** (`@NutshellAnimations`) | 2D Bean-Head Cards / Illustrated Scenes | `5M – 35M` | `3.8 – 4.1 wps` | Relatable social awkwardness + hyper-expressive `2f` pre-word brow/mouth swaps | **Track 1 & 2** (`cartoon-3d-short` / `cartoon-audio-short`) |
| **Mr omi** (`@mr_omix`) | **2D-in-3D Toon World** (Plum `#241726` cards in inked 3D sets) | `1M – 15M+` | **`3.7 wps` median** | 1-sentence historical/physics paradox + `"Luckily / Unluckily"` + `"You see,"` swing analogy | **Track 1** (`.agents/skills/cartoon-3d-short`) |
| **mr miro** (`@miromotions`) | **2D-in-3D Toon World** (Napoleon, Historical Absurdities) | `500K – 8M+` | `3.6 – 3.9 wps` | Military/historical plans gone catastrophically wrong due to one tiny detail | **Track 1 & 2** (`cartoon-3d-short` / `cartoon-audio-short`) |
| **AI Playbook** (`@AIPlaybook-b5c`) | **2D-in-3D Emotional Storytime** (*Hachiko*, *1918 Pigeon*) | `500K – 5M+` | `3.3 – 3.6 wps` | Heartbreaking loyalty or impossible survival against the clock in period 3D sets | **Track 2** (`.agents/skills/cartoon-audio-short`) |
| **Grow With Kaz** (`@GrowWithKaz`) | **Low-Poly Flat-Shaded 3D + Telemetry HUD** | `1M – 12M+` | **`~2.6 wps`** | Science/History/What-If dioramas with live escalating HUD stats (`100% → 5%`) | **Track 3** (`.agents/skills/make-3d-video`) |
| **Hoog** (`@Hoog`) / **Fern** (`@Fern-TV`) | **Stylized / Low-Poly & Atmospheric 3D Dioramas** | `3M – 25M+` | `3.2 – 3.5 wps` | Miniature tilt-shift camera flights through forensic/historical crime scenes & maps | **Track 3 & Track 4** (`make-3d-video` + `blender` MCP) |
| **Zack D. Films** (`@zackdfilms`) | **Realistic 3D Medical / Mechanical Cross-Sections** | **`15M – 120M+`** | `3.5 – 3.8 wps` | Visceral bodily or mechanical question answered with an animated boolean cutaway at `t = 4s` | **Track 4** (`blender` MCP + `.agents/skills/cook`) |
| **Brew** (`@Brew`) / **Kurzgesagt** (`@kurzgesagt`) | Stylized Vector / 2.5D Science & Mystery | `5M – 40M+` | `3.4 – 3.7 wps` | Everyday symptom or cosmic thought experiment escalated to extreme scale | **Track 1, Track 3 & Bonus Track** |
| **Xenost** (`@xenost-j3i`) | **Roblox R6/R15 Storytime & Family Roleplay Skits** | **`1.1M – 5.4M+`** (`1.4M+` subs) | `3.8 – 4.3 wps` | Recurring family cast (`Dad`, `Baby Sister`, `Mom`, `Karen`) + absurd 1-premise POV hooks (*"My DAD..."*, *"A Karen..."*, *"In this world..."*) | **Track 5** (`ropilot` + `forge-gui` + Blender R6/R15) |
| **AIpreneur** (`@AIpreneur2176`) | **AI 3D Motion Graphics** (Claude + Google Flow + CapCut) | `180K+` (tutorials) | `~3.2 – 3.6 wps` | 1 anchor style image + 6s beat-table motion clips + editor-composited kinetic text & paper fades | **Bonus Track** ([[Video 7 Teardown - 3D Motion Graphics With Claude & Google Flow (AIpreneur)]]) |

---

## 2. How to Mine Your Own Outliers in 10 Minutes

Before scripting a new video, run this 3-step **Outlier Ratio Check**:
1. Pick 3 channels from the table above (or adjacent long-form documentary channels like *Veritasium*, *Mustard*, *Imperial*, *Lemmino*, *Simple History*).
2. Sort their Shorts (or Videos) by **Popular** vs. **Latest** over the last 6 months.
3. Calculate the **Outlier Multiplier**:
   $$\text{Outlier Multiplier} = \frac{\text{Video Views}}{\text{Channel Median Views (Last 20 Uploads)}}$$
4. **Selection Rule**: Only adapt topics that achieved an **Outlier Multiplier `≥ 3.5×`** on at least one channel—and then **translate the art style across tracks** (e.g., take a 15M-view *Simple History* 2D video and rebuild it as a **2D-in-3D Toon Short** in Track 1 or a **Low-Poly 3D HUD Short** in Track 3).
