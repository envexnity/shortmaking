"""
make_voice.py — Fish Audio S2-Pro Narration + Two-Pass -14 LUFS + Whisper Word Alignment
for videos/roblox-bruise-town (verbatim story, 26 emotional beats).
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
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-bruise-town"
VOICE_DIR = PROJ_DIR / "voice"
VOICE_DIR.mkdir(parents=True, exist_ok=True)

SR = 48000
FPS = 15
OUT_FPS = 30
OUTRO_DURATION = 10.30
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

# (beat_id, set_tag, pause_after_sec, fish_prompt_text, verbatim_text)
SCRIPT_BEATS = [
    ("b01_intro",           "parking",   0.10, "[calm, storytelling] In this town, nobody gets away with cruelty.",
     "In this town, nobody gets away with cruelty."),
    ("b02_rule",            "parking",   0.06, "[serious, steady] Whenever you hurt someone—a shove in the hallway, a slap, even a cruel word meant to make someone cry—",
     "Whenever you hurt someone— a shove in the hallway, a slap, even a cruel word meant to make someone cry—"),
    ("b03_instantly",       "parking",   0.12, "[serious, intense] the bruise doesn't show up on them. It shows up on you. Instantly. Dark purple, swollen, impossible to cover with makeup.",
     "the bruise doesn't show up on them. It shows up on you. Instantly. Dark purple, swollen, impossible to cover with makeup."),
    ("b04_marcus",          "parking",   0.08, "[calm, storytelling] At school, you can tell who the bullies are from across the parking lot. Marcus Vance, the varsity linebacker, walks around with two permanent black eyes and a split lip he's had since seventh grade.",
     "At school, you can tell who the bullies are from across the parking lot. Marcus Vance, the varsity linebacker, walks around with two permanent black eyes and a split lip he's had since seventh grade."),
    ("b05_town_rule",       "parking",   0.12, "[serious, sober] Nobody sits near him. Nobody hires people with bruised faces. Everyone in town learns the same rule by age five: keep your hands to yourself, or wear your ugliness forever.",
     "Nobody sits near him. Nobody hires people with bruised faces. Everyone in town learns the same rule by age five: keep your hands to yourself, or wear your ugliness forever."),
    ("b06_sam_intro",       "bleachers", 0.10, "[warm, admiring] My older brother, Sam, didn't have a single mark on him.",
     "My older brother, Sam, didn't have a single mark on him."),
    ("b07_sam_work",        "autoshop",  0.10, "[warm, storytelling] Sam was nineteen, six-foot-two, and worked double shifts at the auto shop so we could afford rent after our dad walked out. He never raised his voice. Never swung back when guys at the shop pushed him around.",
     "Sam was nineteen, six-foot-two, and worked double shifts at the auto shop so we could afford rent after our dad walked out. He never raised his voice. Never swung back when guys at the shop pushed him around."),
    ("b08_bleachers",       "bleachers", 0.08, "[serious, storytelling] Even when Marcus cornered me behind the bleachers last October and shoved me into the gravel, Sam just walked up, stepped between us, and let Marcus shove him twice without lifting a finger.",
     "Even when Marcus cornered me behind the bleachers last October and shoved me into the gravel, Sam just walked up, stepped between us, and let Marcus shove him twice without lifting a finger."),
    ("b09_welt",            "bleachers", 0.10, "[calm, admiring] Marcus walked away with a fresh purple welt blooming across his cheek. Sam walked me home without a scratch.",
     "Marcus walked away with a fresh purple welt blooming across his cheek. Sam walked me home without a scratch."),
    ("b10_why_ask",         "bleachers", 0.08, "[earnest, youthful] \"Why don't you ever hit them back?\" I asked him that night while I washed the gravel out of my palms. \"One punch. They deserve it.\"",
     "\"Why don't you ever hit them back?\" I asked him that night while I washed the gravel out of my palms. \"One punch. They deserve it.\""),
    ("b11_no_enemies_sam",  "bleachers", 0.10, "[quiet, gentle] Sam just shook his head, smiling quietly. \"I don't have any enemies, Toby. Nobody deserves to carry that around.\"",
     "Sam just shook his head, smiling quietly. \"I don't have any enemies, Toby. Nobody deserves to carry that around.\""),
    ("b12_strongest",       "bleachers", 0.12, "[warm, admiring] I thought he was the strongest person alive.",
     "I thought he was the strongest person alive."),
    ("b13_mom_sick",        "hospital",  0.10, "[heavy, somber] Then, last winter, our mom got sick. Not a cold—the kind of sickness that meant hospital beds, white walls, and three different medications that cost more than Sam made in a month.",
     "Then, last winter, our mom got sick. Not a cold— the kind of sickness that meant hospital beds, white walls, and three different medications that cost more than Sam made in a month."),
    ("b14_night_shifts",    "autoshop",  0.25, "[heavy, quiet] Sam started working night shifts on top of his day job. Every morning when I woke up for school, he was sitting at the kitchen table in his greasy jacket, drinking black coffee, exhausted—and still completely unmarked.",
     "Sam started working night shifts on top of his day job. Every morning when I woke up for school, he was sitting at the kitchen table in his greasy jacket, drinking black coffee, exhausted— and still completely unmarked."),
    ("b15_tuesday",         "apartment", 0.14, "[tense, hushed] Until Tuesday.",
     "Until Tuesday."),
    ("b16_apartment",       "apartment", 0.08, "[tense, quiet] I came home early because the heater at school broke. The front door was unlocked. The apartment was dead silent, except for the sound of the bathroom faucet running.",
     "I came home early because the heater at school broke. The front door was unlocked. The apartment was dead silent, except for the sound of the bathroom faucet running."),
    ("b17_knock",           "apartment", 0.08, "[tense, hushed] I knocked softly. \"Sam? You home?\" The water stopped. For a full minute, nobody answered. Then the door clicked open—just a crack—and Sam stepped out with his hood pulled low over his forehead.",
     "I knocked softly. \"Sam? You home?\" The water stopped. For a full minute, nobody answered. Then the door clicked open— just a crack— and Sam stepped out with his hood pulled low over his forehead."),
    ("b18_hood",            "apartment", 0.25, "[tense, building] \"Hey, bud,\" he said, his voice rough. \"You're early.\" I reached up and pulled his hood back before he could stop me.",
     "\"Hey, bud,\" he said, his voice rough. \"You're early.\" I reached up and pulled his hood back before he could stop me."),
    ("b19_breath",          "apartment", 0.12, "[shocked, breathless] I couldn't breathe.",
     "I couldn't breathe."),
    ("b20_bruised_face",    "apartment", 0.10, "[shocked, heartbroken] Sam's face was unrecognizable. Both eyes were swollen nearly shut, dark purple and blue. His cheekbone was bruised black, his lip split, his jaw covered in fresh, deep welts—like he'd gone ten rounds in a cage fight.",
     "Sam's face was unrecognizable. Both eyes were swollen nearly shut, dark purple and blue. His cheekbone was bruised black, his lip split, his jaw covered in fresh, deep welts— like he'd gone ten rounds in a cage fight."),
    ("b21_who_did",         "apartment", 0.10, "[desperate, emotional] \"Who did this to you?\" I yelled, tears springing to my eyes. \"Was it Marcus? Was it the guys at the shop? Tell me!\"",
     "\"Who did this to you?\" I yelled, tears springing to my eyes. \"Was it Marcus? Was it the guys at the shop? Tell me!\""),
    ("b22_nobody",          "apartment", 0.10, "[soft, heartbroken] Sam grabbed my shoulders gently. Through his swollen, bruised lips, he forced a quiet smile. \"Nobody touched me, Toby,\" he whispered. \"I didn't hit anybody.\"",
     "Sam grabbed my shoulders gently. Through his swollen, bruised lips, he forced a quiet smile. \"Nobody touched me, Toby,\" he whispered. \"I didn't hit anybody.\""),
    ("b23_remember_rule",   "apartment", 0.10, "[realization, hushed] \"Then how—\" I stopped. My voice died in my throat. I remembered the rule. Not just punches. Cruelty. Every time you lie to someone who loves you. Every time you break a promise. Every time you hurt someone's heart.",
     "\"Then how—\" I stopped. My voice died in my throat. I remembered the rule. Not just punches. Cruelty. Every time you lie to someone who loves you. Every time you break a promise. Every time you hurt someone's heart."),
    ("b24_counter_bottles", "apartment", 0.08, "[heavy, somber] On the kitchen counter behind him sat three orange prescription bottles—paid in full—and a crumpled envelope with our mom's handwriting on the front, torn open on the floor.",
     "On the kitchen counter behind him sat three orange prescription bottles— paid in full— and a crumpled envelope with our mom's handwriting on the front, torn open on the floor."),
    ("b25_dad_truth",       "apartment", 0.10, "[devastated, quiet] Sam had gone to our dad. Our dad, who had walked out four years ago. Our dad, who had sworn he'd only help pay for Mom's medicine if Sam promised to cut Mom and me out of his life forever—and tell Mom she was a burden he couldn't carry anymore.",
     "Sam had gone to our dad. Our dad, who had walked out four years ago. Our dad, who had sworn he'd only help pay for Mom's medicine if Sam promised to cut Mom and me out of his life forever— and tell Mom she was a burden he couldn't carry anymore."),
    ("b26_ending",          "apartment", 0.14, "[devastated, quiet] Sam hadn't thrown a single punch in his life. He had broken his own mother's heart—and left us behind—just so she could live. He squeezed my shoulder one last time, picked up his duffel bag, and walked out the front door with his ruined, bruised face held high.",
     "Sam hadn't thrown a single punch in his life. He had broken his own mother's heart— and left us behind— just so she could live. He squeezed my shoulder one last time, picked up his duffel bag, and walked out the front door with his ruined, bruised face held high."),
]


def synthesize_fish(text: str, model_id: str, out_wav: Path, temp: float = 0.65, top_p: float = 0.78):
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


def read_wav_mono_48k(path: Path, thresh_db: float = -42.0, pad_ms: float = 16.0) -> np.ndarray:
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
    fade = min(int(0.008 * SR), len(samples) // 4)
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
            out.append({"w": tok, "s": round(t_offset + ws_c, 3), "e": round(t_offset + we_c, 3)})
        return out

    # Proportional word mapping anchored inside detected Whisper speech span
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
        out.append({"w": tok, "s": round(t_offset + cur, 3), "e": round(t_offset + cur + max(0.06, wd), 3)})
        cur += wd
    return out


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
         "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(out)],
        check=True, capture_output=True,
    )


def main():
    assert FISH_API_KEY, "Missing FISH_API_KEY in .env!"
    print(f"Synthesizing {len(SCRIPT_BEATS)} beats via Fish Audio S2-Pro ({MAIN_MODEL_ID})")

    from faster_whisper import WhisperModel
    wm = WhisperModel("base", device="cpu", compute_type="int8")

    timeline_chunks = []
    beats_meta = []
    all_words = []

    t_cur = 0.05
    timeline_chunks.append(np.zeros(int(t_cur * SR), dtype=np.float32))

    for idx, (bid, set_tag, pause_s, prompt_txt, caption_txt) in enumerate(SCRIPT_BEATS, 1):
        wav_p = VOICE_DIR / f"{idx:02d}_{bid}.wav"
        synthesize_fish(prompt_txt, MAIN_MODEL_ID, wav_p)
        seg = rms_norm(read_wav_mono_48k(wav_p), 0.14)
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
            "set": set_tag,
            "start": round(t_start, 3),
            "end": round(t_end, 3),
            "clip_end": round(t_cur, 3),
            "duration": round(dur, 3),
            "text": caption_txt,
        })
        print(f"[{idx:02d}/{len(SCRIPT_BEATS)}] {bid:20s} | {t_start:6.2f}s - {t_end:6.2f}s ({dur:5.2f}s)")

    full = np.concatenate(timeline_chunks)
    peak = float(np.max(np.abs(full)) + 1e-9)
    full = np.clip(full / peak * 0.90, -1.0, 1.0)

    raw_wav = VOICE_DIR / "voice_raw.wav"
    pcm16 = (full * 32767.0).astype(np.int16)
    with wave.open(str(raw_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

    master_wav = VOICE_DIR / "voice_master.wav"
    two_pass_loudnorm(raw_wav, master_wav, -14.0, -1.0)

    # Transcribe voice_master.wav using raw 16kHz float32 PCM via ffmpeg pipe
    pcm16k = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(master_wav),
         "-f", "f32le", "-acodec", "pcm_f32le", "-ac", "1", "-ar", "16000", "-"],
        capture_output=True, check=True,
    ).stdout
    audio16k = np.frombuffer(pcm16k, dtype=np.float32)

    # Align per-beat words using the normalized master slice so timestamps match voice_master.wav exactly
    master_48k = read_wav_mono_48k(master_wav, thresh_db=-96.0, pad_ms=0.0)
    for b in beats_meta:
        i0 = min(len(master_48k), int(round(b["start"] * SR)))
        i1 = min(len(master_48k), int(round(b["end"] * SR)))
        seg_m = master_48k[i0:i1]
        if len(seg_m) > 800:
            all_words.extend(align_beat_words(seg_m, b["start"], b["text"], wm))

    # Also verify global Whisper pass succeeded cleanly on master PCM
    segs_chk, _ = wm.transcribe(audio16k[:min(len(audio16k), 16000 * 15)], language="en")
    print("Master preview Whisper check:", " ".join(s.text.strip() for s in segs_chk))

    story_dur = len(master_48k) / SR
    total_dur = story_dur + OUTRO_DURATION

    (VOICE_DIR / "beats.json").write_text(
        json.dumps({
            "story_duration": round(story_dur, 3),
            "outro_duration": round(OUTRO_DURATION, 3),
            "total_duration": round(total_dur, 3),
            "render_fps": FPS,
            "output_fps": OUT_FPS,
            "beats": beats_meta,
        }, indent=2),
        encoding="utf-8",
    )
    (VOICE_DIR / "words.json").write_text(json.dumps(all_words, indent=2), encoding="utf-8")
    print(f"\n[OK] voice_master.wav -> story={story_dur:.2f}s + outro={OUTRO_DURATION:.2f}s = total={total_dur:.2f}s | {len(all_words)} words")


if __name__ == "__main__":
    main()
