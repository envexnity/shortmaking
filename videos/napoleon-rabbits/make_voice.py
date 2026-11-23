"""Generate per-beat ElevenLabs TTS (Daniel - Steady Broadcaster), trim silence, join with tight gaps, write voice_raw.wav + beats.json."""
import json
import os
import re
import shutil
import subprocess
import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE_ID = "onwK4e9ZLuTAKqWW03F9"  # Daniel - Steady Broadcaster (British deadpan)
MODEL_ID = "eleven_turbo_v2_5"
SR = 48000
GAP = 0.08          # tight gap between beats (s)
HEAD = 0.16         # lead-in before first word
TAIL = 0.55         # short landing after last word

with open(os.path.join(HERE, "SCRIPT.md"), encoding="utf-8") as f:
    raw_lines = f.readlines()

in_beats = False
beats = []
for line in raw_lines:
    s = line.strip()
    if s.startswith("## Beats"):
        in_beats = True
        continue
    if in_beats:
        m = re.match(r"^\d+\.\s+(.*)$", s)
        if m:
            beats.append(m.group(1))


def synth_elevenlabs(text: str, out_mp3: str):
    exe = shutil.which("elevenlabs") or shutil.which("elevenlabs.cmd") or "elevenlabs.cmd"
    cmd = [
        exe, "text-to-speech", "convert",
        "--voice-id", VOICE_ID,
        "--model-id", MODEL_ID,
        "--text", text,
        "--output-format", "mp3_44100_128",
        "--voice-settings.speed", "1.12",
        "--voice-settings.stability", "0.42",
        "--voice-settings.similarity-boost", "0.80",
        "--voice-settings.style", "0.20",
        "--voice-settings.use-speaker-boost", "true",
        "-o", out_mp3,
    ]
    subprocess.run(cmd, check=True)


def trim_and_tighten(x: np.ndarray, max_gap: float = 0.20, keep_gap: float = 0.11, thr: float = 0.012) -> np.ndarray:
    a = np.abs(x)
    win = int(SR * 0.012)
    env = np.convolve(a, np.ones(win) / win, mode="same")
    speech = env > thr
    pad = int(SR * 0.04)
    speech = np.convolve(speech.astype(int), np.ones(2 * pad + 1, dtype=int), mode="same") > 0
    parts, i, n = [], 0, len(x)
    while i < n:
        if speech[i]:
            j = i
            while j < n and speech[j]:
                j += 1
            parts.append(x[i:j])
            i = j
        else:
            j = i
            while j < n and not speech[j]:
                j += 1
            dur = (j - i) / SR
            if i == 0 or j == n:
                pass
            elif dur > max_gap:
                h = int(SR * keep_gap) // 2
                parts.append(x[i:i + h])
                parts.append(x[j - h:j])
            else:
                parts.append(x[i:j])
            i = j
    if not parts:
        return x
    y = np.concatenate(parts)
    fi = min(int(SR * 0.008), len(y) // 4)
    if fi > 1:
        y[:fi] *= np.linspace(0.0, 1.0, fi)
        y[-fi:] *= np.linspace(1.0, 0.0, fi)
    return y


def main():
    vdir = os.path.join(HERE, "voice")
    os.makedirs(vdir, exist_ok=True)
    out = [np.zeros(int(SR * HEAD), np.float32)]
    t = HEAD
    info = []
    for i, b in enumerate(beats):
        mp3 = os.path.join(vdir, f"b{i:02d}.mp3")
        wav = os.path.join(vdir, f"b{i:02d}.wav")
        synth_elevenlabs(b, mp3)
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), wav],
            check=True,
        )
        sr, x = wavfile.read(wav)
        x = x.astype(np.float32) / 32768.0
        x = trim_and_tighten(x)
        # Custom slightly longer comedic pause after "And lost." and before "And the man..."
        gap = GAP
        if i == 1:
            gap = 0.14
        elif i == 13:
            gap = 0.12
        elif i == len(beats) - 1:
            gap = TAIL
        info.append({
            "i": i,
            "text": b,
            "start": round(t, 3),
            "end": round(t + len(x) / SR, 3),
        })
        out.append(x)
        t += len(x) / SR
        out.append(np.zeros(int(SR * gap), np.float32))
        t += gap

    y = np.concatenate(out)
    unmastered = os.path.join(vdir, "voice_unmastered.wav")
    raw_wav = os.path.join(vdir, "voice_raw.wav")
    wavfile.write(unmastered, SR, (np.clip(y, -1, 1) * 32767).astype(np.int16))
    af = (
        "highpass=f=85,"
        "equalizer=f=150:width_type=o:width=1.2:g=1.2,"
        "equalizer=f=2900:width_type=o:width=1.3:g=2.0,"
        "equalizer=f=6800:width_type=o:width=1.0:g=-1.0,"
        "acompressor=threshold=-17dB:ratio=2.3:attack=10:release=130:makeup=2.0,"
        "alimiter=limit=0.92"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", unmastered, "-af", af, "-ar", str(SR), "-ac", "1", raw_wav],
        check=True,
    )
    with open(os.path.join(HERE, "beats.json"), "w", encoding="utf-8") as f:
        json.dump({"total": round(len(y) / SR, 3), "beats": info}, f, indent=1)
    for b in info:
        print(f'{b["start"]:6.2f} {b["end"]:6.2f}  {b["text"]}')
    print("total", round(len(y) / SR, 3), "s")


if __name__ == "__main__":
    main()
