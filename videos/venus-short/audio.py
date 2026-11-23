"""Synthesize space ambient score + spot telemetry SFX, duck under voice, and normalize to -14 LUFS."""
import json
import os
import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000

with open(os.path.join(HERE, "beats.json"), encoding="utf-8") as f:
    beats_info = json.load(f)

# Exact cumulative cut durations matching scenes.js (total 47.782s)
DURS = [
    5.569, 3.191, 1.742, 5.637, 3.194, 3.294,
    5.584, 3.189, 3.161, 2.959, 4.588, 5.674,
]
CUTS = [0.0]
for d in DURS:
    CUTS.append(CUTS[-1] + d)

TOTAL = CUTS[-1]
N = int(round(TOTAL * SR))
rng = np.random.default_rng(108)


def T(sec: float) -> int:
    return int(round(sec * SR))


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)


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


def hz(midi: float) -> float:
    return 440.0 * (2.0 ** ((midi - 69.0) / 12.0))


def pad_note(freq: float, dur: float):
    n = max(1, T(dur))
    t = np.arange(n) / SR
    y = (
        np.sin(2 * np.pi * freq * t) * 0.5
        + np.sin(2 * np.pi * freq * 1.0035 * t) * 0.35
        + np.sin(2 * np.pi * freq * 0.9965 * t) * 0.35
        + np.sin(2 * np.pi * freq * 2.0 * t) * 0.14
    )
    y = lp(y, 1200)
    env = np.minimum(1.0, t / 0.55) * np.minimum(1.0, (dur - t) / 0.75).clip(0)
    return y * env


def sub_pulse(freq: float, dur: float = 0.7):
    n = T(dur)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 2 * t)
    return y * np.minimum(1.0, t / 0.015) * np.exp(-t * 3.8)


def sonar_ping(freq: float = 880.0):
    n = T(1.1)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * freq * t) + 0.18 * np.sin(2 * np.pi * freq * 2.0 * t)
    return y * np.minimum(1.0, t / 0.008) * np.exp(-t * 3.8)


def whoosh(dur: float = 0.28):
    n = T(dur)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    w = bp(noise, 260, 2600, order=2)
    env = np.sin(np.pi * (t / dur)) ** 1.6
    return w * env


def thud(freq: float = 72.0, dur: float = 0.26):
    n = T(dur)
    t = np.arange(n) / SR
    f = freq * (1.0 + 1.4 * np.exp(-t * 28.0))
    phase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(phase) * np.minimum(1.0, t / 0.004) * np.exp(-t * 14.0)


def can_crush(dur: float = 0.32):
    n = T(dur)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    crunch = bp(noise, 900, 4800, order=2) * np.exp(-t * 11.0)
    ring = np.sin(2 * np.pi * 620 * t) * np.exp(-t * 20.0) * 0.35
    return thud(78, dur) * 0.7 + crunch * 0.45 + ring


def tick_click():
    n = T(0.035)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1750 * t) * np.exp(-t * 130.0)


def stamp_slam():
    n = T(0.24)
    t = np.arange(n) / SR
    snap = hp(rng.normal(0, 1, n), 1800) * np.exp(-t * 40.0)
    return thud(68, 0.24) * 0.9 + snap * 0.32


# 1. Cosmic space bed
music = np.zeros(N, dtype=np.float64)
chords = [
    (38, [50, 57, 62, 65]),   # Dm9
    (34, [46, 53, 58, 62]),   # Bbmaj7
    (36, [48, 55, 60, 64]),   # C6
    (33, [45, 52, 57, 60]),   # Am7
]
BAR = 4.0
t_cur, bar_i = 0.0, 0
while t_cur < TOTAL - 0.5:
    root, notes = chords[bar_i % len(chords)]
    dur = min(BAR + 0.5, TOTAL - t_cur)
    add(music, pad_note(hz(root), dur), t_cur, 0.34)
    for note in notes:
        add(music, pad_note(hz(note), dur), t_cur, 0.14)
    for k in range(4):
        if t_cur + k * 1.0 < TOTAL - 0.2:
            add(music, sub_pulse(hz(root), 0.72), t_cur + k * 1.0, 0.26)
    add(music, sonar_ping(hz(notes[-1] + 12)), t_cur + 0.22, 0.08)
    t_cur += BAR
    bar_i += 1

fade_n = T(1.0)
music[-fade_n:] *= np.linspace(1.0, 0.0, fade_n)

# 2. Spot SFX + 2-4 frame lead-in transitions
sfx = np.zeros(N, dtype=np.float64)
for c_idx, c_t in enumerate(CUTS[1:-1], start=1):
    # Whoosh peaks 3 frames (0.09s) before cut, low-end thud hits on frame 0 of new cut
    add(sfx, whoosh(0.28), max(0.0, c_t - 0.20), 0.36)
    add(sfx, thud(74, 0.24), c_t, 0.48)
    if c_idx in (2, 5):  # Killer cards
        add(sfx, sonar_ping(hz(74)), c_t + 0.02, 0.22)

# Implosion crunch
add(sfx, can_crush(), 6.05, 0.65)
add(sfx, can_crush(), 16.45, 0.55)

# Pressure dial ticks
for k in range(8):
    add(sfx, tick_click(), 11.1 + k * 0.28, 0.24)

# Receipt & cloud-twist stamp slams
add(sfx, stamp_slam(), 17.25, 0.72)
add(sfx, stamp_slam(), 44.10, 0.72)

# Radio ping + melt sizzle
add(sfx, sonar_ping(1046.5), 37.85, 0.20)

# 3. Mix with voice and duck music under speech
_, vraw = wavfile.read(os.path.join(HERE, "voice", "voice_raw.wav"))
voice = vraw.astype(np.float64) / 32768.0
if len(voice) < N:
    voice = np.pad(voice, (0, N - len(voice)))
else:
    voice = voice[:N]

win = int(SR * 0.08)
env = np.convolve(np.abs(voice), np.ones(win) / win, mode="same")
duck = 1.0 - 0.40 * np.clip(env / 0.035, 0.0, 1.0)

raw_mix = voice * 0.92 + music * 0.28 * duck + sfx * 0.32
peak = np.max(np.abs(raw_mix))
if peak > 0.92:
    raw_mix = raw_mix * (0.92 / peak)

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
print(f"Written {final_mix} ({TOTAL:.3f}s, -14 LUFS)")
