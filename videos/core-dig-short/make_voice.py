"""Multi-character ElevenLabs + Whisper word-level timing generator for core-dig-short."""
import json
import os
import re
import shutil
import subprocess
import numpy as np
from scipy.io import wavfile
from faster_whisper import WhisperModel

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
MODEL_ID = "eleven_turbo_v2_5"

CHARACTERS = {
    "host": {
        "voice_id": "TX3LPaxmHKxFdv7VOQHJ",  # Liam - Energetic, Social Media Creator
        "speed": 1.13,
        "stability": 0.40,
        "similarity": 0.80,
        "style": 0.22,
        "gap_after": 0.16,
    },
    "mrbeast": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam - Dominant, Firm
        "speed": 0.96,
        "stability": 0.65,
        "similarity": 0.80,
        "style": 0.05,
        "gap_after": 0.28,
    },
    "mc": {
        "voice_id": "bIHbv24MWmeRgasZH58o",  # Will - Relaxed Optimist
        "speed": 1.12,
        "stability": 0.35,
        "similarity": 0.80,
        "style": 0.30,
        "gap_after": 0.15,
    },
    "rat": {
        "voice_id": "N2lVS1w4EtoT3dr4eOWO",  # Callum - Husky Trickster
        "speed": 1.14,
        "stability": 0.40,
        "similarity": 0.80,
        "style": 0.25,
        "gap_after": 0.14,
    },
    "guardian": {
        "voice_id": "pqHfZKP75CvOlQylNhV4",  # Bill - Wise, Mature, Balanced
        "speed": 1.06,
        "stability": 0.42,
        "similarity": 0.80,
        "style": 0.20,
        "gap_after": 0.10,
    },
}

CUSTOM_GAPS = {
    0: 0.18,   # Host -> MrBeast deadpan "No."
    1: 0.30,   # Beat after "No." before cut to backyard
    3: 0.22,   # After "Say less." before digging starts
    4: 0.25,   # Floor collapses into sewer
    7: 0.20,   # After dino helmet before lava drop
    11: 0.22,  # Tap thermostat COOL before Guardian yells
    12: 0.28,  # Core freezes solid cyan before geyser launch
    13: 0.55,  # Rocket launch up through Earth & crash onto snowy street
    14: 0.25,  # Shivering beat before Host's shortchange punchline
    15: 0.45,  # Final stare + snowy wind hold before clean end
}


def load_beats(script_path: str):
    beats = []
    with open(script_path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\d+\.\s+\[(\w+)\]\s+(.*)$", line.strip())
            if m:
                beats.append({"speaker": m.group(1), "text": m.group(2).strip()})
    return beats


def tighten_pauses(x: np.ndarray, max_gap: float = 0.20, keep_gap: float = 0.12, thr: float = 0.012) -> np.ndarray:
    a = np.abs(x)
    win = int(SR * 0.014)
    env = np.convolve(a, np.ones(win) / win, mode="same")
    speech = env > thr
    pad = int(SR * 0.045)
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
                parts.append(x[i : i + h])
                parts.append(x[j - h : j])
            else:
                parts.append(x[i:j])
            i = j
    if not parts:
        return x
    y = np.concatenate(parts)
    fi = min(int(SR * 0.010), len(y) // 4)
    if fi > 1:
        y[:fi] *= np.linspace(0.0, 1.0, fi)
        y[-fi:] *= np.linspace(1.0, 0.0, fi)
    return y


def extract_words(whisper_model, wav_path: str):
    w16 = wav_path[:-4] + "_16k.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav_path, "-ar", "16000", "-ac", "1", w16], check=True)
    _, a16 = wavfile.read(w16)
    segs, _ = whisper_model.transcribe(a16.astype(np.float32) / 32768.0, word_timestamps=True)
    words = [{"w": w.word.strip(), "start": round(float(w.start), 3), "end": round(float(w.end), 3)} for s in segs for w in s.words]
    os.remove(w16)
    return words


def master_voice(raw_wav: str, out_wav: str):
    af = (
        "highpass=f=85,"
        "equalizer=f=150:width_type=o:width=1.2:g=1.4,"
        "equalizer=f=2900:width_type=o:width=1.3:g=2.4,"
        "equalizer=f=6800:width_type=o:width=1.0:g=-1.2,"
        "acompressor=threshold=-17dB:ratio=2.5:attack=10:release=130:makeup=2.2,"
        "alimiter=limit=0.92"
    )
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw_wav, "-af", af, "-ar", str(SR), "-ac", "1", out_wav], check=True)


def synth_elevenlabs(text: str, cfg: dict, out_mp3: str):
    exe = shutil.which("elevenlabs") or shutil.which("elevenlabs.cmd") or "elevenlabs.cmd"
    cmd = [
        exe, "text-to-speech", "convert",
        "--voice-id", cfg["voice_id"],
        "--model-id", MODEL_ID,
        "--text", text,
        "--output-format", "mp3_44100_128",
        "--voice-settings.speed", str(cfg["speed"]),
        "--voice-settings.stability", str(cfg["stability"]),
        "--voice-settings.similarity-boost", str(cfg["similarity"]),
        "--voice-settings.style", str(cfg["style"]),
        "--voice-settings.use-speaker-boost", "true",
        "-o", out_mp3,
    ]
    subprocess.run(cmd, check=True)


def main():
    beats = load_beats(os.path.join(HERE, "SCRIPT.md"))
    vdir = os.path.join(HERE, "voice")
    os.makedirs(vdir, exist_ok=True)

    wmodel = WhisperModel("base.en", device="cpu", compute_type="int8")

    HEAD = 0.06
    chunks = [np.zeros(int(SR * HEAD), np.float32)]
    t = HEAD
    info = []

    for i, b in enumerate(beats):
        cfg = CHARACTERS[b["speaker"]]
        mp3_path = os.path.join(vdir, f"b{i:02d}.mp3")
        wav_path = os.path.join(vdir, f"b{i:02d}.wav")

        synth_elevenlabs(b["text"], cfg, mp3_path)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3_path, "-ac", "1", "-ar", str(SR), wav_path], check=True)

        _, raw = wavfile.read(wav_path)
        x = tighten_pauses(raw.astype(np.float32) / 32768.0)
        wavfile.write(wav_path, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))

        words = extract_words(wmodel, wav_path)
        if not words:
            words = [{"w": b["text"], "start": 0.02, "end": round(len(x) / SR - 0.02, 3)}]

        gap = CUSTOM_GAPS.get(i, cfg["gap_after"])
        abs_words = [{"w": w["w"], "start": round(t + w["start"], 3), "end": round(t + w["end"], 3)} for w in words]
        ds = len(x) / SR
        info.append({
            "i": i,
            "speaker": b["speaker"],
            "text": b["text"],
            "start": round(t, 3),
            "speechEnd": round(t + ds, 3),
            "end": round(t + ds + gap, 3),
            "words": abs_words,
        })
        chunks.append(x)
        t += ds
        chunks.append(np.zeros(int(SR * gap), np.float32))
        t += gap

    y = np.concatenate(chunks)
    unm = os.path.join(vdir, "voice_unmastered.wav")
    fin = os.path.join(vdir, "voice_raw.wav")
    wavfile.write(unm, SR, (np.clip(y, -1, 1) * 32767).astype(np.int16))
    master_voice(unm, fin)

    total = round(len(y) / SR, 3)
    with open(os.path.join(HERE, "beats.json"), "w", encoding="utf-8") as f:
        json.dump({"engine": "elevenlabs", "model": MODEL_ID, "total": total, "beats": info}, f, indent=2)
    print(f"Generated ElevenLabs voice_raw.wav ({total:.3f}s, {len(info)} beats)")
    for b in info:
        print(f"  [{b['i']:02d}] {b['start']:5.2f}s - {b['speechEnd']:5.2f}s (end {b['end']:5.2f}s) [{b['speaker']:8s}] {b['text']}")


if __name__ == "__main__":
    main()
