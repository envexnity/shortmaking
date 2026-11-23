"""
audio_mix.py — Multi-layered Roblox Storytime Audio Mix & Mastering for Df1kubCJ-o0 Remake.
Combines:
  - Fish Audio S2-Pro master narration (voice/vo_master.wav, model 5355e61fa47849b4bac5a3417837eb58)
  - Synthesized upbeat comedic Roblox marimba/synth/percussion music bed (with dramatic drop-outs)
  - Synced Foley SFX (paper wrap crinkles, 2-4f pre-cut whooshes, 5AM alarm bell, stopwatch tick,
    party horn, pop-wrap impacts, record scratch, grill sizzle, burger counter dings)
  - Smooth voice-envelope sidechain ducking (-6 dB gated RMS) + FFmpeg -14 LUFS / -1.0 dBTP mastering.
"""
import json
import math
import subprocess
import wave
from pathlib import Path

import numpy as np

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0"
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


def synth_paper_crinkle(dur=0.18, seed=1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    noise = rng.standard_normal(n).astype(np.float32)
    # High-passed snappy crinkle (1-pole diff + burst envelope)
    hp = np.diff(noise, prepend=0.0)
    hp = np.diff(hp, prepend=0.0)
    env = np.exp(-t * 22.0) * (0.5 + 0.5 * np.sin(2 * np.pi * 38.0 * t))
    thud = np.sin(2 * np.pi * 88.0 * t * np.exp(-t * 6.0)) * np.exp(-t * 26.0) * 0.45
    out = hp * env * 0.65 + thud
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_pop_impact(freq0=180.0, freq1=58.0, dur=0.22) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = freq0 * (freq1 / freq0) ** (t / dur)
    phase = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(phase) * np.exp(-t * 18.0)
    snap = np.sin(2 * np.pi * 2400.0 * t) * np.exp(-t * 90.0) * 0.45
    out = sub + snap
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_alarm_bell(dur=0.55) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    ring = (np.sin(2 * np.pi * 1650 * t) + 0.6 * np.sin(2 * np.pi * 3320 * t)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 18 * t)))
    env = np.exp(-t * 3.5)
    out = ring * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_party_horn(dur=0.42) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 460.0 + 180.0 * np.sin(np.pi * t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    # Sawtooth-like cheerful kazoo horn
    wave_s = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.35 * np.sin(3 * ph) + 0.2 * np.sin(4 * ph)
    env = np.minimum(1.0, t / 0.03) * np.exp(-np.maximum(0.0, t - 0.12) * 5.0)
    out = wave_s * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_grill_sizzle(dur=1.4, seed=7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    noise = rng.standard_normal(n).astype(np.float32)
    hp = np.diff(noise, prepend=0.0)
    mod = 0.65 + 0.35 * np.sin(2 * np.pi * 9.0 * t)
    env = np.minimum(1.0, t / 0.1) * np.minimum(1.0, (dur - t) / 0.25)
    out = hp * mod * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_ding(freq=1175.0, dur=0.18) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    out = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2.0 * t)) * np.exp(-t * 16.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_record_scratch(dur=0.28) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 950.0 * np.exp(-t * 9.0) + 120.0
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.sign(np.sin(ph)) * np.sin(ph * 0.5) * np.exp(-t * 6.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_upbeat_roblox_music(total_dur: float, beats_meta: list) -> np.ndarray:
    """
    Quirky, high-energy Roblox storytime marimba + bouncy bass + crisp hi-hat underscore (126 BPM).
    Drops to near silence on dramatic punchlines (b32_one_question, b35_no_job, b37_almost) for contrast!
    """
    n = int(math.ceil(total_dur * SR))
    music = np.zeros(n, dtype=np.float32)
    bpm = 126.0
    step = 60.0 / bpm / 2.0  # 8th note (~0.238s)

    # Playful C-major / A-minor comedic progression (C5, E5, G5, A5, F5, D5...)
    melody = [523.25, 659.25, 783.99, 659.25, 587.33, 698.46, 880.00, 783.99,
              440.00, 523.25, 659.25, 523.25, 493.88, 587.33, 783.99, 659.25]
    bass   = [130.81, 130.81, 164.81, 164.81, 174.61, 174.61, 196.00, 196.00]

    rng = np.random.default_rng(101)
    num_steps = int(total_dur / step) + 1
    for s in range(num_steps):
        t0 = s * step
        # Marimba pluck on melody
        f = melody[s % len(melody)]
        nd = int(0.18 * SR)
        tt = np.linspace(0, 0.18, nd, dtype=np.float32)
        pluck = (np.sin(2 * np.pi * f * tt) + 0.22 * np.sin(2 * np.pi * f * 2 * tt)) * np.exp(-tt * 22.0)
        add_at(music, pluck, t0, gain=0.18 if s % 2 == 0 else 0.12)

        # Warm bouncy bass on quarter notes
        if s % 2 == 0:
            bf = bass[(s // 2) % len(bass)]
            nb = int(0.24 * SR)
            tb = np.linspace(0, 0.24, nb, dtype=np.float32)
            bnote = np.sin(2 * np.pi * bf * tb) * np.exp(-tb * 9.0)
            add_at(music, bnote, t0, gain=0.22)

        # Soft tick hi-hat on off-beats
        if s % 2 == 1:
            nh = int(0.04 * SR)
            th = np.linspace(0, 0.04, nh, dtype=np.float32)
            hat = np.diff(rng.standard_normal(nh).astype(np.float32), prepend=0.0) * np.exp(-th * 85.0)
            add_at(music, hat, t0, gain=0.045)

    # Apply dramatic comedy music drop-outs (-24 dB) on the rejection / question beats!
    for b in beats_meta:
        if b["id"] in ("b32_one_question", "b33_never_cooked", "b35_no_job", "b36_letter", "b37_almost"):
            i0 = max(0, int(b["start"] * SR))
            i1 = min(n, int(b["clip_end"] * SR))
            music[i0:i1] *= 0.12

    return music


def main():
    beats_data = json.loads((PROJ_DIR / "voice" / "beats.json").read_text(encoding="utf-8"))
    vo = load_wav_mono(PROJ_DIR / "voice" / "vo_master.wav")
    n = len(vo)
    total_dur = n / SR

    music = synth_upbeat_roblox_music(total_dur, beats_data["beats"])
    sfx = np.zeros(n, dtype=np.float32)

    whoosh = load_wav_mono(ASSETS_SFX / "whoosh.wav") if (ASSETS_SFX / "whoosh.wav").exists() else synth_paper_crinkle(0.22)
    whoosh_low = load_wav_mono(ASSETS_SFX / "whoosh_low.wav") if (ASSETS_SFX / "whoosh_low.wav").exists() else synth_pop_impact()
    ui_click = load_wav_mono(ASSETS_SFX / "ui_click.wav") if (ASSETS_SFX / "ui_click.wav").exists() else synth_ding()

    # Spot SFX onto every single comedic beat (with 2-4 frame pre-cut whoosh lead-ins!)
    lead = 0.09  # ~3 frames @ 30fps
    for i, b in enumerate(beats_data["beats"]):
        bid = b["id"]
        ts = b["start"]
        te = b["end"]
        dur = b["duration"]

        # Pre-cut whoosh on major environment / punchline cuts
        if i > 0 and bid in (
            "b02_except_me", "b04_party_any", "b08_preparing", "b10_bun_town",
            "b14_no_breakfast", "b20_neighbor", "b26_interview", "b35_no_job",
            "b38_so_tonight", "b42_hired", "b44_first_shift", "b45_midnight_rush",
            "b48_400_burgers", "b50_final_callback",
        ):
            add_at(sfx, whoosh, max(0.0, ts - lead), gain=0.22)

        # HUSS! rapid paper wrap crinkle & rhythmic snap bursts
        if "huss" in bid:
            for k in range(6):
                tk = ts + (k / 6.0) * dur
                add_at(sfx, synth_paper_crinkle(0.15, seed=10 + i * 7 + k), tk, gain=0.40)

        # Party horn on party beats
        if bid in ("b01_hook_town", "b05_birthday_tue", "b20_neighbor", "b44_first_shift", "b45_midnight_rush"):
            add_at(sfx, synth_party_horn(0.38), ts + 0.12, gain=0.20)

        # Alarm clock ring on 5 AM beats
        if bid in ("b12_5am_wrist", "b40_5am_200"):
            add_at(sfx, synth_alarm_bell(0.50), ts + 0.05, gain=0.26)

        # Fold, fold, tuck, roll crinkles
        if bid in ("b15_fold_tuck", "b24_fold_fast"):
            for k in range(4):
                add_at(sfx, synth_paper_crinkle(0.14, seed=50 + k), ts + k * (dur / 4.2), gain=0.35)

        # Stopwatch tick + sad pop on 4 seconds too slow
        if bid == "b16_four_sec":
            add_at(sfx, ui_click, ts + 0.05, gain=0.35)
            add_at(sfx, synth_pop_impact(220, 75, 0.24), ts + dur * 0.55, gain=0.38)

        # Instant POP-WRAP punchline impacts!
        if bid in ("b29_already_wrap", "b30_clipboard_tie"):
            add_at(sfx, synth_pop_impact(260, 65, 0.22), ts + 0.04, gain=0.45)
            add_at(sfx, synth_paper_crinkle(0.16, seed=99), ts + 0.04, gain=0.42)
            if bid == "b30_clipboard_tie":
                add_at(sfx, synth_pop_impact(280, 62, 0.22), ts + dur * 0.52, gain=0.48)
                add_at(sfx, synth_paper_crinkle(0.16, seed=100), ts + dur * 0.52, gain=0.45)

        # Dramatic record scratch on "Can you cook a burger?" and "I did not get the job."
        if bid in ("b32_one_question", "b35_no_job"):
            add_at(sfx, synth_record_scratch(0.28), ts, gain=0.32)

        # Grill sizzle on cooking montage beats
        if bid in ("b34_only_wrap", "b39_learning_cook", "b40_5am_200", "b41_huss_cook"):
            add_at(sfx, synth_grill_sizzle(min(dur, 1.5), seed=200 + i), ts, gain=0.20)

        # Accelerating 001 -> 400 counter dings on "400 burgers. One minute."!
        if bid == "b48_400_burgers":
            for k in range(10):
                tk = ts + (k / 10.0) * dur
                add_at(sfx, synth_ding(900.0 + k * 85.0, 0.14), tk, gain=0.30)

        # Dramatic bass drop on stunned Mayor
        if bid == "b49_mayor_stared":
            add_at(sfx, whoosh_low, ts, gain=0.34)

    # Smooth voice-activity sidechain ducking envelope (-6 dB gated RMS under speech!)
    win = int(0.08 * SR)
    vo_env = np.convolve(np.abs(vo), np.ones(win, dtype=np.float32) / win, mode="same")
    speech_mask = np.clip(vo_env / (np.percentile(vo_env, 85) + 1e-6), 0.0, 1.0)
    duck = 1.0 - 0.52 * speech_mask  # Ducks music smoothly under voice!

    mix = vo * 0.96 + (music * duck) * 0.34 + sfx * 0.48
    peak = np.max(np.abs(mix)) + 1e-6
    if peak > 0.96:
        mix = mix / peak * 0.95

    raw_mix = AUDIO_DIR / "mix_raw.wav"
    with wave.open(str(raw_mix), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((mix * 32767.0).astype(np.int16).tobytes())

    # Master to broadcast -14.0 LUFS / -1.0 dBTP via FFmpeg loudnorm
    final_mix = AUDIO_DIR / "mix.wav"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(raw_mix),
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=7",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        str(final_mix),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Mastered audio (-14 LUFS, -1.0 dBTP) -> {final_mix} ({total_dur:.2f}s)")


if __name__ == "__main__":
    main()
