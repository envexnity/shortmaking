---
title: Openverse API, Real-Sound & Earshot MCP Pipeline
tags:
  - audio
  - earshot
  - openverse
  - real-sound
  - mcp
  - sfx
area: audio
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete technical guide to combining the Openverse CC0 Audio API, the vendored real-sound skill, and the Earshot MCP/Forge/Sheet audio intelligence toolkit.
---

# Openverse API, `real-sound` & `earshot` MCP Pipeline

> [!NOTE] Vendored Audio Skills
> - **`earshot` Skill**: `.agents/skills/earshot/SKILL.md` (`github.com/Leonxlnx/earshot`)
> - **`real-sound` Skill**: `.agents/skills/real-sound/SKILL.md` (with `mix.py`, `arrange.py`, `qa.py`, `audit.py`, `master.py`, `credits.py`, `mux.mjs`)

While [[Procedural Python Audio Synthesis (Music & SFX)]] synthesizes every sound from NumPy equations, **Track 4 (Realistic Blender 3D)**, **Bonus Track (Motion Graphics / EffectCraft)**, and **Roblox Shorts (Track 5)** often need either **verified real-world CC0 Foley** or **AI-measured transient alignment** so sounds never land late on a cut.

---

## 1. Openverse API — Zero-Key CC0 Sound Discovery

Openverse ([`api.openverse.org`](https://api.openverse.org/v1/)) indexes millions of Creative Commons audio recordings across Freesound, Wikimedia Commons, and Jamendo **with no API key required** for standard search queries.

### Querying CC0 Sound Effects Safely in Python
Filter by `license=cc0` (Public Domain Dedication) whenever you want **zero attribution requirements**:

```python
import urllib.request, urllib.parse, json, os

def search_openverse_sfx(query: str, license_filter="cc0", limit=5):
    params = urllib.parse.urlencode({
        "q": query,
        "license": license_filter,
        "page_size": limit,
    })
    url = f"https://api.openverse.org/v1/audio/?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "ShortmakingStudio/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    results = []
    for item in data.get("results", []):
        results.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "duration_ms": item.get("duration"),
            "license": item.get("license"),
            "audio_url": item.get("url"),
            "creator": item.get("creator"),
        })
    return results

# Example: Search CC0 crisp air whooshes & whistle sounds
for hit in search_openverse_sfx("whoosh swoosh"):
    print(hit["title"], "|", hit["duration_ms"], "ms |", hit["audio_url"])
```

> [!TIP] Combining Openverse + `earshot find`
> Many CC0 Freesound clips contain 5–10 consecutive takes in one 20-second file. Download the clip, then run `earshot find clip.ogg "a single crisp fast air whoosh" --top 3` to extract the exact clean millisecond trim (`start..end`) with `head / tail <= -30 dB`!

---

## 2. `earshot` — Giving AI Agents "Ears" (CPU-Only CLI + MCP)

### A. Installation & MCP Setup (Windows)
Prerequisites: **Python 3.10+** and **ffmpeg / ffprobe** on `PATH`.

```powershell
# Quick install via uv or clone into your tools directory:
git clone https://github.com/Leonxlnx/earshot C:\Tools\earshot
cd C:\Tools\earshot
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -e ".[mcp,llm,dev]"
.\.venv\Scripts\python.exe -m earshot doctor --load
```

Add `earshot` to `.mcp.json` / `mcp_config.json` so models stay warm across calls (instead of reloading for 20–40s per CLI invocation):
```json
{
  "mcpServers": {
    "earshot": {
      "command": "C:\\Tools\\earshot\\.venv\\Scripts\\python.exe",
      "args": ["-m", "earshot", "mcp"],
      "env": {
        "EARSHOT_THREADS": "3"
      }
    }
  }
}
```

### B. The 5 Core `earshot` Agent Loops
| Loop | Command / MCP Tool | What It Solves |
| :--- | :--- | :--- |
| **1. Pick & Trim Real SFX** | `earshot rank`, `earshot find`, `earshot describe`, `earshot realness` | Ranks candidate downloads by CLAP z-score (`z ≥ 3.0`), extracts non-clipped single hits (`stroke` / `event`), and checks `p_real`. |
| **2. Visual Sync Review** | `earshot timeline film.mp4 --cues cues.json` & `earshot sheet film.mp4 -o sheet.png` | Generates an **annotated PNG strip** showing video frames, spectrogram, loudness, and **color-coded sync markers** (`green` ≤ 1 frame, `amber` ≤ 100ms, `red` = missing). |
| **3. Launch Film Scorecard** | `earshot critique film.mp4` | Scores LUFS, true peak, LRA, spectral balance, and cut-sync percentage against a profile of 7 pro launch films, printing timestamped `FIX FIRST` rows. |
| **4. Audio-to-Code (`fit`) & Code Synth (`forge`)** | `earshot fit clip.wav -o recipe.py` & `earshot forge whoosh --refset whoosh_fast` | Reverse-engineers any recorded sound into a tunable physical-synthesis Python script (`earshot.forge.dsp`), or evolves new sounds measured against reference sets. |
| **5. Instant 252-Sound Bank (`kit`)** | `earshot kit init --preset launch -o audio/kit.json` → `earshot kit render` → `earshot kit check` | Renders a complete sound kit (`ui_pop`, `knock`, `cut_hit`, `mallet`, `shutter`, `reverse_swell`, `riser`) automatically ducked and leveled (`3–10 dB`) over the music bed. |

---

## 3. `real-sound` Skill (10-Step Real-Recording Pipeline)

Whenever your project asks for **100% real recorded Foley + licensed music** (zero synthesized sounds), follow `.agents/skills/real-sound/SKILL.md`:
1. Export frame-accurate cue timestamps to `out/cues.json`.
2. Source candidate recordings from Openverse / Freesound / Mixkit and gate every trim with `earshot realness`.
3. Run `scripts/audit.py` to block forbidden licences (`NC`, `ND`, `SA`) and allow `CC0`, `CC BY`, and `Mixkit`.
4. Edit the music bar-grid with `scripts/arrange.py` so the drop downbeat lands on your hero reveal frame.
5. Render and master via `scripts/mix.py` + `scripts/master.py` (`-14.0 LUFS`, `≤ -1.0 dBTP`), inspect with `scripts/qa.py --listen --video out/film.mp4`, generate `CREDITS.md`, and mux with `scripts/mux.mjs`.
