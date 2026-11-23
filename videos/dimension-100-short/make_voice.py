"""Multi-character ElevenLabs + Whisper word-level timing generator for dimension-100-short."""
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
        "edge_voice": "en-AU-WilliamNeural",
        "edge_rate": "+8%",
        "edge_pitch": "+2Hz",
        "speed": 1.14,
        "stability": 0.40,
        "similarity": 0.80,
        "style": 0.24,
        "gap_after": 0.15,
    },
    "mrbeast": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam - Dominant, Firm
        "edge_voice": "en-US-ChristopherNeural",
        "edge_rate": "-4%",
        "edge_pitch": "-6Hz",
        "speed": 0.96,
        "stability": 0.65,
        "similarity": 0.80,
        "style": 0.05,
        "gap_after": 0.28,
    },
    "mc": {
        "voice_id": "bIHbv24MWmeRgasZH58o",  # Will - Relaxed Optimist
        "edge_voice": "en-US-GuyNeural",
        "edge_rate": "+10%",
        "edge_pitch": "+4Hz",
        "speed": 1.13,
        "stability": 0.35,
        "similarity": 0.80,
        "style": 0.32,
        "gap_after": 0.14,
    },
    "flat": {
        "voice_id": "N2lVS1w4EtoT3dr4eOWO",  # Callum - Husky Trickster
        "edge_voice": "en-GB-RyanNeural",
        "edge_rate": "+12%",
        "edge_pitch": "+8Hz",
        "speed": 1.15,
        "stability": 0.40,
        "similarity": 0.80,
        "style": 0.28,
        "gap_after": 0.14,
    },
    "warden": {
        "voice_id": "pqHfZKP75CvOlQylNhV4",  # Bill - Wise, Mature, Balanced
        "edge_voice": "en-GB-ThomasNeural",
        "edge_rate": "+6%",
        "edge_pitch": "-4Hz",
        "speed": 1.08,
        "stability": 0.42,
        "similarity": 0.80,
        "style": 0.22,
        "gap_after": 0.12,
    },
}

CUSTOM_GAPS = {
    0: 0.16,   # Host -> MrBeast deadpan "No."
    1: 0.28,   # Beat after "No." before cut to backyard lab
    3: 0.20,   # After "Fire it up." before 1D squash
    4: 0.22,   # Pop into 2D Flatland arcade grid
    6: 0.20,   # Dial crank into 4D Tesseract
    8: 0.18,   # After Klein bottle before 11D String Warden pivot
    10: 0.18,  # Slam overdrive button
    11: 0.14,  # Warden interrupted by 100D flash
    12: 0.32,  # Reality integer-overflows into 6-pixel calculator room
    13: 0.24,  # Warp pop back to 3D street
    14: 0.22,  # Beat before Host's 100D nickel shortchange punchline
    15: 0.06,  # Clean <0.08s cut right after final word "nickel." (Law #5 & #22)
}


def load_beats(script_path: str):
    beats = []
    with open(script_path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\d+\.\s+\[(\w+)\]\s+(.*)$", line.strip())
            if m:
                beats.append({"speaker": m.group(1), "text": m.group(2).strip()})
    return beats


def tighten_pauses(x: np.ndarray, max_gap: float = 0.18, keep_gap: float = 0.10, thr: float = 0.012) -> np.ndarray:
    a = np.abs(x)
    win = int(SR * 0.014)
    env = np.convolve(a, np.ones(win) / win, mode="same")
    speech = env > thr
    pad = int(SR * 0.040)
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


def synth_voice(text: str, cfg: dict, out_mp3: str) -> str:
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
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 500:
        return "elevenlabs"
    # Fallback to edge-tts if ElevenLabs fails or quota exceeded
    subprocess.run([
        "edge-tts",
        "--voice", cfg["edge_voice"],
        f"--rate={cfg['edge_rate']}",
        f"--pitch={cfg['edge_pitch']}",
        "--text", text,
        "--write-media", out_mp3,
    ], check=True)
    return "edge-tts"


def main():
    beats = load_beats(os.path.join(HERE, "SCRIPT.md"))
    vdir = os.path.join(HERE, "voice")
    os.makedirs(vdir, exist_ok=True)

    wmodel = WhisperModel("base.en", device="cpu", compute_type="int8")

    HEAD = 0.05
    chunks = [np.zeros(int(SR * HEAD), np.float32)]
    t = HEAD
    info = []
    engine_used = "elevenlabs"

    for i, b in enumerate(beats):
        cfg = CHARACTERS[b["speaker"]]
        mp3_path = os.path.join(vdir, f"b{i:02d}.mp3")
        wav_path = os.path.join(vdir, f"b{i:02d}.wav")

        if not (os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 500):
            engine_used = synth_voice(b["text"], cfg, mp3_path)
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
        json.dump({"engine": engine_used, "model": MODEL_ID, "total": total, "beats": info}, f, indent=2)
    print(f"Generated {engine_used} voice_raw.wav ({total:.3f}s, {len(info)} beats)")
    for b in info:
        print(f"  [{b['i']:02d}] {b['start']:5.2f}s - {b['speechEnd']:5.2f}s (end {b['end']:5.2f}s) [{b['speaker']:8s}] {b['text']}")


if __name__ == "__main__":
    main()
