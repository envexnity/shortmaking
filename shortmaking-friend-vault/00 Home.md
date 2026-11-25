---
title: Shortmaking Engineering Vault — Home
tags:
  - moc
  - dashboard
  - shortmaking
  - animation
  - remotion
  - threejs
  - blender
  - roblox
area: overview
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-21
summary: Master dashboard and architectural command center for building viral short-form animated videos from scratch across 2D-in-3D Toon, Low-Poly 3D, Realistic/Stylized Blender 5.3 3D, Roblox R6/R15, Undershine 3D Pixel Art, and Kinetic Motion Graphics.
---

# Shortmaking Engineering Vault — Viral Animated Shorts from Scratch

> [!IMPORTANT] AI Agent Entrypoint
> If you are an AI agent (Claude Code, Antigravity, Cursor, Codex), **read [[AGENTS]] first**. It defines the progressive disclosure routing table, the **25 Hard Rules of Viral Animated Shorts**, and the exact pipeline contracts for every art style in this vault.

Welcome to the **Shortmaking Studio Vault**. This vault is a complete, reverse-engineered production system built from a **32,000-frame, 30fps technical study of 20 viral animated shorts**, four creator pipeline teardowns (`mr miro`, `Mr omi`, `Grow With Kaz`, `AI Playbook`), and a full suite of local MCP servers and vendored skills.

> [!TIP] Completed Videos Gallery
> - **Master Showcase**: [[00 Completed Videos]]
> - **⭐ Prime Track 5 (9:16 Roblox Studio R15)**: [[Bun Town Burger Wrapper - Prime Roblox Video Example]] (`videos/roblox-reel-Df1kubCJ-o0-v2/out/final.mp4`, `98.033 s`, `-14.7 LUFS`)
> - **Video 1 (9:16 Low-Poly 3D)**: [[Emu War (1932) - Completed Video]] (`videos/emu-war/out/emu-war.mp4`, `56.10 s`)
> - **Video 2 (16:9 Orbit 2D Space)**: [[Mars - What Would Kill You First (Completed Video)]] (`videos/mars-orbit/out/mars_final.mp4`, `144.45 s`)

---

## 1. Choose Your Art Style & Engine Track

Every viral animated short in this vault runs on one of **6 deterministic code-driven or MCP-driven engines**:

| Track | Art Style | Primary Engine & Skill | Pacing / WPS | Best Niches | Master Guide |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Track 1** | **2D-in-3D Toon Story** (Flat 2D bean-head cards in inked 3D worlds) | **Remotion 4 + Three.js r169** (`.agents/skills/cartoon-3d-short`) | `3.5–4.1 wps` (median `3.7`) | History, Military Fails, Engineering Disasters, Bizarre True Stories | [[Style 1 - 2D-in-3D Toon World (Remotion + Three.js)]] |
| **Track 2** | **Standalone 2D-in-3D Toon** (Zero-React headless browser pipeline) | **Playwright + Three.js + Python Audio** (`.agents/skills/cartoon-audio-short`) | `~3.2–3.7 wps` | Emotional Storytime (Hachiko, 1918 Pigeon), Historical Anecdotes | [[Style 2 - Standalone 2D-in-3D Kit (Playwright + Three.js, No Remotion)]] |
| **Track 3** | **Low-Poly Flat-Shaded 3D Explainer** (Blocky 3D + Glass HUD overlays) | **KAZ Studio (`kit.js` + Three.js r160)** (`.agents/skills/make-3d-video`) | `~2.6 wps` (`timing.py`) | Science ("Why You Forget Dreams"), History ("Road to WW2"), What-If ("Two Moons") | [[Style 3 - Low-Poly Flat-Shaded 3D (Kaz Studio Kit)]] |
| **Track 4** | **Realistic & Stylized 3D** (Zack D. Films / Fern / Diorama style) | **Blender 5.3 (`CYCLES` OptiX / `BLENDER_EEVEE`) + `blender_cinema_lib.py` + `cook`** | `3.3–3.8 wps` | Medical/Anatomy Cross-Sections, Crime/Forensic Reconstructions, How-It-Works | [[Style 4 - Realistic & Stylized 3D in Blender (Blender MCP + Cook)]] |
| **Track 5** | **Roblox Animated Shorts** (R6/R15 Storytime, Noob-vs-Pro, Game Trailers) | **Ropilot MCP + ForgeGUI + Blender 5.3 R6/R15** (`ropilot` + `forge-gui` + `blender-cinema-kit`) | `3.8–4.3 wps` | Roblox Storytime, "Noob to Pro" Retention Edits, VFX Showcases | [[Style 5 - Roblox Animated Shorts (Ropilot + ForgeGUI + Blender R6-R15)]] |
| **Track 6** | **Orbit 2D Space Survival Explainer** (Tiny `YOU` + Animated Gauges + X-Rays + NASA Photos) | **Orbit 2D Canvas Kit + Playwright + NASA Image API** (`.agents/skills/orbit-space-video`) | `~2.5–2.8 wps` | "What Would Kill You First On [Planet]?", Space Survival, Cosmic Scale | [[Style 6 - 2D Space Survival Explainer (Orbit 2D Kit + NASA API)]] |
| **Track 7** | **Undershine 3D Pixel Art** (Atmospheric 3D shadows, hue-shifted lighting, Ghibli foliage & 8-angle cinema) | **Blender 5.3 `BLENDER_EEVEE` + `undershine-blender-pixel-kit`** (`blender_pixel_lib.py` + `pixel_postprocess.py`) | `3.2–3.8 wps` | Atmospheric Stories, Fantasy/History Mysteries, Cozy-Moody Visual Explainers | [[Style 7 - Undershine 3D Pixel Art in Blender (EEVEE Next + Multi-Angle)]] |

---

## 2. Vault Architecture & Map of Content

### 🧠 `10 Ideation & Research` (Powered by `/deepresearchagent`)
- [[Deep Research - Undershine 3D Pixel Art, Atmospheric Shadows & Multi-Angle Blender Cinematography]] — Reverse-engineering `@playundershine` (*UNDERSHINE*), `t3ssel8r`, *A Short Hike*, HD-2D, Blender 4.2 EEVEE Next hue-shifted shaders, Ghibli foliage normals, screen-space Depth/Normal outlines, and the 8-Camera Multi-Angle Cinematography Matrix.
- [[Deep Research - Masterclass on Story Writing, Animation Layout & Comedy Science]] — **120-Source Master Synthesis** unifying narrative causality, 2D/3D animation layout, and the cognitive science of comedy into one production matrix.
- [[Deep Research - How to Write & Tell Stories (Narrative Architecture Bible)]] — How humans write and tell stories: Parker/Stone `"Therefore / But"`, McKee's `"Gap"`, Swain's `Scene & Sequel`, Harmon/Snyder/Truby/Kishōtenketsu, Vonnegut/Reagan 6 Arcs, Hasson fMRI neural coupling, Zak oxytocin/cortisol, and Provost syntax.
- [[Deep Research - How Humans Write Funny Jokes & Comedy Engineering]] — How humans write funny jokes: Benign Violation Theory (McGraw/Warren), Incongruity-Resolution (Suls), GTVH (Raskin/Attardo), Bisociation (Koestler), Greg Dean's 2-Story Connector, Vorhaus's `Truth + Pain` & `Rule of Nine`, Dikkers' 11 Funny Filters, Westbury's plosive phonetics, and Chuck Jones / Edgar Wright visual comedy.
- [[Deep Research - Viral Short Ideation]] — Full 5-phase research synthesis: outlier mining, curiosity-gap neuroscience, retention benchmarks (`>78%` Viewed-vs-Swiped-Away), and cross-niche viral mechanics.
- [[Deep Research - Viral Shortform Hooks, Storytelling & 1M+ Algorithm]] — 73-source study on `<1.5s` survival gate, Paradox & `"In this world..."` hooks, circular loops (`>100%` APV), Zeigarnik/RPE psychology, and 1M+ YT/TikTok/IG signals.
- [[Deep Research - Viral Shortform Visuals, Subtitles, Motion, VFX & SFX]] — 90-source engineering study on kinetic subtitles (`easeOutBack`, `9:16` safe zones), `1.5–3s` pattern interrupts, VFX/bloom/CA, and 4-layer `-14 LUFS` SFX mixing.
- [[The 1-Sentence Paradox Hook Formula]] — How 20/20 reference shorts open with an impossible contradiction stated as plain fact in `10–16 words`.
- [[Script Architecture - 3.7 WPS & The 'You See' Pivot]] — The 6-beat narrative spine, `"Luckily... / Unluckily..."` deadpan double-lines, and the `"You see,"` everyday analogy pivot.
- [[50 Plug-and-Play Viral Video Ideas (All Styles)]] — 50 production-ready video briefs with titles, paradox hooks, visual Frame-0 designs, and twist payoffs across all 6 styles.
- [[Reference Channels & Outlier Matrix]] — Breakdown of *Nutshell Animations*, *Zack D. Films*, *Fern*, *Hoog*, *Brew*, *Kurzgesagt*, *Mr omi*, *mr miro*, *Grow With Kaz*, *AI Playbook*, *Xenost*, and *AIpreneur*.

### 🔬 `20 Reference Teardowns` (All 16 Reference Videos)
- [[Video 1 Teardown - Claude Free vs 20 vs 200 (mr miro)]] — `youtu.be/zGVQt4xoZAM` — Same Napoleon vs. Rabbits prompt across Free Sonnet, $20 Pro Opus, and $200 Max Fable/Opus; exact token economics & why the Skill beats model tier.
- [[Video 2 Teardown - Viral 2D-in-3D Shorts Workflow (Mr omi)]] — `youtu.be/OtbLL6OBNE4` — 20-short 30fps study, *The Bridge That Fell for a Song* (`1880s` Broughton Bridge resonance), and the 12-agent look-match architecture.
- [[Video 3 Teardown - Low-Poly 3D Explainers & Kaz Plugin (Grow With Kaz)]] — `youtu.be/46C6qLvTjnU` — Science, History, and What-If low-poly 3D explainers using the `3d-kaz.plugin` (`make-3d-video`).
- [[Video 4 Teardown - One Story to Full Animated Video (AI Playbook)]] — `youtu.be/W3q1_MpWkok` — *1918 WWI Pigeon* & *Hachiko (10 Years at Shibuya)* built end-to-end with `cartoon-audio-short`.
- [[Video 5 Teardown - Serialized 2D Storytime & Emotional Twist (Kacaurus)]] — `youtube.com/shorts/EH2Zoi1hxDc` (`821K+ views`, `89s`) — Serialized 3-part narrative arc (`Bagian 1/3 → 3/3`), diegetic whistle audio pivot, and prop-clue double twist (*missing heart drawing*).
- [[Video 6 Teardown - Free Audio AI Tools - Openverse API & Earshot (Rakhul Karthick)]] — `youtube.com/shorts/2yNiLmpbHl4` — Fixing generic AI SFX using zero-key **Openverse CC0 API**, **`real-sound` skill**, and **Earshot MCP / Forge / Sheet**.
- [[Video 7 Teardown - 3D Motion Graphics With Claude & Google Flow (AIpreneur)]] — `youtu.be/t9MFvSJHLsI` (`182K+` views) — Zero-AE 3D motion graphics via Claude beat table, 1 anchor style image, Google Flow 6s clips, ElevenLabs VO, and CapCut paper fades + typography.
- [[Video 8 Teardown - Orbit 2D Space Survival (Money Mastery Hub)]] — `youtu.be/ziyWYLrvYaU` — *"Depth Theory moved to Space"* (`orbit-space-video`): 4 script rules, tiny 2D `YOU` astronaut, animated gauges/X-rays, dry humor receipts, real NASA API photos, and 3 stills QA rules.
- [[Video 9 Teardown - How to Make Shorts That Go Viral Every Time (Logan Smith)]] — `youtu.be/gEQ0BLyVJhY` (`3.05M` views) — Hook-Plot-Climax (HPC) framework, delayed payoff, and `1×/day` upload cadence.
- [[Video 10 Teardown - How to Create Irresistible Hooks (Kallaway)]] — `youtu.be/LmXpbP7dD48` (`893K` views) — 3-step Context Lean → Scroll-Stop → Contrarian Snapback, `3–5` word visual hooks, and `<4s` speed to value.
- [[Video 11 Teardown - I Studied 100+ Hooks, This Strategy Will Make You Go Viral (Jade Beason)]] — `youtu.be/dNT7gd3ulAg` (`70K` views) — 3-element hook moment, zero Millennial Pause, and word-by-word captions.
- [[Video 12 Teardown - Give Me 15 Mins, and I'll Make Your Hooks Impossible to Skip (Kallaway)]] — `youtu.be/2byPP_9F0-Q` (`1.18M` views) — 4 Hook Mistakes (Delay, Confusion, Irrelevance, Disinterest) and Stated vs. Implied A-vs-B contrast.
- [[Video 13 Teardown - How to Make Viral YouTube Shorts Captions in One Click (Thomas Creates)]] — `youtu.be/8sb2R11FeVw` (`14.3K` views) — 1-click word-level sync, keyword highlighting, and brand templates.
- [[Video 14 Teardown - 10 Must-Know Short-Form Content Creators (Ben Kaluza)]] — `youtu.be/6US1-_bBS28` (`9.1K` views) — Next-5 funnel, reading score `4–5`, eye-level cut continuity, and remaking past winners.
- [[Video 15 Teardown - Ultimate Guide to Editing Short-Form Content in 2026 (Joseph Video Editing)]] — `youtu.be/ds7DDgGgiVs` (`100K` views) — 7-phase Premiere pipeline: J-cuts, Metropolis 1-word pop-ups, orange glow, blurred zoom-outs, and `100→115%` push-ins.
- [[Video 16 Teardown - The Most Popular Sound Effects for Editing 1240+ (Render Queue)]] — `youtu.be/nbwQWTR0SV4` (`770K` views) — 5-bucket SFX taxonomy for high-retention edits.

### 🎨 `30 Art Styles & Engines`
- [[Style 1 - 2D-in-3D Toon World (Remotion + Three.js)]]
- [[Style 2 - Standalone 2D-in-3D Kit (Playwright + Three.js, No Remotion)]]
- [[Style 3 - Low-Poly Flat-Shaded 3D (Kaz Studio Kit)]]
- [[Style 4 - Realistic & Stylized 3D in Blender (Blender MCP + Cook)]]
- [[Style 5 - Roblox Animated Shorts (Ropilot + ForgeGUI + Blender R6-R15)]]
- [[Roblox R6 Story Cast & Marketplace Character Factory (Blender 5.3)]] — 8 fully rigged Roblox R6 storytime characters (`Alex`, `Noob`, `Rich Kid Dominus`, `Maya`, `Dad/Principal`, `Hacker`, `Admin Boss`, `Chloe`) built on Aeresei's IK+FK Rig V2.22 + 50 real Roblox Marketplace assets, packed `.blend` library, and automated factory scripts (`assets/roblox-r6-characters/`).
- [[In This World Roblox Storytime - Editing, Zooms & VFX Bible]] — Exact `"In this world..."` 3-step hook, punch-in/zoom-out camera grammar, glow/CA/speed-line VFX stack, kinetic subtitles, and 5-layer SFX mix.
- [[Style 6 - 2D Space Survival Explainer (Orbit 2D Kit + NASA API)]]
- [[Style 7 - Undershine 3D Pixel Art in Blender (EEVEE Next + Multi-Angle)]] — Atmospheric, non-arcady `@playundershine`-style 3D-to-pixel-art in Blender 5.3 EEVEE (`270×480` 4× integer scale, real directional shadows, hue-shifted lighting, `t3ssel8r` Normal/Depth outlines & 8-camera switching).
- [[Non-3D Visual Styles Encyclopedia (2D Vector, Storytime Animatics, Documentary Collage, 8-Bit & ASCII Horror)]] — **10 Viral Non-3D Visual Styles**: Flat Vector (*Kurzgesagt*), Editorial Paper Collage (*Vox/Johnny Harris*), Hand-Drawn Animatics (*Jaiden/Kacaurus*), 8-Bit Canvas2D, Terminal ASCII/VHS Horror, Stick-Figure Comedy, UI-Native Storytelling, Comic Halftone, and Data Journalism.
- [[Bonus Track - Kinetic Typography & Motion Graphics (Remotion + EffectCraft + GSAP)]] — Production engineering bible with 5-layer motion stacks, Remotion/GSAP spring physics, ArtCraft 2D MCP pipeline (`VectorCraft` → `FigCraft`/`DesignCraft` → `EffectCraft`), and deterministic Playwright capture.

### ⚙️ `40 Production Pipeline`
- [[04 Next-Generation Retention, Subtitles & Audio Spec]] — **MANDATORY NEXT-GEN DIRECTIVE**: Exact `8sb2R11FeVw` black-bg subtitle pills, minimal on-screen text, `~1 cut/sec` rapid camera/cut cadence, curated music pool — use only when fitting (`@r6rants`, `@Gneef`, `@RyexRBLX`, `@nitrogeniofalante` + atmospheric storytelling tracks), and `nbwQWTR0SV4`/CC0 SFX map.
- [[05 Editing Rhythm, Pre-Vis Animatics & Retention Graph Forensics]] — **Non-3D Editing & Retention Bible**: 2-minute Radio-Cut & Animatic gate, Walter Murch's Rule of Six re-weighted for `<45s` Shorts, 10 pattern-interrupt cut mechanics, and diagnostic repair tables for real retention curves.
- [[01 Voiceover & Word-Level Timing (ElevenLabs + Whisper + DP)]] — ElevenLabs settings, `faster-whisper` word alignment (`words.json`), and dynamic-programming pause detection (`timing.py`).
- [[02 Shot Planning & Camera Grammar]] — Hard cuts vs. `18–40f` smootherstep glides, `0.15–0.35%/f` hold creeps (`push()`), and `7f` sign-flipping impact `KICKS`.
- [[03 Rendering, Encoding & Disk Management]] — Rendering 2K vertical (`1440×2560`), bypassing the `60–110 GB` Remotion temp-bundle disk trap, and FFmpeg stream mapping.

### 📐 `50 Look & Craft Bible` (Measured from 32,000 Reference Frames)
- [[Color Psychology, Typography Pairing & Frame-0 Thumbnail Engineering]] — **Non-3D Visual Design Bible**: 60-30-10 value massing, 8 genre-locked hex palettes, mobile typography pairing (`≥7:1` contrast, `tabular-nums`), and 3-element Frame-0 / Thumbnail engineering (`200 px` Squint Test).
- [[Blender 5.3 Cinematic Rendering & Animation Mastery Bible]] — **Mandatory Blender 5.3.0 Look-Dev & API Bible**: verified 5.3 breaking API table (`BLENDER_EEVEE`, `compositor_effects`, `OutputFile`, Slotted Actions), RTX 2050 OptiX + OIDN GPU setup, `AgX` color management, Kelvin 3-point lighting, non-plastic procedural PBR, physical DOF + motion blur, and 3-gate pre-render verification.
- [[Deep Research - Animation Layout, Staging & Visual Composition]] — **Complete Animation Layout & Staging Bible**: Pixar's Rough/Final Layout pipeline, Stanchfield's Blackout Silhouette & 6 Deadly Tangents, Bruce Block's Contrast/Affinity & 4 Spaces, Mateu-Mestre's 3-Plane Value Massing, Hambidge's Dynamic Symmetry, Payne's 8 Stems, `9:16` Vertical Z-Stacking, and Walter Murch's Rule of Six.
- [[Characters - Bean Heads, Plum Ink & Stick Limbs]] — Superellipse math (`H/W = 0.94`), `#241726` plum ink, `3:1` variable stroke width, lidded eyes, and `4f` blink cycle.
- [[Outlines - Screen-Space Depth & Normal InkPass]] — Custom postprocessing `Pass` before DOF, `NOINK = 3` layer mask, and distance-scaled `5.1px → 2.2px` ink lines.
- [[Lighting - Two-Tone Shaders, Backlit Golden Hour & Contact Blobs]] — `onBeforeCompile` shadow capture, violet-blue golden-hour shadows (`B ratio 1.35–3.0x`), and `cardShade()` (`V ≥ 0.86`).
- [[Depth & Post - Thin-Lens DOF, Sky Gradients & Mipmap Bloom]] — `LensBlurEffect` (`cInf = 10–16px` on CU/MS), `BloomEffect`, and `NEUTRAL` tone mapping.
- [[Color Grade & Procedural Canvas2D Textures]] — 7-knot Hermite `GradeEffect`, 3-zone saturation/tint, and `planksHD` / `stoneHD` / `waterNear` Canvas2D generators.
- [[Readability Traps & Anti-Slop Rules]] — The 12 geometric traps that ruin AI-generated 3D shorts (and how to prevent every single one).

### 🔊 `60 Audio & SFX Engineering`
- [[Voice Acting, Expressive TTS Direction & Vocal Processing Bible]] — **Complete Voice & TTS Bible**: 4-tier auto-TTS priority (`Fish Audio S2.1-Pro` → `Kokoro-82M` → `Edge-TTS` → `Local OS`), inline emotion stage tags, multi-character vocal separation, 6-stage FFmpeg broadcast vocal chain, and word-level lip-sync.
- [[Music Scoring, Dynamic Ducking, Mastering & Copyright Safety Bible]] — **Music & Mastering Bible**: Genre BPM/harmonic scoring matrix, 3-act `<45s` score arc, `8f` pre-climax vacuum drop, 5-bus FFmpeg `sidechaincompress` + `2.4 kHz` vocal-pocket EQ filtergraph, and YouTube/TikTok/IG copyright safety tiers.
- [[Procedural Python Audio Synthesis (Music & SFX)]] — Synthesizing footsteps, wood creaks, snaps, splashes, whooshes, and background scores purely in Python/NumPy (`dsp.py`, `sfx_gen.py`, `music.py`).
- [[SFX Direction & The 2-4 Frame Lead-In Law]] — Acoustic layering (transient/body/weight/tail), pre-cut whoosh lead-ins, `-14 LUFS` loudness normalization, and `-6 dB` gated-RMS mixing.
- [[Openverse API, Real-Sound & Earshot MCP Pipeline]] — Combining zero-key **Openverse CC0** recordings, `.agents/skills/real-sound`, and **Earshot MCP** (`sheet`, `critique`, `forge`, `252`-sound `kit`).
- [[Reference Video Music & Audio Catalog]] — Extracted MP3 tracks + clean credited **LEMMINO** instrumental (`LEMMINO_ulfoU2MziOc.mp3`) from all 8 YouTube reference videos (`60 Audio & SFX Engineering/reference-music/`).

### 🤖 `70 Multi-Agent & QA Loop`
- [[The 12-Agent Look-Match & Sandbox Merge Architecture]] — Running 7 visual critics + 1 sound agent + 4 isolated file-owner build sandboxes (`cam`, `world`, `mat`, `char`) merged via `bridge_merge.py`.
- [[The Cook Loop for Autonomous Visual Polish]] — Running `.agents/skills/cook` for multi-hour iterative visual convergence against reference contact sheets.
- [[Automated Frame & Audio QA (short_qa.py)]] — Catching black frames, white flashes, frozen spans (`≥12f`), and audio clipping automatically.
- [[Post-Completion Visual QA — What, How & Why to Fix]] — Mandatory post-render visual inspection across all 5 styles: what defects to look for on contact sheets/stills, exact fixes, and why each fix protects retention.

### 🔌 `80 MCPs, Skills & Distribution`
- [[Token-Saving Vault Bridge]] — **Live 7-Layer Token-Guard & Ponytail 6×3 Bridge (`C:\Users\AFADAZIO\Obsidian\Token-Saving-Vault`)**: Verified `-47.0%` (standard) to `-64.3%` (`174,762` tokens saved on very hard 13-file systems repo, `20/20` checks) with `token-guard`, `context-diet`, `paleo-auto`, `shell_trim.py`, `token_audit.py`, and the 6×3 Ponytail situational auto-router.
- [[3D Master Vault Bridge (Blender 5.3, Three.js, ArtCraft MCPs & 24 Art Styles)]] — **Live Cross-Vault Bridge (`obsidian` MCP `vault: "3d-master"`)**: 24 3D art styles, **`threejs-devtools` MCP (69 live tools)**, all 10 newly wired ArtCraft MCPs (`materialcraft`, `texturecraft`, `vectorcraft`, `designcraft`, `figcraft`, `soundcraft`, `craft-anything`), `mesh_qa.py`, and 580 vendored GitHub 3D/Three.js skills.
- [[Complete Machine MCP & Skill Registry]] — Every MCP server (`blender`, `effectcraft`, `effectcraft-live`, `ropilot`, `forge-gui`, `figma`, `obsidian`, `windows-desktop`) and all **34 vendored skills** in `.agents/skills/`.
- [[ArtCraft Suite & MCP Directory (All 16 Crafting Apps)]] — Complete guide to all **16 open-source Rust ArtCraft MCPs** (`AniCraft`, `EffectCraft`, `FilmCraft`, `SoundCraft`, `TextureCraft`, `MaterialCraft`, `VectorCraft`, `FigCraft`, etc.) and local binaries.
- [[Online Skills & Community Repos Index]] — Direct links, install commands, and architectural comparisons of top open-source animation & audio skills (`Leonxlnx/earshot`, `storytold/artcraft`, Remotion, Blender, Manim).
- [[Channel Strategy, Series IP, Batch Ops & Monetization Playbook]] — Repeatable format IP, recurring cast franchises, weekly `5–7` short batch SOP, Shorts → Long-Form RPM compilation bridge (`20×–60×` RPM), and systematic A/B winner cloning.
- [[Uploading, Algorithm Packaging & Retention Optimization]] — YouTube Shorts, TikTok, and Reels packaging, Frame-0 thumbnail hooks, seamless loop seams, and retention diagnostics.

### 🧰 `90 Templates & Starter Kits`
- [[short-brief]] | [[script-template]] | [[storyboard-beat-sheet]] | [[sfx-cue-sheet]] | [[retention-postmortem-template]]
- Full runnable code kits located in `90 Templates & Starter Kits/`:
  - `cartoon-3d-short-kit/` (Remotion + Three.js + Python Audio + QA scripts)
  - `kaz-3d-studio-kit/` (`kit.js` + `render.js` + `timing.py` + 4 full example projects)
  - `cartoon-audio-short-kit/` (Standalone Playwright + Three.js + Roman Soldier example)
  - `orbit-2d-space-kit/` (2D Canvas Orbit Engine + `fetch_nasa.py` + `render.js`)
  - `blender-cinema-kit/` (`blender_cinema_lib.py` — Blender 5.3.0 Cycles OptiX / EEVEE RT, Kelvin 3-point rig, bounded fog, non-plastic PBR, Slotted Actions easing, multi-cam DOF & `compositor_effects`)
  - `undershine-blender-pixel-kit/` (Blender 5.3 EEVEE 3D-to-Pixel-Art library + `t3ssel8r` multi-pass post-processor + Multi-Angle camera engine)
  - `assets/roblox-r6-characters/` (Aeresei R6 IK+FK V2.22 source rig, 50 cached Roblox Marketplace assets, 8 rigged `.blend` story characters, `Roblox_R6_Story_Cast.blend` & automated factory scripts)

### 🚀 `100 Social Media & Auto-Publishing Vault` (Unified Distribution Module)
- **Master Distribution Hub**: [[00 Social Publishing Home]] | **Visual Pipeline**: [[Omnichannel Auto-Upload Pipeline.canvas]] | **Spec Matrix**: [[Platform Spec Matrix.base]]
- **Platform Playbooks (All Networks)**:
  - [[01 YouTube Shorts & Long-Form Master Guide]] — Engaged Views vs. Impressions, `Related Video` funnel bridge, title truncation, and 15-hashtag spam limit.
  - [[02 TikTok Algorithm, SEO & Publishing Guide]] — Point-weight FYP scoring, 4-layer TikTok Search SEO, and `<60s` velocity vs. `60s+` Creator Rewards RPM.
  - [[03 Instagram Reels, Trial Reels & Threads Guide]] — Sends per Reach (DM shares) ranking, Trial Reels non-follower testing, `3–5` hashtag cap, and `3:4` grid safe zones.
  - [[04 X (Twitter), Facebook Reels, LinkedIn, Snapchat & Reddit Guide]] — X Reply #1 link law (`+75x` author reply weight), Facebook Reels originality, LinkedIn video dwell time, and Reddit/Pinterest syndication.
- **Optimization & Automation Pillars**:
  - [[20 Description, Hashtag & SEO Optimization Bible]] — 3-Layer Multimodal SEO (ASR + OCR + NLP), platform hashtag counts, and pinned-comment loop multipliers.
  - [[30 Upload Timing, Cadence & Global Timezone Matrix]] — 90-minute pre-peak indexing law, `US EST` ↔ `UTC` ↔ `WIB UTC+7` posting matrix, and 45-minute `private` VP9 warm-up.
  - [[40 Automated Uploading Research & Full Engineering Architecture]] — 4-tier automation architecture: Official APIs (`YouTube v3`, `TikTok v2`, `IG Graph v21`, `X v2`), self-hosted **Postiz**, **Playwright / Patchright** stealth browsers, **Cloudflare R2** staging, and `scripts/omnichannel_publish.py`.
- **Ready-to-Publish Video Packages**: [[Upload Package - Emu War (1932)]] | [[Upload Package - Mars What Would Kill You First]]

---

## 3. Interactive Visual Canvas & Live Databases

- **Visual Architecture Flowcharts**:
  - Studio Production Graph: [[Shortmaking Master Pipeline.canvas]]
  - Omnichannel Auto-Upload Graph: [[Omnichannel Auto-Upload Pipeline.canvas]]
- **Live Omnichannel Upload Queue**:

![[Upload Queue & Tracker.base]]

- **Live Vault Index**:

![[Vault Index.base]]

- **Viral Idea Bank**:

![[Idea Bank.base]]
