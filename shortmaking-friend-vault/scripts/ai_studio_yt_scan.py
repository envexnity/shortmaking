"""Connect to Google AI Studio (Gemini API) to analyze YouTube channel performance
and write actionable recommendations for the next day's pixel countryball Shorts.

Usage:
    python scripts/ai_studio_yt_scan.py --input scripts/yt_snapshot.json \
        --out "10 Ideation & Research/ai_studio_yt_insights.md"
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "10 Ideation & Research" / "ai_studio_yt_insights.md"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-4-hydrogen"


def call_google_ai_studio(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Call Google AI Studio generateContent REST endpoint using GOOGLE_API_KEY."""
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY / GEMINI_API_KEY in environment.")

    url = f"{API_BASE}/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 4096},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Google AI Studio HTTP {exc.code}: {body}") from exc

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"No candidates returned from Google AI Studio: {data}")
    parts = candidates[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts).strip()


def build_prompt(snapshot: dict) -> str:
    """Construct the performance-audit prompt for Google AI Studio."""
    return (
        "You are an expert YouTube Shorts growth strategist and animated countryball "
        "showrunner. Analyze the following YouTube channel snapshot and recent video "
        "performance metrics for our channel.\n\n"
        "Channel & Video Data (JSON):\n"
        f"```json\n{json.dumps(snapshot, indent=2, ensure_ascii=False)}\n```\n\n"
        "Deliver a crisp, actionable Markdown report with these exact sections:\n"
        "1. **Top Performers vs Underperformers** — what topics, title patterns, "
        "hooks, and durations are winning vs losing.\n"
        "2. **Pixel Countryball Content & Retention Upgrades** — concrete changes to "
        "pacing, visual gags, camera motion, subtitles, and audio/SFX for our 8-bit "
        "pixel countryball Shorts (`scripts/pixel_short_kit/`).\n"
        "3. **Title, Hook & Packaging Rules for Tomorrow** — exact title formulas, "
        "emoji/hashtag usage, and 1-sentence paradox hooks.\n"
        "4. **2 Specific Pixel Countryball Video Ideas for 04:00 AM Generation** — "
        "each with working title, 1-sentence paradox hook, countryball cast, and "
        "why it will beat our current median views.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Google AI Studio YouTube Performance Scanner")
    parser.add_argument("--input", required=True, help="Path to JSON snapshot from YouTube MCP")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output Markdown insights path")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini model ID")
    args = parser.parse_args()

    snapshot = json.loads(Path(args.input).read_text(encoding="utf-8"))
    analysis = call_google_ai_studio(build_prompt(snapshot), model=args.model)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = (
        f"# Google AI Studio YouTube Performance Insights\n\n"
        f"- **Updated:** {stamp}\n"
        f"- **Model:** `{args.model}`\n\n---\n\n"
    )
    out_path.write_text(header + analysis + "\n", encoding="utf-8")
    print(f"Wrote insights to {out_path}")


if __name__ == "__main__":
    main()
