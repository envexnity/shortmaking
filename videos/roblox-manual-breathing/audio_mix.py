"""
audio_mix.py — Multi-Layered Storytime Audio Mix & Mastering for roblox-manual-breathing.
Combines:
  - Single-voice Fish Audio S2-Pro master VO (voice/vo_master.wav)
  - TEMPOREX "Numbers" bed (reused from roblox-reel-Df1kubCJ-o0-v2/audio/song_numbers.mp3)
    with sudden record-scratch + power-down cutoff at b15_manual_mode into tense heartbeat!
  - Synced Foley & UI SFX (2-4f pre-cut whooshes, timer ticks, breath puffs, disconnect thud,
    no-pause buzzer, 20k counter ticks, alert alarm, frantic manual button clicks)
  - Smooth voice-envelope sidechain ducking (<= -7 dB under speech) + FFmpeg -14 LUFS / -1.0 dBTP mastering.
"""
import json
import math
import subprocess
import wave
from pathlib import Path

import numpy as np

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-manual-breathing"
AUDIO_DIR = PROJ_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_SFX = SHORTMAKING_ROOT / "assets" / "sfx"
SONG_PATH = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2" / "audio" / "song_numbers.mp3"

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


def synth_breath_whoosh(dur: float = 0.42, inhale: bool = True, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    noise = rng.standard_normal(n).astype(np.float32)
    # Bandpass-ish airy texture
    smooth = np.convolve(noise, np.ones(18, dtype=np.float32) / 18.0, mode="same")
    air = np.diff(smooth, prepend=0.0) * 6.0
    env = (t / dur) ** 1.4 * np.sin(math.pi * t / dur) if inhale else np.exp(-t * 4.5) * np.sin(math.pi * t / dur)
    out = air * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_pop_impact(freq0: float = 220.0, freq1: float = 55.0, dur: float = 0.24) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = freq0 * (freq1 / freq0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 15.0)
    click = np.sin(2 * np.pi * 1800.0 * t) * np.exp(-t * 85.0) * 0.35
    out = sub + click
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_ding(freq: float = 1175.0, dur: float = 0.16) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    out = (np.sin(2 * np.pi * freq * t) + 0.30 * np.sin(2 * np.pi * freq * 2.0 * t)) * np.exp(-t * 17.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_error_buzz(dur: float = 0.28) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    w = np.tanh(2.5 * (np.sin(2 * np.pi * 145 * t) + 0.6 * np.sin(2 * np.pi * 158 * t)))
    env = np.minimum(1.0, t / 0.015) * np.exp(-t * 7.5)
    out = w * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_record_scratch(dur: float = 0.28) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 950.0 * np.exp(-t * 9.0) + 110.0
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.sign(np.sin(ph)) * np.sin(ph * 0.5) * np.exp(-t * 6.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_alert_beep(dur: float = 0.22) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    w = np.sin(2 * np.pi * 880 * t) + 0.4 * np.sin(2 * np.pi * 1320 * t)
    env = np.minimum(1.0, t / 0.008) * np.minimum(1.0, (dur - t) / 0.025)
    out = w * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_heartbeat(dur: float = 0.36) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    b1 = np.sin(2 * np.pi * 58 * t) * np.exp(-t * 22.0)
    t2 = np.maximum(0.0, t - 0.14)
    b2 = np.where(t >= 0.14, np.sin(2 * np.pi * 50 * t2) * np.exp(-t2 * 24.0) * 0.75, 0.0)
    out = b1 + b2
    return out / (np.max(np.abs(out)) + 1e-6)


def load_song_bed(total_dur: float, beats_meta: list) -> np.ndarray:
    raw = load_wav_mono(SONG_PATH)
    r = float(np.sqrt(np.mean(raw ** 2)) + 1e-9)
    raw = raw * (0.14 / r)

    n = int(math.ceil(total_dur * SR))
    if len(raw) >= n:
        music = raw[:n].copy()
    else:
        music = np.tile(raw, int(math.ceil(n / len(raw))))[:n].copy()

    # Cut music sharply at b15_manual_mode ("Suddenly, the automatic mode turns off...")!
    b15 = next((b for b in beats_meta if b["id"] == "b15_manual_mode"), None)
    if b15 is not None:
        i_cut = max(0, int(round((b15["start"] - 0.04) * SR)))
        fade_len = int(0.12 * SR)
        i0 = max(0, i_cut - fade_len)
        if i_cut > i0:
            music[i0:i_cut] *= np.linspace(1.0, 0.0, i_cut - i0, dtype=np.float32)
        music[i_cut:] = 0.0

    # Subtle dip during dark logout beat (b06..b07)
    b06 = next((b for b in beats_meta if b["id"] == "b06_stop_black"), None)
    b07 = next((b for b in beats_meta if b["id"] == "b07_logout"), None)
    if b06 and b07:
        i0 = max(0, int(round(b06["start"] * SR)))
        i1 = min(n, int(round(b07["clip_end"] * SR)))
        music[i0:i1] *= 0.25

    fi = min(int(0.12 * SR), n // 4)
    if fi > 0:
        music[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    return music


def main():
    beats_data = json.loads((PROJ_DIR / "voice" / "beats.json").read_text(encoding="utf-8"))
    vo = load_wav_mono(PROJ_DIR / "voice" / "vo_master.wav")
    n = len(vo)
    total_dur = n / SR

    music = load_song_bed(total_dur, beats_data["beats"])
    sfx = np.zeros(n, dtype=np.float32)

    whoosh = load_wav_mono(ASSETS_SFX / "whoosh.wav") if (ASSETS_SFX / "whoosh.wav").exists() else synth_breath_whoosh(0.24)
    riser_hit = load_wav_mono(ASSETS_SFX / "riser_hit.wav") if (ASSETS_SFX / "riser_hit.wav").exists() else synth_pop_impact()
    ui_click = load_wav_mono(ASSETS_SFX / "ui_click.wav") if (ASSETS_SFX / "ui_click.wav").exists() else synth_ding(1400.0, 0.08)

    pop = synth_pop_impact()
    buzz = synth_error_buzz()
    scratch = synth_record_scratch()
    alert = synth_alert_beep()
    hb = synth_heartbeat()

    for b in beats_data["beats"]:
        bid = b["id"]
        ts, te = b["start"], b["end"]

        # 2-4f pre-cut whooshes on major scene cuts
        if bid in ("b03_pull_gas", "b06_stop_black", "b08_no_pause", "b11_sleeping", "b14_dont_realize", "b15_manual_mode"):
            add_at(sfx, whoosh, max(0.0, ts - 0.08), gain=0.22)

        if bid == "b01_timer":
            for k in range(4):
                add_at(sfx, ui_click, ts + 0.35 + k * 0.45, gain=0.18)
        elif bid == "b02_resets":
            add_at(sfx, synth_ding(1320.0, 0.16), ts + 0.35, gain=0.26)
        elif bid in ("b03_pull_gas", "b05_face_holes"):
            add_at(sfx, synth_breath_whoosh(0.45, inhale=True, seed=3), ts + 0.25, gain=0.28)
        elif bid == "b04_lungs":
            add_at(sfx, pop, ts + 0.12, gain=0.24)
        elif bid == "b06_stop_black":
            add_at(sfx, hb, ts + 0.65, gain=0.38)
        elif bid == "b07_logout":
            add_at(sfx, synth_pop_impact(180.0, 42.0, 0.32), ts + 0.10, gain=0.45)
            add_at(sfx, buzz, ts + 0.45, gain=0.26)
        elif bid == "b08_no_pause":
            add_at(sfx, buzz, ts + 0.85, gain=0.36)
        elif bid == "b09_walking":
            for k in range(3):
                add_at(sfx, ui_click, ts + 0.15 + k * 0.35, gain=0.16)
        elif bid == "b10_eating":
            add_at(sfx, pop, ts + 0.15, gain=0.22)
        elif bid == "b11_sleeping":
            add_at(sfx, synth_breath_whoosh(0.55, inhale=False, seed=11), ts + 0.40, gain=0.24)
        elif bid == "b12_auto_force":
            add_at(sfx, synth_breath_whoosh(0.38, inhale=True, seed=12), ts + 0.20, gain=0.22)
            add_at(sfx, synth_breath_whoosh(0.38, inhale=False, seed=13), ts + 1.15, gain=0.22)
        elif bid == "b13_20k_times":
            for k in range(7):
                add_at(sfx, synth_ding(880 + k * 90, 0.08), ts + 0.15 + k * 0.22, gain=0.16)
        elif bid == "b15_manual_mode":
            add_at(sfx, scratch, max(0.0, ts - 0.06), gain=0.42)
            add_at(sfx, alert, ts + 0.08, gain=0.30)
            add_at(sfx, synth_pop_impact(200.0, 48.0, 0.30), ts + 0.05, gain=0.42)
            # Tense heartbeat under manual mode
            for k in range(5):
                add_at(sfx, hb, ts + 0.45 + k * 0.58, gain=0.35)
        elif bid == "b16_good_luck":
            for k in range(5):
                add_at(sfx, ui_click, ts + 0.05 + k * 0.13, gain=0.28)
            add_at(sfx, synth_pop_impact(160.0, 42.0, 0.34), te - 0.15, gain=0.40)

    # Smooth voice-envelope sidechain ducking (<= -7 dB under speech)
    win = int(0.08 * SR)
    env = np.convolve(np.abs(vo), np.ones(win, dtype=np.float32) / win, mode="same")
    duck = np.where(env > 0.015, 0.22, 0.55).astype(np.float32)
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
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(raw_wav), "-af", "loudnorm=I=-14:TP=-1.0:LRA=7", "-ar", str(SR), "-ac", "2", str(mix_wav)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Mastered audio -> {mix_wav} ({total_dur:.2f}s)")


if __name__ == "__main__":
    main()
