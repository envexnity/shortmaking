"""Mix Black Hole Short with 'Snowfall (Slowed + Reverb)' — Øneheart & reidenshi, real CC0 SFX on rapid ~1.25s sub-cuts, and -14 LUFS."""
import os
import subprocess
import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SR = 48000

DURS = [
    4.667, 3.351, 2.297, 3.650, 3.643, 3.809,
    2.312, 6.222, 5.047, 6.021, 4.593, 7.256,
]

SUB_CUTS = []
t_acc = 0.0
for d in DURS:
    n_sub = max(1, round(d / 1.25))
    sub_d = d / n_sub
    for k in range(n_sub):
        ct = t_acc + k * sub_d
        if ct > 0.01:
            SUB_CUTS.append((ct, k == 0))
    t_acc += d

TOTAL = t_acc
N = int(round(TOTAL * SR))


def T(sec: float) -> int:
    return int(round(sec * SR))


def load_wav(path: str) -> np.ndarray:
    sr_in, x = wavfile.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x.astype(np.float64) / 32768.0


def add(buf, x, at, g=1.0):
    i = T(at)
    if i >= len(buf):
        return
    if i < 0:
        x = x[-i:]
        i = 0
    m = min(len(x), len(buf) - i)
    if m > 0:
        buf[i : i + m] += x[:m] * g


def thud(freq: float = 68.0, dur: float = 0.24):
    n = T(dur)
    t = np.arange(n) / SR
    f = freq * (1.0 + 1.5 * np.exp(-t * 30.0))
    phase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(phase) * np.minimum(1.0, t / 0.004) * np.exp(-t * 14.0)


# 1. Real user-requested music: "Snowfall (Slowed + Reverb)" — Øneheart & reidenshi
music_raw = load_wav(os.path.join(ROOT, "assets", "music", "snowfall_clip.wav"))
if len(music_raw) < N:
    reps = int(np.ceil(N / len(music_raw)))
    music = np.tile(music_raw, reps)[:N]
else:
    music = music_raw[:N].copy()

fade_in = T(0.25)
fade_out = T(1.2)
music[:fade_in] *= np.linspace(0.0, 1.0, fade_in)
music[-fade_out:] *= np.linspace(1.0, 0.0, fade_out)

# 2. Verified CC0 SFX layered on rapid sub-cuts (2-4 frame lead-ins + frame-0 impacts)
whoosh_clip = load_wav(os.path.join(ROOT, "assets", "sfx", "whoosh.wav"))[: T(0.26)]
whoosh_low = load_wav(os.path.join(ROOT, "assets", "sfx", "whoosh_low.wav"))[: T(0.32)]
ui_click = load_wav(os.path.join(ROOT, "assets", "sfx", "ui_click.wav"))[: T(0.10)]
riser_hit = load_wav(os.path.join(ROOT, "assets", "sfx", "riser_hit.wav"))

sfx = np.zeros(N, dtype=np.float64)
for c_t, is_major in SUB_CUTS:
    if is_major:
        add(sfx, whoosh_low, max(0.0, c_t - 0.18), 0.34)
        add(sfx, thud(66, 0.24), c_t, 0.46)
    else:
        add(sfx, whoosh_clip, max(0.0, c_t - 0.14), 0.22)
        add(sfx, ui_click, c_t, 0.20)
        add(sfx, thud(76, 0.16), c_t, 0.22)

# Risers into Killer #1 & Killer #2
add(sfx, riser_hit[: T(1.5)], max(0.0, 8.02 - 1.1), 0.25)
add(sfx, riser_hit[: T(1.5)], max(0.0, 21.42 - 1.1), 0.25)

# 3. Mix with voice (music + sfx at ~ -6 dB gated RMS relative to voice, ducked under speech)
voice = load_wav(os.path.join(HERE, "voice", "voice_raw.wav"))
if len(voice) < N:
    voice = np.pad(voice, (0, N - len(voice)))
else:
    voice = voice[:N]


def rms(x):
    nz = x[np.abs(x) > 1e-4]
    return float(np.sqrt(np.mean(nz ** 2) + 1e-12)) if len(nz) else 1e-6


vr = rms(voice)
music *= (vr * 0.50) / rms(music)
sfx *= (vr * 0.24) / rms(sfx)

vad = np.convolve(np.abs(voice), np.ones(T(0.05)) / T(0.05), "same") > 0.01
duck = 1.0 - 0.25 * np.convolve(vad.astype(float), np.ones(T(0.16)) / T(0.16), "same")

raw_mix = voice + (music + sfx) * duck
peak = float(np.max(np.abs(raw_mix)))
if peak > 0.92:
    raw_mix *= 0.92 / peak

os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
unnorm = os.path.join(HERE, "audio", "mix_raw.wav")
final_mix = os.path.join(HERE, "audio", "mix.wav")
wavfile.write(unnorm, SR, (np.clip(raw_mix, -1.0, 1.0) * 32767).astype(np.int16))

subprocess.run(
    [
        "ffmpeg", "-y", "-v", "error", "-i", unnorm,
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=7",
        "-ar", str(SR), "-ac", "1", final_mix,
    ],
    check=True,
)
print(f"Written {final_mix} with Snowfall (Slowed + Reverb) ({TOTAL:.3f}s, -14 LUFS)")
