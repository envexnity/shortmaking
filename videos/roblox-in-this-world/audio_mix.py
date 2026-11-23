"""
audio_mix.py — Track 5 Roblox "In This World" Storytime Audio & Foley Mix (< 45s)
Implements the 5-Layer Timeline Mix from [[In This World Roblox Storytime - Editing, Zooms & VFX Bible]]:
  1. Voiceover (-14 LUFS, zero dead air)
  2. 2-4 Frame Pre-Cut Whooshes
  3. Risers & 65 Hz Sub-Bass Impacts
  4. Classic Roblox Foley (R6 plastic footsteps, Gravity Coil boing, Robux taxi-meter ticks, Lava crack, Admin Ban Hammer)
  5. Underscore Music Bed (-6 dB gated RMS ducking)
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
    _, data = wavfile.read(tmp)
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


def place_sfx(buf: np.ndarray, sfx: np.ndarray, t_sec: float, gain: float = 0.30):
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


def synth_gravity_coil_boing(dur_s: float = 0.65) -> np.ndarray:
    """Classic Roblox Gravity Coil springy resonant pitch-bend boing."""
    n = int(dur_s * SR)
    t = np.linspace(0, dur_s, n, dtype=np.float32)
    freq = 180.0 + 540.0 * (t / dur_s) ** 0.7 + 45.0 * np.sin(2.0 * np.pi * 18.0 * t)
    phase = 2.0 * np.pi * np.cumsum(freq) / SR
    sig = (0.65 * np.sin(phase) + 0.35 * np.sin(2.0 * phase)) * np.exp(-t * 3.4)
    return np.stack([sig, sig], axis=1).astype(np.float32)


def synth_bass_drop(dur_s: float = 0.45) -> np.ndarray:
    """65 Hz sub-bass impact thud + 2.5 kHz slap transient."""
    n = int(dur_s * SR)
    t = np.linspace(0, dur_s, n, dtype=np.float32)
    freq = 115.0 * np.exp(-t * 7.5) + 58.0
    phase = 2.0 * np.pi * np.cumsum(freq) / SR
    sub = np.sin(phase) * np.exp(-t * 5.2)
    click = np.sin(2.0 * np.pi * 2200.0 * t) * np.exp(-t * 48.0) * 0.35
    sig = np.tanh((sub + click) * 1.4)
    return np.stack([sig, sig], axis=1).astype(np.float32)


def synth_coin_tick(freq_hz: float = 1650.0, dur_s: float = 0.075) -> np.ndarray:
    """Crisp Robux taxi-meter deduction ping."""
    n = int(dur_s * SR)
    t = np.linspace(0, dur_s, n, dtype=np.float32)
    sig = (0.7 * np.sin(2.0 * np.pi * freq_hz * t) + 0.3 * np.sin(2.0 * np.pi * (freq_hz * 1.5) * t)) * np.exp(-t * 38.0)
    return np.stack([sig, sig], axis=1).astype(np.float32)


def synth_error_buzzer(dur_s: float = 0.32) -> np.ndarray:
    """Zero-Robux warning double-buzz."""
    n = int(dur_s * SR)
    t = np.linspace(0, dur_s, n, dtype=np.float32)
    gate = np.where((t < 0.13) | (t > 0.18), 1.0, 0.0).astype(np.float32)
    sig = np.sign(np.sin(2.0 * np.pi * 145.0 * t)) * 0.35 * gate * np.exp(-t * 2.5)
    b, a = butter(2, 950.0 / (SR * 0.5), btype="low")
    sig = filtfilt(b, a, sig).astype(np.float32)
    return np.stack([sig, sig], axis=1)


def find_word_time(words, target_low: str, after_sec: float = 0.0, default_sec: float = 1.0) -> float:
    for w in words:
        if float(w["s"]) >= after_sec and w["w"].strip(".,!?:;\"").lower() == target_low:
            return float(w["s"])
    return default_sec


def build_mix(cut_times_sec):
    voice_mp3 = os.path.join(BASE, "voice", "voice.mp3")
    words_path = os.path.join(BASE, "voice", "words.json")
    words_data = json.load(open(words_path, encoding="utf-8")) if os.path.exists(words_path) else {}
    sections = words_data.get("sections", {})
    words = words_data.get("words", [])

    vo = load_audio_stereo(voice_mp3)
    total_samples = len(vo) + int(0.45 * SR)
    vo_pad = np.zeros((total_samples, 2), dtype=np.float32)
    vo_pad[: len(vo)] = vo

    vo_rms = float(np.sqrt(np.mean(vo ** 2)) + 1e-6)
    vo_pad *= 0.195 / vo_rms

    # -6 dB gated RMS ducking envelope
    vo_mono = np.abs(vo_pad.mean(axis=1))
    win = int(0.08 * SR)
    env = np.convolve(vo_mono, np.ones(win, dtype=np.float32) / win, mode="same")
    duck = np.where(env > 0.025, 0.30, 0.52).astype(np.float32)
    b_l, a_l = butter(2, 5.0 / (SR * 0.5), btype="low")
    duck = np.clip(filtfilt(b_l, a_l, duck).astype(np.float32), 0.26, 0.56)

    # Music bed from curated pool
    music_path = os.path.join(ROOT, "assets", "music", "snowfall_clip.wav")
    if not os.path.exists(music_path):
        music_path = os.path.join(ROOT, "assets", "music", "apathy_slowed_reverb.wav")
    if os.path.exists(music_path):
        mus = load_audio_stereo(music_path)
        reps = int(np.ceil(total_samples / len(mus))) + 1
        mus = np.tile(mus, (reps, 1))[:total_samples]
        mus_rms = float(np.sqrt(np.mean(mus ** 2)) + 1e-6)
        mus *= 0.14 / mus_rms
        fi, fo = int(0.25 * SR), int(0.55 * SR)
        mus[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
        mus[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    else:
        mus = np.zeros((total_samples, 2), dtype=np.float32)

    sfx_buf = np.zeros((total_samples, 2), dtype=np.float32)

    w_hi_p = os.path.join(ROOT, "assets", "sfx", "whoosh.wav")
    w_lo_p = os.path.join(ROOT, "assets", "sfx", "whoosh_low.wav")
    riser_p = os.path.join(ROOT, "assets", "sfx", "riser_hit.wav")
    click_p = os.path.join(ROOT, "assets", "sfx", "ui_click.wav")

    w_hi = load_audio_stereo(w_hi_p) if os.path.exists(w_hi_p) else None
    w_lo = load_audio_stereo(w_lo_p) if os.path.exists(w_lo_p) else None
    riser = load_audio_stereo(riser_p) if os.path.exists(riser_p) else None
    click = load_audio_stereo(click_p) if os.path.exists(click_p) else None

    bass_drop = synth_bass_drop()
    coil_boing = synth_gravity_coil_boing()
    buzzer = synth_error_buzzer()

    # 1. Frame 0 opening blurred punch-out whoosh + Hook snapback bass drop
    if w_hi is not None:
        place_sfx(sfx_buf, w_hi, 0.02, gain=0.22)
    t_zero1 = find_word_time(words, "zero", 2.0, 4.2)
    place_sfx(sfx_buf, bass_drop, t_zero1, gain=0.26)
    place_sfx(sfx_buf, buzzer, t_zero1 + 0.05, gain=0.22)

    # 2. Rich kids bunny-hopping ticks & boings in Beat 2
    b2_s = sections.get("beat2", {}).get("start", 6.5)
    for hop_i in range(4):
        place_sfx(sfx_buf, synth_coin_tick(1450.0 + hop_i * 120.0), b2_s + 1.2 + hop_i * 0.65, gain=0.18)

    # 3. Beat 3 Lava floor crack + "balance flashed zero" buzzer
    b3_s = sections.get("beat3", {}).get("start", 11.5)
    place_sfx(sfx_buf, bass_drop, b3_s + 0.4, gain=0.22)
    t_zero2 = find_word_time(words, "zero", b3_s + 1.0, b3_s + 4.8)
    place_sfx(sfx_buf, buzzer, t_zero2, gain=0.25)

    # 4. Beat 4 Gravity Coil boing + roof smash impact
    b4_s = sections.get("beat4", {}).get("start", 17.5)
    t_coil = find_word_time(words, "coil", b4_s, b4_s + 2.2)
    place_sfx(sfx_buf, coil_boing, t_coil, gain=0.30)
    t_launched = find_word_time(words, "launched", b4_s, b4_s + 3.2)
    place_sfx(sfx_buf, coil_boing, t_launched, gain=0.34)
    place_sfx(sfx_buf, bass_drop, t_launched + 0.45, gain=0.28)

    # 5. Beat 5 Rapid Taxi-Meter Robux Debt Ticks (-R$ 100 -> -R$ 4,200!)
    b5_s = sections.get("beat5", {}).get("start", 24.0)
    for tick_i in range(14):
        place_sfx(
            sfx_buf,
            synth_coin_tick(1500.0 + (tick_i % 5) * 140.0, 0.055),
            b5_s + 1.1 + tick_i * 0.22,
            gain=0.16,
        )
    t_neg = find_word_time(words, "negative", b5_s, b5_s + 4.5)
    place_sfx(sfx_buf, bass_drop, t_neg, gain=0.28)

    # 6. Beat 6 Admin Ban Hammer Gavel Impact + Riser
    b6_s = sections.get("beat6", {}).get("start", 31.8)
    if riser is not None:
        place_sfx(sfx_buf, riser, max(0.0, b6_s - 0.65), gain=0.18)
    t_banned = find_word_time(words, "banned", b6_s, b6_s + 0.8)
    place_sfx(sfx_buf, bass_drop, t_banned, gain=0.30)
    if click is not None:
        place_sfx(sfx_buf, click, t_banned, gain=0.25)

    # 7. Mandatory 2-4 Frame Pre-Cut Whooshes on every scene cut (Law #21)
    for i, t_cut in enumerate(cut_times_sec):
        if t_cut <= 0.1:
            continue
        clip = w_lo if (i % 2 == 0 and w_lo is not None) else w_hi
        if clip is not None:
            place_sfx(sfx_buf, clip, t_cut - 0.09, gain=0.20)

    mix = vo_pad + mus * duck[:, None] + sfx_buf
    peak = float(np.max(np.abs(mix)) + 1e-6)
    if peak > 0.92:
        mix *= 0.92 / peak

    raw_wav = os.path.join(AUDIO_DIR, "mix_raw.wav")
    out_wav = os.path.join(AUDIO_DIR, "mix.wav")
    wavfile.write(raw_wav, SR, (np.clip(mix, -1.0, 1.0) * 32767.0).astype(np.int16))

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
    print(f"[OK] Built -14 LUFS Roblox Storytime mix -> {out_wav} ({total_samples / SR:.2f}s)")
    return out_wav, total_samples / SR


if __name__ == "__main__":
    meta_path = os.path.join(BASE, "shots_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            cuts = [s["start_sec"] for s in json.load(f)["shots"]]
    else:
        cuts = [0.0, 2.2, 4.0, 6.5, 11.5, 17.5, 21.0, 24.5, 28.5, 32.0]
    build_mix(cuts)
