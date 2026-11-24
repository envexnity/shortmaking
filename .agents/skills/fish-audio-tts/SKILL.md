---
name: fish-audio-tts
description: Expressive Text-to-Speech, voice cloning, voice design, speech-to-text, and automatic best-available TTS model selection across fish-audio, kokoro-tts, edge-tts, and local-os-tts MCP servers.
---

# Fish Audio & Auto-Tiered TTS MCP Guide

Use this skill whenever generating narration, character dialogue, voiceovers, voice clones, or transcripts.

## 1. Automatic Best-Available TTS Model Selection (Priority Order)

Agents MUST automatically select and switch to the **best available TTS model** in the following priority order (falling back automatically if a higher tier is unauthenticated, offline, rate-limited, or missing):

1. **Tier 1 — `fish-audio` MCP (`S2.1-Pro` / `s2.1-pro-free`) [Default Best]**
   - **When to use:** Always try `fish-audio` first when authenticated (via OAuth). Use `s2.1-pro-free` ($0 prototyping) or `s2.1-pro` (expressive production).
   - **Why:** Best emotional range, inline stage-direction tags (`[whispers sweetly]`, `[laughing nervously]`, `[sigh]`, `[excited]`, `[pause]`), 83 languages, 2,000,000+ voices, and voice cloning/design.
2. **Tier 2 — `kokoro-tts` MCP (`agent-fm`, Kokoro-82M ONNX)**
   - **When to use:** Automatic fallback when `fish-audio` is not yet signed in, offline, or out of credits, and you need high-quality **offline** neural speech without an API key.
   - **Capabilities:** 82M-parameter local ONNX neural TTS, 54 voices, 9 languages, runs on CPU.
3. **Tier 3 — `edge-tts` MCP (`edge_tts_mcp`) / `edge-tts` CLI (`en-AU-WilliamNeural`, `rate="+4%"`)**
   - **When to use:** Fallback when `fish-audio` is unavailable and you need Microsoft neural voices (300+ voices, 50+ languages, free, no API key) or when a legacy kit specifically requires `edge-tts` subtitle/word-timing integration.
4. **Tier 4 — `local-os-tts` MCP (`text-to-speech-mcp`)**
   - **When to use:** Last-resort zero-setup offline fallback (Windows SAPI / macOS `say` / Linux `espeak-ng`) or for instant local spoken notifications (`speak_text`).

> **Rule:** Never fail a voiceover task just because `fish-audio` needs OAuth or credits — automatically fall back to `kokoro-tts` → `edge-tts` (`en-AU-WilliamNeural` @ `+4%`) → `local-os-tts`, and note which tier was used.

---

## 2. How to Use Fish Audio MCP & New Features

### A. Expressive Text-to-Speech (TTS) & Natural Language Control
- **Inline Emotion & Vocal Cues (`S2.1-Pro` / `s2.1-pro-free`):**
  Direct how lines are delivered directly inside the text using bracketed tags—not restricted to a rigid preset list, so natural-language stage directions work:
  - Examples: `[whispers sweetly]`, `[laughing nervously]`, `[sigh]`, `[excited]`, `[pause]`, `[deadpan]`, `[out of breath]`.
  - Shortmaking tip: Use `[pause]` or `[deadpan]` for dry reversals, and `[excited]` or `[whispering]` for the `"You see,"` analogy pivot.
- **Massive Multilingual Reach:** 83 languages supported with automatic language detection, preserving natural accents and cadence across borders.
- **Community Voice Library:** Search and select from **2,000,000+** user-uploaded and studio voices (from warm audiobook narrators to dramatic game characters) using the `fish-audio` MCP voice search tools.

### B. Flexible Voice Cloning & Design
- **Instant (Zero-Shot) Cloning:** Replicate a voice from just a **10–30 second** audio clip; built-in audio enhancement automatically strips background noise.
- **Persistent & Professional Clones:** Train reusable voice models for consistent channel branding, or create verified studio-grade clones.
- **Text-to-Voice Design:** Generate completely original character voices from a **plain-text description** (e.g. *"raspy exhausted 1880s British bridge engineer, warm baritone"*) without needing a reference audio sample.

### C. Production & Audio Tools (Fish Audio Web App)
- **Story Studio:** Multi-speaker editor for long-form audiobooks, podcasts, and radio dramas with distinct character voices.
- **Voice Changer:** Speech-to-speech transformation converting an existing recording into a target voice while preserving original timing and inflection (ideal for acting out cartoon character lines yourself, then transforming the voice).
- **Music, SFX & Stem Separation:** Generate background music and cinematic sound effects from text prompts, or split existing audio tracks into isolated vocal and instrumental stems.

### D. Developer-First Capabilities
- **Ultra-Low Latency Streaming:** Achieves **~100–150ms** time-to-first-audio over WebSockets for real-time conversational AI agents and live voice assistants.
- **Smart Speech-to-Text (STT):** `transcribe-1-pro` and streaming ASR models transcribe up to **60-minute** multi-speaker recordings with:
  - Speaker diarization
  - Word/segment timestamps (great for syncing shortmaking captions!)
  - Inline emotion & sound event detection (e.g., `[laughter]`)
- **Open-Source Foundation & Free Tier:** Built on open-source **Fish-Speech**, with the **$0 prototyping model (`s2.1-pro-free`)** for zero-cost workflow testing.
