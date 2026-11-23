"""8-bit Multi-Dimensional Chiptune Score + Layered Foley/SFX Mixer for dimension-100-short.
Mixes voice_raw.wav with dynamic dimension-shifting 8-bit chiptune BGM + synced SFX at -6 dB gated RMS,
and masters final mix.wav to -14.0 LUFS / -1.0 dBTP.
"""
import json
import os
import subprocess
import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SFX_DIR = os.path.join(REPO_ROOT, "assets", "sfx")
SR = 48000


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


def synth_chiptune_bgm(total_sec: float, beats: list) -> np.ndarray:
    n_total = int(total_sec * SR)
    bgm = np.zeros(n_total, np.float32)

    # Key timing boundaries
    t_no_start = beats[1]["start"] - 0.04
    t_no_end = beats[1]["end"] - 0.04
    t_1d_start = beats[4]["start"]
    t_4d_start = beats[7]["start"]
    t_11d_start = beats[9]["start"]
    t_100d_flash = beats[12]["start"] - 0.06
    t_100d_calc = beats[13]["start"]
    t_return_start = beats[14]["start"]

    step_dur = 60.0 / 144.0 / 2.0  # 8th note at 144 BPM (~0.208s)
    steps = int(total_sec / step_dur) + 1

    # 3D Street theme (playful C major)
    mel_street  = [72, 76, 79, 76, 74, 77, 81, 77, 72, 76, 79, 84, 83, 79, 76, 74]
    bass_street = [48, 48, 55, 48, 53, 53, 48, 53, 45, 45, 52, 45, 55, 55, 48, 55]

    # 1D / 2D Flatland Arcade theme (driving A minor)
    mel_2d      = [69, 72, 76, 81, 79, 76, 72, 69, 67, 71, 74, 79, 77, 74, 71, 68]
    bass_2d     = [45, 45, 52, 45, 45, 45, 52, 45, 43, 43, 50, 43, 40, 40, 47, 40]

    # 4D Tesseract theme (Lydian / Whole-tone shimmering mystery)
    mel_4d      = [74, 78, 80, 84, 82, 78, 76, 74, 76, 80, 82, 86, 84, 80, 78, 76]
    bass_4d     = [50, 50, 57, 50, 52, 52, 59, 52, 50, 50, 57, 50, 48, 48, 55, 48]

    # 11D-99D String Theory Overdrive (rising sci-fi arpeggio)
    mel_11d     = [76, 79, 83, 88, 78, 81, 85, 90, 80, 83, 87, 92, 81, 84, 88, 93]
    bass_11d    = [52, 52, 59, 52, 54, 54, 61, 54, 56, 56, 63, 56, 57, 57, 64, 57]

    rng = np.random.default_rng(100)

    for s in range(steps):
        ts = s * step_dur
        if ts >= total_sec:
            break
        # Deadpan silence during MrBeast "No." and the instant 100D flash
        if (t_no_start <= ts <= t_no_end) or (t_100d_flash <= ts < t_100d_calc):
            continue

        i0 = int(ts * SR)
        sn = min(int(step_dur * SR), n_total - i0)
        if sn <= 10:
            continue
        tt = np.arange(sn, dtype=np.float32) / SR
        env = np.exp(-tt * 7.8)
        idx = s % 16

        if ts < t_1d_start:
            # 3D Street
            m_note = mel_street[idx]
            b_note = bass_street[idx]
            lead = pulse_wave(np.full(sn, midi_hz(m_note), np.float32), 0.25) * env * 0.22
            bass = tri_wave(np.full(sn, midi_hz(b_note), np.float32)) * np.exp(-tt * 3.5) * 0.34
            bgm[i0:i0 + sn] += lead + bass
            if s % 2 == 1:
                hat = rng.standard_normal(sn).astype(np.float32) * np.exp(-tt * 42.0) * 0.11
                bgm[i0:i0 + sn] += hat
        elif ts < t_4d_start:
            # 1D / 2D Flatland
            m_note = mel_2d[idx]
            b_note = bass_2d[idx]
            lead = pulse_wave(np.full(sn, midi_hz(m_note), np.float32), 0.125) * env * 0.21
            bass = tri_wave(np.full(sn, midi_hz(b_note), np.float32)) * np.exp(-tt * 4.0) * 0.34
            bgm[i0:i0 + sn] += lead + bass
            if s % 2 == 1:
                hat = rng.standard_normal(sn).astype(np.float32) * np.exp(-tt * 45.0) * 0.12
                bgm[i0:i0 + sn] += hat
        elif ts < t_11d_start:
            # 4D Tesseract (crystalline dual sine + triangle)
            m_note = mel_4d[idx]
            b_note = bass_4d[idx]
            bell = (np.sin(2 * np.pi * midi_hz(m_note) * tt) + 0.5 * np.sin(2 * np.pi * midi_hz(m_note + 7) * tt)) * np.exp(-tt * 6.0) * 0.19
            bass = tri_wave(np.full(sn, midi_hz(b_note), np.float32)) * np.exp(-tt * 3.0) * 0.28
            bgm[i0:i0 + sn] += bell + bass
        elif ts < t_100d_flash:
            # 11D -> 99D String Theory Overdrive
            m_note = mel_11d[idx]
            b_note = bass_11d[idx]
            lead = pulse_wave(np.full(sn, midi_hz(m_note), np.float32), 0.5) * env * 0.23
            bass = tri_wave(np.full(sn, midi_hz(b_note), np.float32)) * np.exp(-tt * 3.8) * 0.35
            hat = rng.standard_normal(sn).astype(np.float32) * np.exp(-tt * 38.0) * 0.13
            bgm[i0:i0 + sn] += lead + bass + hat
        elif ts < t_return_start:
            # 100D Calculator 6-Pixel World (hilarious sparse 1-bit pocket calculator piezo beeps!)
            calc_note = [84, 0, 79, 0, 84, 0, 76, 0][s % 8]
            if calc_note > 0:
                beep = pulse_wave(np.full(sn, midi_hz(calc_note), np.float32), 0.5) * np.exp(-tt * 14.0) * 0.18
                bgm[i0:i0 + sn] += beep
        else:
            # Street return deadpan 2-note walk
            m_note = [64, 0, 60, 0][s % 4]
            b_note = [45, 0, 41, 0][s % 4]
            if m_note > 0:
                bgm[i0:i0 + sn] += pulse_wave(np.full(sn, midi_hz(m_note), np.float32), 0.25) * env * 0.18
            if b_note > 0:
                bgm[i0:i0 + sn] += tri_wave(np.full(sn, midi_hz(b_note), np.float32)) * np.exp(-tt * 3.5) * 0.28

    return bgm


def place(bus: np.ndarray, clip: np.ndarray, t_sec: float, gain: float = 1.0):
    i0 = max(0, int(t_sec * SR))
    n = min(len(clip), len(bus) - i0)
    if n > 0:
        bus[i0:i0 + n] += clip[:n] * gain


def synth_sfx_chip_pop(f0=620, f1=1240, dur=0.11):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    f = np.linspace(f0, f1, n, dtype=np.float32)
    return pulse_wave(f, 0.5) * np.exp(-t * 24.0) * 0.45


def synth_sfx_1d_squash(dur=0.28):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    f = np.linspace(980, 95, n, dtype=np.float32)
    zap = pulse_wave(f, 0.25) * np.exp(-t * 10.0) * 0.55
    thud = np.sin(2 * np.pi * np.linspace(140, 48, n) * t) * np.exp(-t * 16.0) * 0.65
    return zap + thud


def synth_sfx_4d_shimmer(dur=0.45):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    chime = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 8.0) for f in (1046.5, 1318.5, 1480.0, 1975.5)) * 0.20
    return chime.astype(np.float32)


def synth_sfx_overdrive_riser(dur=0.85):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    f = np.linspace(180, 1760, n, dtype=np.float32)
    sweep = pulse_wave(f, 0.5) * (t / dur) ** 0.8 * 0.45
    sub = np.sin(2 * np.pi * np.linspace(90, 45, n) * t) * np.exp(-t * 4.0) * 0.55
    return sweep + sub


def synth_sfx_100d_downgrade(dur=0.38):
    # Integer overflow crash into 6-pixel calculator beep!
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    steps = np.floor(t / (dur / 6))
    freqs = 1400.0 - steps * 190.0
    return pulse_wave(freqs.astype(np.float32), 0.5) * np.exp(-t * 4.5) * 0.55


def synth_sfx_coin_nickel(dur=0.22):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    c1 = np.sin(2 * np.pi * 2637.0 * t) * np.exp(-t * 22.0)
    c2 = np.sin(2 * np.pi * 3520.0 * np.maximum(0, t - 0.045)) * np.exp(-np.maximum(0, t - 0.045) * 18.0) * (t >= 0.045)
    return ((c1 + c2) * 0.45).astype(np.float32)


def main():
    with open(os.path.join(HERE, "beats.json"), encoding="utf-8") as f:
        bd = json.load(f)
    beats = bd["beats"]
    total = bd["total"]

    voice = load_wav_mono(os.path.join(HERE, "voice", "voice_raw.wav"))
    n_total = len(voice)

    bgm_raw = synth_chiptune_bgm(total + 0.2, beats)
    bgm = bgm_raw[:n_total]
    if len(bgm) < n_total:
        bgm = np.pad(bgm, (0, n_total - len(bgm)))
    sfx = np.zeros(n_total, np.float32)

    whoosh = load_wav_mono(os.path.join(SFX_DIR, "whoosh.wav"))
    ui_click = load_wav_mono(os.path.join(SFX_DIR, "ui_click.wav"))
    riser_hit = load_wav_mono(os.path.join(SFX_DIR, "riser_hit.wav"))

    # Law #21: 2-4 frame pre-cut whooshes on major scene cuts (t_cut - 0.08s)
    for bi in [2, 4, 5, 7, 9, 11, 13, 14]:
        if bi < len(beats):
            place(sfx, whoosh, beats[bi]["start"] - 0.09, 0.55)

    # Beat 3: $2,000 cash pop + toaster door click
    place(sfx, synth_sfx_chip_pop(780, 1560, 0.14), beats[3]["start"], 0.65)
    place(sfx, ui_click, beats[3]["end"] - 0.14, 0.90)

    # Beat 4: Dial starts at 1D -> squash zap!
    place(sfx, ui_click, beats[4]["start"] + 0.15, 0.85)
    place(sfx, synth_sfx_1d_squash(), beats[4]["end"] - 0.45, 0.85)

    # Beat 5: 2D Flatland arcade pop
    place(sfx, synth_sfx_chip_pop(520, 1040, 0.12), beats[5]["start"] - 0.05, 0.70)

    # Beat 6: Crank dial past 3!
    place(sfx, ui_click, beats[6]["end"] - 0.18, 0.95)

    # Beat 7-8: 4D Tesseract shimmer + Klein bottle pop
    place(sfx, synth_sfx_4d_shimmer(), beats[7]["start"], 0.80)
    place(sfx, synth_sfx_chip_pop(980, 440, 0.16), beats[8]["end"] - 0.55, 0.75)

    # Beat 9: 11D String Warden origami fold shimmer
    place(sfx, synth_sfx_4d_shimmer(0.35), beats[9]["start"] + 0.10, 0.70)

    # Beat 10-12: Maximum Overdrive button click + riser into 100D integer overflow!
    place(sfx, ui_click, beats[10]["end"] - 0.16, 0.95)
    place(sfx, synth_sfx_overdrive_riser(), beats[11]["start"] + 0.10, 0.75)
    place(sfx, riser_hit[-int(1.1 * SR):], beats[12]["start"] - 0.25, 0.55)
    place(sfx, synth_sfx_100d_downgrade(), beats[12]["end"] - 0.15, 0.85)

    # Beat 14: Pop back onto 3D street
    place(sfx, synth_sfx_1d_squash(0.22), beats[14]["start"] - 0.08, 0.75)

    # Beat 15: Nickel drop clink at the final punchline!
    place(sfx, synth_sfx_coin_nickel(), beats[15]["speechEnd"] - 0.28, 0.95)

    # Gated-RMS ducking & -6 dB relative music+SFX mix (Law #22)
    env = np.convolve(np.abs(voice), np.ones(int(SR * 0.08)) / int(SR * 0.08), mode="same")
    speech_mask = env > (np.max(env) * 0.08)
    duck = np.where(speech_mask, 0.35, 1.0).astype(np.float32)
    duck = np.convolve(duck, np.ones(int(SR * 0.12)) / int(SR * 0.12), mode="same")

    bed = (bgm + sfx) * duck
    v_rms = np.sqrt(np.mean(voice[speech_mask] ** 2)) + 1e-9
    b_rms = np.sqrt(np.mean(bed[speech_mask] ** 2)) + 1e-9
    target_ratio = 0.38
    bed = bed * (v_rms * target_ratio / b_rms)

    raw_mix = voice + bed
    os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
    pre_wav = os.path.join(HERE, "audio", "mix_pre.wav")
    fin_wav = os.path.join(HERE, "audio", "mix.wav")
    wavfile.write(pre_wav, SR, (np.clip(raw_mix, -0.98, 0.98) * 32767).astype(np.int16))

    # Loudness master to -14 LUFS / -1.0 dBTP
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", pre_wav,
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=7",
        "-ar", str(SR), "-ac", "1", fin_wav,
    ], check=True)
    print(f"Mastered {fin_wav} (-14 LUFS)")


if __name__ == "__main__":
    main()
