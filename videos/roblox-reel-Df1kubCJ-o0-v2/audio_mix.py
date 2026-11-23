"""
audio_mix.py — Multi-Layered Storytime Audio Mix & Mastering for Df1kubCJ-o0 Remake v2.
Combines:
  - Single-voice Fish Audio S2-Pro + MyInstants HUSS SFX master VO (voice/vo_master.wav)
  - TEMPOREX "Numbers" instrumental/song bed (audio/song_numbers.mp3) with smooth comedy dip on rejection
  - Synced Foley SFX (assets/sfx/ + subtle paper slaps on huss_hit_times, 2-4f pre-cut whooshes,
    5AM alarm, stopwatch ticks, party horn, record scratch, grill sizzle, pop-wrap impacts, 400-burger dings)
  - Smooth voice-envelope sidechain ducking (<= -7 dB under speech) + FFmpeg -14 LUFS / -1.0 dBTP mastering.
"""
import json
import math
import subprocess
import wave
from pathlib import Path

import numpy as np

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2"
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


def synth_paper_fold(dur=0.14, seed=1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    noise = rng.standard_normal(n).astype(np.float32)
    hp = np.diff(np.diff(noise, prepend=0.0), prepend=0.0)
    env = np.exp(-t * 28.0) * (0.65 + 0.35 * np.sin(2 * np.pi * 45.0 * t))
    thump = np.sin(2 * np.pi * 115.0 * t * np.exp(-t * 8.0)) * np.exp(-t * 32.0) * 0.55
    out = hp * env * 0.55 + thump
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_pop_impact(freq0=240.0, freq1=64.0, dur=0.19) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = freq0 * (freq1 / freq0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 19.0)
    click = np.sin(2 * np.pi * 2100.0 * t) * np.exp(-t * 95.0) * 0.38
    out = sub + click
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_alarm_bell(dur=0.52) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    ring = (np.sin(2 * np.pi * 1580 * t) + 0.5 * np.sin(2 * np.pi * 3160 * t)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 18 * t)))
    out = ring * np.exp(-t * 3.8)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_party_horn(dur=0.38) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 440.0 + 160.0 * np.sin(np.pi * t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    w = np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.28 * np.sin(3 * ph)
    env = np.minimum(1.0, t / 0.025) * np.exp(-np.maximum(0.0, t - 0.10) * 6.0)
    out = w * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_grill_sizzle(dur=1.5, seed=7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    noise = rng.standard_normal(n).astype(np.float32)
    hp = np.diff(noise, prepend=0.0)
    env = np.minimum(1.0, t / 0.12) * np.minimum(1.0, (dur - t) / 0.25)
    out = hp * (0.7 + 0.3 * np.sin(2 * np.pi * 8.0 * t)) * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_ding(freq=1175.0, dur=0.16) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    out = (np.sin(2 * np.pi * freq * t) + 0.30 * np.sin(2 * np.pi * freq * 2.0 * t)) * np.exp(-t * 17.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_record_scratch(dur=0.26) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 920.0 * np.exp(-t * 9.5) + 115.0
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.sign(np.sin(ph)) * np.sin(ph * 0.5) * np.exp(-t * 6.5)
    return out / (np.max(np.abs(out)) + 1e-6)


def load_song_bed(total_dur: float, beats_meta: list) -> np.ndarray:
    """Load TEMPOREX 'Numbers' track, normalize RMS, crossfade-loop if needed, and dip smoothly on rejection beats."""
    song_path = AUDIO_DIR / "song_numbers.mp3"
    raw = load_wav_mono(song_path)
    r = float(np.sqrt(np.mean(raw ** 2)) + 1e-9)
    raw = raw * (0.14 / r)

    n = int(math.ceil(total_dur * SR))
    xf = int(1.5 * SR)
    if len(raw) >= n:
        music = raw[:n].copy()
    else:
        # Equal-power cosine crossfade loop
        music = np.zeros(n, dtype=np.float32)
        pos = 0
        while pos < n:
            if pos == 0:
                take = min(n, len(raw))
                music[:take] = raw[:take]
                pos = take
            else:
                ov = min(xf, pos, len(raw), n - pos + xf)
                if ov > 0 and pos >= ov:
                    t_xf = np.linspace(0.0, math.pi * 0.5, ov, dtype=np.float32)
                    music[pos - ov:pos] = music[pos - ov:pos] * np.cos(t_xf) + raw[:ov] * np.sin(t_xf)
                rem = n - pos
                chunk = min(rem, max(0, len(raw) - ov))
                if chunk > 0:
                    music[pos:pos + chunk] = raw[ov:ov + chunk]
                    pos += chunk
                else:
                    break

    # Edge fades (0.15s fade-in, 0.60s fade-out)
    fi = min(int(0.15 * SR), n // 4)
    fo = min(int(0.60 * SR), n // 4)
    if fi > 0:
        music[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 0:
        music[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)

    # Smooth ramped comedy dip (0.12x) during rejection sequence b32..b37
    dip_beats = [b for b in beats_meta if b["id"] in ("b32_one_question", "b33_never_cooked", "b34_only_wrap", "b35_no_job", "b36_letter", "b37_almost")]
    if dip_beats:
        t0_dip = min(b["start"] for b in dip_beats)
        t1_dip = max(b["clip_end"] for b in dip_beats)
        i0 = max(0, int(round(t0_dip * SR)))
        i1 = min(n, int(round(t1_dip * SR)))
        ramp = int(0.15 * SR)
        env = np.ones(n, dtype=np.float32)
        env[i0:i1] = 0.12
        r0 = max(0, i0 - ramp)
        if i0 > r0:
            env[r0:i0] = np.linspace(1.0, 0.12, i0 - r0, dtype=np.float32)
        r1 = min(n, i1 + ramp)
        if r1 > i1:
            env[i1:r1] = np.linspace(0.12, 1.0, r1 - i1, dtype=np.float32)
        music *= env

    return music


def main():
    beats_data = json.loads((PROJ_DIR / "voice" / "beats.json").read_text(encoding="utf-8"))
    vo = load_wav_mono(PROJ_DIR / "voice" / "vo_master.wav")
    n = len(vo)
    total_dur = n / SR

    music = load_song_bed(total_dur, beats_data["beats"])
    sfx = np.zeros(n, dtype=np.float32)

    whoosh = load_wav_mono(ASSETS_SFX / "whoosh.wav") if (ASSETS_SFX / "whoosh.wav").exists() else synth_paper_fold(0.20)
    riser_hit = load_wav_mono(ASSETS_SFX / "riser_hit.wav") if (ASSETS_SFX / "riser_hit.wav").exists() else synth_pop_impact()
    ui_click = load_wav_mono(ASSETS_SFX / "ui_click.wav") if (ASSETS_SFX / "ui_click.wav").exists() else synth_ding(1400.0, 0.08)

    alarm = synth_alarm_bell()
    horn = synth_party_horn()
    sizzle = synth_grill_sizzle(1.6)
    scratch = synth_record_scratch()
    pop = synth_pop_impact()

    for idx, b in enumerate(beats_data["beats"]):
        bid = b["id"]
        ts, te = b["start"], b["end"]

        # Pre-cut 2-4f whoosh transitions on major scene switches
        if bid in ("b02_except_me", "b10_bun_town", "b21_come_out", "b26_interview", "b38_so_tonight", "b42_hired", "b45_midnight_rush", "b49_mayor_stared"):
            add_at(sfx, whoosh, max(0.0, ts - 0.08), gain=0.22)

        # Ultra-subtle tactile paper slap under the real MyInstants HUSS SFX so it never muddies
        for hi, ht in enumerate(b.get("huss_hit_times", [])):
            add_at(sfx, synth_paper_fold(0.12, seed=idx * 10 + hi), ht + 0.01, gain=0.10)

        if bid in ("b12_5am_wrist", "b40_5am_200"):
            add_at(sfx, alarm, ts, gain=0.26)
        elif bid in ("b15_fold_tuck", "b24_fold_fast"):
            for k in range(4):
                add_at(sfx, synth_paper_fold(0.12, seed=k + 30), ts + k * 0.34, gain=0.28)
        elif bid == "b16_four_sec":
            for k in range(4):
                add_at(sfx, ui_click, ts + k * 0.35, gain=0.22)
        elif bid == "b21_come_out":
            add_at(sfx, horn, ts + 0.04, gain=0.24)
        elif bid in ("b29_already_wrap", "b30_clipboard_tie"):
            add_at(sfx, pop, ts + 0.05, gain=0.34)
            if bid == "b30_clipboard_tie":
                add_at(sfx, pop, ts + 1.05, gain=0.36)
        elif bid == "b32_one_question":
            add_at(sfx, scratch, ts + 1.08, gain=0.30)
        elif bid in ("b39_learning_cook", "b41_huss_cook"):
            add_at(sfx, sizzle, ts, gain=0.22)
        elif bid == "b45_midnight_rush":
            add_at(sfx, riser_hit, ts, gain=0.24)
        elif bid == "b48_400_burgers":
            for k in range(6):
                add_at(sfx, synth_ding(960 + k * 140, 0.14), ts + k * 0.16, gain=0.24)

    # Smooth voice-envelope sidechain ducking (<= -7 dB under speech!)
    win = int(0.08 * SR)
    env = np.convolve(np.abs(vo), np.ones(win, dtype=np.float32) / win, mode="same")
    duck = np.where(env > 0.015, 0.22, 0.56).astype(np.float32)
    duck = np.convolve(duck, np.ones(int(0.07 * SR), dtype=np.float32) / int(0.07 * SR), mode="same")

    bed = music * duck + sfx * 0.85
    # Verify bed RMS <= -7 dB relative to voice RMS while voice active
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
