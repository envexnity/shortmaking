"""Generate studio documentary narration via local Kokoro-82M (default), Gemini 2.5 Flash TTS, or Edge-TTS.

Outputs:
  - voice/voice_raw.wav  (48 kHz mono mastered vocal)
  - beats.json           (exact beat + word-level timestamps)
"""
import argparse
import asyncio
import base64
import json
import os
import re
import ssl
import subprocess
import urllib.request
import wave

import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
KOKORO_MODEL = os.path.join(REPO_ROOT, ".models", "kokoro", "kokoro-v1.0.onnx")
KOKORO_VOICES = os.path.join(REPO_ROOT, ".models", "kokoro", "voices-v1.0.bin")

SR = 48000
GAP = 0.16          # crisp narrative breath between beats
HEAD = 0.25         # short lead-in
TAIL = 1.0          # ring-out tail

KOKORO_PRESETS = {
    "orbit_us": {"blend": [("am_michael", 0.45), ("am_fenrir", 0.55)], "lang": "en-us", "speed": 1.03},
    "orbit_uk": {"blend": [("bm_lewis", 0.60), ("bm_george", 0.40)], "lang": "en-gb", "speed": 1.03},
    "fenrir": {"blend": [("am_fenrir", 1.0)], "lang": "en-us", "speed": 1.00},
    "michael": {"blend": [("am_michael", 1.0)], "lang": "en-us", "speed": 1.05},
    "adam": {"blend": [("am_adam", 1.0)], "lang": "en-us", "speed": 1.00},
    "lewis": {"blend": [("bm_lewis", 1.0)], "lang": "en-gb", "speed": 1.03},
    "george": {"blend": [("bm_george", 1.0)], "lang": "en-gb", "speed": 1.03},
    "heart": {"blend": [("af_heart", 1.0)], "lang": "en-us", "speed": 1.03},
}


def load_beats(script_path: str) -> list[str]:
    with open(script_path, encoding="utf-8") as f:
        script_txt = f.read()
    beats = []
    in_beats = False
    for line in script_txt.splitlines():
        if line.strip().startswith("## Beats"):
            in_beats = True
            continue
        if in_beats:
            m = re.match(r"^\d+\.\s+(.*)$", line.strip())
            if m:
                beats.append(m.group(1).strip())
    return beats


def clean_for_kokoro(text: str) -> str:
    """Normalize typography dashes so Kokoro reads rhythmic pauses naturally."""
    t = text.replace(" — ", ", ").replace("—", ", ")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def tighten_pauses(x: np.ndarray, max_gap: float = 0.22, keep_gap: float = 0.14, thr: float = 0.011) -> np.ndarray:
    """Trim head/tail silence and shrink internal pauses > max_gap down to keep_gap."""
    a = np.abs(x)
    win = int(SR * 0.014)
    env = np.convolve(a, np.ones(win) / win, mode="same")
    speech = env > thr
    pad = int(SR * 0.045)
    speech = np.convolve(speech.astype(int), np.ones(2 * pad + 1, dtype=int), mode="same") > 0

    parts = []
    i = 0
    n = len(x)
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
                keep = int(SR * keep_gap)
                h = keep // 2
                parts.append(x[i : i + h])
                parts.append(x[j - h : j])
            else:
                parts.append(x[i:j])
            i = j
    if not parts:
        return x
    y = np.concatenate(parts)
    fi = min(int(SR * 0.012), len(y) // 4)
    if fi > 1:
        y[:fi] *= np.linspace(0.0, 1.0, fi)
        y[-fi:] *= np.linspace(1.0, 0.0, fi)
    return y


def extract_words(whisper_model, wav_path: str) -> list[dict]:
    w16 = wav_path[:-4] + "_16k.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav_path, "-ar", "16000", "-ac", "1", w16], check=True)
    _, a16 = wavfile.read(w16)
    segs, _ = whisper_model.transcribe(a16.astype(np.float32) / 32768.0, word_timestamps=True)
    words = [
        {"w": w.word.strip(), "start": round(float(w.start), 3), "end": round(float(w.end), 3)}
        for s in segs
        for w in s.words
    ]
    os.remove(w16)
    return words


def master_voice(raw_wav: str, out_wav: str) -> None:
    """Broadcast documentary vocal EQ: clean sub-rumble, warm chest, crisp 3 kHz presence, smooth leveling."""
    af = (
        "highpass=f=75,"
        "equalizer=f=145:width_type=o:width=1.2:g=1.5,"
        "equalizer=f=3000:width_type=o:width=1.3:g=2.4,"
        "equalizer=f=6800:width_type=o:width=1.0:g=-1.2,"
        "acompressor=threshold=-18dB:ratio=2.4:attack=12:release=140:makeup=2.2,"
        "alimiter=limit=0.92"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", raw_wav, "-af", af, "-ar", str(SR), "-ac", "1", out_wav],
        check=True,
    )


def synth_kokoro_beats(beats: list[str], preset_name: str, vdir: str) -> list[str]:
    from kokoro_onnx import Kokoro

    kokoro = Kokoro(KOKORO_MODEL, KOKORO_VOICES)
    cfg = KOKORO_PRESETS.get(preset_name, {"blend": [(preset_name, 1.0)], "lang": "en-us", "speed": 1.02})
    style_vec = sum(w * kokoro.get_voice_style(v) for v, w in cfg["blend"])

    wavs = []
    for i, b in enumerate(beats):
        samples, sr24 = kokoro.create(
            clean_for_kokoro(b),
            voice=style_vec,
            speed=cfg["speed"],
            lang=cfg["lang"],
        )
        raw24 = os.path.join(vdir, f"b{i:02d}_24k.wav")
        wav48 = os.path.join(vdir, f"b{i:02d}.wav")
        wavfile.write(raw24, sr24, (np.clip(samples, -1, 1) * 32767).astype(np.int16))
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", raw24, "-ac", "1", "-ar", str(SR), wav48],
            check=True,
        )
        os.remove(raw24)
        wavs.append(wav48)
    return wavs


async def synth_edge_beats(beats: list[str], voice: str, vdir: str) -> list[str]:
    import edge_tts

    wavs = []
    for i, b in enumerate(beats):
        mp3 = os.path.join(vdir, f"b{i:02d}.mp3")
        wav48 = os.path.join(vdir, f"b{i:02d}.wav")
        await edge_tts.Communicate(b, voice, rate="+2%").save(mp3)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), wav48], check=True)
        os.remove(mp3)
        wavs.append(wav48)
    return wavs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="kokoro", choices=["kokoro", "edge"])
    ap.add_argument("--voice", default="orbit_us", help="Kokoro preset/voice or Edge neural voice name")
    args = ap.parse_args()

    beats = load_beats(os.path.join(HERE, "SCRIPT.md"))
    vdir = os.path.join(HERE, "voice")
    os.makedirs(vdir, exist_ok=True)

    use_kokoro = args.engine == "kokoro" and os.path.exists(KOKORO_MODEL) and os.path.exists(KOKORO_VOICES)
    if use_kokoro:
        voice_label = f"kokoro:{args.voice}"
        raw_wavs = synth_kokoro_beats(beats, args.voice, vdir)
    else:
        edge_voice = args.voice if "-" in args.voice else "en-US-AndrewMultilingualNeural"
        voice_label = f"edge:{edge_voice}"
        raw_wavs = asyncio.run(synth_edge_beats(beats, edge_voice, vdir))

    from faster_whisper import WhisperModel
    wmodel = WhisperModel("base.en", device="cpu", compute_type="int8")

    out_chunks = [np.zeros(int(SR * HEAD), np.float32)]
    t = HEAD
    info = []

    for i, (b, wav_path) in enumerate(zip(beats, raw_wavs)):
        _, raw = wavfile.read(wav_path)
        x = tighten_pauses(raw.astype(np.float32) / 32768.0)
        wavfile.write(wav_path, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
        words = extract_words(wmodel, wav_path)

        g = GAP if i < len(beats) - 1 else TAIL
        if i in (1, 4, 8, 11):
            g = 0.26

        dur_speech = len(x) / SR
        abs_words = [
            {"w": w["w"], "start": round(t + w["start"], 3), "end": round(t + w["end"], 3)}
            for w in words
        ]
        info.append({
            "i": i,
            "text": b,
            "start": round(t, 3),
            "end": round(t + dur_speech + g, 3),
            "speechEnd": round(t + dur_speech, 3),
            "words": abs_words,
        })
        out_chunks.append(x)
        t += dur_speech
        out_chunks.append(np.zeros(int(SR * g), np.float32))
        t += g
        heard = " ".join(w["w"] for w in words)
        print(f"Beat {i:02d} ({dur_speech:5.2f}s | {len(b.split())/dur_speech:.2f}wps): {heard[:75]}")

    y_raw = np.concatenate(out_chunks)
    unmastered = os.path.join(vdir, "voice_unmastered.wav")
    final_voice = os.path.join(vdir, "voice_raw.wav")
    wavfile.write(unmastered, SR, (np.clip(y_raw, -1, 1) * 32767).astype(np.int16))
    master_voice(unmastered, final_voice)

    total = round(len(y_raw) / SR, 3)
    with open(os.path.join(HERE, "beats.json"), "w", encoding="utf-8") as f:
        json.dump({"voice": voice_label, "total": total, "beats": info}, f, indent=2)

    print(f"\nVoice [{voice_label}] written ({total:.3f}s total)")


if __name__ == "__main__":
    main()
