"""
make_voice.py — Fish Audio S2-Pro Narration + Real HUSS SFX + Dad Pitch Shift + Word Alignment
for videos/roblox-theo-631 ("Theo #631 — 1 in 250,000,000 Race").
Strictly enforces < 44.5s total duration cap.
"""
import json
import os
import re
import subprocess
import time
import urllib.request
import wave
from pathlib import Path

import numpy as np

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-theo-631"
REF_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2"
VOICE_DIR = PROJ_DIR / "voice"
VOICE_DIR.mkdir(parents=True, exist_ok=True)

SR = 48000
FPS = 30
MAIN_MODEL_ID = "eb4bcc6dbb634e9eaee239c94266935e"


def load_env():
    env = {}
    env_p = SHORTMAKING_ROOT / ".env"
    if env_p.exists():
        for line in env_p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


ENV = load_env()
FISH_API_KEY = ENV.get("FISH_API_KEY") or os.environ.get("FISH_API_KEY", "")

# (beat_id, shot_tag, pause_after_sec, mode, fish_prompt_text, display_caption_text)
SCRIPT_BEATS = [
    ("b01_teamwork",        "hook_couple",     0.06, "main",
     "[deadpan, intriguing] In this world, to create a new human, two people of the opposite gender have to use... teamwork.",
     "In this world, to create a new human, two people of the opposite gender have to use... teamwork."),
    ("b02_huss",            "house_shake",     0.08, "huss_3",
     "", "HUSS! HUSS! HUSS!"),
    ("b03_deadliest_race",  "tunnel_gate",     0.08, "main",
     "[serious, dramatic] And in this world, to actually be born, you have to win the deadliest race in existence.",
     "And in this world, to actually be born, you have to win the deadliest race in existence."),
    ("b04_theo_intro",      "theo_stat_card",  0.06, "main",
     "[confident, determined] Hi, I'm Theo. I'm sperm number 631, and I'm competing against a billion other sperm just to get a shot at life.",
     "Hi, I’m Theo. I’m sperm number 631, and I’m competing against a billion other sperm just to get a shot at life."),
    ("b05_countdown_go",    "race_countdown",  0.04, "countdown",
     "", "3... 2... 1... GO!"),
    ("b06_dropping",        "race_hazards",    0.06, "main",
     "[fast, energetic] Most of them don't even make it past the first five minutes. Guys are dropping left and right. Sperm 42? Gone. Sperm 12? Cooked.",
     "Most of them don't even make it past the first five minutes. Guys are dropping left and right. Sperm 42? Gone. Sperm 12? Cooked."),
    ("b07_neck_and_neck",   "race_burst",      0.06, "main",
     "[tense, urgent] It's me and one other sperm left. Neck and neck.",
     "It’s me and one other sperm left. Neck and neck."),
    ("b08_climax_win",      "race_climax",     0.12, "main",
     "[triumphant, emotional] I gave it everything I had... and I actually won. I beat a billion-to-one odds. I'm gonna be born.",
     "I gave it everything I had... and I actually won. I beat a billion-to-one odds. I’m gonna be born."),
    ("b09_hospital_doctor", "hospital_doc",    0.08, "main",
     "[confused, hesitant] Wait... why is the doctor looking at me like that?",
     "Wait... why is the doctor looking at me like that?"),
    ("b10_dad_twist",       "dad_horror",      0.18, "dad",
     "[shocked, horrified, loud] Wait a minute... why does he have blonde hair?!",
     "Wait a minute... why does he have blonde hair?!"),
]


def synthesize_fish(text: str, model_id: str, out_wav: Path, temp: float = 0.68, top_p: float = 0.80):
    if out_wav.exists() and out_wav.stat().st_size > 3000:
        return
    payload = json.dumps({
        "text": text,
        "reference_id": model_id,
        "format": "wav",
        "temperature": temp,
        "top_p": top_p,
        "normalize": True,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.fish.audio/v1/tts",
        data=payload,
        headers={
            "Authorization": f"Bearer {FISH_API_KEY}",
            "Content-Type": "application/json",
            "model": "s2-pro",
        },
        method="POST",
    )
    for attempt in range(4):
        try:
            data = urllib.request.urlopen(req, timeout=60).read()
            out_wav.write_bytes(data)
            return
        except Exception as e:
            print(f"  retry {attempt+1} for {out_wav.name}: {e}")
            time.sleep(2.0)
    raise RuntimeError(f"Failed Fish Audio TTS for {out_wav.name}")


def read_wav_mono_48k(path: Path, thresh_db: float = -40.0, pad_ms: float = 16.0,
                      tempo: float = 1.0, semitones: float = 0.0) -> np.ndarray:
    filters = []
    if abs(semitones) > 1e-4:
        pitch_factor = 2.0 ** (semitones / 12.0)
        filters.append(f"asetrate={SR}*{pitch_factor:.6f},aresample={SR}")
        comp_tempo = tempo / pitch_factor
    else:
        comp_tempo = tempo
    while comp_tempo > 2.0:
        filters.append("atempo=2.0")
        comp_tempo /= 2.0
    while comp_tempo < 0.5:
        filters.append("atempo=0.5")
        comp_tempo /= 0.5
    if abs(comp_tempo - 1.0) > 1e-4:
        filters.append(f"atempo={comp_tempo:.5f}")

    cmd = ["ffmpeg", "-y", "-i", str(path), "-ac", "1", "-ar", str(SR)]
    if filters:
        cmd.extend(["-af", ",".join(filters)])
    cmd.extend(["-f", "f32le", "pipe:1"])
    raw = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
    samples = np.frombuffer(raw, dtype=np.float32).copy()
    thresh = 10 ** (thresh_db / 20.0)
    nz = np.where(np.abs(samples) > thresh)[0]
    if len(nz) > 0:
        pad = int((pad_ms / 1000.0) * SR)
        s0 = max(0, int(nz[0]) - pad)
        s1 = min(len(samples), int(nz[-1]) + pad)
        samples = samples[s0:s1]
    fade = min(int(0.006 * SR), len(samples) // 4)
    if fade > 0:
        samples[:fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)
        samples[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)
    return samples


def rms_norm(x: np.ndarray, target_rms: float = 0.14) -> np.ndarray:
    r = float(np.sqrt(np.mean(x ** 2)) + 1e-9)
    y = x * (target_rms / r)
    pk = float(np.max(np.abs(y)) + 1e-9)
    if pk > 0.92:
        y = y * (0.92 / pk)
    return y


def load_huss_sfx(path: Path) -> tuple[np.ndarray, list[float]]:
    cmd = ["ffmpeg", "-y", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "pipe:1"]
    raw = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
    clip = rms_norm(np.frombuffer(raw, dtype=np.float32).copy(), target_rms=0.145)
    w = int(0.020 * SR)
    env = np.convolve(np.abs(clip), np.ones(w, dtype=np.float32) / w, mode="same")
    n3 = len(env)
    rel3 = []
    for k in range(3):
        a, b = int(k * n3 / 3), int((k + 1) * n3 / 3)
        seg = env[a:b]
        thr = 0.35 * float(np.max(seg))
        nz = np.where(seg >= thr)[0]
        idx_on = (int(nz[0]) + a) if len(nz) else a
        rel3.append(round(idx_on / SR, 3))
    return clip, rel3


def align_beat_words(seg_audio: np.ndarray, t_offset: float, display_text: str, wm) -> list[dict]:
    tokens = display_text.split()
    dur = len(seg_audio) / SR
    if not tokens:
        return []

    n16 = max(1, int(round(len(seg_audio) * 16000 / SR)))
    idx16 = np.linspace(0, len(seg_audio) - 1, n16)
    a16 = np.interp(idx16, np.arange(len(seg_audio)), seg_audio).astype(np.float32)

    raw_words = []
    try:
        segs, _ = wm.transcribe(a16, word_timestamps=True, language="en")
        for s in segs:
            for w in (s.words or []):
                wt = w.word.strip()
                if wt:
                    raw_words.append((float(w.start), float(w.end), wt))
    except Exception:
        raw_words = []

    if len(raw_words) == len(tokens):
        out = []
        for (ws, we, _), tok in zip(raw_words, tokens):
            ws_c = max(0.0, min(dur - 0.05, ws))
            we_c = max(ws_c + 0.06, min(dur, we))
            out.append({"start": round(t_offset + ws_c, 3), "end": round(t_offset + we_c, 3), "word": tok})
        return out

    if raw_words:
        t0 = max(0.0, raw_words[0][0])
        t1 = min(dur, max(t0 + 0.15, raw_words[-1][1]))
    else:
        t0, t1 = 0.02, max(0.20, dur - 0.02)

    weights = [max(2, len(re.sub(r"[^A-Za-z0-9]", "", t))) for t in tokens]
    total_w = sum(weights)
    cur = t0
    span = max(0.15, t1 - t0)
    out = []
    for tok, wgt in zip(tokens, weights):
        wd = span * (wgt / total_w)
        out.append({"start": round(t_offset + cur, 3), "end": round(t_offset + cur + max(0.06, wd), 3), "word": tok})
        cur += wd
    return out


def build_timeline(wm, huss_clip, rel3, tempo: float = 1.0):
    timeline_chunks = []
    beats_meta = []
    all_words = []

    t_cur = 0.04
    timeline_chunks.append(np.zeros(int(t_cur * SR), dtype=np.float32))

    for idx, (bid, shot_tag, pause_s, mode, prompt_txt, caption_txt) in enumerate(SCRIPT_BEATS, 1):
        wav_p = VOICE_DIR / f"{idx:02d}_{bid}.wav"
        huss_hit_times = []
        countdown_ticks = []

        if mode == "huss_3":
            seg = huss_clip.copy()
            pcm_h = (np.clip(seg, -1.0, 1.0) * 32767.0).astype(np.int16)
            with wave.open(str(wav_p), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(SR)
                wf.writeframes(pcm_h.tobytes())

            huss_hit_times = [round(t_cur + rh, 3) for rh in rel3]
            seg_dur = len(seg) / SR
            for j, rh in enumerate(rel3):
                end_rh = rel3[j + 1] - 0.015 if j + 1 < len(rel3) else seg_dur
                all_words.append({
                    "start": round(t_cur + rh, 3),
                    "end": round(t_cur + max(rh + 0.12, end_rh), 3),
                    "word": "HUSS!",
                })
        elif mode == "countdown":
            seg = np.zeros(int(round(0.84 * SR)), dtype=np.float32)
            ticks = [("3...", 0.00, 0.20), ("2...", 0.21, 0.41), ("1...", 0.42, 0.62), ("GO!", 0.63, 0.84)]
            for tok, s_rel, e_rel in ticks:
                ts = round(t_cur + s_rel, 3)
                te = round(t_cur + e_rel, 3)
                countdown_ticks.append({"label": tok, "start": ts, "end": te})
                all_words.append({"start": ts, "end": te, "word": tok})
        else:
            synthesize_fish(prompt_txt, MAIN_MODEL_ID, wav_p, temp=0.68, top_p=0.80)
            semitones = -1.2 if mode == "dad" else 0.0
            seg = rms_norm(read_wav_mono_48k(wav_p, tempo=tempo, semitones=semitones), 0.138)
            all_words.extend(align_beat_words(seg, t_cur, caption_txt, wm))

        dur = len(seg) / SR
        t_start = t_cur
        t_end = t_cur + dur
        timeline_chunks.append(seg)
        gap_samples = int(round(pause_s * SR))
        timeline_chunks.append(np.zeros(gap_samples, dtype=np.float32))
        t_cur = t_end + pause_s

        beats_meta.append({
            "index": idx,
            "id": bid,
            "shot": shot_tag,
            "start": round(t_start, 3),
            "end": round(t_end, 3),
            "clip_end": round(t_cur, 3),
            "duration": round(dur, 3),
            "huss_hit_times": huss_hit_times,
            "countdown_ticks": countdown_ticks,
            "caption": caption_txt,
        })

    return timeline_chunks, beats_meta, all_words


def main():
    assert FISH_API_KEY, "Missing FISH_API_KEY in .env!"
    print(f"Main Model: {MAIN_MODEL_ID}")

    huss_sfx_path = REF_DIR / "audio" / "huss_sfx_clean.wav"
    assert huss_sfx_path.exists(), f"Missing {huss_sfx_path}"
    huss_clip, rel3 = load_huss_sfx(huss_sfx_path)
    print(f"HUSS SFX loaded: {len(huss_clip)/SR:.3f}s, 3 hit onsets={rel3}")

    from faster_whisper import WhisperModel
    wm = WhisperModel("small", device="cpu", compute_type="int8")

    tempo = 1.0
    timeline_chunks, beats_meta, all_words = build_timeline(wm, huss_clip, rel3, tempo=tempo)
    total_dur = sum(len(c) for c in timeline_chunks) / SR
    if total_dur >= 44.5:
        tempo = 1.06
        print(f"Duration {total_dur:.2f}s >= 44.5s; rebuilding spoken segments at tempo={tempo}x...")
        timeline_chunks, beats_meta, all_words = build_timeline(wm, huss_clip, rel3, tempo=tempo)
        total_dur = sum(len(c) for c in timeline_chunks) / SR

    assert total_dur < 44.5, f"Duration {total_dur:.2f}s still >= 44.5s!"

    for b in beats_meta:
        print(f"[{b['index']:02d}/{len(SCRIPT_BEATS)}] {b['id']:20s} | {b['start']:6.2f}s - {b['end']:6.2f}s ({b['duration']:4.2f}s) | {b['caption'][:48]}")

    full = np.concatenate(timeline_chunks)
    peak = float(np.max(np.abs(full)) + 1e-9)
    full = np.clip(full / peak * 0.92, -1.0, 1.0)
    master_wav = VOICE_DIR / "vo_master.wav"
    pcm16 = (full * 32767.0).astype(np.int16)
    with wave.open(str(master_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

    (VOICE_DIR / "beats.json").write_text(
        json.dumps({"total_duration": round(total_dur, 3), "fps": FPS, "beats": beats_meta}, indent=2),
        encoding="utf-8",
    )
    (VOICE_DIR / "words.json").write_text(json.dumps(all_words, indent=2), encoding="utf-8")
    print(f"\nSTEP 1 VO COMPLETE -> {master_wav} | Duration: {total_dur:.2f}s | {len(all_words)} words | tempo={tempo}x")


if __name__ == "__main__":
    main()
