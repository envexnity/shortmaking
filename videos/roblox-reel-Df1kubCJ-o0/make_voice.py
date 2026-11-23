"""
make_voice.py — Generates the full expressive Roblox storytime narration for our remake of
Instagram Reel Df1kubCJ-o0 using Fish Audio S2-Pro API and the Roblox voice model:
  modelId: 5355e61fa47849b4bac5a3417837eb58 ("roblox rant")

Reads FISH_API_KEY from workspace .env.
Generates per-beat WAV clips with rich Fish Audio stage-direction prompts, trims dead air,
stitches vo_master.wav, builds beats.json + words.json via faster-whisper on PCM arrays.
"""
import io
import json
import os
import subprocess
import time
import urllib.request
import wave
from pathlib import Path

import numpy as np

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0"
VOICE_DIR = PROJ_DIR / "voice"
VOICE_DIR.mkdir(parents=True, exist_ok=True)


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
FISH_MODEL_ID = ENV.get("FISH_ROBLOX_MODEL_ID") or "5355e61fa47849b4bac5a3417837eb58"

# Beat-by-beat script faithfully matching @thedrizzleshow Df1kubCJ-o0 with expressive Fish Audio S2-Pro tags!
# Format: (beat_id, shot_tag, pause_after_sec, fish_prompt_text, display_caption_text)
SCRIPT_BEATS = [
    ("b01_hook_town",     "town_party_open",     0.12, "[matter-of-fact, slightly annoyed] In this town, everybody is out partying.", "In this town, everybody is out partying."),
    ("b02_except_me",     "alex_wrap_intro",     0.12, "[deadpan, serious] Except me.", "Except me."),
    ("b03_huss_1",        "wrap_pov_1",          0.14, "[intense, sharp rapid grunts] Huss! Huss! Huss! Huss! Huss! Huss!", "HUSS! HUSS! HUSS! HUSS! HUSS! HUSS!"),
    ("b04_party_any",     "town_party_any",      0.10, "[conversational, incredulous] They will party for anything.", "They will party for anything."),
    ("b05_birthday_tue",  "town_party_bday",     0.10, "[listing casually] A birthday. A Tuesday.", "A birthday. A Tuesday."),
    ("b06_nice_rock",     "town_party_rock",     0.14, "[deadpan amused] Once because somebody found a nice rock.", "Once because somebody found a nice rock."),
    ("b07_while_party_1", "town_party_pan",      0.08, "[casual, smug setup] While they are out partying, by the way,", "While they are out partying, by the way,"),
    ("b08_preparing",     "alex_room_prep",      0.12, "[locked in, determined] I am in here, preparing for my job interview.", "I am in here, preparing for my job interview."),
    ("b09_huss_2",        "wrap_pov_2",          0.14, "[intense, fast sharp grunts] Huss! Huss! Huss! Huss! Huss! Huss!", "HUSS! HUSS! HUSS! HUSS! HUSS! HUSS!"),
    ("b10_bun_town",      "buntown_exterior",    0.12, "[proud, matter-of-fact] The job is wrapping burgers at Bun Town.", "The job is wrapping burgers at Bun Town."),
    ("b11_so_i_train",    "alex_train_start",    0.10, "[intense, serious] So I train.", "So I train."),
    ("b12_5am_wrist",     "alex_wrist_stretch",  0.12, "[focused, disciplined] Five AM, wrist stretches.", "5 AM. Wrist stretches."),
    ("b13_200_wraps",     "alex_200_wraps",      0.12, "[rapid, determined] Two hundred wraps before breakfast.", "200 wraps before breakfast."),
    ("b14_no_breakfast",  "wrap_breakfast_pov",  0.10, "[deadpan] I do not eat breakfast. I wrap it.", "I do not eat breakfast. I wrap it."),
    ("b15_fold_tuck",     "wrap_fold_tuck",      0.10, "[rhythmic, crisp] Fold, fold, tuck, roll.", "Fold, fold, tuck, roll."),
    ("b16_four_sec",      "alex_stopwatch_4s",   0.12, "[disappointed, strict] Four seconds. Too slow.", "Four seconds. Too slow."),
    ("b17_huss_3",        "wrap_pov_3",          0.12, "[faster, intense grunts] Huss! Huss! Huss! Huss! Huss!", "HUSS! HUSS! HUSS! HUSS! HUSS!"),
    ("b18_wrap_items",    "alex_wrap_plate",     0.10, "[deadpan escalating] I wrap the burger. I wrap the plate.", "I wrap the burger. I wrap the plate."),
    ("b19_wrap_cat",      "alex_wrap_cat",       0.12, "[completely deadpan] I wrap my neighbor's cat. The cat is fine. The cat is warm.", "I wrap my neighbor's cat. The cat is fine. The cat is warm."),
    ("b20_neighbor",      "neighbor_window",     0.10, "[slightly annoyed] My neighbor has a party every single night.", "My neighbor has a party every single night."),
    ("b21_come_out",      "neighbor_door",       0.12, "[cheerful, imitating party bro] Come out, he says. You only live once.", "Come out, he says. You only live once."),
    ("b22_exactly",       "alex_exactly",        0.10, "[deadpan, locked in] Exactly. One life. One interview.", "Exactly. One life. One interview."),
    ("b23_huss_4",        "wrap_pov_4",          0.10, "[super fast intense grunts] Huss! Huss! Huss! Huss! Huss! Huss!", "HUSS! HUSS! HUSS! HUSS! HUSS! HUSS!"),
    ("b24_fold_fast",     "alex_fast_wrap",      0.08, "[fast rhythmic] Fold, fold, tuck, roll. Two seconds. One second.", "Fold, fold, tuck, roll. Two seconds. One second."),
    ("b25_blur_hands",    "alex_blur_hands",     0.16, "[amazed, unhinged] I stopped being able to see my own hands.", "I stopped being able to see my own hands."),
    ("b26_interview",     "buntown_walkin",      0.12, "[dramatic narration] Then came the interview.", "Then came the interview."),
    ("b27_one_burger",    "counter_burger_cu",   0.12, "[suspenseful, steady] The manager put one burger on the counter.", "The manager put one burger on the counter."),
    ("b28_whenever",      "manager_ready",       0.12, "[polite manager tone] Whenever you are ready, he said.", "Whenever you are ready, he said."),
    ("b29_already_wrap",  "manager_burger_wrap", 0.12, "[smug, instant punchline] It was already wrapped.", "It was already wrapped."),
    ("b30_clipboard_tie", "manager_clip_tie",    0.14, "[deadpan rapid-fire] So was his clipboard. So was his tie.", "So was his clipboard. So was his tie."),
    ("b31_impressed",     "manager_impressed",   0.14, "[delusionally confident] He was impressed. I could tell.", "He was impressed. I could tell."),
    ("b32_one_question",  "manager_question",    0.12, "[dramatic turn] Then he asked me one question. Can you cook a burger?", "Then he asked me one question. Can you cook a burger?"),
    ("b33_never_cooked",  "alex_confession",     0.12, "[honest, completely blank] I have never cooked a burger. I have never even eaten one.", "I have never cooked a burger. I have never even eaten one."),
    ("b34_only_wrap",     "grill_wrap_fail",     0.18, "[deadpan] I only wrap.", "I only wrap."),
    ("b35_no_job",        "alex_rejection_ext",  0.10, "[defeated, dry] I did not get the job.", "I did not get the job."),
    ("b36_letter",        "letter_closeup",      0.20, "[dry reading] The letter said, thank you for wrapping my tie.", "The letter said: Thank you for wrapping my tie."),
    ("b37_almost",        "alex_almost",         0.28, "[barely holding it together, forcing a smile] Almost. Almost.", "Almost. Almost."),
    ("b38_so_tonight",    "town_night_party",    0.10, "[resolute, comeback energy] So tonight, while they are out partying, by the way,", "So tonight, while they are out partying, by the way,"),
    ("b39_learning_cook", "alex_grill_train",    0.10, "[determined] I am back in here, learning to cook.", "I am back in here, learning to cook."),
    ("b40_5am_200",       "alex_grill_200",      0.10, "[focused, energetic] Five AM. Two hundred burgers before breakfast.", "5 AM. 200 burgers before breakfast."),
    ("b41_huss_cook",     "alex_grill_huss",     0.14, "[intense rapid grunts] Huss! Huss! Huss! Huss! Huss! Huss!", "HUSS! HUSS! HUSS! HUSS! HUSS! HUSS!"),
    ("b42_hired",         "manager_hired",       0.10, "[excited manager] You are hired, he said. When can you start?", "You are hired, he said. When can you start?"),
    ("b43_already_start", "alex_already_start",  0.16, "[deadpan smug] I had already started.", "I had already started."),
    ("b44_first_shift",   "town_biggest_party",  0.12, "[epic storytelling] My first shift was Saturday night. The biggest party of the year.", "My first shift was Saturday night. The biggest party of the year."),
    ("b45_midnight_rush", "buntown_crowd_rush",  0.10, "[building urgency] At midnight, the whole town walked in. Hungry. Four hundred people.", "At midnight, the whole town walked in. Hungry. 400 people."),
    ("b46_one_of_me",     "alex_one_of_me",      0.10, "[locked in, badass] One of me.", "One of me."),
    ("b47_huss_climax",   "wrap_pov_climax",     0.10, "[ferocious rapid grunts] Huss! Huss! Huss! Huss! Huss! Huss!", "HUSS! HUSS! HUSS! HUSS! HUSS! HUSS!"),
    ("b48_400_burgers",   "buntown_flying_400",  0.14, "[triumphant, crisp] Four hundred burgers. One minute.", "400 burgers. One minute."),
    ("b49_mayor_stared",  "mayor_stunned",       0.12, "[amazed, imitating stunned mayor] The mayor stared at me. How did you do that?", "The mayor stared at me. How did you do that?"),
    ("b50_final_callback","alex_final_smug",     0.08, "[smug, iconic callback] While you were out partying, I said. By the way,", "While you were out partying, I said. By the way,"),
    ("b51_final_huss",    "wrap_pov_final",      0.10, "[ferocious final grunts] Huss! Huss! Huss! Huss! Huss! Huss!", "HUSS! HUSS! HUSS! HUSS! HUSS! HUSS!"),
]


def synthesize_fish(text: str, out_wav: Path):
    if out_wav.exists() and out_wav.stat().st_size > 4000:
        return
    payload = json.dumps({
        "text": text,
        "reference_id": FISH_MODEL_ID,
        "format": "wav",
        "temperature": 0.72,
        "top_p": 0.82,
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
    for attempt in range(3):
        try:
            data = urllib.request.urlopen(req, timeout=45).read()
            out_wav.write_bytes(data)
            return
        except Exception as e:
            print(f"  retry {attempt+1} for {out_wav.name}: {e}")
            time.sleep(2.0)
    raise RuntimeError(f"Failed Fish Audio TTS for {out_wav.name}")


def read_wav_mono_48k(path: Path) -> np.ndarray:
    """Decode any wav cleanly via ffmpeg to 48kHz mono float32 and trim leading/trailing silence."""
    cmd = [
        "ffmpeg", "-y", "-i", str(path),
        "-ac", "1", "-ar", "48000", "-f", "f32le", "pipe:1"
    ]
    raw = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
    samples = np.frombuffer(raw, dtype=np.float32).copy()
    # Trim silence below -42 dB with 25ms safety pad
    thresh = 10 ** (-42 / 20.0)
    nz = np.where(np.abs(samples) > thresh)[0]
    if len(nz) > 0:
        pad = int(0.025 * 48000)
        s0 = max(0, nz[0] - pad)
        s1 = min(len(samples), nz[-1] + pad)
        samples = samples[s0:s1]
    # Soft fade 8ms on edges to avoid clicks
    fade = min(int(0.008 * 48000), len(samples) // 4)
    if fade > 0:
        samples[:fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)
        samples[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)
    return samples


def main():
    assert FISH_API_KEY, "Missing FISH_API_KEY in .env!"
    print(f"Using Fish Audio S2-Pro | Roblox Model ID: {FISH_MODEL_ID}")

    sr = 48000
    timeline_chunks = []
    beats_meta = []
    t_cur = 0.05  # Start almost immediately on Frame 1-2 (zero Millennial Pause!)
    timeline_chunks.append(np.zeros(int(t_cur * sr), dtype=np.float32))

    for idx, (bid, shot_tag, pause_s, prompt_txt, caption_txt) in enumerate(SCRIPT_BEATS, 1):
        wav_p = VOICE_DIR / f"{idx:02d}_{bid}.wav"
        synthesize_fish(prompt_txt, wav_p)
        seg = read_wav_mono_48k(wav_p)
        dur = len(seg) / sr
        t_start = t_cur
        t_end = t_cur + dur
        timeline_chunks.append(seg)
        gap_samples = int(pause_s * sr)
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
            "prompt": prompt_txt,
            "caption": caption_txt,
        })
        print(f"[{idx:02d}/{len(SCRIPT_BEATS)}] {bid:18s} | {t_start:6.2f}s - {t_end:6.2f}s ({dur:4.2f}s) | {caption_txt[:50]}")

    # Write stitched 48kHz mono WAV
    full = np.concatenate(timeline_chunks)
    peak = np.max(np.abs(full)) + 1e-9
    full = np.clip(full / peak * 0.92, -1.0, 1.0)
    master_wav = VOICE_DIR / "vo_master.wav"
    pcm16 = (full * 32767.0).astype(np.int16)
    with wave.open(str(master_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())

    total_dur = len(full) / sr
    print(f"\nSaved stitched Fish Audio master VO -> {master_wav} (total {total_dur:.2f}s)")

    # Save beats.json
    beats_path = VOICE_DIR / "beats.json"
    beats_path.write_text(json.dumps({"total_duration": round(total_dur, 3), "fps": 30, "beats": beats_meta}, indent=2), encoding="utf-8")

    # Word-level alignment via faster-whisper on 16kHz numpy PCM
    print("Running faster-whisper word alignment on vo_master.wav...")
    raw16 = subprocess.check_output(["ffmpeg", "-y", "-i", str(master_wav), "-ac", "1", "-ar", "16000", "-f", "f32le", "pipe:1"], stderr=subprocess.DEVNULL)
    audio16 = np.frombuffer(raw16, dtype=np.float32).copy()
    from faster_whisper import WhisperModel
    wm = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = wm.transcribe(audio16, word_timestamps=True, language="en")
    words = []
    for s in segments:
        for w in (s.words or []):
            wt = w.word.strip()
            # Normalize "Hush" -> "HUSS!" during HUSS beats for exact authentic captions
            words.append({"start": round(w.start, 3), "end": round(w.end, 3), "word": wt})

    # Post-fix HUSS captions inside huss beats!
    huss_ranges = [(b["start"] - 0.08, b["end"] + 0.08) for b in beats_meta if "huss" in b["id"]]
    for w in words:
        mid = 0.5 * (w["start"] + w["end"])
        if any(a <= mid <= b for a, b in huss_ranges):
            if any(k in w["word"].lower() for k in ["hush", "huss", "hus", "sh", "huh", "us", "ha", "ho"]):
                w["word"] = "HUSS!"

    words_path = VOICE_DIR / "words.json"
    words_path.write_text(json.dumps(words, indent=2), encoding="utf-8")
    print(f"Saved {len(words)} aligned words -> {words_path}")


if __name__ == "__main__":
    main()
