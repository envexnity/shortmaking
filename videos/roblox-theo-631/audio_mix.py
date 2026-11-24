"""
audio_mix.py — Multi-Layer Storytime Audio Mix & Two-Pass -14 LUFS Master for roblox-theo-631.
Combines:
  - voice/vo_master.wav (single Fish Audio Roblox narrator + real 3-hit HUSS + deeper Dad twist)
  - TEMPOREX "Numbers" bed (sidechain-ducked -7 dB under voice, abrupt record-scratch cut on Dad twist)
  - 2-4 frame pre-cut whooshes, wooden door slam, house-shake sub-thuds, stat card ding/pop,
    4-tone race countdown, liquid tail-whip swishes, cartoon bonk (#42), zap/sizzle (#12),
    heartbeat + riser into golden egg shimmer, hospital monitor pings, and Dad vine-boom sub-drop.
  - Two-pass FFmpeg loudnorm (I=-14.0, TP=-1.0, LRA=11) -> audio/mix.wav
"""
import json
import math
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
REF_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2"
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-theo-631"
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


def synth_pop_impact(freq0=220.0, freq1=54.0, dur=0.25) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = freq0 * (freq1 / freq0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 15.0)
    click = np.sin(2 * np.pi * 1900.0 * t) * np.exp(-t * 85.0) * 0.32
    out = sub + click
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_door_slam(dur=0.30, seed=11) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    wood = np.sin(2 * np.pi * (145.0 * np.exp(-t * 14.0)) * t) * np.exp(-t * 16.0)
    thud = np.sin(2 * np.pi * (72.0 * np.exp(-t * 8.0)) * t) * np.exp(-t * 11.0) * 0.8
    snap = np.diff(rng.standard_normal(n).astype(np.float32), prepend=0.0) * np.exp(-t * 48.0) * 0.35
    out = wood + thud + snap
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_sub_thud(freq=65.0, dur=0.24) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    out = np.sin(2 * np.pi * (freq * np.exp(-t * 5.0)) * t) * np.exp(-t * 13.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_race_tone(freq=440.0, dur=0.14, is_go=False) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    env = np.minimum(1.0, t / 0.008) * np.exp(-t * (8.0 if is_go else 14.0))
    if is_go:
        sig = (
            np.sin(2 * np.pi * 880.0 * t) * 0.65
            + np.sin(2 * np.pi * 1318.5 * t) * 0.45
            + np.sin(2 * np.pi * 1760.0 * t) * 0.25
        )
    else:
        sig = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 2.0 * t)
    out = sig * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_liquid_swish(dur=0.22, seed=5) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    noise = rng.standard_normal(n).astype(np.float32)
    sm = np.convolve(noise, np.hanning(33), mode="same")
    bp = np.diff(sm, prepend=0.0)
    env = np.maximum(0.0, np.sin(np.pi * t / dur)) ** 1.2
    out = bp * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_cartoon_bonk(dur=0.26) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 420.0 * np.exp(-t * 11.0) + 120.0
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.sin(ph) * np.exp(-t * 13.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_cooked_zap(dur=0.30, seed=9) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 680.0 * np.exp(-t * 6.5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    buzz = (np.sign(np.sin(ph)) * 0.45 + np.sin(ph) * 0.45) * np.exp(-t * 10.0)
    sizzle = np.diff(rng.standard_normal(n).astype(np.float32), prepend=0.0) * np.exp(-t * 9.0) * 0.40
    out = buzz + sizzle
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_dream_shimmer(dur=1.4) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    out = (
        np.sin(2 * np.pi * 523.25 * t) * 0.40
        + np.sin(2 * np.pi * 659.25 * t) * 0.35
        + np.sin(2 * np.pi * 783.99 * t) * 0.30
        + np.sin(2 * np.pi * 1046.50 * t) * 0.22
    ) * (np.maximum(0.0, np.sin(np.pi * t / dur)) ** 1.2)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_monitor_beep(dur=0.14, freq=880.0) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    out = np.sin(2 * np.pi * freq * t) * np.minimum(1.0, t / 0.008) * np.exp(-t * 11.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_record_scratch(dur=0.28, seed=13) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 920.0 * (1.0 - 0.72 * (t / dur)) + 160.0 * np.sin(2 * np.pi * 28.0 * t)
    ph = 2 * np.pi * np.cumsum(np.maximum(60.0, f)) / SR
    scratch = np.sin(ph) * 0.65 + np.diff(rng.standard_normal(n).astype(np.float32), prepend=0.0) * 0.35
    env = np.minimum(1.0, t / 0.015) * np.exp(-t * 8.5)
    out = scratch * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_vine_boom(dur=0.75) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 98.0 * np.exp(-t * 3.8) + 46.0
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.minimum(1.0, t / 0.006) * np.exp(-t * 4.2)
    punch = np.sin(2 * np.pi * 165.0 * t) * np.exp(-t * 28.0) * 0.35
    out = sub + punch
    return out / (np.max(np.abs(out)) + 1e-6)


def load_song_bed(total_dur: float, cut_at_sec: float) -> np.ndarray:
    song_path = REF_DIR / "audio" / "song_numbers.mp3"
    raw = load_wav_mono(song_path)
    r = float(np.sqrt(np.mean(raw ** 2)) + 1e-9)
    raw = raw * (0.14 / r)

    n = int(math.ceil(total_dur * SR))
    if len(raw) >= n:
        music = raw[:n].copy()
    else:
        music = np.resize(raw, n).astype(np.float32)

    fi = min(int(0.15 * SR), n // 4)
    if fi > 0:
        music[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)

    # Abrupt comedy cut right as Dad starts his twist line!
    cut_idx = min(n, max(0, int(round(cut_at_sec * SR))))
    fade_cut = min(int(0.04 * SR), cut_idx)
    if fade_cut > 0:
        music[cut_idx - fade_cut:cut_idx] *= np.linspace(1.0, 0.0, fade_cut, dtype=np.float32)
    if cut_idx < n:
        music[cut_idx:] = 0.0
    return music


def find_word_time(words: list[dict], target: str, default_t: float, after: float = 0.0) -> float:
    tgt = target.lower()
    for w in words:
        clean = re.sub(r"[^a-z0-9]", "", w["word"].lower())
        if clean == tgt and w["start"] >= after:
            return float(w["start"])
    return default_t


def two_pass_loudnorm(inp: Path, out: Path, target_i: float = -14.0, target_tp: float = -1.0):
    p1 = subprocess.run(
        ["ffmpeg", "-hide_banner", "-y", "-i", str(inp), "-af",
         f"loudnorm=I={target_i}:TP={target_tp}:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    m = re.search(r"\{[\s\S]*?\}", p1.stderr)
    if not m:
        raise RuntimeError(f"loudnorm pass 1 failed:\n{p1.stderr}")
    stats = json.loads(m.group(0))
    af = (
        f"loudnorm=I={target_i}:TP={target_tp}:LRA=11:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true:print_format=summary"
    )
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-y", "-i", str(inp), "-af", af,
         "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(out)],
        check=True, capture_output=True,
    )


def main():
    beats_data = json.loads((PROJ_DIR / "voice" / "beats.json").read_text(encoding="utf-8"))
    words = json.loads((PROJ_DIR / "voice" / "words.json").read_text(encoding="utf-8"))
    beats = {b["id"]: b for b in beats_data["beats"]}

    vo = load_wav_mono(PROJ_DIR / "voice" / "vo_master.wav")
    n = len(vo)
    total_dur = n / SR

    b10_start = beats["b10_dad_twist"]["start"]
    music = load_song_bed(total_dur, cut_at_sec=max(0.0, b10_start - 0.04))
    sfx = np.zeros(n, dtype=np.float32)

    whoosh = load_wav_mono(ASSETS_SFX / "whoosh.wav")
    whoosh_low = load_wav_mono(ASSETS_SFX / "whoosh_low.wav")
    ding = load_wav_mono(ASSETS_SFX / "ding.wav")
    ui_click = load_wav_mono(ASSETS_SFX / "ui_click.wav")
    heartbeat = load_wav_mono(ASSETS_SFX / "heartbeat.wav")
    riser_hit = load_wav_mono(ASSETS_SFX / "riser_hit.wav")

    # 1. 2-4 frame (0.08s) pre-cut whooshes on major scene/angle cuts
    for bid in ("b03_deadliest_race", "b04_theo_intro", "b05_countdown_go",
                "b06_dropping", "b07_neck_and_neck", "b08_climax_win",
                "b09_hospital_doctor", "b10_dad_twist"):
        ts = beats[bid]["start"]
        add_at(sfx, whoosh if bid != "b03_deadliest_race" else whoosh_low, max(0.0, ts - 0.08), gain=0.24)

    # 2. b01 door slam right before b02_huss
    add_at(sfx, synth_door_slam(), max(0.0, beats["b02_huss"]["start"] - 0.14), gain=0.38)

    # 3. b02 house-shake sub-thuds synced to the 3 HUSS hits
    for ht in beats["b02_huss"].get("huss_hit_times", []):
        add_at(sfx, synth_sub_thud(64.0, 0.24), ht, gain=0.38)

    # 4. b04 stat card pop / ding
    b04s = beats["b04_theo_intro"]["start"]
    add_at(sfx, ui_click, b04s + 0.02, gain=0.28)
    add_at(sfx, ding, b04s + 0.06, gain=0.20)

    # 5. b05 4-tone race countdown + launch boost
    for tk in beats["b05_countdown_go"].get("countdown_ticks", []):
        is_go = "GO" in tk["label"]
        add_at(sfx, synth_race_tone(440.0, 0.22 if is_go else 0.13, is_go=is_go), tk["start"], gain=0.34 if is_go else 0.28)
        if is_go:
            add_at(sfx, whoosh, tk["start"], gain=0.30)

    # 6. b06 liquid tail-whips + Sperm 42 Gone (bonk) + Sperm 12 Cooked (zap) + dodge impacts
    b06s, b06e = beats["b06_dropping"]["start"], beats["b06_dropping"]["end"]
    t_sw = b06s + 0.15
    k = 0
    while t_sw < b06e - 0.30:
        add_at(sfx, synth_liquid_swish(0.20, seed=30 + k), t_sw, gain=0.22)
        t_sw += 0.95
        k += 1
    t_42 = find_word_time(words, "42", b06s + 3.0, after=b06s)
    t_gone = find_word_time(words, "gone", t_42 + 0.35, after=t_42)
    t_12 = find_word_time(words, "12", t_gone + 0.35, after=t_gone)
    t_cooked = find_word_time(words, "cooked", t_12 + 0.35, after=t_12)
    add_at(sfx, synth_cartoon_bonk(), t_gone, gain=0.36)
    add_at(sfx, synth_pop_impact(210.0, 58.0, 0.22), t_42 + 0.20, gain=0.26)
    add_at(sfx, synth_cooked_zap(), t_cooked, gain=0.34)
    add_at(sfx, synth_pop_impact(240.0, 62.0, 0.20), b06s + 1.65, gain=0.26)

    # 7. b07 + b08 heartbeat, riser, egg contact impact, and celestial white-light shimmer
    b07s = beats["b07_neck_and_neck"]["start"]
    b08s = beats["b08_climax_win"]["start"]
    b08e = beats["b08_climax_win"]["end"]
    add_at(sfx, heartbeat, b07s, gain=0.26)
    add_at(sfx, riser_hit, max(b08s, b08s + 0.4), gain=0.26)
    t_won = find_word_time(words, "won", b08s + 1.5, after=b08s)
    add_at(sfx, synth_pop_impact(240.0, 50.0, 0.32), t_won - 0.04, gain=0.40)
    add_at(sfx, synth_dream_shimmer(1.35), max(b08s, b08e - 0.55), gain=0.26)

    # 8. b09 hospital monitor pings
    b09s = beats["b09_hospital_doctor"]["start"]
    add_at(sfx, synth_monitor_beep(0.14, 960.0), b09s + 0.15, gain=0.18)
    add_at(sfx, synth_monitor_beep(0.14, 960.0), b09s + 1.25, gain=0.18)

    # 9. b10 record scratch + vine boom drop on blonde hair punchline
    add_at(sfx, synth_record_scratch(0.28), max(0.0, b10_start - 0.06), gain=0.34)
    t_blonde = find_word_time(words, "blonde", b10_start + 1.2, after=b10_start)
    add_at(sfx, synth_vine_boom(0.75), t_blonde, gain=0.44)

    # Smooth voice-envelope sidechain ducking (-7 dB under speech)
    win = int(0.08 * SR)
    env = np.convolve(np.abs(vo), np.ones(win, dtype=np.float32) / win, mode="same")
    duck = np.where(env > 0.015, 0.22, 0.56).astype(np.float32)
    duck = np.convolve(duck, np.ones(int(0.07 * SR), dtype=np.float32) / int(0.07 * SR), mode="same")

    bed = music * duck + sfx * 0.88
    active = env > 0.02
    if np.any(active):
        v_rms = float(np.sqrt(np.mean(vo[active] ** 2)) + 1e-9)
        b_rms = float(np.sqrt(np.mean(bed[active] ** 2)) + 1e-9)
        target_b = v_rms * 0.44
        if b_rms > target_b:
            bed *= (target_b / b_rms)

    mix_raw = np.clip(np.nan_to_num(vo + bed), -0.98, 0.98)
    raw_wav = AUDIO_DIR / "mix_raw.wav"
    pcm = (mix_raw * 32767.0).astype(np.int16)
    with wave.open(str(raw_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

    mix_wav = AUDIO_DIR / "mix.wav"
    two_pass_loudnorm(raw_wav, mix_wav, target_i=-14.0, target_tp=-1.0)
    print(f"STEP 2 AUDIO MASTER COMPLETE -> {mix_wav} ({total_dur:.2f}s)")


if __name__ == "__main__":
    main()
