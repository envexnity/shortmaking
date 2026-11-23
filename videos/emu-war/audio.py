"""Original score + synthesized SFX + mix for The Great Emu War. Writes audio/mix.wav (48k) at exact video length."""
import json, os, subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
info = json.load(open(os.path.join(HERE, "beats.json")))
CUT = [0, 5.40, 6.195, 9.575, 14.905, 17.895, 20.975, 22.615, 25.885, 30.615, 33.405, 36.55, 38.955, 43.855, 48.235, 49.68, 50.995, 56.089]
FR = [round(c * 30) for c in CUT]
TOTAL = FR[-1] / 30
N = int(round(TOTAL * SR))
rng = np.random.default_rng(7)

def T(sec): return int(round(sec * SR))
def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)
def lp(x, f, order=2): return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)
def env(n, a=.005, d=.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def add(buf, x, at, g=1.0):
    i = T(at)
    if i >= len(buf): return
    if i < 0: x = x[-i:]; i = 0
    m = min(len(x), len(buf) - i); buf[i:i + m] += x[:m] * g
def hz(m): return 440 * 2 ** ((m - 69) / 12)

# ---------------------------------------------------------------- instruments
def pluck(f, dur=.5, bright=1.0):
    n = T(dur); t = np.arange(n) / SR; y = np.zeros(n)
    for h in range(1, 9):
        y += np.sin(2 * np.pi * f * h * t) * (bright ** (h - 1)) / h * np.exp(-t * (3 + h * 2.2))
    return y * np.minimum(1, t / .002)
def bass(f, dur=.35):
    n = T(dur); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t) + .12 * np.sin(6 * np.pi * f * t)
    return y * np.minimum(1, t / .004) * np.exp(-t * 5)
def lead(f, dur=.3):
    n = T(dur); t = np.arange(n) / SR
    vib = 1 + .006 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / .15)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    y = np.sin(ph) + .25 * np.sin(2 * ph) + .1 * np.sin(3 * ph)
    e = np.minimum(1, t / .015) * np.minimum(1, (dur - t) / .04).clip(0) * (0.8 + .2 * np.exp(-t * 6))
    return y * e
def kick():
    n = T(.3); t = np.arange(n) / SR
    f = 110 * np.exp(-t * 18) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
def snare():
    n = T(.2); t = np.arange(n) / SR
    return (bp(rng.standard_normal(n), 1500, 7000) * .9 + np.sin(2 * np.pi * 190 * t) * .5) * np.exp(-t * 22)
def hat():
    n = T(.05); return hp(rng.standard_normal(n), 7000) * np.exp(-np.arange(n) / SR * 80) * .5

# ---------------------------------------------------------------- score (original bush-march, G major, 116 bpm)
BPM = 116; BEAT = 60 / BPM
prog = [(55, [55, 59, 62]), (60, [60, 64, 67]), (62, [62, 66, 69]), (55, [55, 59, 62]),
        (52, [52, 55, 59]), (60, [60, 64, 67]), (62, [62, 66, 69]), (55, [55, 59, 62])]
mel = [[74, 71, 74, 76], [76, 72, 76, 79], [78, 74, 69, 74], [71, None, 67, None],
       [71, 67, 71, 74], [72, 76, 72, 69], [69, 72, 74, 78], [79, None, None, None]]

def score(start, end, out, gain=1.0, tension=False):
    t = start; bar = 0
    while t < end - .05:
        root, ch = prog[bar % 8]
        if tension: root, ch = root - 5, [c - 5 for c in ch]
        for b in range(4):
            tb = t + b * BEAT
            if tb >= end: break
            add(out, bass(hz(root - 24 + (0 if b % 2 == 0 else 7))), tb, .55 * gain)
            for c in ch: add(out, pluck(hz(c), .25, .5), tb + BEAT / 2, .10 * gain)
            add(out, kick(), tb, (.55 if b % 2 == 0 else .25) * gain)
            if b % 2 == 1: add(out, snare(), tb, .22 * gain)
            add(out, hat(), tb + BEAT / 2, .18 * gain)
            m = mel[bar % 8][b]
            if m and not tension and bar % 16 >= 0: add(out, lead(hz(m), BEAT * .9), tb, .16 * gain)
            if tension and b in (0, 2): add(out, pluck(hz(ch[0] + 12), .4, .7), tb, .14 * gain)
        t += 4 * BEAT; bar += 1

music = np.zeros(N)
score(0.0, 5.40, music)
score(6.195, 33.405, music)
score(33.405, 54.40, music, gain=.95)
# final stinger: big G chord + cymbal at "Undefeated"
for c in [43, 55, 59, 62, 67, 71, 74, 79]: add(music, pluck(hz(c), 1.8, .6), 54.45, .16)
add(music, lead(hz(79), 1.4), 54.45, .2)
add(music, kick(), 54.45, .9)
cym = hp(rng.standard_normal(T(1.6)), 5000) * np.exp(-np.arange(T(1.6)) / SR * 2.5) * .25
add(music, cym, 54.45)
# fade music out exactly at end
fade = np.ones(N); fade[-T(.6):] = np.linspace(1, 0, T(.6)); music *= fade

# ---------------------------------------------------------------- sfx
sfx = np.zeros(N)
def whoosh(dur=.35):
    n = T(dur); t = np.arange(n) / SR; x = rng.standard_normal(n)
    sw = np.sin(np.pi * t / dur) ** 2
    return bp(x, 400, 3500) * sw * .5
def thud():
    n = T(.4); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(75 * np.exp(-t * 4) + 40) / SR) * np.exp(-t * 9)
def pop():
    n = T(.12); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(500 + 900 * t / .12) / SR) * np.exp(-t * 35)
def ding(f=1320):
    n = T(.8); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 5)
def shot():
    n = T(.09); t = np.arange(n) / SR
    return (lp(rng.standard_normal(n), 2500) * 1.2 + np.sin(2 * np.pi * 90 * t)) * np.exp(-t * 45)
def gun(at, dur, rate):
    k = 0
    while k / rate < dur: add(sfx, shot(), at + k / rate, .55); k += 1
def clank():
    n = T(.25); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 820 * t) + np.sin(2 * np.pi * 1370 * t) * .7 + bp(rng.standard_normal(n), 2000, 6000) * .6) * np.exp(-t * 18)
def engine(dur, bumpy=False):
    n = T(dur); t = np.arange(n) / SR
    f = 38 + 4 * np.sin(2 * np.pi * .7 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sign(np.sin(ph)) * .3 + np.sin(ph * 2) * .3
    y = lp(y, 700) + lp(rng.standard_normal(n), 300) * .3
    if bumpy:
        bumps = (np.abs(np.sin(2 * np.pi * 1.43 * t)) ** 8) * 1.5
        y = y * (1 + bumps) + bp(rng.standard_normal(n), 800, 3000) * bumps * .4
    e = np.minimum(1, t / .3) * np.minimum(1, (dur - t) / .3).clip(0)
    return y * e
def rumble(dur):
    n = T(dur); t = np.arange(n) / SR
    thumps = np.zeros(n)
    for k in range(int(dur * 26)):
        tt = rng.uniform(0, dur); add_i = T(tt); m = min(T(.08), n - add_i)
        if m > 0: thumps[add_i:add_i + m] += np.sin(2 * np.pi * 70 * np.arange(m) / SR) * np.exp(-np.arange(m) / SR * 40) * rng.uniform(.3, 1)
    return (thumps + lp(rng.standard_normal(n), 200) * .4) * np.minimum(1, t / .4) * np.minimum(1, (dur - t) / .4).clip(0)
def footfalls(dur, rate=9):
    n = T(dur); y = np.zeros(n)
    for k in range(int(dur * rate)):
        i = T(k / rate + rng.uniform(0, .03)); m = min(T(.05), n - i)
        if m > 0: y[i:i + m] += bp(rng.standard_normal(m), 150, 1200) * np.exp(-np.arange(m) / SR * 60)
    return y
def zip_(dur=.25):
    n = T(dur); t = np.arange(n) / SR
    f = 3200 * np.exp(-t * 6) + 600
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / dur) * .35
def tick():
    n = T(.03); t = np.arange(n) / SR
    return np.sin(2 * np.pi * rng.uniform(2500, 4200) * t) * np.exp(-t * 160)
def tinkle():
    n = T(.15); t = np.arange(n) / SR; f = rng.uniform(2800, 4800)
    return (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.3 * t)) * np.exp(-t * 30)

# transition whooshes peak ~3 frames before every cut, thud on frame 0
for c in CUT[1:-1]:
    add(sfx, whoosh(.35), c - .175 - .1, .35)
add(sfx, thud(), 5.40, .9)                                   # "And lost."
add(sfx, rumble(3.4), 6.195, .55)                            # stampede
for t0 in [1.2, 2.25, 3.3, 4.35]: add(sfx, pop(), 9.575 + t0, .5)
gun(14.905, 1.9, 11); add(sfx, footfalls(2.9, 8), 15.3, .25); add(sfx, pop(), 14.905 + 1.9, .45)
add(sfx, footfalls(3.0, 10), 17.9, .18)
gun(20.975, .62, 13); add(sfx, clank(), 20.975 + .64, .8)
hiss = hp(rng.standard_normal(T(.8)), 3000) * np.exp(-np.arange(T(.8)) / SR * 4) * .25; add(sfx, hiss, 21.62)
add(sfx, engine(3.2), 22.615, .45); add(sfx, ding(1568), 22.615 + .9, .35)
add(sfx, engine(4.7, bumpy=True), 25.885, .5); add(sfx, footfalls(4.7, 16), 25.885, .35); add(sfx, pop(), 25.885 + 1.7, .45)
add(sfx, pop(), 30.615 + 2.15, .45)
add(sfx, engine(1.6), 33.6, .35); add(sfx, whoosh(.6), 33.405 + 1.25, .5); add(sfx, footfalls(1.6, 22), 34.85, .4)
add(sfx, thud(), 36.55 + 1.15, .35)
for k in range(40): add(sfx, tick(), 36.55 + 1.2 + (k / 40) ** 1.6 * 1.2, .35)
for k in range(60): add(sfx, tinkle(), 38.955 + .3 + k / 60 * 3.4 + rng.uniform(0, .05), .18)
add(sfx, pop(), 38.955 + 3.9, .45)
for k in range(9): add(sfx, zip_(), 43.855 + .2 + k * .47, .4)
add(sfx, ding(2093), 43.855 + 3.8, .3)
add(sfx, engine(1.5) * np.linspace(1, .2, T(1.5)), 48.235, .35)
for k in range(5): add(sfx, tick() * .5, 49.9 + k * .22, .2)

# ---------------------------------------------------------------- mix
sr, v = wavfile.read(os.path.join(HERE, "voice", "voice_raw.wav"))
v = v.astype(np.float64) / 32768
voice = np.zeros(N); voice[:min(N, len(v))] = v[:N]
def rms(x): return np.sqrt(np.mean(x[np.abs(x) > 1e-4] ** 2) + 1e-12)
# voice activity envelope for ducking
a = np.abs(voice); w = T(.05)
vad = np.convolve(a, np.ones(w) / w, "same") > .01
duck = np.convolve(vad.astype(float), np.ones(T(.15)) / T(.15), "same")
duck = 1 - .35 * duck
vr = rms(voice)
music *= (vr * 0.28 * 1.41) / rms(music)   # music ~ -6 dB re voice (+3 dB house rule)
sfx *= (vr * 0.28 * .7) / rms(sfx)         # sfx ~ -9 dB re voice
mix = voice + (music + sfx) * duck
os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
for name, x in [("music", music), ("sfx", sfx), ("premix", mix)]:
    wavfile.write(os.path.join(HERE, "audio", name + ".wav"), SR, (np.clip(x / max(1, np.abs(x).max()), -1, 1) * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(HERE, "audio", "premix.wav"),
                "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-ar", str(SR), "-t", f"{TOTAL:.4f}",
                os.path.join(HERE, "audio", "mix.wav")], check=True)
print("mix written", TOTAL, "s")
