"""
audio_mix.py — Track 7 Undershine Choose-a-World Audio Mix
(-14 LUFS, -6 dB gated ducking, 2-4f pre-cut whooshes, countdown ticks & world ambience).
"""
import os
import json
import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, filtfilt

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
AUDIO_DIR = os.path.join(BASE, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

SR = 48000


def load_audio_stereo(path: str, sr: int = SR) -> np.ndarray:
    tmp = os.path.join(AUDIO_DIR, "_tmp_decode.wav")
    subprocess.run(
        ["ffmpeg", "-y", "-i", path, "-ac", "2", "-ar", str(sr), "-f", "wav", tmp],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _, data = wavfile.read(tmp)
    os.remove(tmp)
    if data.dtype == np.int16:
        arr = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        arr = data.astype(np.float32) / 2147483648.0
    else:
        arr = data.astype(np.float32)
    if arr.ndim == 1:
        arr = np.stack([arr, arr], axis=1)
    return arr


def place_sfx(buf: np.ndarray, sfx: np.ndarray, t_sec: float, gain: float = 0.30):
    i0 = int(round(t_sec * SR))
    if i0 >= len(buf):
        return
    src_start = 0
    if i0 < 0:
        src_start = -i0
        i0 = 0
    n = min(len(sfx) - src_start, len(buf) - i0)
    if n > 0:
        buf[i0 : i0 + n] += sfx[src_start : src_start + n] * gain


def synth_world_ambience(n_samples: int, sections: dict) -> np.ndarray:
    """Subtle atmospheric soundscape shifting per world (cosmic hum -> desert wind -> canopy -> lake -> furnace)."""
    rng = np.random.default_rng(77)
    noise = rng.standard_normal(n_samples).astype(np.float32)

    b_lo, a_lo = butter(2, [65 / (SR * 0.5), 320 / (SR * 0.5)], btype="band")
    rumble = filtfilt(b_lo, a_lo, noise).astype(np.float32)
    rumble /= max(1e-5, np.max(np.abs(rumble)))

    b_mid, a_mid = butter(2, [350 / (SR * 0.5), 1400 / (SR * 0.5)], btype="band")
    wind = filtfilt(b_mid, a_mid, noise).astype(np.float32)
    wind /= max(1e-5, np.max(np.abs(wind)))

    t = np.arange(n_samples, dtype=np.float32) / SR
    bed_l = np.zeros(n_samples, dtype=np.float32)
    bed_r = np.zeros(n_samples, dtype=np.float32)

    w1_s = sections.get("world1", {}).get("start", 5.5)
    w2_s = sections.get("world2", {}).get("start", 18.0)
    w3_s = sections.get("world3", {}).get("start", 30.0)
    w4_s = sections.get("world4", {}).get("start", 42.0)

    # Subtle wind on World 1 & World 2
    wind_mask = np.where((t >= w1_s) & (t < w3_s), 1.0, 0.25).astype(np.float32)
    swell = (0.7 + 0.3 * np.sin(t * 0.8)) * wind_mask
    bed_l += wind * swell * 0.032
    bed_r += np.roll(wind, 1100) * swell * 0.032

    # Heavy volcanic furnace rumble on World 4 + deep sub-hum across space
    rumble_mask = np.where(t >= w4_s, 1.35, np.where(t < w1_s, 0.75, 0.45)).astype(np.float32)
    bed_l += rumble * rumble_mask * 0.045
    bed_r += np.roll(rumble, 700) * rumble_mask * 0.045

    # Gentle ember crackles in World 4
    tc = w4_s + 0.4
    fire = np.zeros(n_samples, dtype=np.float32)
    while tc < n_samples / SR - 0.15:
        idx = int(tc * SR)
        dur = int(rng.uniform(0.004, 0.013) * SR)
        if idx + dur < n_samples:
            pop = rng.standard_normal(dur).astype(np.float32)
            env = np.exp(-np.linspace(0, 6.0, dur, dtype=np.float32))
            fire[idx : idx + dur] += pop * env * rng.uniform(0.08, 0.18)
        tc += rng.uniform(0.08, 0.26)
    bf, af = butter(2, [1500 / (SR * 0.5), 6200 / (SR * 0.5)], btype="band")
    fire = filtfilt(bf, af, fire).astype(np.float32)
    return np.stack([bed_l + fire * 0.4, bed_r + fire * 0.5], axis=1)


def build_mix(cut_times_sec):
    voice_mp3 = os.path.join(BASE, "voice", "voice.mp3")
    words_path = os.path.join(BASE, "voice", "words.json")
    words_data = json.load(open(words_path, encoding="utf-8")) if os.path.exists(words_path) else {}
    sections = words_data.get("sections", {})
    words = words_data.get("words", [])

    vo = load_audio_stereo(voice_mp3)
    total_samples = len(vo) + int(0.85 * SR)
    vo_pad = np.zeros((total_samples, 2), dtype=np.float32)
    vo_pad[: len(vo)] = vo

    vo_rms = float(np.sqrt(np.mean(vo ** 2)) + 1e-6)
    vo_pad *= 0.19 / vo_rms

    # -6 dB gated RMS ducking envelope
    vo_mono = np.abs(vo_pad.mean(axis=1))
    win = int(0.08 * SR)
    env = np.convolve(vo_mono, np.ones(win, dtype=np.float32) / win, mode="same")
    duck = np.where(env > 0.025, 0.32, 0.54).astype(np.float32)
    b_l, a_l = butter(2, 5.0 / (SR * 0.5), btype="low")
    duck = np.clip(filtfilt(b_l, a_l, duck).astype(np.float32), 0.28, 0.58)

    # Music bed: Apathy (Slowed + Reverb) for moody retro-sci-fi mystery, fallback Snowfall
    music_path = os.path.join(ROOT, "assets", "music", "apathy_slowed_reverb.wav")
    if not os.path.exists(music_path):
        music_path = os.path.join(ROOT, "assets", "music", "snowfall_clip.wav")
    if os.path.exists(music_path):
        mus = load_audio_stereo(music_path)
        reps = int(np.ceil(total_samples / len(mus))) + 1
        mus = np.tile(mus, (reps, 1))[:total_samples]
        mus_rms = float(np.sqrt(np.mean(mus ** 2)) + 1e-6)
        mus *= 0.15 / mus_rms
        fi, fo = int(0.35 * SR), int(0.90 * SR)
        mus[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
        mus[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    else:
        mus = np.zeros((total_samples, 2), dtype=np.float32)

    amb = synth_world_ambience(total_samples, sections)
    sfx_buf = np.zeros((total_samples, 2), dtype=np.float32)

    w_hi_p = os.path.join(ROOT, "assets", "sfx", "whoosh.wav")
    w_lo_p = os.path.join(ROOT, "assets", "sfx", "whoosh_low.wav")
    riser_p = os.path.join(ROOT, "assets", "sfx", "riser_hit.wav")
    click_p = os.path.join(ROOT, "assets", "sfx", "ui_click.wav")

    w_hi = load_audio_stereo(w_hi_p) if os.path.exists(w_hi_p) else None
    w_lo = load_audio_stereo(w_lo_p) if os.path.exists(w_lo_p) else None
    riser = load_audio_stereo(riser_p) if os.path.exists(riser_p) else None
    click = load_audio_stereo(click_p) if os.path.exists(click_p) else None

    # Crisp UI ticks on countdown "5, 4, 3, 2, 1"
    if click is not None:
        intro_end = sections.get("intro", {}).get("end", 6.0)
        for w in words:
            if w["s"] > intro_end:
                break
            token = w["w"].strip(".,!?").lower()
            if token in {"5", "4", "3", "2", "1", "five", "four", "three", "two", "one"}:
                place_sfx(sfx_buf, click, w["s"], gain=0.22)

    # 2-4f pre-cut whooshes on every cut (Law #21)
    for i, t_cut in enumerate(cut_times_sec):
        if t_cut <= 0.1:
            continue
        clip = w_lo if (i % 2 == 0 and w_lo is not None) else w_hi
        if clip is not None:
            place_sfx(sfx_buf, clip, t_cut - 0.10, gain=0.18)

    # Subtle impact risers on World 1 start & World 4 twist start
    if riser is not None:
        for sec_name in ("world1", "world4"):
            if sec_name in sections:
                place_sfx(sfx_buf, riser, max(0.0, sections[sec_name]["start"] - 0.75), gain=0.15)

    mix = vo_pad + (mus + amb) * duck[:, None] + sfx_buf
    peak = float(np.max(np.abs(mix)) + 1e-6)
    if peak > 0.92:
        mix *= 0.92 / peak

    raw_wav = os.path.join(AUDIO_DIR, "mix_raw.wav")
    out_wav = os.path.join(AUDIO_DIR, "mix.wav")
    wavfile.write(raw_wav, SR, (np.clip(mix, -1.0, 1.0) * 32767.0).astype(np.int16))

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", raw_wav,
            "-af", "loudnorm=I=-14:TP=-1.0:LRA=7",
            "-ar", str(SR), "-ac", "2",
            out_wav,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    os.remove(raw_wav)
    print(f"[OK] Built -14 LUFS mix -> {out_wav} ({total_samples / SR:.2f}s)")
    return out_wav, total_samples / SR


if __name__ == "__main__":
    meta_path = os.path.join(BASE, "shots_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            cuts = [s["start_sec"] for s in json.load(f)["shots"]]
    else:
        cuts = [0.0, 5.5, 18.0, 30.0, 42.0]
    build_mix(cuts)
