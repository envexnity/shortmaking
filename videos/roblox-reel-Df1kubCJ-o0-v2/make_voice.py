"""
make_voice.py — Single-Model Fish Audio S2-Pro Narration + MyInstants HUSS SFX + Word Alignment for Df1kubCJ-o0 Remake v2.
Model:
  - MAIN_MODEL_ID: eb4bcc6dbb634e9eaee239c94266935e ("Roblox" — all spoken lines)
HUSS SFX:
  - audio/huss_sfx_clean.wav (trimmed MyInstants "in-this-town-huss.mp3" 3-hit burst)

Generates per-beat 48 kHz mono WAVs, splices real MyInstants HUSS! bursts cleanly with transient onset detection,
stitches voice/vo_master.wav, aligns words via faster-whisper, and exports voice/beats.json, voice/words.json, and voice/shots.json.
"""
import json
import math
import os
import re
import subprocess
import time
import urllib.request
import wave
from pathlib import Path

import numpy as np

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2"
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
# mode: "main" | "huss_6" | "huss_3"
SCRIPT_BEATS = [
    ("b01_hook_town",      "town_party_open",     0.10, "main", "[deadpan, matter-of-fact] In this town, everybody is out partying.", "In this town, everybody is out partying."),
    ("b02_except_me",      "alex_wrap_intro",     0.10, "main", "[dry, serious] Except me.", "Except me."),
    ("b03_huss_1",         "wrap_pov_1",          0.12, "huss_6", "", "HUSS! HUSS! HUSS! HUSS! HUSS! HUSS!"),
    ("b04_party_any",      "town_party_any",      0.08, "main", "[conversational, dry] They will party for anything.", "They will party for anything."),
    ("b05_birthday_tue",   "town_party_bday",     0.08, "main", "[listing deadpan] A birthday. A Tuesday.", "A birthday. A Tuesday."),
    ("b06_nice_rock",      "town_party_rock",     0.12, "main", "[deadpan amused] Once, because somebody found a nice rock.", "Once because somebody found a nice rock."),
    ("b07_while_party_1",  "town_party_pan",      0.06, "main", "[casual, smug setup] While they are out partying, by the way,", "While they are out partying, by the way,"),
    ("b08_preparing",      "alex_room_prep",      0.10, "main", "[locked in, serious] I am in here, preparing for my job interview.", "I am in here, preparing for my job interview."),
    ("b09_huss_2",         "wrap_pov_2",          0.12, "huss_6", "", "HUSS! HUSS! HUSS! HUSS! HUSS! HUSS!"),
    ("b10_bun_town",       "buntown_exterior",    0.10, "main", "[proud, matter-of-fact] The job is wrapping burgers at Bun Town.", "The job is wrapping burgers at Bun Town."),
    ("b11_so_i_train",     "alex_train_start",    0.08, "main", "[intense, serious] So I train.", "So I train."),
    ("b12_5am_wrist",      "alex_wrist_stretch",  0.10, "main", "[focused, disciplined] Five AM. Wrist stretches.", "5 AM. Wrist stretches."),
    ("b13_200_wraps",      "alex_200_wraps",      0.10, "main", "[rapid, determined] Two hundred wraps before breakfast.", "200 wraps before breakfast."),
    ("b14_no_breakfast",   "wrap_breakfast_pov",  0.08, "main", "[deadpan] I do not eat breakfast. I wrap it.", "I do not eat breakfast. I wrap it."),
    ("b15_fold_tuck",      "wrap_fold_tuck",      0.08, "main", "[rhythmic, crisp] Fold, fold, tuck, roll.", "Fold, fold, tuck, roll."),
    ("b16_four_sec",       "alex_stopwatch_4s",   0.10, "main", "[disappointed, strict] Four seconds. Too slow.", "Four seconds. Too slow."),
    ("b17_huss_3",         "wrap_pov_3",          0.10, "huss_3", "", "HUSS! HUSS! HUSS!"),
    ("b18_wrap_items",     "alex_wrap_plate",     0.08, "main", "[deadpan escalating] I wrap the burger. I wrap the plate.", "I wrap the burger. I wrap the plate."),
    ("b19_wrap_cat",       "alex_wrap_cat",       0.12, "main", "[completely deadpan] I wrap my neighbor's cat. The cat is fine. The cat is warm.", "I wrap my neighbor's cat. The cat is fine. The cat is warm."),
    ("b20_neighbor",       "neighbor_window",     0.08, "main", "[slightly annoyed] My neighbor has a party every single night.", "My neighbor has a party every single night."),
    ("b21_come_out",       "neighbor_door",       0.10, "main", "[cheerful deadpan impression] Come out, he says. You only live once.", "Come out, he says. You only live once."),
    ("b22_exactly",        "alex_exactly",        0.08, "main", "[deadpan, locked in] Exactly. One life. One interview.", "Exactly. One life. One interview."),
    ("b23_huss_4",         "wrap_pov_4",          0.08, "huss_6", "", "HUSS! HUSS! HUSS! HUSS! HUSS! HUSS!"),
    ("b24_fold_fast",      "alex_fast_wrap",      0.06, "main", "[fast rhythmic] Fold, fold, tuck, roll. Two seconds. One second.", "Fold, fold, tuck, roll. Two seconds. One second."),
    ("b25_blur_hands",     "alex_blur_hands",     0.14, "main", "[amazed, deadpan] I stopped being able to see my own hands.", "I stopped being able to see my own hands."),
    ("b26_interview",      "buntown_walkin",      0.10, "main", "[storytelling] Then came the interview.", "Then came the interview."),
    ("b27_one_burger",     "counter_burger_cu",   0.10, "main", "[steady] The manager put one burger on the counter.", "The manager put one burger on the counter."),
    ("b28_whenever",       "manager_ready",       0.10, "main", "[warm polite older manager] Whenever you are ready, he said.", "Whenever you are ready, he said."),
    ("b29_already_wrap",   "manager_burger_wrap", 0.10, "main", "[smug, instant punchline] It was already wrapped.", "It was already wrapped."),
    ("b30_clipboard_tie",  "manager_clip_tie",    0.12, "main", "[deadpan rapid-fire] So was his clipboard. So was his tie.", "So was his clipboard. So was his tie."),
    ("b31_impressed",      "manager_impressed",   0.12, "main", "[delusionally confident] He was impressed. I could tell.", "He was impressed. I could tell."),
    ("b32_one_question",   "manager_question",    0.10, "main", "[dramatic turn] Then he asked me one question. Can you cook a burger?", "Then he asked me one question. Can you cook a burger?"),
    ("b33_never_cooked",   "alex_confession",     0.10, "main", "[honest, completely blank] I have never cooked a burger. I have never even eaten one.", "I have never cooked a burger. I have never even eaten one."),
    ("b34_only_wrap",      "grill_wrap_fail",     0.16, "main", "[deadpan] I only wrap.", "I only wrap."),
    ("b35_no_job",         "alex_rejection_ext",  0.08, "main", "[defeated, dry] I did not get the job.", "I did not get the job."),
    ("b36_letter",         "letter_closeup",      0.16, "main", "[dry reading] The letter said, thank you for wrapping my tie.", "The letter said: Thank you for wrapping my tie."),
    ("b37_almost",         "alex_almost",         0.24, "main", "[barely holding it together, quiet] Almost. Almost.", "Almost. Almost."),
    ("b38_so_tonight",     "town_night_party",    0.08, "main", "[resolute, comeback] So tonight, while they are out partying, by the way,", "So tonight, while they are out partying, by the way,"),
    ("b39_learning_cook",  "alex_grill_train",    0.08, "main", "[determined] I am back in here, learning to cook.", "I am back in here, learning to cook."),
    ("b40_5am_200",        "alex_grill_200",      0.08, "main", "[focused, energetic] Five AM. Two hundred burgers before breakfast.", "5 AM. 200 burgers before breakfast."),
    ("b41_huss_cook",      "alex_grill_huss",     0.12, "huss_6", "", "HUSS! HUSS! HUSS! HUSS! HUSS! HUSS!"),
    ("b42_hired",          "manager_hired",       0.08, "main", "[excited manager] You are hired, he said. When can you start?", "You are hired, he said. When can you start?"),
    ("b43_already_start",  "alex_already_start",  0.14, "main", "[deadpan smug] I had already started.", "I had already started."),
    ("b44_first_shift",    "town_biggest_party",  0.10, "main", "[storytelling] My first shift was Saturday night. The biggest party of the year.", "My first shift was Saturday night. The biggest party of the year."),
    ("b45_midnight_rush",  "buntown_crowd_rush",  0.08, "main", "[building urgency] At midnight, the whole town walked in. Hungry. Four hundred people.", "At midnight, the whole town walked in. Hungry. 400 people."),
    ("b46_one_of_me",      "alex_one_of_me",      0.08, "main", "[locked in, serious] One of me.", "One of me."),
    ("b47_huss_climax",    "wrap_pov_climax",     0.08, "huss_6", "", "HUSS! HUSS! HUSS! HUSS! HUSS! HUSS!"),
    ("b48_400_burgers",    "buntown_flying_400",  0.12, "main", "[triumphant, crisp] Four hundred burgers. One minute.", "400 burgers. One minute."),
    ("b49_mayor_stared",   "mayor_stunned",       0.10, "main", "[amazed, stunned older mayor] The mayor stared at me. How did you do that?", "The mayor stared at me. How did you do that?"),
    ("b50_final_callback", "alex_final_smug",     0.06, "main", "[smug, iconic callback] While you were out partying, I said. By the way,", "While you were out partying, I said. By the way,"),
    ("b51_final_huss",     "wrap_pov_final",      0.08, "huss_6", "", "HUSS! HUSS! HUSS! HUSS! HUSS! HUSS!"),
]


def synthesize_fish(text: str, model_id: str, out_wav: Path, temp: float = 0.70, top_p: float = 0.80):
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
    raise RuntimeError(f"Failed Fish Audio TTS for {out_wav.name} (model {model_id})")


def read_wav_mono_48k(path: Path, thresh_db: float = -40.0, pad_ms: float = 18.0) -> np.ndarray:
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


def load_huss_sfx(path: Path) -> tuple[np.ndarray, list[float]]:
    """Load clean trimmed MyInstants 3-hit HUSS SFX WAV and detect its 3 transient hit onsets."""
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


def rms_norm(x: np.ndarray, target_rms: float = 0.14) -> np.ndarray:
    r = float(np.sqrt(np.mean(x ** 2)) + 1e-9)
    y = x * (target_rms / r)
    pk = float(np.max(np.abs(y)) + 1e-9)
    if pk > 0.92:
        y = y * (0.92 / pk)
    return y


def align_beat_words(seg_audio: np.ndarray, t_offset: float, display_text: str, wm) -> list[dict]:
    """Align words inside one beat clip using faster-whisper, snapped cleanly to display tokens."""
    tokens = display_text.split()
    dur = len(seg_audio) / SR
    if not tokens:
        return []

    # Resample 48k -> 16k for faster-whisper
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

    # Robust fallback / monotonic re-mapping across raw_words span if count differs (e.g. "5 AM" vs "five a.m.")
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

    huss_sfx_path = PROJ_DIR / "audio" / "huss_sfx_clean.wav"
    assert huss_sfx_path.exists(), f"Missing {huss_sfx_path}"
    huss_clip, rel3 = load_huss_sfx(huss_sfx_path)
    print(f"HUSS SFX loaded: {len(huss_clip)/SR:.3f}s, 3 hit onsets={rel3}")

    from faster_whisper import WhisperModel
    wm = WhisperModel("small", device="cpu", compute_type="int8")

    timeline_chunks = []
    beats_meta = []
    all_words = []

    t_cur = 0.04
    timeline_chunks.append(np.zeros(int(t_cur * SR), dtype=np.float32))

    for idx, (bid, shot_tag, pause_s, mode, prompt_txt, caption_txt) in enumerate(SCRIPT_BEATS, 1):
        wav_p = VOICE_DIR / f"{idx:02d}_{bid}.wav"
        huss_hit_times = []

        if mode in ("huss_3", "huss_6"):
            if mode == "huss_3":
                seg = huss_clip.copy()
                rel_hits = list(rel3)
            else:
                gap = np.zeros(int(0.015 * SR), dtype=np.float32)
                seg = np.concatenate([huss_clip, gap, huss_clip])
                dt2 = len(huss_clip) / SR + 0.015
                rel_hits = list(rel3) + [round(dt2 + r, 3) for r in rel3]

            pcm_h = (np.clip(seg, -1.0, 1.0) * 32767.0).astype(np.int16)
            with wave.open(str(wav_p), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(SR)
                wf.writeframes(pcm_h.tobytes())

            huss_hit_times = [round(t_cur + rh, 3) for rh in rel_hits]
            seg_dur = len(seg) / SR
            for j, rh in enumerate(rel_hits):
                end_rh = rel_hits[j + 1] - 0.015 if j + 1 < len(rel_hits) else seg_dur
                all_words.append({
                    "start": round(t_cur + rh, 3),
                    "end": round(t_cur + max(rh + 0.12, end_rh), 3),
                    "word": "HUSS!",
                })
        else:
            synthesize_fish(prompt_txt, MAIN_MODEL_ID, wav_p, temp=0.68, top_p=0.80)
            seg = rms_norm(read_wav_mono_48k(wav_p), 0.135)
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
            "caption": caption_txt,
        })
        print(f"[{idx:02d}/{len(SCRIPT_BEATS)}] {bid:18s} | {t_start:6.2f}s - {t_end:6.2f}s ({dur:4.2f}s) | {caption_txt[:45]}")

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

    # Export shots.json for short_qa.py
    qa_shots = []
    for i, b in enumerate(beats_meta):
        fa = int(round(b["start"] * FPS))
        fb = int(round(beats_meta[i + 1]["start"] * FPS)) - 1 if i + 1 < len(beats_meta) else int(round(total_dur * FPS)) - 1
        qa_shots.append({"id": b["id"], "a": max(0, fa), "b": max(fa, fb)})
    (VOICE_DIR / "shots.json").write_text(json.dumps({"shots": qa_shots}, indent=2), encoding="utf-8")
    print(f"\nGATE 0 VO COMPLETE -> {master_wav} | Duration: {total_dur:.2f}s | {len(all_words)} words | {len(qa_shots)} shots")


if __name__ == "__main__":
    main()
