---
title: Online Skills & Community Repos Index
tags:
  - skills
  - github
  - open-source
  - remotion
  - blender
  - manim
area: tools
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Curated directory of the best open-source animation, Remotion, Blender MCP, Manim, and motion-graphics skills available online to expand your pipeline.
---

# Online Skills & Community Repos Index

In addition to the **34 skills** already vendored in `.agents/skills/`, this directory tracks the top open-source repositories across GitHub and Google Drive for code-driven animation, ArtCraft native Rust apps, and AI audio intelligence.

---

## 1. Core Reference Video & Audio Repositories (Already Vendored Locally)

| Repository / Archive | Creator | Source URL | Local Vendored Path |
| :--- | :--- | :--- | :--- |
| **`mromidev/claude-animated-shorts`** | **Mr omi** (`@mr_omix`) | `https://github.com/mromidev/claude-animated-shorts` | `.agents/skills/cartoon-3d-short/` |
| **`3d-kaz.plugin` (`make-3d-video`)** | **Grow With Kaz** (`@GrowWithKaz`) | Google Drive `168sNBEQzRl05XHbQgv2Ktjz-PBMzzoxJ` | `.agents/skills/make-3d-video/` |
| **`cartoon-short-kit` (`cartoon-audio-short`)** | **AI Playbook / mr miro** | Google Drive `16vwh4Wpcxs8KSsTzSCQ8Ga23weSAhy3j` | `.agents/skills/cartoon-audio-short/` |
| **`Leonxlnx/earshot`** (`earshot` + `real-sound`) | **Leon Lin** (Featured in Short 6: `2yNiLmpbHl4`) | `https://github.com/Leonxlnx/earshot` | `.agents/skills/earshot/` & `.agents/skills/real-sound/` |
| **`storytold/artcraft` & `craft-skills`** | **ArtCraft (`getartcraft.com`)** | `https://github.com/storytold` | Documented in [[ArtCraft Suite & MCP Directory (All 16 Crafting Apps)]] |

---

## 2. Additional Online Skills for Code-Driven Video & 3D Animation

| Repository | Engine / Stack | Best Use Case | Install / Clone Command |
| :--- | :--- | :--- | :--- |
| **`remotion-dev/skills`** (Official Remotion Skills) | Remotion 4 + React + Three.js | Official `@remotion/three`, `@remotion/captions`, `@remotion/lottie`, and 3D camera choreography rules. | `npx skills add remotion-dev/skills` |
| **`haidrrrry/claude-remotion-skill`** | Remotion + Claude Code | High-retention product launch videos, kinetic typography, and social shorts in React. | `git clone https://github.com/haidrrrry/claude-remotion-skill` |
| **`whaleyxbt/claude-motion`** | Remotion + GSAP + Tailwind | Fast motion-graphics scenes, glassmorphism UI cards, and data-driven charts for Shorts/Reels. | `git clone https://github.com/whaleyxbt/claude-motion` |
| **`ahujasid/blender-mcp`** | Blender Python (`bpy`) + MCP | The upstream Blender MCP server powering `execute_blender_code`, PolyHaven, Sketchfab, and Hyper3D asset generation. | `git clone https://github.com/ahujasid/blender-mcp` |
| **`arjun988/blender-skills`** | Blender `bpy` Skill Pack | Modular Claude skills for procedural modeling, geometry nodes, rigid-body destruction, and Cycles lighting setups. | `git clone https://github.com/arjun988/blender-skills` |
| **`Yusuke710/manim-skill`** & **`awesome-skills/manim-skill`** | Manim Community (Python) | **3Blue1Brown-style mathematical, physics, and algorithmic animations** rendered at 60fps in vertical 9:16 (`config.frame_width = 9`, `config.frame_height = 16`). | `git clone https://github.com/Yusuke710/manim-skill` |
| **`TapXWorld/MathModelAgent`** / **Motion Canvas Skills** | Motion Canvas (TypeScript) | Procedural vector animations, state machines, and code-step walkthroughs with generator-based `yield*` timing. | `npm init @motion-canvas@latest` |

---

## 3. When to Add Manim or Motion Canvas to a 3D Short

In hybrid explainers (like *Fern*, *Veritasium*, or *Grow With Kaz* Science shorts):
- Use **Three.js / Blender** for the **physical world** (the bedroom, the suspension bridge, the battlefield, the human brain).
- Use **Manim (`manim-skill`) or Remotion SVG** for **2–4 second analytical cutaways** (e.g., plotting the sine-wave resonance buildup of the bridge `f_0 = 1.97 Hz`, or graphing the exponential decay of dream memory from `100% → 5%`).
- Composite or cut between the 3D scene and the analytical graph on the `"You see,"` pivot beat!
