---
title: Video 13 Teardown — How to Make Viral YouTube Shorts Captions in One Click (Thomas Creates)
tags:
  - teardown
  - captions
  - subtitles
  - typography
  - automation
area: teardowns
style: all
status: evergreen
created: 2026-11-16
updated: 2026-11-16
summary: Breakdown of Thomas Creates' viral Shorts captions workflow (youtu.be/8sb2R11FeVw) covering automated word-level transcription, keyword color highlighting, emoji injection, reusable brand templates, and multilingual caption localization.
---

# Video 13 Teardown — How to Make Viral YouTube Shorts Captions in One Click

- **Creator**: **Thomas Creates** (`@thomascreates12`, `49.1K` subscribers)
- **Video URL**: [https://youtu.be/8sb2R11FeVw](https://youtu.be/8sb2R11FeVw)
- **Metrics**: `14,367` views · `595 s` (`9m 55s`) · `3840×2160 @ 30 fps` · Uploaded `2026-11-03`

---

## 1. Core Workflow: Automated Word-by-Word Captions
Thomas demonstrates a 1-click AI captioning pipeline (using **Vizard**) designed to eliminate manual transcription and keyframe timing while maintaining high visual polish:

1. **Word-Level Timestamp Sync**: Auto-transcribe speech and lock every caption token to exact millisecond boundaries so words pop in sync with spoken syllables.
2. **Animation Presets**: Apply kinetic pop/bounce presets across the entire timeline in one pass rather than keyframing individual text layers.
3. **AI Keyword Highlighting**: Automatically color-code nouns, numbers, and emotional punch words (e.g., yellow/green/red emphasis against white base text) to anchor eye tracking.
4. **Emoji & B-Roll Injection**: Pair key emotional or object words with inline emojis or quick B-roll cutaways to break visual monotony.
5. **Reusable Brand Templates**: Save font family, stroke/shadow, highlight palette, and safe-zone Y-position as a locked template so every Short has instant channel recognition.
6. **Multilingual Localization**: Translate burned-in/SRT captions into secondary languages for international Shorts expansion.

---

## 2. Actionable Takeaways for Shortmaking Code Pipelines
- **Template-First Typography**: Just as Vizard locks a reusable brand template, our Remotion/Playwright/Premiere pipelines should lock `fontFamily`, `highlightColor`, `bounceCurve`, and `safeZoneY` in a single config object.
- **Automated Keyword Tagging**: Pair `words.json` (`faster-whisper`) with a keyword classifier that flags numbers, stakes nouns, and twist words for `color` + `1.15×` scale pop.
- **Related Notes**: [[Video 15 Teardown - Ultimate Guide to Editing Short-Form Content in 2026 (Joseph Video Editing)]], [[In This World Roblox Storytime - Editing, Zooms & VFX Bible]].
