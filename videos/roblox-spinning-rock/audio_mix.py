"""
audio_mix.py — Multi-Layered Storytime Audio Mix & Mastering for roblox-spinning-rock.
Combines:
  - Single-voice Fish Audio S2-Pro master VO (voice/vo_master.wav)
  - TEMPOREX "Numbers" bed (videos/roblox-reel-Df1kubCJ-o0-v2/audio/song_numbers.mp3)
    with sudden brake-screech / record-scratch stop at b11_hit_brakes!
  - Synced Foley SFX (2-4f pre-cut whooshes on all cuts + sub-cuts, gravity magnetic lock thud,
    orbital space whoosh, merry-go-round/rollercoaster clack, dog bark, car horn honk,
    brake-stop screech + 65Hz sub drop + launch blast!)
  - Smooth voice-envelope sidechain ducking (<= -7 dB under speech) + FFmpeg -14 LUFS / -1.0 dBTP mastering.
"""
import json
import math
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-spinning-rock"
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


def synth_pop_impact(freq0: float = 230.0, freq1: float = 55.0, dur: float = 0.24) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = freq0 * (freq1 / freq0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 15.0)
    click = np.sin(2 * np.pi * 1900.0 * t) * np.exp(-t * 85.0) * 0.32
    out = sub + click
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_magnet_lock(dur: float = 0.28) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    thud = np.sin(2 * np.pi * (180.0 * np.exp(-t * 14.0) + 48.0) * t) * np.exp(-t * 14.0)
    hum = (np.sin(2 * np.pi * 420.0 * t) + 0.4 * np.sin(2 * np.pi * 840.0 * t)) * np.exp(-t * 16.0) * 0.4
    out = thud + hum
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_space_sweep(dur: float = 0.75, seed: int = 3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    noise = rng.standard_normal(n).astype(np.float32)
    smooth = np.convolve(noise, np.hanning(35), mode="same")
    air = np.diff(smooth, prepend=0.0) * 5.0
    env = np.maximum(0.0, np.sin(np.pi * t / dur)) ** 1.3
    sub = np.sin(2 * np.pi * (75.0 + 45.0 * (t / dur)) * t) * env * 0.35
    out = air * env + sub
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_coaster_clack(dur: float = 0.14) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    out = (np.sin(2 * np.pi * 620.0 * t) + 0.5 * np.sin(2 * np.pi * 1240.0 * t)) * np.exp(-t * 28.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_dog_bark(dur: float = 0.16) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 420.0 - 190.0 * (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = (np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)) * np.minimum(1.0, t / 0.015) * np.exp(-t * 14.0)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_car_horn(dur: float = 0.26) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    w = np.sin(2 * np.pi * 392.0 * t) + 0.85 * np.sin(2 * np.pi * 494.0 * t) + 0.35 * np.sin(2 * np.pi * 784.0 * t)
    env = np.minimum(1.0, t / 0.012) * np.minimum(1.0, (dur - t) / 0.03)
    out = np.tanh(w * 1.4) * env
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_record_scratch(dur: float = 0.30) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 1020.0 * np.exp(-t * 8.5) + 105.0
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.sign(np.sin(ph)) * np.sin(ph * 0.5) * np.exp(-t * 6.5)
    return out / (np.max(np.abs(out)) + 1e-6)


def synth_launch_blast(dur: float = 0.85, seed: int = 9) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 190.0 * np.exp(-t * 6.5) + 42.0
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 3.8)
    noise = np.convolve(rng.standard_normal(n).astype(np.float32), np.hanning(17), mode="same")
    whoosh = noise * np.minimum(1.0, t / 0.03) * np.exp(-t * 3.2) * 0.55
    out = sub + whoosh
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

    # Cut music cleanly right before "if the rock ever hits the brakes" / b11_hit_brakes midpoint!
    b11 = next((b for b in beats_meta if b["id"] == "b11_hit_brakes"), None)
    if b11 is not None:
        t_brake = b11["start"] + 1.25
        i_cut = max(0, int(round(t_brake * SR)))
        fade_len = int(0.10 * SR)
        i0 = max(0, i_cut - fade_len)
        if i_cut > i0:
            music[i0:i_cut] *= np.linspace(1.0, 0.0, i_cut - i0, dtype=np.float32)
        music[i_cut:] = 0.0

    fi = min(int(0.10 * SR), n // 4)
    if fi > 0:
        music[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    return music


def main():
    beats_data = json.loads((PROJ_DIR / "voice" / "beats.json").read_text(encoding="utf-8"))
    beats = {b["id"]: b for b in beats_data["beats"]}
    vo = load_wav_mono(PROJ_DIR / "voice" / "vo_master.wav")
    n = len(vo)
    total_dur = n / SR

    music = load_song_bed(total_dur, beats_data["beats"])
    sfx = np.zeros(n, dtype=np.float32)

    whoosh = load_wav_mono(ASSETS_SFX / "whoosh.wav")
    whoosh_low = load_wav_mono(ASSETS_SFX / "whoosh_low.wav")
    riser_hit = load_wav_mono(ASSETS_SFX / "riser_hit.wav")
    ui_click = load_wav_mono(ASSETS_SFX / "ui_click.wav")

    pop_imp = synth_pop_impact()
    mag_lock = synth_magnet_lock()
    space_sw = synth_space_sweep()
    clack = synth_coaster_clack()
    bark = synth_dog_bark()
    horn = synth_car_horn()
    scratch = synth_record_scratch()
    blast = synth_launch_blast()

    # 2-4 frame (0.08s) pre-cut whooshes on every cut + subtle frame-0 impact weight
    for i, b in enumerate(beats_data["beats"]):
        if i == 0:
            add_at(sfx, pop_imp, 0.02, 0.24)
            continue
        ts = b["start"]
        add_at(sfx, whoosh_low if b["shot"].startswith("set2") else whoosh, ts - 0.08, 0.16)
        add_at(sfx, pop_imp, ts, 0.14)

    # Beat-specific storytelling Foley
    add_at(sfx, space_sw, beats["b01b_spin_1000"]["start"], 0.24)
    # Gravity lock thud on "gluing your shoes"
    add_at(sfx, mag_lock, beats["b03_glue_force"]["start"] + 2.30, 0.28)
    # 67,000 mph orbit sweep
    add_at(sfx, space_sw, beats["b05_orbit_sun"]["start"] + 0.15, 0.26)
    add_at(sfx, whoosh_low, beats["b06_expanding_void"]["start"] + 0.20, 0.22)
    # Merry-go-round / rollercoaster rhythmic clacks
    t_mgr = beats["b07_merry_go_round"]["start"]
    for k in range(6):
        add_at(sfx, clack, t_mgr + 0.35 + k * 0.42, 0.14)
    # Dog bark (x2) & Car horn (x2)
    add_at(sfx, bark, beats["b09_casual_dog"]["start"] + 1.35, 0.22)
    add_at(sfx, bark, beats["b09_casual_dog"]["start"] + 1.56, 0.18)
    add_at(sfx, ui_click, beats["b10a_paying_taxes"]["start"] + 0.15, 0.22)
    add_at(sfx, horn, beats["b10b_arguing_traffic"]["start"] + 0.25, 0.18)
    add_at(sfx, horn, beats["b10b_arguing_traffic"]["start"] + 0.56, 0.14)

    # Record scratch / brake halt on "hits the brakes", then huge launch blast on b12!
    t_brake = beats["b11_hit_brakes"]["start"] + 1.25
    add_at(sfx, scratch, t_brake, 0.34)
    add_at(sfx, riser_hit, beats["b12_launched_space"]["start"] - 0.65, 0.20)
    add_at(sfx, blast, beats["b12_launched_space"]["start"], 0.42)

    # Smooth voice-envelope sidechain ducking (~ -7 dB under active speech)
    vo_abs = np.abs(vo)
    win = int(0.08 * SR)
    env = np.convolve(vo_abs, np.ones(win, dtype=np.float32) / win, mode="same")
    duck = np.where(env > 0.014, 0.30, 0.64).astype(np.float32)
    smooth_win = int(0.06 * SR)
    duck = np.convolve(duck, np.ones(smooth_win, dtype=np.float32) / smooth_win, mode="same")

    bed = music * duck + sfx
    bed_rms = float(np.sqrt(np.mean(bed ** 2)) + 1e-9)
    vo_rms = float(np.sqrt(np.mean(vo ** 2)) + 1e-9)
    max_bed_rms = vo_rms * 0.46  # <= -6.7 dB gated relative to voice
    if bed_rms > max_bed_rms:
        bed *= max_bed_rms / bed_rms

    mix = vo + bed
    pk = float(np.max(np.abs(mix)) + 1e-9)
    if pk > 0.94:
        mix *= 0.94 / pk

    raw_wav = AUDIO_DIR / "mix_raw.wav"
    pcm16 = (np.clip(mix, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(raw_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        stereo = np.stack([pcm16, pcm16], axis=1).reshape(-1)
        wf.writeframes(stereo.tobytes())

    # Two-pass EBU R128 loudnorm (-14.0 LUFS, -1.0 dBTP)
    p1 = subprocess.run(
        ["ffmpeg", "-y", "-i", str(raw_wav), "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=9:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    )
    m = re.search(r"\{[\s\S]*?\}", p1.stderr)
    st = json.loads(m.group(0))
    af = (
        f"loudnorm=I=-14.0:TP=-1.0:LRA=9:"
        f"measured_I={st['input_i']}:measured_TP={st['input_tp']}:"
        f"measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:"
        f"offset={st['target_offset']}:linear=true:print_format=summary"
    )
    final_wav = AUDIO_DIR / "mix.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(raw_wav), "-af", af, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(final_wav)],
        check=True, capture_output=True,
    )
    print(f"[OK] Master audio mixed & loudnormed -> {final_wav} ({total_dur:.2f}s)")


if __name__ == "__main__":
    main()
