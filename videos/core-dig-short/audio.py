"""8-bit Chiptune Score + Layered Foley/SFX Mixer for core-dig-short.
Mixes ElevenLabs voice_raw.wav with dynamic 8-bit chiptune BGM + synced SFX at -6 dB gated RMS,
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
        # Resample cleanly via ffmpeg
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

    # Cut windows for deadpan comedy vacuum
    t_no_start = beats[1]["start"] - 0.04
    t_no_end = beats[1]["end"] - 0.05
    t_core_start = beats[10]["start"]
    t_freeze = beats[12]["end"] - 0.15
    t_snow_start = beats[14]["start"] - 0.15

    # 8-bit melody & bass progression (140 BPM 16th steps)
    step_dur = 60.0 / 140.0 / 2.0  # 8th note ~0.214s
    steps = int(total_sec / step_dur) + 1

    # C major / A minor playful street -> driving minor underground -> dreamy core
    melody_street = [72, 76, 79, 76, 74, 77, 81, 77, 72, 76, 79, 84, 83, 79, 76, 74]
    bass_street   = [48, 48, 55, 48, 53, 53, 48, 53, 45, 45, 52, 45, 55, 55, 48, 55]

    melody_dig    = [69, 72, 76, 72, 69, 72, 77, 76, 67, 71, 74, 71, 65, 69, 72, 71]
    bass_dig      = [45, 45, 52, 45, 45, 45, 52, 45, 43, 43, 50, 43, 41, 41, 48, 43]

    melody_core   = [76, 0, 79, 0, 84, 0, 79, 0, 77, 0, 81, 0, 79, 0, 74, 0]
    bass_core     = [53, 53, 60, 53, 53, 53, 60, 53, 55, 55, 62, 55, 55, 55, 62, 55]

    rng = np.random.default_rng(42)

    for s in range(steps):
        ts = s * step_dur
        if ts >= total_sec:
            break
        # Deadpan silence during MrBeast "No." and frozen blizzard ending
        if (t_no_start <= ts <= t_no_end) or (t_freeze <= ts <= t_snow_start):
            continue

        i0 = int(ts * SR)
        sn = min(int(step_dur * SR), n_total - i0)
        if sn <= 10:
            continue
        tt = np.arange(sn, dtype=np.float32) / SR
        env = np.exp(-tt * 7.5)

        idx = s % 16
        if ts < t_core_start:
            is_dig = ts >= beats[4]["start"]
            m_note = (melody_dig if is_dig else melody_street)[idx]
            b_note = (bass_dig if is_dig else bass_street)[idx]
            if ts >= t_snow_start:
                # Sad low-pitched 2-note deadpan snow loop
                m_note = [64, 0, 60, 0][s % 4]
                b_note = [45, 0, 41, 0][s % 4]
            if m_note > 0:
                lead = pulse_wave(np.full(sn, midi_hz(m_note), np.float32), 0.25) * env * 0.22
                bgm[i0:i0 + sn] += lead
            if b_note > 0:
                bass = tri_wave(np.full(sn, midi_hz(b_note), np.float32)) * np.exp(-tt * 3.5) * 0.35
                bgm[i0:i0 + sn] += bass
            # Crisp 8-bit noise hi-hat on offbeats
            if s % 2 == 1 and ts < t_snow_start:
                hat = rng.standard_normal(sn).astype(np.float32) * np.exp(-tt * 42.0) * 0.12
                bgm[i0:i0 + sn] += hat
        else:
            # Twinkling core music box
            m_note = melody_core[idx]
            b_note = bass_core[idx]
            if m_note > 0:
                bell = np.sin(2 * np.pi * midi_hz(m_note) * tt) * np.exp(-tt * 6.0) * 0.22
                bgm[i0:i0 + sn] += bell
            if b_note > 0:
                bass = tri_wave(np.full(sn, midi_hz(b_note), np.float32)) * np.exp(-tt * 3.0) * 0.24
                bgm[i0:i0 + sn] += bass

    return bgm


def place(bus: np.ndarray, clip: np.ndarray, t_sec: float, gain: float = 1.0):
    i0 = max(0, int(t_sec * SR))
    n = min(len(clip), len(bus) - i0)
    if n > 0:
        bus[i0:i0 + n] += clip[:n] * gain


def synth_sfx_chip_pop(f0=620, f1=1240, dur=0.10):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    f = np.linspace(f0, f1, n, dtype=np.float32)
    return pulse_wave(f, 0.5) * np.exp(-t * 24.0) * 0.45


def synth_sfx_dig(dur=0.16):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    rng = np.random.default_rng(7)
    thud = np.sin(2 * np.pi * np.linspace(140, 55, n) * t) * np.exp(-t * 28.0) * 0.7
    grit = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 32.0) * 0.35
    return thud + grit


def synth_sfx_freeze(dur=0.45):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    rng = np.random.default_rng(19)
    chime = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 10.0) for f in (1320, 1760, 2640, 3520)) * 0.22
    ice_crack = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 18.0) * 0.5
    sub = np.sin(2 * np.pi * np.linspace(120, 42, n) * t) * np.exp(-t * 8.0) * 0.7
    return chime + ice_crack + sub


def synth_sfx_geyser(dur=0.90):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    rng = np.random.default_rng(99)
    noise = rng.standard_normal(n).astype(np.float32) * np.sin(np.pi * t / dur) ** 0.7 * 0.45
    sweep = np.sin(2 * np.pi * np.linspace(90, 620, n) * t) * np.exp(-t * 2.5) * 0.55
    return noise + sweep


def main():
    with open(os.path.join(HERE, "beats.json"), encoding="utf-8") as f:
        bd = json.load(f)
    beats = bd["beats"]
    total = bd["total"]

    voice = load_wav_mono(os.path.join(HERE, "voice", "voice_raw.wav"))
    n_total = len(voice)

    bgm_raw = synth_chiptune_bgm(total + 0.1, beats)
    bgm = bgm_raw[:n_total]
    if len(bgm) < n_total:
        bgm = np.pad(bgm, (0, n_total - len(bgm)))
    sfx = np.zeros(n_total, np.float32)

    whoosh = load_wav_mono(os.path.join(SFX_DIR, "whoosh.wav"))
    ui_click = load_wav_mono(os.path.join(SFX_DIR, "ui_click.wav"))
    riser_hit = load_wav_mono(os.path.join(SFX_DIR, "riser_hit.wav"))

    # 2-4 frame pre-cut whooshes on major scene cuts!
    for bi in [2, 4, 5, 7, 8, 10, 14]:
        place(sfx, whoosh, beats[bi]["start"] - 0.10, 0.55)

    # Coin / cash pop when MC sees $2,000
    place(sfx, synth_sfx_chip_pop(780, 1560, 0.14), beats[3]["start"], 0.65)
    # Shovel digs
    for dt in [0.15, 0.55, 0.95, 1.35]:
        place(sfx, synth_sfx_dig(), beats[4]["start"] + dt, 0.75)
    # Sewer drop impact
    place(sfx, synth_sfx_dig(0.24), beats[5]["start"] - 0.08, 0.95)
    # Melted shovel sizzle pop
    place(sfx, synth_sfx_chip_pop(480, 220, 0.18), beats[8]["start"] + 1.8, 0.6)
    # Thermostat COOL click!
    place(sfx, ui_click, beats[11]["end"] - 0.15, 0.95)
    # Core freeze + geyser rocket!
    place(sfx, synth_sfx_freeze(), beats[12]["end"] - 0.15, 0.90)
    place(sfx, synth_sfx_geyser(), beats[13]["start"], 0.85)
    # Crash into snowy street
    place(sfx, riser_hit[-int(1.2 * SR):], beats[14]["start"] - 0.35, 0.55)
    # Final $1,000 drop click
    place(sfx, ui_click, beats[15]["start"] + 2.5, 0.80)

    # Gated-RMS ducking & -6 dB relative music+SFX mix
    env = np.convolve(np.abs(voice), np.ones(int(SR * 0.08)) / int(SR * 0.08), mode="same")
    speech_mask = env > (np.max(env) * 0.08)
    duck = np.where(speech_mask, 0.35, 1.0).astype(np.float32)
    duck = np.convolve(duck, np.ones(int(SR * 0.12)) / int(SR * 0.12), mode="same")

    bed = (bgm + sfx) * duck
    v_rms = np.sqrt(np.mean(voice[speech_mask] ** 2)) + 1e-9
    b_rms = np.sqrt(np.mean(bed[speech_mask] ** 2)) + 1e-9
    # Target bed at -6 dB (0.50x RMS -> ~0.35x linear) relative to voice
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
