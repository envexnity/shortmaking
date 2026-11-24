"""
make_voice.py — Single-Model Fish Audio S2-Pro Narration + Word Alignment for roblox-spinning-rock.
Reuses the exact Fish Audio Roblox narrator model (eb4bcc6dbb634e9eaee239c94266935e) from Fada Theorem shorts.
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
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-spinning-rock"
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

# (beat_id, set_tag, pause_after_sec, fish_prompt_text, display_caption_text)
SCRIPT_BEATS = [
    ("b01a_town_rock",       "set1_town",    0.02, "[deadpan, intriguing] In this world, everyone lives on a giant rock",
     "In this world, everyone lives on a giant rock"),
    ("b01b_spin_1000",       "set2_space",   0.08, "[matter-of-fact] spinning at a thousand miles an hour.",
     "spinning at a thousand miles an hour."),
    ("b02_no_guardrails",    "set1_town",    0.06, "[deadpan] Nobody feels it, and there are no guardrails.",
     "Nobody feels it, and there are no guardrails."),
    ("b03_glue_force",       "set1_town",    0.08, "[storytelling, steady] The only thing stopping you from flying off the map is an invisible force gluing your shoes to the dirt.",
     "The only thing stopping you from flying off the map is an invisible force gluing your shoes to the dirt."),
    ("b04_not_parked",       "set2_space",   0.05, "[dry, building] And that rock isn't even parked.",
     "And that rock isn't even parked."),
    ("b05_orbit_sun",        "set2_space",   0.04, "[energetic, amazed] It's whipping around an even bigger burning rock at sixty-seven thousand miles an hour,",
     "It's whipping around an even bigger burning rock at sixty-seven thousand miles an hour—"),
    ("b06_expanding_void",   "set2_space",   0.10, "[dramatic, vast] while the whole system flies through an infinitely expanding empty void.",
     "while the whole system flies through an infinitely expanding empty void."),
    ("b07_merry_go_round",   "set3_analogy", 0.03, "[conversational, vivid] You see, it's like standing on a merry-go-round strapped to a rollercoaster",
     "You see, it's like standing on a merry-go-round strapped to a rollercoaster"),
    ("b08_stretching_lobby", "set3_analogy", 0.09, "[deadpan, eerie] inside a pitch-black lobby that never stops stretching.",
     "inside a pitch-black lobby that never stops stretching."),
    ("b09_casual_dog",       "set1_town",    0.04, "[casual, amused] Yet everyone on the rock is just casually walking their dog,",
     "Yet everyone on the rock is just casually walking their dog,"),
    ("b10a_paying_taxes",    "set1_town",    0.04, "[listing, brisk] paying taxes,",
     "paying taxes,"),
    ("b10b_arguing_traffic", "set1_town",    0.06, "[listing, deadpan] and arguing about traffic,",
     "and arguing about traffic—"),
    ("b11_hit_brakes",       "set1_sunset",  0.05, "[tense, urgent] completely ignoring the fact that if the rock ever hits the brakes for one second,",
     "completely ignoring the fact that if the rock ever hits the brakes for one second,"),
    ("b12_launched_space",   "set1_launch",  0.14, "[deadpan punchline] everyone gets launched sideways into space.",
     "everyone gets launched sideways into space."),
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
            data = urllib.request.urlopen(req, timeout=45).read()
            out_wav.write_bytes(data)
            return
        except Exception as e:
            print(f"  retry {attempt+1} for {out_wav.name}: {e}")
            time.sleep(2.0)
    raise RuntimeError(f"Failed Fish Audio TTS for {out_wav.name}")


def read_wav_mono_48k(path: Path, thresh_db: float = -40.0, pad_ms: float = 16.0) -> np.ndarray:
    cmd = ["ffmpeg", "-y", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "pipe:1"]
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


def main():
    assert FISH_API_KEY, "Missing FISH_API_KEY in .env!"
    print(f"Main Model (Single Voice): {MAIN_MODEL_ID}")

    from faster_whisper import WhisperModel
    wm = WhisperModel("small", device="cpu", compute_type="int8")

    timeline_chunks = []
    beats_meta = []
    all_words = []

    t_cur = 0.04
    timeline_chunks.append(np.zeros(int(t_cur * SR), dtype=np.float32))

    for idx, (bid, set_tag, pause_s, prompt_txt, caption_txt) in enumerate(SCRIPT_BEATS, 1):
        wav_p = VOICE_DIR / f"{idx:02d}_{bid}.wav"
        synthesize_fish(prompt_txt, MAIN_MODEL_ID, wav_p)
        seg = rms_norm(read_wav_mono_48k(wav_p), 0.135)
        beat_words = align_beat_words(seg, t_cur, caption_txt, wm)
        all_words.extend(beat_words)

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
            "shot": set_tag,
            "start": round(t_start, 3),
            "end": round(t_end, 3),
            "clip_end": round(t_cur, 3),
            "duration": round(dur, 3),
            "caption": caption_txt,
            "word_range": [len(all_words) - len(beat_words), len(all_words)],
        })
        print(f"[{idx:02d}/{len(SCRIPT_BEATS)}] {bid:20s} | {t_start:6.2f}s - {t_end:6.2f}s ({dur:4.2f}s) | {caption_txt[:52]}")

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

    total_dur = len(full) / SR
    (VOICE_DIR / "beats.json").write_text(
        json.dumps({"total_duration": round(total_dur, 3), "fps": FPS, "beats": beats_meta}, indent=2),
        encoding="utf-8",
    )
    (VOICE_DIR / "words.json").write_text(json.dumps(all_words, indent=2), encoding="utf-8")

    qa_shots = []
    for i, b in enumerate(beats_meta):
        fa = int(round(b["start"] * FPS))
        fb = int(round(beats_meta[i + 1]["start"] * FPS)) - 1 if i + 1 < len(beats_meta) else int(round(total_dur * FPS)) - 1
        qa_shots.append({"id": b["id"], "a": max(0, fa), "b": max(fa, fb)})
    (VOICE_DIR / "shots.json").write_text(json.dumps({"shots": qa_shots}, indent=2), encoding="utf-8")

    print(f"\nGATE 0 VO COMPLETE -> {master_wav} | Duration: {total_dur:.2f}s | {len(all_words)} words | {len(qa_shots)} beats")


if __name__ == "__main__":
    main()
