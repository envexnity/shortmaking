"""Voiceover & Whisper word-level timing generator for ascii-real-horror-short (< 45s)."""
import json
import os
import re
import shutil
import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, filtfilt
from faster_whisper import WhisperModel

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SR = 48000
MODEL_ID = "eleven_turbo_v2_5"

SPEAKERS = {
    "narrator": {
        "voice_id": "nPczCjzI2devNBz1zQrb",  # Brian - Deep, Resonant Storyteller
        "kokoro_voice": "am_onyx",
        "kokoro_speed": 1.14,
        "edge_voice": "en-US-ChristopherNeural",
        "edge_rate": "+8%",
        "edge_pitch": "-4Hz",
        "speed": 1.15,
        "stability": 0.38,
        "similarity": 0.80,
        "style": 0.28,
        "gap_after": 0.12,
    },
    "doppelganger": {
        "voice_id": "N2lVS1w4EtoT3dr4eOWO",  # Callum - Husky Trickster -> walkie-talkie CRT FX
        "kokoro_voice": "am_fenrir",
        "kokoro_speed": 0.94,
        "edge_voice": "en-GB-RyanNeural",
        "edge_rate": "-8%",
        "edge_pitch": "-10Hz",
        "speed": 0.92,
        "stability": 0.34,
        "similarity": 0.82,
        "style": 0.34,
        "gap_after": 0.15,
    },
}

CUSTOM_GAPS = {
    0: 0.14,
    2: 0.12,
    5: 0.16,   # Eyes snap wide -> "Luckily..."
    6: 0.18,   # Brief breath before "Unluckily..."
    7: 0.16,   # "wearing his exact face." -> "You see,"
    11: 0.16,  # "room he just left:" -> walkie-talkie voice
    12: 0.15,  # "Why'd you lock me out?" -> final monitor reveal
    13: 0.06,  # Cut < 0.08s after final word "chair." (Law #5 & #22)
}


def load_beats(script_path: str):
    beats = []
    with open(script_path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\d+\.\s+\[(\w+)\]\s+(.*)$", line.strip())
            if m:
                beats.append({"speaker": m.group(1), "text": m.group(2).strip()})
    return beats


def tighten_pauses(x: np.ndarray, max_gap: float = 0.15, keep_gap: float = 0.08, thr: float = 0.014) -> np.ndarray:
    a = np.abs(x)
    win = int(SR * 0.014)
    env = np.convolve(a, np.ones(win) / win, mode="same")
    speech = env > thr
    pad = int(SR * 0.036)
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
    fi = min(int(SR * 0.008), len(y) // 4)
    if fi > 1:
        y[:fi] *= np.linspace(0.0, 1.0, fi)
        y[-fi:] *= np.linspace(1.0, 0.0, fi)
    return y


def apply_radio_fx(x: np.ndarray) -> np.ndarray:
    """Walkie-talkie speaker distortion + eerie hallway echo for the doppelganger line."""
    n = len(x)
    b, a = butter(2, [340.0 / (SR * 0.5), 3200.0 / (SR * 0.5)], btype="band")
    y = filtfilt(b, a, x).astype(np.float32)
    # Soft overdrive + faint static hiss
    rng = np.random.default_rng(2006)
    hiss = rng.standard_normal(n).astype(np.float32) * 0.012
    y = np.tanh(y * 2.2) + hiss
    echo = np.zeros_like(y)
    d1, d2 = int(0.022 * SR), int(0.055 * SR)
    if n > d1:
        echo[d1:] += y[:-d1] * 0.25
    if n > d2:
        echo[d2:] += y[:-d2] * 0.12
    out = y + echo
    rms_in = np.sqrt(np.mean(x ** 2)) + 1e-8
    rms_out = np.sqrt(np.mean(out ** 2)) + 1e-8
    return (out * (rms_in * 1.05 / rms_out)).astype(np.float32)


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
        "equalizer=f=145:width_type=o:width=1.2:g=1.6,"
        "equalizer=f=2800:width_type=o:width=1.3:g=2.2,"
        "equalizer=f=6800:width_type=o:width=1.0:g=-1.2,"
        "acompressor=threshold=-17dB:ratio=2.4:attack=10:release=130:makeup=2.2,"
        "alimiter=limit=0.92"
    )
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw_wav, "-af", af, "-ar", str(SR), "-ac", "1", out_wav], check=True)


_KOKORO = None


def synth_kokoro(text: str, cfg: dict, out_mp3: str):
    global _KOKORO
    if _KOKORO is None:
        from kokoro_onnx import Kokoro
        _KOKORO = Kokoro(
            os.path.join(REPO_ROOT, ".models", "kokoro", "kokoro-v1.0.onnx"),
            os.path.join(REPO_ROOT, ".models", "kokoro", "voices-v1.0.bin"),
        )
    samples, ksr = _KOKORO.create(text, voice=cfg["kokoro_voice"], speed=cfg["kokoro_speed"], lang="en-us")
    tmp = out_mp3 + ".tmp.wav"
    wavfile.write(tmp, ksr, (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-b:a", "192k", out_mp3], check=True)
    os.remove(tmp)


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
    try:
        synth_kokoro(text, cfg, out_mp3)
        if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 500:
            return "kokoro-onnx"
    except Exception:
        pass
    subprocess.run([
        "edge-tts", "--voice", cfg["edge_voice"],
        f"--rate={cfg['edge_rate']}", f"--pitch={cfg['edge_pitch']}",
        "--text", text, "--write-media", out_mp3,
    ], check=True)
    return "edge-tts"


def main():
    beats = load_beats(os.path.join(HERE, "SCRIPT.md"))
    vdir = os.path.join(HERE, "voice")
    os.makedirs(vdir, exist_ok=True)
    wmodel = WhisperModel("base.en", device="cpu", compute_type="int8")

    HEAD = 0.04
    chunks = [np.zeros(int(SR * HEAD), np.float32)]
    t = HEAD
    info = []
    engines = set()

    for i, b in enumerate(beats):
        cfg = SPEAKERS[b["speaker"]]
        mp3_path = os.path.join(vdir, f"b{i:02d}.mp3")
        wav_path = os.path.join(vdir, f"b{i:02d}.wav")

        if not (os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 500):
            eng = synth_voice(b["text"], cfg, mp3_path)
        else:
            eng = "cached"
        engines.add(eng)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3_path, "-ac", "1", "-ar", str(SR), wav_path], check=True)

        _, raw = wavfile.read(wav_path)
        x = tighten_pauses(raw.astype(np.float32) / 32768.0)
        wavfile.write(wav_path, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))

        words = extract_words(wmodel, wav_path)
        if not words:
            words = [{"w": b["text"], "start": 0.02, "end": round(len(x) / SR - 0.02, 3)}]

        if b["speaker"] == "doppelganger":
            x = apply_radio_fx(x)
            wavfile.write(wav_path, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))

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
    assert total < 45.0, f"Exceeded 45s cap! Got {total:.3f}s"
    with open(os.path.join(HERE, "beats.json"), "w", encoding="utf-8") as f:
        json.dump({"engines": sorted(engines), "model": MODEL_ID, "total": total, "beats": info}, f, indent=2)
    print(f"Generated voice_raw.wav via {sorted(engines)} ({total:.3f}s, {len(info)} beats)")
    for b in info:
        print(f"  [{b['i']:02d}] {b['start']:5.2f}s - {b['speechEnd']:5.2f}s (end {b['end']:5.2f}s) [{b['speaker']:12s}] {b['text']}")


if __name__ == "__main__":
    main()
