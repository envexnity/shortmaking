"""
audio_mix.py — Step 2 Audio Mix for videos/roblox-bruise-town.
Combines:
  - voice/voice_master.wav (0 .. story_duration, -14 LUFS)
  - assets/music/story_bg_music.wav (looped over story_duration, -6 dB gated ducking under speech)
  - assets/sfx/{ding,whoosh,heartbeat,clock_tick}.wav at exact beat timestamps from voice/beats.json
  - assets/outro_clips/thorfinn_outro.mp4 audio spliced cleanly at story_duration (0.06s crossfade)
Outputs two-pass -14 LUFS normalized audio/mix.wav (48kHz stereo PCM).
"""
import json
import os
import re
import subprocess
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, filtfilt

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
VOICE_DIR = BASE / "voice"
AUDIO_DIR = BASE / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

SR = 48000


def load_stereo_48k(path: Path) -> np.ndarray:
    tmp = AUDIO_DIR / f"_tmp_{path.stem}.wav"
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-y", "-i", str(path),
         "-vn", "-ac", "2", "-ar", str(SR), "-f", "wav", str(tmp)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    _, data = wavfile.read(tmp)
    tmp.unlink(missing_ok=True)
    if data.dtype == np.int16:
        arr = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        arr = data.astype(np.float32) / 2147483648.0
    else:
        arr = data.astype(np.float32)
    if arr.ndim == 1:
        arr = np.stack([arr, arr], axis=1)
    return arr


def place_sfx(buf: np.ndarray, sfx: np.ndarray, t_sec: float, gain: float = 0.25, max_dur_s: float | None = None):
    if max_dur_s is not None:
        sfx = sfx[:int(round(max_dur_s * SR))].copy()
        fo = min(int(0.15 * SR), len(sfx) // 3)
        if fo > 0:
            sfx[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    i0 = int(round(t_sec * SR))
    if i0 >= len(buf):
        return
    src_start = 0
    if i0 < 0:
        src_start = -i0
        i0 = 0
    n = min(len(sfx) - src_start, len(buf) - i0)
    if n > 0:
        buf[i0:i0 + n] += sfx[src_start:src_start + n] * gain


def two_pass_loudnorm(inp: Path, out: Path, target_i: float = -14.0, target_tp: float = -1.0):
    p1 = subprocess.run(
        ["ffmpeg", "-hide_banner", "-y", "-i", str(inp), "-af",
         f"loudnorm=I={target_i}:TP={target_tp}:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    m = re.search(r"\{[\s\S]*?\}", p1.stderr)
    if not m:
        raise RuntimeError(f"loudnorm pass 1 failed:\n{p1.stderr}")
    stats = json.loads(m.group(0))
    af = (
        f"loudnorm=I={target_i}:TP={target_tp}:LRA=11:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true:print_format=summary"
    )
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-y", "-i", str(inp), "-af", af,
         "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(out)],
        check=True, capture_output=True,
    )


def main():
    beats_data = json.loads((VOICE_DIR / "beats.json").read_text(encoding="utf-8"))
    beats = {b["id"]: b for b in beats_data["beats"]}
    words = json.loads((VOICE_DIR / "words.json").read_text(encoding="utf-8"))

    vo = load_stereo_48k(VOICE_DIR / "voice_master.wav")
    outro = load_stereo_48k(ROOT / "assets" / "outro_clips" / "thorfinn_outro.mp4")

    story_samples = len(vo)
    story_dur = story_samples / SR
    outro_samples = len(outro)
    outro_dur = outro_samples / SR

    # Ducking envelope for story BG music (-6 dB gated / 0.26x under speech)
    vo_mono = np.abs(vo.mean(axis=1))
    win = int(0.08 * SR)
    env = np.convolve(vo_mono, np.ones(win, dtype=np.float32) / win, mode="same")
    duck = np.where(env > 0.020, 0.28, 0.56).astype(np.float32)
    b_l, a_l = butter(2, 5.0 / (SR * 0.5), btype="low")
    duck = np.clip(filtfilt(b_l, a_l, duck).astype(np.float32), 0.25, 0.60)

    # Story background music (original Nujabes - Aruarian Dance, gentle presence under voice)
    mus_raw = load_stereo_48k(ROOT / "assets" / "music" / "aruarian_dance_original.wav")
    reps = int(np.ceil(story_samples / len(mus_raw))) + 1
    mus = np.tile(mus_raw, (reps, 1))[:story_samples].copy()
    mus_rms = float(np.sqrt(np.mean(mus ** 2)) + 1e-6)
    vo_rms = float(np.sqrt(np.mean(vo ** 2)) + 1e-6)
    # Match ~ -6 dB relative before ducking (further reduced by duck envelope under active voice)
    mus *= (vo_rms * 0.55) / mus_rms
    fi = min(int(0.30 * SR), story_samples // 4)
    fo = min(int(0.20 * SR), story_samples // 4)
    mus[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    mus[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]

    # Inline SFX placement
    sfx_buf = np.zeros((story_samples, 2), dtype=np.float32)
    ding = load_stereo_48k(ROOT / "assets" / "sfx" / "ding.wav")
    whoosh = load_stereo_48k(ROOT / "assets" / "sfx" / "whoosh.wav")
    heartbeat = load_stereo_48k(ROOT / "assets" / "sfx" / "heartbeat.wav")
    clock_tick = load_stereo_48k(ROOT / "assets" / "sfx" / "clock_tick.wav")

    # Normalize SFX RMS gently so gains are predictable
    def norm_sfx(x, tgt=0.14):
        r = float(np.sqrt(np.mean(x ** 2)) + 1e-6)
        return x * (tgt / r)

    ding = norm_sfx(ding, 0.13)
    whoosh = norm_sfx(whoosh, 0.14)
    heartbeat = norm_sfx(heartbeat, 0.16)
    clock_tick = norm_sfx(clock_tick, 0.10)

    # 1. Ding on premise rule ("Instantly." / "keep your hands to yourself")
    for w in words:
        wt = w["w"].strip(".,!?;:\"'—").lower()
        if wt == "instantly" and w["s"] < 15.0:
            place_sfx(sfx_buf, ding, w["s"], gain=0.28, max_dur_s=1.2)
            break
    if "b05_town_rule" in beats:
        place_sfx(sfx_buf, ding, beats["b05_town_rule"]["end"] - 2.4, gain=0.22, max_dur_s=1.1)

    # 2. Whoosh 0.08s lead-in before major set transitions
    for bid in ("b04_marcus", "b06_sam_intro", "b07_sam_work", "b08_bleachers",
                "b13_mom_sick", "b14_night_shifts", "b16_apartment", "b24_counter_bottles"):
        if bid in beats:
            place_sfx(sfx_buf, whoosh, max(0.0, beats[bid]["start"] - 0.08), gain=0.26, max_dur_s=1.1)
    # Pre-outro whoosh right into Thorfinn outro
    place_sfx(sfx_buf, whoosh, max(0.0, story_dur - 0.18), gain=0.32, max_dur_s=0.9)

    # 3. Heartbeat under "Until Tuesday.", "pulled his hood back", and "I couldn't breathe."
    for bid, dur_cap, g in (("b15_tuesday", 1.8, 0.34), ("b18_hood", 2.8, 0.30), ("b19_breath", 2.0, 0.36)):
        if bid in beats:
            place_sfx(sfx_buf, heartbeat, beats[bid]["start"], gain=g, max_dur_s=dur_cap)

    # 4. Clock tick under "night shifts" and "For a full minute, nobody answered."
    if "b14_night_shifts" in beats:
        place_sfx(sfx_buf, clock_tick, beats["b14_night_shifts"]["start"] + 0.1, gain=0.26, max_dur_s=2.8)
    if "b17_knock" in beats:
        place_sfx(sfx_buf, clock_tick, beats["b17_knock"]["start"] + 2.0, gain=0.28, max_dur_s=2.8)

    story_mix = vo + mus * duck[:, None] + sfx_buf

    # Normalize outro RMS close to -14 LUFS story_mix before crossfading
    outro_scaled = outro.copy()
    outro_rms = float(np.sqrt(np.mean(outro_scaled ** 2)) + 1e-6)
    story_active_rms = float(np.sqrt(np.mean(story_mix[vo_mono > 0.02] ** 2)) + 1e-6)
    outro_scaled *= (story_active_rms * 0.98) / outro_rms

    # 0.06s crossfade splice between story_mix and outro_scaled
    xf = int(round(0.06 * SR))
    total_samples = story_samples + outro_samples - xf
    full_mix = np.zeros((total_samples, 2), dtype=np.float32)
    full_mix[:story_samples] = story_mix
    fade_out = np.linspace(1.0, 0.0, xf, dtype=np.float32)[:, None]
    fade_in = np.linspace(0.0, 1.0, xf, dtype=np.float32)[:, None]
    s0 = story_samples - xf
    full_mix[s0:story_samples] = story_mix[s0:story_samples] * fade_out + outro_scaled[:xf] * fade_in
    full_mix[story_samples:] = outro_scaled[xf:]

    pk = float(np.max(np.abs(full_mix)) + 1e-6)
    if pk > 0.94:
        full_mix *= 0.94 / pk

    raw_wav = AUDIO_DIR / "mix_raw.wav"
    out_wav = AUDIO_DIR / "mix.wav"
    wavfile.write(raw_wav, SR, (np.clip(full_mix, -1.0, 1.0) * 32767.0).astype(np.int16))
    two_pass_loudnorm(raw_wav, out_wav, -14.0, -1.0)
    raw_wav.unlink(missing_ok=True)

    # Update beats.json with exact outro splice timestamps matching mix.wav
    final_mix_dur = total_samples / SR
    beats_data["story_duration"] = round(story_dur, 3)
    beats_data["outro_start"] = round(s0 / SR, 3)
    beats_data["outro_duration"] = round(outro_dur, 3)
    beats_data["total_duration"] = round(final_mix_dur, 3)
    (VOICE_DIR / "beats.json").write_text(json.dumps(beats_data, indent=2), encoding="utf-8")

    print(f"[OK] Built -14 LUFS mix -> {out_wav} | story={story_dur:.2f}s + outro={outro_dur:.2f}s -> total={final_mix_dur:.2f}s")


if __name__ == "__main__":
    main()
