"""Shared 8-Bit Chiptune Synthesizer & -14 LUFS Ducking Mixer for pixel shorts."""
import json
import os
import subprocess
import numpy as np
from scipy.io import wavfile

SR = 48000
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SFX_DIR = os.path.join(REPO_ROOT, "assets", "sfx")


def load_wav_mono(path: str) -> np.ndarray:
    sr, data = wavfile.read(path)
    x = data.astype(np.float32) / (32768.0 if data.dtype == np.int16 else 1.0)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != SR:
        tmp = path + "_48k.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "1", tmp], check=True)
        _, d2 = wavfile.read(tmp)
        os.remove(tmp)
        x = d2.astype(np.float32) / 32768.0
    return x


def pulse_wave(freq_arr: np.ndarray, duty: float = 0.25) -> np.ndarray:
    phase = np.cumsum(freq_arr / SR) % 1.0
    return np.where(phase < duty, 1.0, -1.0).astype(np.float32)


def tri_wave(freq_arr: np.ndarray) -> np.ndarray:
    phase = np.cumsum(freq_arr / SR) % 1.0
    return (4.0 * np.abs(phase - 0.5) - 1.0).astype(np.float32)


def midi_hz(m: float) -> float:
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def place(bus: np.ndarray, clip: np.ndarray, t_sec: float, gain: float = 1.0):
    i0 = max(0, int(t_sec * SR))
    n = min(len(clip), len(bus) - i0)
    if n > 0:
        bus[i0:i0 + n] += clip[:n] * gain


def synth_chip_pop(f0=620, f1=1240, dur=0.12):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    f = np.linspace(f0, f1, n, dtype=np.float32)
    return pulse_wave(f, 0.5) * np.exp(-t * 24.0) * 0.45


def synth_impact_zap(f0=980, f1=75, dur=0.28):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    f = np.linspace(f0, f1, n, dtype=np.float32)
    zap = pulse_wave(f, 0.25) * np.exp(-t * 10.0) * 0.50
    sub = np.sin(2 * np.pi * np.linspace(140, 46, n) * t) * np.exp(-t * 15.0) * 0.65
    return zap + sub


def synth_shimmer(freqs=(1046.5, 1318.5, 1480.0, 1975.5), dur=0.45):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    return (sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 7.5) for f in freqs) * 0.20).astype(np.float32)


def synth_roar_rumble(dur=0.55):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    rng = np.random.default_rng(33)
    noise = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 4.5) * 0.35
    growl = pulse_wave(np.linspace(110, 58, n, dtype=np.float32), 0.5) * np.exp(-t * 3.5) * 0.45
    return noise + growl


def synth_bubble_bloop(dur=0.22):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    f = 320 + 680 * (t / dur) ** 1.5
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 12.0) * 0.55


def synth_overdrive_riser(dur=0.80):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    f = np.linspace(180, 1760, n, dtype=np.float32)
    sweep = pulse_wave(f, 0.5) * (t / dur) ** 0.8 * 0.42
    sub = np.sin(2 * np.pi * np.linspace(90, 45, n) * t) * np.exp(-t * 4.0) * 0.55
    return sweep + sub


def synth_coin_clink(dur=0.22):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    c1 = np.sin(2 * np.pi * 2637.0 * t) * np.exp(-t * 22.0)
    c2 = np.sin(2 * np.pi * 3520.0 * np.maximum(0, t - 0.045)) * np.exp(-np.maximum(0, t - 0.045) * 18.0) * (t >= 0.045)
    return ((c1 + c2) * 0.45).astype(np.float32)


def synth_segmented_bgm(total_sec: float, beats: list, segments: list, bpm: float = 142.0, seed: int = 42) -> np.ndarray:
    """Synthesize a multi-section 8-bit chiptune score.
    segments: list of dicts {start_beat, end_beat, melody, bass, duty, bell, hat, silent}
    """
    n_total = int(total_sec * SR)
    bgm = np.zeros(n_total, np.float32)
    step_dur = 60.0 / bpm / 2.0
    steps = int(total_sec / step_dur) + 1
    rng = np.random.default_rng(seed)

    # Deadpan silence during MrBeast "No."
    t_no_start = beats[1]["start"] - 0.04
    t_no_end = beats[1]["end"] - 0.04

    for s in range(steps):
        ts = s * step_dur
        if ts >= total_sec or (t_no_start <= ts <= t_no_end):
            continue

        seg = segments[-1]
        for cand in segments:
            t0 = beats[cand["start_beat"]]["start"] if cand["start_beat"] < len(beats) else total_sec
            t1 = beats[cand["end_beat"]]["end"] if cand["end_beat"] < len(beats) else total_sec + 1.0
            if t0 <= ts < t1:
                seg = cand
                break

        if seg.get("silent"):
            continue

        i0 = int(ts * SR)
        sn = min(int(step_dur * SR), n_total - i0)
        if sn <= 10:
            continue
        tt = np.arange(sn, dtype=np.float32) / SR
        env = np.exp(-tt * 7.6)

        mel = seg["melody"]
        bas = seg["bass"]
        m_note = mel[s % len(mel)]
        b_note = bas[s % len(bas)]

        if m_note > 0:
            if seg.get("bell"):
                lead = (np.sin(2 * np.pi * midi_hz(m_note) * tt) + 0.4 * np.sin(2 * np.pi * midi_hz(m_note + 12) * tt)) * np.exp(-tt * 6.0) * 0.20
            else:
                lead = pulse_wave(np.full(sn, midi_hz(m_note), np.float32), seg.get("duty", 0.25)) * env * 0.22
            bgm[i0:i0 + sn] += lead
        if b_note > 0:
            bass = tri_wave(np.full(sn, midi_hz(b_note), np.float32)) * np.exp(-tt * 3.5) * 0.34
            bgm[i0:i0 + sn] += bass
        if seg.get("hat", True) and s % 2 == 1:
            hat = rng.standard_normal(sn).astype(np.float32) * np.exp(-tt * 42.0) * 0.11
            bgm[i0:i0 + sn] += hat

    return bgm


def mix_and_master(project_dir: str, bgm_fn, sfx_fn):
    with open(os.path.join(project_dir, "beats.json"), encoding="utf-8") as f:
        bd = json.load(f)
    beats = bd["beats"]
    total = bd["total"]

    voice = load_wav_mono(os.path.join(project_dir, "voice", "voice_raw.wav"))
    n_total = len(voice)

    bgm_raw = bgm_fn(total + 0.2, beats)
    bgm = bgm_raw[:n_total]
    if len(bgm) < n_total:
        bgm = np.pad(bgm, (0, n_total - len(bgm)))
    sfx = np.zeros(n_total, np.float32)

    whoosh = load_wav_mono(os.path.join(SFX_DIR, "whoosh.wav"))
    ui_click = load_wav_mono(os.path.join(SFX_DIR, "ui_click.wav"))
    riser_hit = load_wav_mono(os.path.join(SFX_DIR, "riser_hit.wav"))

    # Pre-cut whooshes on major scene transitions (Law #21)
    for bi in [2, 4, 5, 7, 9, 11, 13, 14]:
        if bi < len(beats):
            place(sfx, whoosh, beats[bi]["start"] - 0.09, 0.55)

    sfx_fn(sfx, beats, {"whoosh": whoosh, "ui_click": ui_click, "riser_hit": riser_hit})

    # Gated-RMS ducking & -6 dB relative music+SFX mix (Law #22)
    env = np.convolve(np.abs(voice), np.ones(int(SR * 0.08)) / int(SR * 0.08), mode="same")
    speech_mask = env > (np.max(env) * 0.08)
    duck = np.where(speech_mask, 0.35, 1.0).astype(np.float32)
    duck = np.convolve(duck, np.ones(int(SR * 0.12)) / int(SR * 0.12), mode="same")

    bed = (bgm + sfx) * duck
    v_rms = np.sqrt(np.mean(voice[speech_mask] ** 2)) + 1e-9
    b_rms = np.sqrt(np.mean(bed[speech_mask] ** 2)) + 1e-9
    bed = bed * (v_rms * 0.38 / b_rms)

    raw_mix = voice + bed
    os.makedirs(os.path.join(project_dir, "audio"), exist_ok=True)
    pre_wav = os.path.join(project_dir, "audio", "mix_pre.wav")
    fin_wav = os.path.join(project_dir, "audio", "mix.wav")
    wavfile.write(pre_wav, SR, (np.clip(raw_mix, -0.98, 0.98) * 32767).astype(np.int16))

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", pre_wav,
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=7",
        "-ar", str(SR), "-ac", "1", fin_wav,
    ], check=True)
    print(f"[{os.path.basename(project_dir)}] Mastered {fin_wav} (-14 LUFS)")
