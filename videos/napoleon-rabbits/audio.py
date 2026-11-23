"""Original 1807 French fife-and-strings comedy march + layered Foley SFX + -14 LUFS master for napoleon-rabbits."""
import json
import os
import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SFX_DIR = os.path.join(REPO_ROOT, "assets", "sfx")
SR = 48000

CUT = [
    0, 2.25, 4.69, 5.40, 7.75, 10.51, 12.45, 15.16, 17.90, 19.95, 22.18, 24.10, 25.98, 28.20,
    30.02, 32.85, 34.61, 37.15, 39.16, 41.85, 43.64, 45.75, 47.49, 49.45, 51.26, 52.50, 53.74, 55.65, 57.315,
]
FR = [round(c * 30) for c in CUT]
TOTAL = FR[-1] / 30.0  # exact 57.300s
N = int(round(TOTAL * SR))
rng = np.random.default_rng(1807)


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
        buf[i:i + m] += x[:m] * g


def hz(m: float) -> float:
    return 440.0 * 2.0 ** ((m - 69.0) / 12.0)


def load_wav(path: str) -> np.ndarray:
    sr, d = wavfile.read(path)
    x = d.astype(np.float64) / (32768.0 if d.dtype == np.int16 else 1.0)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != SR:
        tmp = path + "_48k.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "1", tmp], check=True)
        _, d2 = wavfile.read(tmp)
        os.remove(tmp)
        x = d2.astype(np.float64) / 32768.0
    return x


# ---------------------------------------------------------------- instruments
def pizz(f, dur=0.35, bright=0.75):
    n = T(dur)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for h in range(1, 7):
        y += np.sin(2 * np.pi * f * h * t) * (bright ** (h - 1)) / h * np.exp(-t * (5 + h * 3.0))
    return y * np.minimum(1.0, t / 0.003)


def tuba(f, dur=0.35):
    n = T(dur)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t)
    return lp(y, 900) * np.minimum(1.0, t / 0.008) * np.exp(-t * 5.2)


def fife(f, dur=0.28):
    n = T(dur)
    t = np.arange(n) / SR
    vib = 1.0 + 0.005 * np.sin(2 * np.pi * 5.8 * t) * np.minimum(1.0, t / 0.10)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    y = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.07 * np.sin(3 * ph)
    env = np.minimum(1.0, t / 0.015) * np.minimum(1.0, (dur - t) / 0.035).clip(0)
    return y * env


def march_kick():
    n = T(0.28)
    t = np.arange(n) / SR
    f = 105 * np.exp(-t * 16) + 46
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)


def march_snare():
    n = T(0.18)
    t = np.arange(n) / SR
    return (bp(rng.standard_normal(n), 1400, 6800) * 0.85 + np.sin(2 * np.pi * 185 * t) * 0.45) * np.exp(-t * 24)


def hat():
    n = T(0.04)
    return hp(rng.standard_normal(n), 7200) * np.exp(-np.arange(n) / SR * 85) * 0.45


# ---------------------------------------------------------------- 1807 Comic Imperial March (120 BPM, C major / A minor)
BPM = 120.0
BEAT = 60.0 / BPM

prog_maj = [
    (48, [60, 64, 67]), (55, [59, 62, 67]), (53, [60, 65, 69]), (55, [59, 62, 67]),
    (45, [60, 64, 69]), (53, [60, 65, 69]), (50, [62, 65, 69]), (55, [59, 62, 67]),
]
mel_maj = [
    [72, 76, 79, 76], [74, 71, 67, None], [77, 76, 74, 72], [74, None, 71, None],
    [76, 72, 69, 72], [77, 76, 74, 72], [74, 77, 76, 74], [79, None, None, None],
]
prog_chase = [
    (45, [57, 60, 64]), (52, [59, 64, 68]), (45, [57, 60, 64]), (53, [57, 60, 65]),
    (50, [57, 62, 65]), (52, [59, 64, 68]), (45, [57, 60, 64]), (52, [59, 64, 68]),
]
mel_chase = [
    [81, 79, 76, 74], [76, 74, 71, 68], [72, 76, 81, 79], [77, 76, 74, 72],
    [74, 77, 81, 77], [76, 74, 71, 68], [69, 72, 76, 81], [83, None, None, None],
]


def score(start, end, out, gain=1.0, mode="maj"):
    t = start
    bar = 0
    while t < end - 0.05:
        if mode == "chase":
            root, ch = prog_chase[bar % 8]
            m_row = mel_chase[bar % 8]
        else:
            root, ch = prog_maj[bar % 8]
            m_row = mel_maj[bar % 8]
        for b in range(4):
            tb = t + b * BEAT
            if tb >= end:
                break
            add(out, tuba(hz(root + (0 if b % 2 == 0 else 7))), tb, 0.50 * gain)
            for c in ch:
                add(out, pizz(hz(c), 0.22, 0.7), tb + BEAT * 0.5, 0.11 * gain)
            add(out, march_kick(), tb, (0.55 if b % 2 == 0 else 0.25) * gain)
            if b % 2 == 1:
                add(out, march_snare(), tb, 0.24 * gain)
            if mode == "chase":
                add(out, hat(), tb + BEAT * 0.25, 0.16 * gain)
                add(out, hat(), tb + BEAT * 0.75, 0.16 * gain)
            m = m_row[b]
            if m:
                add(out, fife(hz(m), BEAT * 0.82), tb, 0.14 * gain)
        t += 4 * BEAT
        bar += 1


music = np.zeros(N)
score(0.0, 4.65, music, gain=0.95, mode="maj")          # opening march (cuts out for "And lost.")
score(5.40, 25.95, music, gain=0.95, mode="maj")        # setup + cages + laughing
score(25.98, 39.15, music, gain=0.85, mode="maj")       # flank + You see analogy
score(39.16, 51.26, music, gain=1.05, mode="chase")     # swarming + carriage chase
score(51.26, 55.65, music, gain=0.80, mode="maj")       # dusk retreat + pedestal

# Big triumphant final chord + cymbal on "dinner time."
for c in [48, 60, 64, 67, 72, 76, 79, 84]:
    add(music, pizz(hz(c), 1.6, 0.8), 55.90, 0.16)
add(music, fife(hz(84), 1.2), 55.90, 0.18)
add(music, march_kick(), 55.90, 0.9)
cym = hp(rng.standard_normal(T(1.5)), 5000) * np.exp(-np.arange(T(1.5)) / SR * 2.6) * 0.25
add(music, cym, 55.90)

fade = np.ones(N)
fade[-T(0.55):] = np.linspace(1.0, 0.0, T(0.55))
music *= fade


# ---------------------------------------------------------------- SFX & Foley
sfx = np.zeros(N)

whoosh_real = load_wav(os.path.join(SFX_DIR, "whoosh.wav"))
whoosh_low = load_wav(os.path.join(SFX_DIR, "whoosh_low.wav"))
ui_click = load_wav(os.path.join(SFX_DIR, "ui_click.wav"))


def thud():
    n = T(0.38)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(78 * np.exp(-t * 4.5) + 38) / SR) * np.exp(-t * 9.5)


def pop(f0=520, f1=1280):
    n = T(0.11)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(f0 + (f1 - f0) * t / 0.11) / SR) * np.exp(-t * 36)


def ding(f=1480):
    n = T(0.7)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.75 * t)) * np.exp(-t * 5.5)


def swish_crop():
    n = T(0.18)
    t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 900, 4500) * np.sin(np.pi * t / 0.18) ** 2 * 0.75


def boing():
    n = T(0.28)
    t = np.arange(n) / SR
    f = 240 + 180 * np.sin(2 * np.pi * 18 * t) * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8.5) * 0.55


def hops(dur, rate=18):
    n = T(dur)
    y = np.zeros(n)
    for k in range(int(dur * rate)):
        i = T(k / rate + rng.uniform(0, 0.025))
        m = min(T(0.045), n - i)
        if m > 0:
            y[i:i + m] += bp(rng.standard_normal(m), 180, 1400) * np.exp(-np.arange(m) / SR * 65) * rng.uniform(0.4, 1.0)
    return y * np.minimum(1.0, np.arange(n) / max(1, T(0.25))) * np.minimum(1.0, (n - np.arange(n)) / max(1, T(0.25)))


def cage_latch():
    n = T(0.16)
    t = np.arange(n) / SR
    return (bp(rng.standard_normal(n), 800, 4000) * 0.8 + np.sin(2 * np.pi * 620 * t) * 0.4) * np.exp(-t * 28)


def door_slam():
    n = T(0.32)
    t = np.arange(n) / SR
    return (lp(rng.standard_normal(n), 1200) * 1.1 + np.sin(2 * np.pi * 95 * np.exp(-t * 8) * t) * 0.9) * np.exp(-t * 14)


def coin_clink():
    n = T(0.24)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 3100 * t) + 0.6 * np.sin(2 * np.pi * 4750 * t)) * np.exp(-t * 18) * 0.45


def hooves_and_wheels(dur):
    n = T(dur)
    t = np.arange(n) / SR
    y = lp(rng.standard_normal(n), 450) * (0.25 + 0.15 * np.sin(2 * np.pi * 3.5 * t))
    for k in range(int(dur * 9)):
        i = T(k / 9.0 + (0.04 if k % 2 else 0))
        m = min(T(0.05), n - i)
        if m > 0:
            y[i:i + m] += bp(rng.standard_normal(m), 250, 1600) * np.exp(-np.arange(m) / SR * 55) * 0.65
    return y * np.minimum(1.0, t / 0.2) * np.minimum(1.0, (dur - t) / 0.2).clip(0)


# Pre-cut 2-4 frame whoosh lead-ins on major scene switches
for idx, c in enumerate(CUT[1:-1]):
    w_clip = whoosh_low if idx % 3 == 0 else whoosh_real
    add(sfx, w_clip[:T(0.35)], c - 0.14, 0.26)

# Specific story beat Foley
add(sfx, thud(), 4.69, 0.95)                                  # "And lost."
add(sfx, pop(), 6.10, 0.5)                                    # Russia X
add(sfx, pop(), 6.60, 0.5)                                    # Prussia X
for k in range(8):
    add(sfx, pop(440 + k * 45, 980 + k * 50), 10.55 + k * 0.14, 0.28)  # Cages popping in
for k in range(4):
    add(sfx, cage_latch(), 15.42 + k * 0.08, 0.55)            # Cages opening
add(sfx, hops(4.2, 22), 17.90, 0.55)                          # Wall of fur charging
add(sfx, swish_crop(), 24.45, 0.6)                            # Riding crop swat 1
add(sfx, boing(), 24.62, 0.6)                                 # Rabbit bounce 1
add(sfx, swish_crop(), 25.05, 0.6)                            # Riding crop swat 2
add(sfx, boing(), 25.22, 0.6)                                 # Rabbit bounce 2
add(sfx, thud(), 25.98, 0.85)                                 # "Unluckily..."
add(sfx, hops(3.9, 26), 26.05, 0.58)                          # Flanking boots
add(sfx, whoosh_real[:T(0.3)], 30.45, 0.45)                   # Wild hare bolts
add(sfx, coin_clink(), 33.15, 0.65)                           # Buying tame farm rabbits
add(sfx, coin_clink(), 33.32, 0.55)
add(sfx, ui_click, 35.75, 0.45)                               # "NOT A HUNTER"
add(sfx, ding(1568), 37.55, 0.55)                             # Waiter bringing cabbage!
add(sfx, hops(4.3, 28), 39.20, 0.45)                          # Climbing & swarming
add(sfx, thud(), 43.64, 0.70)                                 # Sprint to carriage
add(sfx, door_slam(), 46.35, 0.95)                            # Carriage door slammed!
add(sfx, hooves_and_wheels(3.7), 47.49, 0.65)                 # Chasing the carriage
add(sfx, pop(580, 1400), 49.65, 0.45)                         # Leaping through windows
add(sfx, pop(640, 1520), 49.95, 0.45)
add(sfx, pop(700, 1600), 50.25, 0.45)
add(sfx, ding(1760), 56.00, 0.45)                             # "dinner time" pedestal pop!


# ---------------------------------------------------------------- Mix & -14 LUFS Master
sr_v, v = wavfile.read(os.path.join(HERE, "voice", "voice_raw.wav"))
v = v.astype(np.float64) / 32768.0
voice = np.zeros(N)
voice[:min(N, len(v))] = v[:N]


def rms(x):
    active = x[np.abs(x) > 1e-4]
    return np.sqrt(np.mean(active ** 2) + 1e-12) if len(active) else 1e-6


a = np.abs(voice)
w = T(0.05)
vad = np.convolve(a, np.ones(w) / w, "same") > 0.01
duck = np.convolve(vad.astype(float), np.ones(T(0.14)) / T(0.14), "same")
duck = 1.0 - 0.35 * duck

vr = rms(voice)
music *= (vr * 0.28 * 1.35) / rms(music)   # ~ -6 dB re voice
sfx *= (vr * 0.28 * 0.80) / rms(sfx)       # crisp SFX punch below voice
mix = voice + (music + sfx) * duck

os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
for name, x in [("music", music), ("sfx", sfx), ("premix", mix)]:
    peak = max(1.0, float(np.abs(x).max()))
    wavfile.write(
        os.path.join(HERE, "audio", name + ".wav"),
        SR,
        (np.clip(x / peak, -1.0, 1.0) * 32767).astype(np.int16),
    )

subprocess.run(
    [
        "ffmpeg", "-y", "-v", "error",
        "-i", os.path.join(HERE, "audio", "premix.wav"),
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
        "-ar", str(SR), "-t", f"{TOTAL:.4f}",
        os.path.join(HERE, "audio", "mix.wav"),
    ],
    check=True,
)
print("mix written:", TOTAL, "s")
