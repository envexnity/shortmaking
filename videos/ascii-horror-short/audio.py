"""Horror ASCII Audio Mix & Foley Synthesizer for ascii-horror-short (< 45s).
Layers:
  1. Voiceover (ElevenLabs Brian + CRT Entity FX, normalized forward)
  2. Curated Dark Ambient Music: Apathy (Slowed + Reverb) - Oneheart (Law #29)
     with dramatic drops at 'Luckily' cord-pull & before 'Found the exit.'
  3. Pre-cut 2-4 frame whooshes (t_cut - 0.09s) from assets/sfx/
  4. Synthesized ASCII Horror Foley (60Hz CRT hum, breaker clack, fluorescent buzz,
     entity heartbeat, electric spark snap, crimson CRT surge boom, terminal typing,
     and ASCII hand rasterization glitch)
  5. -6 dB gated-RMS ducking + FFmpeg -14.0 LUFS / -1.0 dBTP master
"""
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


def synth_breaker_clack(dur: float = 0.22) -> np.ndarray:
    """Heavy industrial wall breaker snap + metallic spring ring."""
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    rng = np.random.default_rng(11)
    snap = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 95.0) * 0.9
    thud = np.sin(2 * np.pi * np.linspace(180, 55, n) * t) * np.exp(-t * 28.0) * 0.85
    ring = (np.sin(2 * np.pi * 1120 * t) + 0.5 * np.sin(2 * np.pi * 2460 * t)) * np.exp(-t * 22.0) * 0.35
    return np.tanh((snap + thud + ring) * 1.4).astype(np.float32)


def synth_fluorescent_hum(dur: float = 3.2) -> np.ndarray:
    """Overhead concrete hallway 60Hz/120Hz/180Hz fluorescent tube buzz + starter flicker."""
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    hum = (
        0.45 * np.sin(2 * np.pi * 60.0 * t)
        + 0.35 * np.sin(2 * np.pi * 120.0 * t)
        + 0.20 * np.sin(2 * np.pi * 240.0 * t)
        + 0.12 * np.sin(2 * np.pi * 420.0 * t)
    )
    # Initial tube ignition stutter for first 0.22s
    ign = np.where(t < 0.22, 0.35 + 0.65 * (np.sin(2 * np.pi * 24.0 * t) > 0), 1.0)
    env = np.minimum(1.0, t / 0.05) * np.minimum(1.0, (dur - t) / 0.25)
    return (hum * ign * env * 0.35).astype(np.float32)


def synth_sub_boom(f0: float = 110.0, f1: float = 38.0, dur: float = 0.65) -> np.ndarray:
    """Deep cinematic horror sub-bass thud + eerie metallic transient."""
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    freq = f1 + (f0 - f1) * np.exp(-t * 9.0)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    sub = np.sin(phase) * np.exp(-t * 4.2)
    rng = np.random.default_rng(77)
    transient = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 55.0) * 0.45
    return np.tanh((sub + transient) * 1.5).astype(np.float32)


def synth_heartbeat_double(dur: float = 0.55) -> np.ndarray:
    """Low ominous lub-dub pulse."""
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    p1 = np.sin(2 * np.pi * 52.0 * t) * np.exp(-t * 16.0)
    t2 = np.maximum(0.0, t - 0.18)
    p2 = np.sin(2 * np.pi * 46.0 * t2) * np.exp(-t2 * 15.0) * (t >= 0.18) * 0.8
    return np.tanh((p1 + p2) * 1.4).astype(np.float32)


def synth_cord_yank_spark(dur: float = 0.36) -> np.ndarray:
    """Electric plug yanked from wall socket: crisp crackle + CRT discharge whine down."""
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    rng = np.random.default_rng(42)
    noise = rng.standard_normal(n).astype(np.float32)
    b, a = butter(2, [900.0 / (SR * 0.5), 6500.0 / (SR * 0.5)], btype="band")
    spark = filtfilt(b, a, noise).astype(np.float32) * np.exp(-t * 18.0) * 1.1
    # CRT flyback power-down whine (9.5 kHz -> 220 Hz)
    freq = 9500.0 * np.exp(-t * 11.0) + 180.0
    whine = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 7.5) * 0.25
    thump = np.sin(2 * np.pi * 75.0 * t) * np.exp(-t * 24.0) * 0.65
    return np.tanh((spark + whine + thump) * 1.3).astype(np.float32)


def synth_crt_crimson_surge(dur: float = 0.85) -> np.ndarray:
    """Dissonant analog horror power-on screech + sub-drop when unplugged CRT turns red."""
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    f_sweep = np.linspace(140.0, 2650.0, n)
    screech = (
        0.5 * np.sin(2 * np.pi * np.cumsum(f_sweep) / SR)
        + 0.35 * np.sign(np.sin(2 * np.pi * 117.0 * t))
        + 0.35 * np.sign(np.sin(2 * np.pi * 123.5 * t))  # beating tritone/dissonance
    )
    b, a = butter(2, 3200.0 / (SR * 0.5), btype="low")
    screech = filtfilt(b, a, screech).astype(np.float32) * np.exp(-t * 3.2) * 0.45
    sub = synth_sub_boom(125.0, 36.0, dur) * 0.90
    return np.tanh((screech + sub) * 1.25).astype(np.float32)


def synth_terminal_key_click(pitch_hz: float = 1350.0, dur: float = 0.045) -> np.ndarray:
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    rng = np.random.default_rng(int(pitch_hz))
    burst = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 140.0) * 0.5
    tone = np.sin(2 * np.pi * pitch_hz * t) * np.exp(-t * 90.0) * 0.5
    return (burst + tone).astype(np.float32)


def synth_ascii_dissolve_glitch(dur: float = 1.45) -> np.ndarray:
    """Bit-crushed rising horror data-corruption wash for hands turning into ASCII."""
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    rng = np.random.default_rng(999)
    # Sample-and-hold stepped digital noise sweeping up
    step_hz = np.linspace(450.0, 3400.0, n)
    phase = np.cumsum(step_hz / SR)
    held = np.zeros(n, np.float32)
    last_p = -1
    val = 0.0
    for i in range(n):
        ip = int(phase[i])
        if ip != last_p:
            last_p = ip
            val = float(rng.uniform(-1.0, 1.0))
        held[i] = val
    drone = np.sin(2 * np.pi * np.linspace(55.0, 165.0, n) * t) * 0.55
    env = (t / dur) ** 0.75 * np.minimum(1.0, (dur - t) / 0.06)
    return np.tanh((held * 0.38 + drone) * env * 1.3).astype(np.float32)


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
    total = bd["total"]

    voice = load_wav_mono(os.path.join(HERE, "voice", "voice_raw.wav"))
    n_total = len(voice)

    # 1. Background Music: Apathy (Slowed + Reverb) - start at 26s where eerie synth swells cleanly
    music_raw = load_wav_mono(MUSIC_PATH)
    offset = int(26.0 * SR)
    if len(music_raw) > offset + n_total:
        bgm = music_raw[offset : offset + n_total].copy()
    else:
        bgm = np.tile(music_raw, int(np.ceil(n_total / len(music_raw))))[:n_total].copy()

    # Lowpass music slightly during intense narration so voice remains crystal clear,
    # and carve brief dread silence drops before key shocks!
    t_lights = find_word(beats[1]["words"], "slams", beats[1]["start"])
    t_blink = find_word(beats[5]["words"], "blinks", beats[5]["start"])
    t_lunge = find_word(beats[6]["words"], "three", beats[6]["start"])
    t_ripped = find_word(beats[7]["words"], "ripped", beats[7]["start"])
    t_unluckily = beats[8]["start"]
    t_blood_red = find_word(beats[8]["words"], "blood", beats[8]["start"])
    t_crawl = find_word(beats[11]["words"], "crawl", beats[11]["start"])
    t_entity = beats[13]["start"]
    t_turning = find_word(beats[14]["words"], "turning", beats[14]["start"])

    # Drop music during the cord-pull false relief -> violent re-entry at Unluckily/blood red,
    # and silence briefly for the entity's "Found the exit." line!
    bgm_env = np.ones(n_total, dtype=np.float32)
    def fade_dip(t0, t1, level=0.12, ramp=0.08):
        i0, i1 = max(0, int(t0 * SR)), min(n_total, int(t1 * SR))
        r = max(1, int(ramp * SR))
        if i1 <= i0:
            return
        bgm_env[i0:i1] = level
        if i0 + r < i1:
            bgm_env[i0 : i0 + r] = np.linspace(1.0, level, r)
        if i1 - r > i0:
            bgm_env[i1 - r : i1] = np.linspace(level, 1.0, r)

    fade_dip(t_ripped + 0.15, t_unluckily + 0.35, level=0.05, ramp=0.10)
    fade_dip(t_entity - 0.12, beats[13]["speechEnd"] + 0.08, level=0.06, ramp=0.06)
    bgm = bgm * bgm_env

    # Normalize BGM baseline cleanly before mixing
    bgm_rms = float(np.sqrt(np.mean(bgm ** 2)) + 1e-8)
    bgm = bgm * (0.18 / bgm_rms)

    # 2. SFX & Horror Foley Bus
    sfx = np.zeros(n_total, dtype=np.float32)
    whoosh = load_wav_mono(os.path.join(SFX_DIR, "whoosh.wav"))
    whoosh_low = load_wav_mono(os.path.join(SFX_DIR, "whoosh_low.wav"))
    riser_hit = load_wav_mono(os.path.join(SFX_DIR, "riser_hit.wav"))
    ui_click = load_wav_mono(os.path.join(SFX_DIR, "ui_click.wav"))

    # Law #21: 2-4 frame pre-cut whooshes on major scene cuts (t_cut - 0.09s)
    for bi in [1, 3, 4, 6, 7, 8, 9, 10, 12, 14]:
        if bi < len(beats):
            clip = whoosh_low if bi in (6, 8, 12, 14) else whoosh
            place(sfx, clip, beats[bi]["start"] - 0.09, 0.38)

    # Beat 0: Subtle ominous CRT hum & sub-pulse at Frame 0 + ASCII reveal click
    t_ascii0 = find_word(beats[0]["words"], "ASCII", 2.56)
    place(sfx, synth_sub_boom(88, 34, 0.70), 0.01, 0.55)
    place(sfx, ui_click, t_ascii0 - 0.04, 0.65)
    place(sfx, synth_heartbeat_double(), find_word(beats[0]["words"], "two", 3.46) - 0.04, 0.60)

    # Beat 1-2: Breaker slam + overhead concrete fluorescent tube hum
    place(sfx, synth_breaker_clack(), t_lights - 0.02, 0.85)
    place(sfx, synth_fluorescent_hum(beats[2]["end"] - t_lights), t_lights + 0.04, 0.42)

    # Beat 3-4: CRT monitor hum + static wipe whisper
    place(sfx, synth_sub_boom(72, 42, 0.45), beats[3]["start"], 0.42)

    # Beat 5: Wall blinks (sharp CRT tick + heartbeat)
    place(sfx, ui_click, t_blink - 0.03, 0.85)
    place(sfx, synth_heartbeat_double(), t_blink, 0.68)

    # Beat 6: Entity steps three feet out of the dark -> Riser hit + sub boom!
    place(sfx, riser_hit[-int(1.0 * SR):], t_lunge - 0.55, 0.45)
    place(sfx, synth_sub_boom(120, 36, 0.75), t_lunge - 0.02, 0.90)

    # Beat 7: Luckily, ripped power cord -> Spark snap + power-down whine!
    place(sfx, synth_cord_yank_spark(), t_ripped - 0.02, 0.85)

    # Beat 8: Unluckily, unplugged screen stayed on & turned blood red -> Violent crimson surge!
    place(sfx, synth_sub_boom(92, 34, 0.50), t_unluckily, 0.55)
    place(sfx, synth_crt_crimson_surge(), t_blood_red - 0.08, 0.88)

    # Beat 9-11: "You see," pivot + ASCII bars splitting + claws crawling through
    place(sfx, ui_click, beats[10]["start"], 0.55)
    place(sfx, riser_hit[-int(1.2 * SR):], t_crawl - 0.70, 0.42)
    place(sfx, synth_sub_boom(105, 38, 0.55), t_crawl - 0.02, 0.65)

    # Beat 12: Monitor types "> DOORWAY: OPEN" — rapid tactile mechanical terminal key clicks!
    t_type0 = beats[12]["start"] + 0.35
    for k in range(13):
        place(sfx, synth_terminal_key_click(1200 + (k % 3) * 140), t_type0 + k * 0.105, 0.55)

    # Beat 13: Entity "Found the exit." -> Cold impact thud!
    place(sfx, synth_sub_boom(135, 33, 0.80), t_entity - 0.03, 0.92)

    # Beat 14: Hands turning into ASCII -> Digital rasterization corruption sweep!
    place(sfx, synth_ascii_dissolve_glitch(beats[14]["end"] - t_turning + 0.15), t_turning - 0.15, 0.65)
    place(sfx, synth_sub_boom(115, 36, 0.40), beats[14]["speechEnd"] - 0.22, 0.75)

    # 3. Gated-RMS Ducking & -6 dB Relative Bed Mix (Law #22)
    env = np.convolve(np.abs(voice), np.ones(int(SR * 0.07)) / int(SR * 0.07), mode="same")
    speech_mask = env > (np.max(env) * 0.08)
    duck = np.where(speech_mask, 0.36, 1.0).astype(np.float32)
    duck = np.convolve(duck, np.ones(int(SR * 0.11)) / int(SR * 0.11), mode="same")

    bed = (bgm + sfx) * duck
    v_rms = float(np.sqrt(np.mean(voice[speech_mask] ** 2)) + 1e-9)
    b_rms = float(np.sqrt(np.mean(bed[speech_mask] ** 2)) + 1e-9)
    target_ratio = 0.44  # ~ -7 dB relative speech-gated bed, letting SFX impacts punch through cleanly
    bed = bed * (v_rms * target_ratio / b_rms)

    raw_mix = voice + bed
    pre_wav = os.path.join(HERE, "audio", "mix_pre.wav")
    fin_wav = os.path.join(HERE, "audio", "mix.wav")
    wavfile.write(pre_wav, SR, (np.clip(raw_mix, -0.98, 0.98) * 32767).astype(np.int16))

    # Loudness master to -14.0 LUFS / -1.0 dBTP
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", pre_wav,
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=7",
        "-ar", str(SR), "-ac", "1", fin_wav,
    ], check=True)
    print(f"Mastered {fin_wav} (-14 LUFS)")


if __name__ == "__main__":
    main()
