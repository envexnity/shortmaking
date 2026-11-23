"""
audio_mix.py — Multi-Layered Storytime Audio Mix & Mastering for roblox-human-survival.
Combines:
  - Single-voice Fish Audio S2-Pro master VO (voice/vo_master.wav)
  - TEMPOREX "Numbers" bed (reused from roblox-reel-Df1kubCJ-o0-v2/audio/song_numbers.mp3)
  - Synced Foley SFX (2-4f pre-cut whooshes, inhale gusts, stopwatch ticks, game-over thud,
    eyelid slap blinks, eye fire hiss, water pour/glug, tank alarm, crunchy teeth chomp,
    acid bubble sizzle, dream chime, save-failed error bonk, stamina drain, final crash)
  - Smooth voice-envelope sidechain ducking (<= -7 dB under speech) + FFmpeg -14 LUFS / -1.0 dBTP mastering.
"""
import json
import math
import subprocess
import wave
from pathlib import Path

import numpy as np

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
REF_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2"
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-human-survival"
AUDIO_DIR = PROJ_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_SFX = SHORTMAKING_ROOT / "assets" / "sfx"

SR = 48000


def load_wav_mono(path: Path) -> np.ndarray:
    raw = subprocess.check_output(
        ["ffmpeg", "-y", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "pipe:1"],
        stderr=subprocess.DEVNULL,
    )
    return np.frombuffer(raw, dtype=np.float32).copy()


def add_at(buf: np.ndarray, clip: np.ndarray, t_sec: float, gain: float = 1.0):
    i0 = int(round(t_sec * SR))
    if i0 >= len(buf) or i0 + len(clip) <= 0:
        return
    c0 = max(0, -i0)
    b0 = max(0, i0)
    n = min(len(clip) - c0, len(buf) - b0)
    if n > 0:
        buf[b0:b0 + n] += clip[c0:c0 + n] * gain


def synth_inhale(dur=0.55, seed=1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    noise = rng.standard_normal(n).astype(np.float32)
    # Band-limited airy whoosh
    bp = np.convolve(noise, np.hanning(45), mode="same")
    bp = np.diff(bp, prepend=0.0)
    env = np.maximum(0.0, np.sin(np.pi * t / dur)) ** 1.4
    out = bp * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_pop_impact(freq0=240.0, freq1=58.0, dur=0.22) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = freq0 * (freq1 / freq0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 17.0)
    click = np.sin(2 * np.pi * 2100.0 * t) * np.exp(-t * 95.0) * 0.35
    out = sub + click
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_eyelid_slap(dur=0.11, seed=2) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    thump = np.sin(2 * np.pi * (320.0 * np.exp(-t * 28.0)) * t) * np.exp(-t * 36.0)
    slap = np.diff(rng.standard_normal(n).astype(np.float32), prepend=0.0) * np.exp(-t * 52.0) * 0.45
    out = thump + slap
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_fire_flare(dur=0.85, seed=3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    noise = rng.standard_normal(n).astype(np.float32)
    smooth = np.convolve(noise, np.hanning(31), mode="same")
    env = np.minimum(1.0, t / 0.08) * np.exp(-np.maximum(0.0, t - 0.15) * 2.8)
    rumble = np.sin(2 * np.pi * 95.0 * t) * env * 0.35
    out = smooth * env + rumble
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_water_glug(dur=0.28) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 340.0 + 360.0 * (t / dur) ** 0.8
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.sin(ph) * np.sin(np.pi * t / dur) * np.exp(-t * 4.5)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_crunch(dur=0.20, seed=4) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    noise = rng.standard_normal(n).astype(np.float32)
    hp = np.diff(np.diff(noise, prepend=0.0), prepend=0.0)
    mod = (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 24.0 * t)))
    out = hp * mod * np.exp(-t * 14.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_error_bonk(dur=0.36) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    # Classic two-tone warning error
    f = np.where(t < dur * 0.45, 310.0, 215.0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = (np.sign(np.sin(ph)) * 0.4 + np.sin(ph) * 0.6) * np.exp(-t * 5.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_dream_shimmer(dur=1.4) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    out = (
        np.sin(2 * np.pi * 523.25 * t) * 0.4
        + np.sin(2 * np.pi * 659.25 * t) * 0.35
        + np.sin(2 * np.pi * 783.99 * t) * 0.3
        + np.sin(2 * np.pi * 1046.5 * t) * 0.2
    ) * (np.maximum(0.0, np.sin(np.pi * t / dur)) ** 1.2)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_alarm_beep(dur=0.14, freq=880.0) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    out = np.sin(2 * np.pi * freq * t) * np.minimum(1.0, t / 0.01) * np.exp(-t * 10.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def load_song_bed(total_dur: float) -> np.ndarray:
    song_path = REF_DIR / "audio" / "song_numbers.mp3"
    if not song_path.exists():
        song_path = AUDIO_DIR / "song_numbers.mp3"
    raw = load_wav_mono(song_path)
    r = float(np.sqrt(np.mean(raw ** 2)) + 1e-9)
    raw = raw * (0.14 / r)

    n = int(math.ceil(total_dur * SR))
    if len(raw) >= n:
        music = raw[:n].copy()
    else:
        music = np.resize(raw, n).astype(np.float32)

    fi = min(int(0.15 * SR), n // 4)
    fo = min(int(0.55 * SR), n // 4)
    if fi > 0:
        music[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 0:
        music[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)
    return music


def main():
    beats_data = json.loads((PROJ_DIR / "voice" / "beats.json").read_text(encoding="utf-8"))
    vo = load_wav_mono(PROJ_DIR / "voice" / "vo_master.wav")
    n = len(vo)
    total_dur = n / SR

    music = load_song_bed(total_dur)
    sfx = np.zeros(n, dtype=np.float32)

    whoosh_p = REF_DIR / "audio" / "whoosh.wav"
    whoosh = load_wav_mono(whoosh_p) if whoosh_p.exists() else synth_inhale(0.22)
    riser_p = REF_DIR / "audio" / "riser_hit.wav"
    riser_hit = load_wav_mono(riser_p) if riser_p.exists() else synth_pop_impact()
    click_p = REF_DIR / "audio" / "ui_click.wav"
    ui_click = load_wav_mono(click_p) if click_p.exists() else synth_alarm_beep(0.08, 1250.0)

    # 2-4f pre-cut whooshes on every major world / shot transition
    for b in beats_data["beats"]:
        ts = b["start"]
        if b["index"] > 1:
            add_at(sfx, whoosh, max(0.0, ts - 0.08), gain=0.22)

    # Specific Foley synced to exact word timestamps
    # World 1: Breathing
    add_at(sfx, synth_inhale(0.65, seed=1), 1.35, gain=0.22)   # "pull invisible gas"
    add_at(sfx, synth_inhale(0.50, seed=2), 3.15, gain=0.20)   # "holes in your face"
    for k in range(3):
        add_at(sfx, ui_click, 8.35 + k * 0.30, gain=0.22)      # "three minutes" ticks
    add_at(sfx, synth_pop_impact(180.0, 48.0, 0.32), 10.48, gain=0.38)  # "instant game over"
    add_at(sfx, synth_error_bonk(0.32), 10.52, gain=0.22)

    # World 2: Blinking
    for k in range(4):
        add_at(sfx, synth_eyelid_slap(0.11, seed=10 + k), 12.40 + k * 0.58, gain=0.28)
    add_at(sfx, synth_water_glug(0.22), 16.05, gain=0.18)      # "keep your eyes wet"
    add_at(sfx, synth_fire_flare(0.95, seed=7), 19.05, gain=0.32)       # "eyes literally start burning"
    add_at(sfx, synth_pop_impact(220.0, 62.0, 0.22), 19.22, gain=0.28)

    # World 3: Water
    for k in range(4):
        add_at(sfx, synth_water_glug(0.26), 21.25 + k * 0.34, gain=0.24)  # "pour clear liquid"
    for k in range(3):
        add_at(sfx, synth_alarm_beep(0.14, 920.0), 27.15 + k * 0.42, gain=0.20)  # "organs start failing"
    add_at(sfx, synth_error_bonk(0.28), 28.00, gain=0.22)

    # World 4: Eating
    for k in range(4):
        add_at(sfx, synth_crunch(0.18, seed=20 + k), 30.15 + k * 0.44, gain=0.28)  # "crush up dead plants... tiny rocks"
    add_at(sfx, synth_fire_flare(0.65, seed=9), 34.30, gain=0.20)       # "stomach acid melt"
    add_at(sfx, synth_alarm_beep(0.18, 1320.0), 35.95, gain=0.20)       # "turn them into fuel"

    # World 5: Sleep & Breakdown
    add_at(sfx, synth_dream_shimmer(1.6), 42.40, gain=0.22)             # "hallucinate"
    add_at(sfx, synth_error_bonk(0.35), 46.65, gain=0.28)               # "stops saving data"
    add_at(sfx, synth_alarm_beep(0.14, 620.0), 48.00, gain=0.22)        # "stamina bar hits zero"
    add_at(sfx, synth_alarm_beep(0.16, 440.0), 48.35, gain=0.24)
    add_at(sfx, riser_hit, 49.40, gain=0.24)
    add_at(sfx, synth_pop_impact(200.0, 45.0, 0.35), 50.15, gain=0.42)  # "breaking down" crash

    # Smooth voice-envelope sidechain ducking (<= -7 dB under speech!)
    win = int(0.08 * SR)
    env = np.convolve(np.abs(vo), np.ones(win, dtype=np.float32) / win, mode="same")
    duck = np.where(env > 0.015, 0.22, 0.56).astype(np.float32)
    duck = np.convolve(duck, np.ones(int(0.07 * SR), dtype=np.float32) / int(0.07 * SR), mode="same")

    bed = music * duck + sfx * 0.85
    active = env > 0.02
    if np.any(active):
        v_rms = float(np.sqrt(np.mean(vo[active] ** 2)) + 1e-9)
        b_rms = float(np.sqrt(np.mean(bed[active] ** 2)) + 1e-9)
        target_b = v_rms * 0.42
        if b_rms > target_b:
            bed *= (target_b / b_rms)

    mix_raw = np.clip(vo + bed, -0.98, 0.98)
    raw_wav = AUDIO_DIR / "mix_raw.wav"
    pcm = (mix_raw * 32767.0).astype(np.int16)
    with wave.open(str(raw_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

    mix_wav = AUDIO_DIR / "mix.wav"
    cmd = [
        "ffmpeg", "-y", "-i", str(raw_wav),
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=5",
        "-ar", "48000", "-ac", "2",
        str(mix_wav),
    ]
    subprocess.check_call(cmd, stderr=subprocess.DEVNULL)
    print(f"Mastered audio -> {mix_wav} ({total_dur:.2f}s)")


if __name__ == "__main__":
    main()
