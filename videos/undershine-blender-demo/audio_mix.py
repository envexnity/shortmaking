"""
audio_mix.py — Track 7 Undershine Audio Mix (-14 LUFS, -6 dB gated ducking, 2-4f pre-cut whooshes).
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
    rate, data = wavfile.read(tmp)
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


def place_sfx(buf: np.ndarray, sfx: np.ndarray, t_sec: float, gain: float = 0.35):
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


def synth_valley_ambience(n_samples: int, campfire_start_sec: float) -> np.ndarray:
    """Subtle mountain river bed + cozy campfire crackles in final third."""
    rng = np.random.default_rng(42)
    noise = rng.standard_normal(n_samples).astype(np.float32)
    # Soft river murmur (bandpass 180-1100 Hz)
    b, a = butter(2, [180 / (SR * 0.5), 1100 / (SR * 0.5)], btype="band")
    river = filtfilt(b, a, noise).astype(np.float32)
    river /= max(1e-5, np.max(np.abs(river)))
    # Slow natural swell
    t = np.arange(n_samples, dtype=np.float32) / SR
    swell = 0.75 + 0.25 * np.sin(t * 0.65)
    bed_l = river * swell * 0.045
    bed_r = np.roll(river, 900) * swell * 0.045

    # Cozy campfire crackles from campfire_start_sec onward
    fire = np.zeros(n_samples, dtype=np.float32)
    t_c = campfire_start_sec
    while t_c < n_samples / SR - 0.15:
        idx = int(t_c * SR)
        dur = int(rng.uniform(0.004, 0.014) * SR)
        if idx + dur < n_samples:
            pop = rng.standard_normal(dur).astype(np.float32)
            env = np.exp(-np.linspace(0, 6.0, dur, dtype=np.float32))
            fire[idx : idx + dur] += pop * env * rng.uniform(0.08, 0.22)
        t_c += rng.uniform(0.06, 0.24)
    bf, af = butter(2, [1400 / (SR * 0.5), 6500 / (SR * 0.5)], btype="band")
    fire = filtfilt(bf, af, fire).astype(np.float32)
    return np.stack([bed_l + fire * 0.45, bed_r + fire * 0.55], axis=1)


def build_mix(cut_times_sec):
    voice_mp3 = os.path.join(BASE, "voice", "voice.mp3")
    vo = load_audio_stereo(voice_mp3)

    # Pad 0.75s clean twilight tail after final word for crane reveal payoff
    total_samples = len(vo) + int(0.85 * SR)
    vo_pad = np.zeros((total_samples, 2), dtype=np.float32)
    vo_pad[: len(vo)] = vo

    # Normalize VO RMS to ~0.18
    vo_rms = float(np.sqrt(np.mean(vo ** 2)) + 1e-6)
    vo_pad *= 0.19 / vo_rms

    # Voice activity envelope for -6 dB gated ducking
    vo_mono = np.abs(vo_pad.mean(axis=1))
    win = int(0.08 * SR)
    kernel = np.ones(win, dtype=np.float32) / win
    env = np.convolve(vo_mono, kernel, mode="same")
    duck = np.where(env > 0.025, 0.34, 0.56).astype(np.float32)
    # Smooth ducking transitions
    b_l, a_l = butter(2, 5.0 / (SR * 0.5), btype="low")
    duck = np.clip(filtfilt(b_l, a_l, duck).astype(np.float32), 0.30, 0.62)

    # Music bed: Snowfall (Slowed + Reverb)
    music_path = os.path.join(ROOT, "assets", "music", "snowfall_clip.wav")
    if os.path.exists(music_path):
        mus = load_audio_stereo(music_path)
        reps = int(np.ceil(total_samples / len(mus))) + 1
        mus = np.tile(mus, (reps, 1))[:total_samples]
        mus_rms = float(np.sqrt(np.mean(mus ** 2)) + 1e-6)
        mus *= 0.16 / mus_rms
        # Fade in/out
        fi = int(0.35 * SR)
        fo = int(0.80 * SR)
        mus[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
        mus[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    else:
        mus = np.zeros((total_samples, 2), dtype=np.float32)

    # Ambience + SFX
    amb = synth_valley_ambience(total_samples, campfire_start_sec=max(0.0, (cut_times_sec[-2] if len(cut_times_sec) >= 2 else 10.0) - 1.5))
    sfx_buf = np.zeros((total_samples, 2), dtype=np.float32)

    whoosh_p = os.path.join(ROOT, "assets", "sfx", "whoosh.wav")
    whoosh_low_p = os.path.join(ROOT, "assets", "sfx", "whoosh_low.wav")
    riser_p = os.path.join(ROOT, "assets", "sfx", "riser_hit.wav")

    w_hi = load_audio_stereo(whoosh_p) if os.path.exists(whoosh_p) else None
    w_lo = load_audio_stereo(whoosh_low_p) if os.path.exists(whoosh_low_p) else None
    riser = load_audio_stereo(riser_p) if os.path.exists(riser_p) else None

    for i, t_cut in enumerate(cut_times_sec):
        if t_cut <= 0.1:
            continue
        # Law #21: 2-4 frames (0.10s) lead-in before visual cut
        clip = w_lo if (i % 2 == 0 and w_lo is not None) else w_hi
        if clip is not None:
            place_sfx(sfx_buf, clip, t_cut - 0.10, gain=0.20)

    # Subtle twilight reveal riser on penultimate -> final crane reveal
    if riser is not None and len(cut_times_sec) >= 2:
        place_sfx(sfx_buf, riser, max(0.0, cut_times_sec[-1] - 0.85), gain=0.14)

    mix = vo_pad + (mus + amb) * duck[:, None] + sfx_buf
    peak = float(np.max(np.abs(mix)) + 1e-6)
    if peak > 0.92:
        mix *= 0.92 / peak

    raw_wav = os.path.join(AUDIO_DIR, "mix_raw.wav")
    out_wav = os.path.join(AUDIO_DIR, "mix.wav")
    wavfile.write(raw_wav, SR, (np.clip(mix, -1.0, 1.0) * 32767.0).astype(np.int16))

    # Loudnorm to -14 LUFS, TP -1.0 dBTP
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
        cuts = [0.0, 2.8, 5.4, 8.0, 10.6, 13.4, 16.0]
    build_mix(cuts)
