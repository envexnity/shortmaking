---
title: Voice Acting, Expressive TTS Direction & Vocal Processing Bible
tags:
  - audio
  - voiceover
  - tts
  - fish-audio
  - kokoro
  - edge-tts
  - voice-acting
  - mixing
  - lip-sync
area: audio
style: all
status: evergreen
created: 2026-11-21
updated: 2026-11-21
summary: Complete voice production bible covering the 4-tier auto-TTS stack (Fish Audio S2.1-Pro, Kokoro-82M, Edge-TTS, Local OS), inline emotion & stage-tag direction, multi-character dialogue casting, dead-air removal, broadcast FFmpeg vocal EQ/compression chains, and word-level lip-sync.
---

# Voice Acting, Expressive TTS Direction & Vocal Processing Bible

> [!IMPORTANT] Voice Is the Retention Backbone
> Viewers forgive stylized 2D stick figures or retro 8-bit graphics in 0.2 seconds—**they never forgive robotic, muddy, or sluggish voiceover**. Voiceover controls pacing (`3.5–4.1 wps`), comedic timing, emotional escalation, and millisecond cut alignment across every single track in this vault.

---

## 1. The 4-Tier Auto-TTS Priority Stack (Law 24)

Always load `.agents/skills/fish-audio-tts/SKILL.md` before synthesizing speech. Unless the user requests a specific voice engine, select automatically in priority order:

| Priority | Engine / MCP | Best Strengths | Ideal Use Cases | Key Config / Notes |
| :---: | :--- | :--- | :--- | :--- |
| **Tier 1** | **`fish-audio` MCP** (`s2.1-pro` / `$0` `s2.1-pro-free`) | Inline emotional stage tags (`[whispers]`, `[sigh]`, `[laughing nervously]`), `2M+` voices, `10–30 s` zero-shot voice cloning, Text-to-Voice Design, 83 languages | Flagship storytelling, Roblox dialogue casts, comedy timing, emotional twists, character acting | Supports `transcribe-1-pro` STT for exact word timestamps; keep inline tags sparse (`1–2` per beat) so pacing stays crisp. |
| **Tier 2** | **`kokoro-tts` MCP** (`agent-fm`) | Fast 82M-param local ONNX neural TTS; zero API latency/cost; crisp clean narrator diction | Rapid animatic prototyping, high-volume batch explainers, offline runs | Great for clean neutral/British/American narrators (`af_heart`, `am_michael`, `bm_george`). |
| **Tier 3** | **`edge-tts`** (MCP / CLI) | Reliable free Microsoft Neural voices with explicit rate & pitch control | Fast reliable fallback (`en-AU-WilliamNeural`, `rate="+4%"` to `"+7%"`) | Pair with FFmpeg `silenceremove` to strip synthetic inter-sentence breaths (`>0.15 s`). |
| **Tier 4** | **`local-os-tts` MCP** (`text-to-speech-mcp`) | Zero-dependency Windows SAPI fallback | Emergency offline scratch tracks / radio-cut pre-vis only | Never ship final video on Tier 4; upgrade to Tier 1–3 before final mux. |

---

## 2. Expressive Stage Direction & Prosody Engineering (`Fish Audio S2.1-Pro`)

Flat TTS reads every sentence with the same rising-falling news-anchor curve. Break TTS monotony with **beat-locked vocal direction**:

### A. Story-Beat Stage Tag Map
| Narrative Beat | Vocal Delivery Objective | Fish Audio Inline Tag Examples | Cadence & Pitch Shape |
| :--- | :--- | :--- | :--- |
| **Beat 1 — Paradox Hook (`0–3.5 s`)** | Instant authority + absurd matter-of-factness (zero "YouTuber hype" screaming) | *(Clean dry start)* or `[serious]` → `[surprised]` on the twist word | Start mid-high pitch, punch the impossible noun, drop cleanly into Beat 2 with `<0.08 s` gap. |
| **Beat 2 — Escalation / Setup** | Brisk conversational momentum (`3.7–4.0 wps`) | `[conversational]`, `[curious]` | Keep phrase endings slightly *lifted* (upward inflection on commas) so the ear expects the next clause. |
| **Beat 3 — `"Luckily... / Unluckily..."`** | Deadpan comedic reversal | `[relieved]` on *Luckily...* → `[sigh]` / `[deadpan]` on *Unluckily...* | Insert an exact **`0.14–0.18 s` comic micro-beat** right before *"Unluckily,"*—short enough to avoid dead air, long enough to prime the laugh. |
| **Beat 4 — `"You see,"` Mechanism Pivot** | Conspiratorial "lean-in" explainer tone | `[intrigued]`, `[whispers]` (for horror/mystery) | Drop volume `1–2 dB` slightly and slow `5%` for 1 second to signal *"pay attention, here's the secret."* |
| **Beat 5 — Climax / Chaos** | Urgent, breathless intensity | `[excited]`, `[panicked]`, `[laughing nervously]` | Accelerate `5–8%` (`4.1–4.3 wps`), trim all pauses to `<0.06 s`. |
| **Beat 6 — Final Callback Punchline** | Dry, abrupt, zero-outro mic-drop | `[deadpan]`, `[amused]` | Land the final syllable firmly downward and **hard-cut the video `<0.08 s` later** for seamless looping. |

### B. Punctuation Hacks That Control Any TTS Engine (Even Without Stage Tags)
- **Short choppy sentences beat long clauses**: Break 28-word sentences into `6–11 word` staccato units—neural TTS places stronger natural stress on shorter clauses.
- **Em-dash (`—`) vs. Ellipsis (`...`)**: Use `—` for an abrupt interruption (`0.12 s` pause); avoid `...` unless you deliberately want a `0.40 s` horror pause (which otherwise wastes `<45s` budget).
- **Phonetic Spelling for Weird Nouns/Numbers**: Spell out tricky acronyms, foreign names, or dates phonetically in the TTS input string (`"eighteen eighty"`, `"one hundred Robux"`, `"Koo-ree"`), while keeping the clean spelling in your subtitle script!

---

## 3. Multi-Character Dialogue Casting & Acoustic Separation

When a story includes multiple characters (e.g., Roblox Storytime cast: *Alex, Noob, Dad/Principal, Rich Kid, Hacker, Maya* — see [[Roblox R6 Story Cast & Marketplace Character Factory (Blender 5.3)]]), listeners must identify **who is speaking in `<0.3 seconds` with their eyes closed**:

| Cast Archetype | Pitch / Formant Target | Speaking Pace | Acoustic EQ Signature |
| :--- | :--- | :--- | :--- |
| **Main Protagonist / Narrator** | Natural mid-range, clear diction, friendly-dry | `3.7–4.0 wps` | Full broadcast presence (`3.2 kHz +2.5 dB`) |
| **Goofy Best Friend (Noob)** | Slightly higher pitch (`+1.5 to +2.5 semitones`), energetic inflection | `4.0–4.4 wps` | Bright crisp upper-mid (`4.5 kHz +2 dB`) |
| **Authority (Dad / Teacher / Admin)** | Deeper chest resonance (`-2 to -3 semitones`), clipped consonants | `3.3–3.6 wps` | Warm chest body (`160–220 Hz +2 dB`) |
| **Rival / Rich Kid / Karen** | Smug drawl or sharp staccato emphasis | `3.5–3.8 wps` | Crisp upper sheen (`5–7 kHz +2 dB`) |
| **Hacker / Radio / Intercom / Bot** | Filtered bandpass (`350 Hz – 3.2 kHz`) + subtle bitcrush/distortion | Staccato `3.4 wps` | FFmpeg `highpass=f=380,lowpass=f=3200,acompressor` |

> [!TIP] The Zero-Gap Dialogue Overlap Law
> In real comedy and animation, Character B starts speaking **`2–4 frames` (`66–133 ms`) BEFORE** Character A's final reverb tail finishes. Overlapping lines slightly makes dialogue feel alive and slashes dead air automatically.

---

## 4. Broadcast Vocal Processing Chain (FFmpeg & SoundCraft)

Raw TTS or home-mic audio sounds thin on phone speakers or boomy on headphones. Always run voiceover through this **6-stage broadcast vocal chain** BEFORE mixing with music and SFX:

1. **Zero Dead-Air Breath & Silence Trim**: Collapse every internal pause `>0.16 s` down to `0.08–0.12 s` (except intentional horror/comedy beats) and strip leading silence (`t = 0.00 s` speech start!).
2. **High-Pass Rumble Cut (`85 Hz`)**: Removes sub-bass desk thumps and plosive mud that fight your `60–80 Hz` SFX sub-hits.
3. **Boxiness / Mud Dip (`250 Hz`, `-2.5 dB`, `Q = 1.4`)**: Clears woolliness so voice sounds expensive and close-mic'd.
4. **Presence & Intelligibility Boost (`3,200 Hz`, `+2.5 dB`, `Q = 1.2`)**: Makes consonants cut cleanly through tiny smartphone speakers at 40% volume.
5. **De-Ess & Smooth Air (`6,800 Hz`, `-2.0 dB`, `Q = 2.0` + `11,000 Hz`, `+1.2 dB` shelf)**: Tames harsh `"s"/"t"` sibilance while keeping crisp sheen.
6. **Consistent Vocal Compression (`3:1` ratio) + `-14.0 LUFS` Loudnorm (`TP = -1.0 dBTP`)**: Locks every syllable at uniform forward volume.

### Copy-Paste Production FFmpeg Broadcast Voice Command
```powershell
ffmpeg -y -i voice_raw.wav `
  -af "silenceremove=start_periods=1:start_silence=0.02:start_threshold=-42dB,highpass=f=85,equalizer=f=250:t=q:w=1.4:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=6800:t=q:w=2.0:g=-2.0,treble=g=1.2:f=11000,acompressor=threshold=-18dB:ratio=3:attack=8:release=110:makeup=2,loudnorm=I=-14:TP=-1.0:LRA=5" `
  -ar 48000 -ac 2 voice_master.wav
```

---

## 5. Word-Level Timing, Subtitles & 2-Frame Lip-Sync Pipeline

1. **Generate Master Voice FIRST**: Never animate timings from word-count guesses. Lock `voice_master.wav` first so the entire timeline conforms to real milliseconds.
2. **Extract Exact Word Timestamps (`words.json`)**:
   - Run `faster-whisper` (via `tools/timing.py`) or Fish Audio `transcribe-1-pro` to produce `{ "word": "...", "start": 0.42, "end": 0.68 }` for every single spoken word.
3. **Drive 3 Systems Simultaneously From One `words.json`**:
   - **Subtitles**: Group into `2–4` word black-pill pages (`[[04 Next-Generation Retention, Subtitles & Audio Spec]]`) with exact active-word highlight frame.
   - **2-Frame Reaction Lead (Law 15)**: Trigger character expression swaps (`brows='v'`, `mouth='o'`, shock zoom) at `word.start - 0.067s` (`2 frames` early) so the character reacts right before the syllable lands.
   - **Amplitude-Gated Mouth Animation**: Sample `voice_master.wav` RMS energy in `33.3 ms` frame buckets (`30 fps`):
     - `RMS < -38 dB` → `'closed'` / resting expression (`line` / `smirk`)
     - `-38 dB ≤ RMS < -22 dB` → `'mid'` vowel shape
     - `RMS ≥ -22 dB` (or stressed open vowels `A/O/E`) → `'open'` / `'o'` shape, clamped to `10–12 Hz` max mouth-swap rate so lips never buzz!

## Related Vault Guides
- [[01 Voiceover & Word-Level Timing (ElevenLabs + Whisper + DP)]]
- [[Music Scoring, Dynamic Ducking, Mastering & Copyright Safety Bible]]
- [[SFX Direction & The 2-4 Frame Lead-In Law]]
- [[04 Next-Generation Retention, Subtitles & Audio Spec]]
