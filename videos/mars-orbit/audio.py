"""Synthesize dark cosmic space ambient score + spot telemetry SFX, duck under voice, and normalize to -14 LUFS."""
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

# Exact cumulative cut timestamps matching scenes.js (seconds)
DURS = [
    4.200, 5.869, 4.255, 1.793, 14.276, 6.200, 3.414, 3.502, 14.342, 4.597,
    11.400, 4.394, 5.318, 13.312, 15.424, 8.050, 6.444, 5.800, 6.564, 5.321,
]
CUTS = [0.0]
for d in DURS:
    CUTS.append(CUTS[-1] + d)

TOTAL = CUTS[-1]
N = int(round(TOTAL * SR))
rng = np.random.default_rng(42)


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


# ---------------- Space Ambient Synth Instruments ----------------
def pad_note(freq: float, dur: float):
    n = T(dur)
    t = np.arange(n) / SR
    # Warm detuned cosmic analog pad
    y = (
        np.sin(2 * np.pi * freq * t) * 0.5
        + np.sin(2 * np.pi * freq * 1.0035 * t) * 0.35
        + np.sin(2 * np.pi * freq * 0.9965 * t) * 0.35
        + np.sin(2 * np.pi * freq * 2.0 * t) * 0.14
    )
    y = lp(y, 1200)
    env = np.minimum(1.0, t / 0.65) * np.minimum(1.0, (dur - t) / 0.85).clip(0)
    return y * env


def sub_pulse(freq: float, dur: float = 0.7):
    n = T(dur)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 2 * t)
    return y * np.minimum(1.0, t / 0.015) * np.exp(-t * 3.8)


def sonar_ping(freq: float = 880.0):
    n = T(1.2)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * freq * t) + 0.18 * np.sin(2 * np.pi * freq * 2.0 * t)
    return y * np.minimum(1.0, t / 0.008) * np.exp(-t * 3.6)


# Deep ominous D minor space harmonic progression (8-bar slow cycle)
music = np.zeros(N, dtype=np.float64)
chords = [
    (38, [50, 57, 62, 65]),   # Dm9
    (34, [46, 53, 58, 62]),   # Bbmaj7
    (36, [48, 55, 60, 64]),   # C6
    (33, [45, 52, 57, 60]),   # Am7
]
BAR = 4.0
t_cur = 0.0
bar_i = 0
while t_cur < TOTAL - 0.5:
    root, notes = chords[bar_i % len(chords)]
    dur = min(BAR + 0.6, TOTAL - t_cur)
    add(music, pad_note(hz(root), dur), t_cur, 0.35)
    for note in notes:
        add(music, pad_note(hz(note), dur), t_cur, 0.14)
    # Slow orbital sub-pulse every 1.0s
    for k in range(4):
        if t_cur + k * 1.0 < TOTAL - 0.2:
            add(music, sub_pulse(hz(root), 0.75), t_cur + k * 1.0, 0.28)
    # Sparse glassy ping at chord change
    add(music, sonar_ping(hz(notes[-1] + 12)), t_cur + 0.25, 0.09)
    t_cur += BAR
    bar_i += 1

fade_n = T(1.2)
music[-fade_n:] *= np.linspace(1.0, 0.0, fade_n)

# ---------------- Spot Telemetry & Comic Timing SFX ----------------
sfx = np.zeros(N, dtype=np.float64)


def whoosh(dur=0.32):
    n = T(dur)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    return bp(x, 300, 2600) * (np.sin(np.pi * t / dur) ** 2) * 0.45


def thud():
    n = T(0.45)
    t = np.arange(n) / SR
    f = 82 * np.exp(-t * 5.0) + 34
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8.5)


def ui_blip(freq=1180.0):
    n = T(0.08)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * 55)


def fizz_bubbles(dur=3.2):
    n = T(dur)
    y = hp(rng.standard_normal(n), 3200) * 0.08
    for _ in range(int(dur * 28)):
        i = int(rng.uniform(0, max(1, n - T(0.06))))
        m = T(0.04)
        tt = np.arange(m) / SR
        bf = rng.uniform(900, 2400)
        y[i : i + m] += np.sin(2 * np.pi * (bf + 600 * tt / 0.04) * tt) * np.exp(-tt * 90) * 0.25
    env = np.minimum(1.0, np.arange(n) / SR / 0.4) * np.minimum(1.0, (dur - np.arange(n) / SR) / 0.5).clip(0)
    return y * env


def stamp_slam():
    n = T(0.28)
    t = np.arange(n) / SR
    low = np.sin(2 * np.pi * (140 * np.exp(-t * 14) + 45) * t) * np.exp(-t * 14)
    snap = lp(rng.standard_normal(n), 3500) * np.exp(-t * 35) * 0.55
    return low + snap


def wind_cold(dur=6.0):
    n = T(dur)
    t = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 220, 720) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.35 * t))
    env = np.minimum(1.0, t / 0.7) * np.minimum(1.0, (dur - t) / 0.8).clip(0)
    return x * env * 0.35


def geiger_ticks(dur=8.0, rate=7.5):
    n = T(dur)
    y = np.zeros(n)
    t0 = 0.0
    while t0 < dur - 0.1:
        i = T(t0)
        m = min(T(0.012), n - i)
        if m > 0:
            y[i : i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / SR * 400)
        t0 += rng.exponential(1.0 / rate)
    return y * 0.4


# Pre-cut whooshes 3 frames (~0.10s) before major cuts
for c in CUTS[1:-1]:
    add(sfx, whoosh(0.30), c - 0.18, 0.28)

# Killer cards spotlight thuds (scenes 3, 7, 9, 12 -> cuts indices 3, 7, 9, 12)
for idx in (3, 7, 9, 12):
    add(sfx, thud(), CUTS[idx], 0.85)
    add(sfx, ui_blip(980), CUTS[idx] + 0.06, 0.3)

# Scene 4: Pressure gauge sweep ticks down to 6 mbar + warning beep
for k in range(16):
    add(sfx, ui_blip(1400 - k * 45), CUTS[4] + 0.5 + k * 0.45, 0.16)
add(sfx, ui_blip(620), CUTS[4] + 6.2, 0.35)

# Scene 5 & 6: Saliva fizz + MARS SODA CO. CARBONATED stamp slam
add(sfx, fizz_bubbles(4.0), CUTS[5] + 0.5, 0.45)
add(sfx, stamp_slam(), CUTS[6] + DURS[6] * 0.45, 0.85)

# Scene 8: Cold Martian wind + thermometer chimes
add(sfx, wind_cold(10.0), CUTS[8] + 0.6, 0.55)
add(sfx, sonar_ping(660), CUTS[8] + 4.6, 0.22)

# Scene 11: Doormat Notice card pop + TOXIC DUST stamp slam
add(sfx, ui_blip(1240), CUTS[11] + 0.15, 0.3)
add(sfx, stamp_slam(), CUTS[11] + DURS[11] * 0.38, 0.8)

# Scene 13: Chest X-ray radiation Geiger ticks
add(sfx, geiger_ticks(9.5, rate=8.0), CUTS[13] + 0.7, 0.55)

# Scene 14: Opportunity counter cards
add(sfx, ui_blip(1040), CUTS[14] + 0.3, 0.28)
add(sfx, ui_blip(1320), CUTS[14] + 3.4, 0.28)

# Scene 15: Knocked-down options ticks + deep space radio sonar pings
for k in range(3):
    add(sfx, thud(), CUTS[15] + 0.6 + k * 2.2, 0.45)
for k in range(4):
    add(sfx, sonar_ping(1120), CUTS[16] + 0.5 + k * 1.4, 0.18)

# Scene 18: Deep magma rumble
add(sfx, thud(), CUTS[18] + 0.2, 0.7)

# ---------------- Mix & Normalize (-14 LUFS) ----------------
sr_v, v = wavfile.read(os.path.join(HERE, "voice", "voice_raw.wav"))
v = v.astype(np.float64) / 32768.0
voice = np.zeros(N, dtype=np.float64)
voice[: min(N, len(v))] = v[:N]


def rms(x):
    nz = x[np.abs(x) > 1e-4]
    return np.sqrt(np.mean(nz ** 2) + 1e-12) if len(nz) else 1e-6


vad = np.convolve(np.abs(voice), np.ones(T(0.05)) / T(0.05), "same") > 0.01
duck = 1.0 - 0.36 * np.convolve(vad.astype(float), np.ones(T(0.18)) / T(0.18), "same")

vr = rms(voice)
music *= (vr * 0.24) / rms(music)     # moody space ambient bed ~ -12.4 dB below voice RMS
sfx *= (vr * 0.25) / rms(sfx)         # crisp spot SFX
mix = voice + (music + sfx) * duck

os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
for name, buf in [("music", music), ("sfx", sfx), ("premix", mix)]:
    peak = max(1.0, float(np.abs(buf).max()))
    wavfile.write(os.path.join(HERE, "audio", f"{name}.wav"), SR, (np.clip(buf / peak, -1, 1) * 32767).astype(np.int16))

subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-i", os.path.join(HERE, "audio", "premix.wav"),
    "-af", "loudnorm=I=-14:TP=-1.0:LRA=7",
    "-ar", str(SR),
    "-t", f"{TOTAL:.4f}",
    os.path.join(HERE, "audio", "mix.wav"),
], check=True)
print(f"mix.wav written ({TOTAL:.3f}s, {SR}Hz)")
