"""Voiceover & Whisper word-level timing generator for ascii-horror-short (< 45s cap)."""
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
    "entity": {
        "voice_id": "N2lVS1w4EtoT3dr4eOWO",  # Callum - Husky Trickster -> CRT voice FX
        "kokoro_voice": "am_fenrir",
        "kokoro_speed": 0.92,
        "edge_voice": "en-GB-RyanNeural",
        "edge_rate": "-12%",
        "edge_pitch": "-14Hz",
        "speed": 0.88,
        "stability": 0.32,
        "similarity": 0.82,
        "style": 0.35,
        "gap_after": 0.16,
    },
}

# Tight pacing gaps (seconds) keeping dead air < 1.0s total and runtime < 45s
CUSTOM_GAPS = {
    0: 0.14,   # Hook -> slams lights
    2: 0.12,   # Concrete / footsteps -> CRT monitor
    5: 0.14,   # "blinks—" -> lunge!
    6: 0.16,   # "out of the dark." -> "Luckily"
    7: 0.18,   # Brief breath after ripping cord before "Unluckily"
    8: 0.18,   # "turned blood red." -> "You see," pivot
    12: 0.16,  # "one final line:" -> entity whisper
    13: 0.14,  # "Found the exit." -> final twist
    14: 0.06,  # Cut < 0.08s after final word "ASCII." (Law #5 & #22)
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


def apply_crt_entity_fx(x: np.ndarray) -> np.ndarray:
    """Subtle eerie CRT terminal speaker timbre (intelligible, cold, ominous)."""
    n = len(x)
    t = np.arange(n, dtype=np.float32) / SR
    # Band-shape like an old monitor speaker (220 Hz - 3.6 kHz) + subtle 55 Hz ring modulation
    b, a = butter(2, [210.0 / (SR * 0.5), 3600.0 / (SR * 0.5)], btype="band")
    y = filtfilt(b, a, x).astype(np.float32)
    ring = 0.80 + 0.20 * np.sin(2.0 * np.pi * 55.0 * t)
    y = y * ring
    # Subtle short metallic terminal slapback (18ms + 42ms)
    echo = np.zeros_like(y)
    d1, d2 = int(0.018 * SR), int(0.044 * SR)
    if n > d1:
        echo[d1:] += y[:-d1] * 0.30
    if n > d2:
        echo[d2:] += y[:-d2] * 0.16
    out = np.tanh((y + echo) * 1.45) * 0.90
    rms_in = np.sqrt(np.mean(x ** 2)) + 1e-8
    rms_out = np.sqrt(np.mean(out ** 2)) + 1e-8
    return (out * (rms_in * 1.08 / rms_out)).astype(np.float32)


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


def synth_kokoro(text: str, cfg: dict, out_wav_or_mp3: str):
    global _KOKORO
    if _KOKORO is None:
        from kokoro_onnx import Kokoro
        _KOKORO = Kokoro(
            os.path.join(REPO_ROOT, ".models", "kokoro", "kokoro-v1.0.onnx"),
            os.path.join(REPO_ROOT, ".models", "kokoro", "voices-v1.0.bin"),
        )
    samples, ksr = _KOKORO.create(text, voice=cfg["kokoro_voice"], speed=cfg["kokoro_speed"], lang="en-us")
    tmp = out_wav_or_mp3 + ".tmp.wav"
    wavfile.write(tmp, ksr, (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-b:a", "192k", out_wav_or_mp3], check=True)
    os.remove(tmp)


def synth_voice(text: str, cfg: dict, out_mp3: str) -> str:
    # Tier 1/CLI: ElevenLabs OAuth (since fish-audio MCP is not configured on this machine)
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

    # Tier 2: Local Kokoro-82M ONNX
    try:
        synth_kokoro(text, cfg, out_mp3)
        if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 500:
            return "kokoro-onnx"
    except Exception as e:
        print(f"[WARN] Kokoro fallback failed: {e}")

    # Tier 3: edge-tts
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

        if b["speaker"] == "entity":
            x = apply_crt_entity_fx(x)
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
    assert total < 45.0, f"Video exceeded 45s cap! Got {total:.3f}s"
    with open(os.path.join(HERE, "beats.json"), "w", encoding="utf-8") as f:
        json.dump({"engines": sorted(engines), "model": MODEL_ID, "total": total, "beats": info}, f, indent=2)
    print(f"Generated voice_raw.wav via {sorted(engines)} ({total:.3f}s, {len(info)} beats)")
    for b in info:
        print(f"  [{b['i']:02d}] {b['start']:5.2f}s - {b['speechEnd']:5.2f}s (end {b['end']:5.2f}s) [{b['speaker']:8s}] {b['text']}")


if __name__ == "__main__":
    main()
