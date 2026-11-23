"""Horror Foley & Dark Ambient Audio Mixer for ascii-real-horror-short (< 45s)."""
import json
import os
import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, filtfilt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SFX_DIR = os.path.join(REPO_ROOT, "assets", "sfx")
MUSIC_PATH = os.path.join(REPO_ROOT, "assets", "music", "apathy_slowed_reverb.wav")
SR = 48000


def load_wav_mono(path: str) -> np.ndarray:
    tmp = os.path.join(HERE, "audio", "_tmp_mono.wav")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "1", tmp], check=True)
    _, d = wavfile.read(tmp)
    os.remove(tmp)
    if d.dtype == np.int16:
        return d.astype(np.float32) / 32768.0
    if d.dtype == np.int32:
        return d.astype(np.float32) / 2147483648.0
    return d.astype(np.float32)


def place(bus: np.ndarray, clip: np.ndarray, t_sec: float, gain: float = 1.0):
    i0 = int(round(t_sec * SR))
    src0 = 0
    if i0 < 0:
        src0 = -i0
        i0 = 0
    n = min(len(clip) - src0, len(bus) - i0)
    if n > 0:
        bus[i0 : i0 + n] += clip[src0 : src0 + n] * gain


def synth_knock_triple(dur: float = 0.72) -> np.ndarray:
    """Three hollow metallic hallway knocks (knock-knock-knock)."""
    n = int(SR * dur)
    out = np.zeros(n, dtype=np.float32)
    t_all = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    for k_t in (0.02, 0.22, 0.42):
        dt = np.maximum(0.0, t_all - k_t)
        mask = (t_all >= k_t) & (t_all < k_t + 0.16)
        hit = (
            0.75 * np.sin(2 * np.pi * np.linspace(145, 72, n) * dt) * np.exp(-dt * 26.0)
            + 0.45 * np.sin(2 * np.pi * 410.0 * dt) * np.exp(-dt * 38.0)
        ) * mask
        out += hit
    return np.tanh(out * 1.35).astype(np.float32)


def synth_handle_latch(dur: float = 0.26) -> np.ndarray:
    """Metallic door handle pull + latch click."""
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    rng = np.random.default_rng(31)
    click1 = (np.sin(2 * np.pi * 1450 * t) + 0.5 * rng.standard_normal(n)) * np.exp(-t * 75.0) * 0.55
    t2 = np.maximum(0.0, t - 0.11)
    click2 = (np.sin(2 * np.pi * 920 * t2) + 0.4 * np.sin(2 * np.pi * 220 * t2)) * np.exp(-t2 * 42.0) * (t >= 0.11) * 0.75
    return np.tanh((click1 + click2) * 1.4).astype(np.float32)


def synth_glass_slam(dur: float = 0.55) -> np.ndarray:
    """Heavy palm slam against reinforced security glass + sub thud + high glass ring."""
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    rng = np.random.default_rng(91)
    sub = np.sin(2 * np.pi * np.linspace(135, 42, n) * t) * np.exp(-t * 8.5) * 0.95
    slap = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 65.0) * 0.85
    ring = (0.4 * np.sin(2 * np.pi * 780 * t) + 0.25 * np.sin(2 * np.pi * 1640 * t)) * np.exp(-t * 9.0)
    return np.tanh((sub + slap + ring) * 1.45).astype(np.float32)


def synth_bolt_lock(dur: float = 0.28) -> np.ndarray:
    """Heavy steel deadbolt sliding shut."""
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    slide = np.sin(2 * np.pi * 520 * t) * np.exp(-t * 25.0) * 0.55
    clunk = np.sin(2 * np.pi * 165 * np.maximum(0, t - 0.08)) * np.exp(-np.maximum(0, t - 0.08) * 32.0) * (t >= 0.08) * 0.85
    return np.tanh((slide + clunk) * 1.35).astype(np.float32)


def synth_sub_boom(f0: float = 120.0, f1: float = 35.0, dur: float = 0.70) -> np.ndarray:
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    freq = f1 + (f0 - f1) * np.exp(-t * 8.5)
    sub = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 4.0)
    rng = np.random.default_rng(77)
    click = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 50.0) * 0.45
    return np.tanh((sub + click) * 1.5).astype(np.float32)


def synth_footsteps_run(dur: float = 2.0) -> np.ndarray:
    """Rapid sprinting footsteps + subtle metallic key jingle."""
    n = int(SR * dur)
    out = np.zeros(n, dtype=np.float32)
    t_all = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    rng = np.random.default_rng(55)
    for k in range(10):
        st = k * 0.19
        if st >= dur:
            break
        dt = np.maximum(0.0, t_all - st)
        mask = (t_all >= st) & (t_all < st + 0.12)
        thud = np.sin(2 * np.pi * 88.0 * dt) * np.exp(-dt * 34.0) * mask * 0.55
        jingle = (np.sin(2 * np.pi * (4200 + (k % 3) * 550) * dt) * rng.uniform(0.3, 0.8)) * np.exp(-dt * 42.0) * mask * 0.16
        out += thud + jingle
    return np.tanh(out * 1.2).astype(np.float32)


def synth_radio_squelch(dur: float = 0.24) -> np.ndarray:
    """Walkie-talkie static burst + squelch chirp."""
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    rng = np.random.default_rng(2006)
    noise = rng.standard_normal(n).astype(np.float32)
    b, a = butter(2, [850.0 / (SR * 0.5), 4200.0 / (SR * 0.5)], btype="band")
    burst = filtfilt(b, a, noise).astype(np.float32) * np.exp(-t * 14.0) * 0.85
    chirp = np.sin(2 * np.pi * 1850 * t) * np.exp(-t * 45.0) * 0.45
    return np.tanh((burst + chirp) * 1.3).astype(np.float32)


def find_word(words, target: str, default_sec: float) -> float:
    t_low = target.lower()
    for w in words:
        if w["w"].strip(".,!?:;\"'—").lower() == t_low:
            return float(w["start"])
    return default_sec


def main():
    os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
    with open(os.path.join(HERE, "beats.json"), encoding="utf-8") as f:
        bd = json.load(f)
    beats = bd["beats"]

    voice = load_wav_mono(os.path.join(HERE, "voice", "voice_raw.wav"))
    n_total = len(voice)

    music_raw = load_wav_mono(MUSIC_PATH)
    offset = int(34.0 * SR)
    if len(music_raw) > offset + n_total:
        bgm = music_raw[offset : offset + n_total].copy()
    else:
        bgm = np.tile(music_raw, int(np.ceil(n_total / len(music_raw))))[:n_total].copy()

    # Brief eerie silence drops on "Luckily..." lock and before radio voice
    t_lock = beats[6]["start"]
    t_unluck = beats[7]["start"]
    t_radio = beats[12]["start"]
    bgm_env = np.ones(n_total, dtype=np.float32)

    def fade_dip(t0, t1, level=0.10, ramp=0.07):
        i0, i1 = max(0, int(t0 * SR)), min(n_total, int(t1 * SR))
        r = max(1, int(ramp * SR))
        if i1 <= i0:
            return
        bgm_env[i0:i1] = level
        if i0 + r < i1:
            bgm_env[i0 : i0 + r] = np.linspace(1.0, level, r)
        if i1 - r > i0:
            bgm_env[i1 - r : i1] = np.linspace(level, 1.0, r)

    fade_dip(t_lock, t_unluck + 0.15, level=0.12)
    fade_dip(t_radio - 0.12, beats[12]["speechEnd"] + 0.08, level=0.06)
    bgm = bgm * bgm_env
    bgm = bgm * (0.18 / (float(np.sqrt(np.mean(bgm ** 2))) + 1e-8))

    sfx = np.zeros(n_total, dtype=np.float32)
    whoosh = load_wav_mono(os.path.join(SFX_DIR, "whoosh.wav"))
    whoosh_low = load_wav_mono(os.path.join(SFX_DIR, "whoosh_low.wav"))
    riser_hit = load_wav_mono(os.path.join(SFX_DIR, "riser_hit.wav"))
    ui_click = load_wav_mono(os.path.join(SFX_DIR, "ui_click.wav"))

    # Law #21: 2-4f pre-cut whooshes on major scene cuts
    for bi in [1, 3, 4, 6, 7, 8, 10, 11, 13]:
        clip = whoosh_low if bi in (4, 7, 10, 13) else whoosh
        place(sfx, clip, beats[bi]["start"] - 0.09, 0.36)

    # Beat 0: Knocking inside locked hallway
    t_knock = find_word(beats[0]["words"], "knocking", 1.55)
    place(sfx, synth_knock_triple(), t_knock - 0.04, 0.72)

    # Beat 1: Grabs steel door handle
    place(sfx, synth_handle_latch(), find_word(beats[1]["words"], "grabs", 4.75), 0.78)

    # Beat 4: Hand slams onto the glass!
    t_slam = find_word(beats[4]["words"], "slams", 9.85)
    place(sfx, synth_glass_slam(), t_slam - 0.02, 0.92)

    # Beat 5: Eyes snap wide
    place(sfx, riser_hit[-int(0.8 * SR):], beats[5]["start"] - 0.15, 0.40)

    # Beat 6: Steel bolt locked
    place(sfx, synth_bolt_lock(), find_word(beats[6]["words"], "locked", 13.85), 0.75)

    # Beat 7: Unluckily, wearing his exact face -> Sub boom!
    place(sfx, synth_sub_boom(125, 34, 0.75), find_word(beats[7]["words"], "exact", 16.5), 0.90)

    # Beat 8-9: "You see," tick + creepy smile tension riser
    place(sfx, ui_click, beats[8]["start"], 0.55)
    place(sfx, riser_hit[-int(1.2 * SR):], beats[9]["end"] - 0.95, 0.45)

    # Beat 10: Sprints down stairwell + keys shaking
    place(sfx, synth_footsteps_run(beats[10]["end"] - beats[10]["start"]), beats[10]["start"], 0.75)

    # Beat 11-12: Walkie-talkie static squelch -> doppelganger voice -> final monitor sting!
    place(sfx, synth_radio_squelch(), find_word(beats[11]["words"], "crackles", 27.6), 0.78)
    place(sfx, synth_radio_squelch(0.16), beats[12]["speechEnd"], 0.50)
    place(sfx, synth_sub_boom(135, 33, 0.85), beats[13]["start"] + 0.15, 0.92)

    # Gated-RMS ducking & -14 LUFS master (Law #22)
    env = np.convolve(np.abs(voice), np.ones(int(SR * 0.07)) / int(SR * 0.07), mode="same")
    speech_mask = env > (np.max(env) * 0.08)
    duck = np.where(speech_mask, 0.36, 1.0).astype(np.float32)
    duck = np.convolve(duck, np.ones(int(SR * 0.11)) / int(SR * 0.11), mode="same")

    bed = (bgm + sfx) * duck
    v_rms = float(np.sqrt(np.mean(voice[speech_mask] ** 2)) + 1e-9)
    b_rms = float(np.sqrt(np.mean(bed[speech_mask] ** 2)) + 1e-9)
    bed = bed * (v_rms * 0.44 / b_rms)

    raw_mix = voice + bed
    pre_wav = os.path.join(HERE, "audio", "mix_pre.wav")
    fin_wav = os.path.join(HERE, "audio", "mix.wav")
    wavfile.write(pre_wav, SR, (np.clip(raw_mix, -0.98, 0.98) * 32767).astype(np.int16))

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", pre_wav,
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=7",
        "-ar", str(SR), "-ac", "1", fin_wav,
    ], check=True)
    print(f"Mastered {fin_wav} (-14 LUFS)")


if __name__ == "__main__":
    main()
