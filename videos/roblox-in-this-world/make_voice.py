import os
import json
import asyncio
import subprocess
import numpy as np
from scipy.io import wavfile
import edge_tts
from faster_whisper import WhisperModel

BASE = os.path.dirname(os.path.abspath(__file__))
VOICE_DIR = os.path.join(BASE, "voice")
os.makedirs(VOICE_DIR, exist_ok=True)

SECTIONS = [
    ("beat1", "In this world, every jump you make costs one hundred Robux. Everyone else walked slowly. Except me. I woke up inside a lava obby with zero Robux in my account."),
    ("beat2", "At Roblox High, rich kids with Dominus crowns bunny-hopped down the hallway just to flex on us."),
    ("beat3", "When the floor cracked into glowing red lava bricks, the teacher yelled, Jump to the safe platform! My balance flashed zero."),
    ("beat4", "Luckily, my noob best friend threw me a free gravity coil. Unluckily, it launched me straight through the roof and registered forty-two jumps."),
    ("beat5", "You see, the Roblox tax bot counts every stud of airtime like a taxi meter on turbo. My overhead debt counter hit negative four thousand Robux before I even landed."),
    ("beat6", "So the Admin banned gravity from my legs... and now I float to class for free."),
]

MP3_PATH = os.path.join(VOICE_DIR, "voice.mp3")
WORDS_PATH = os.path.join(VOICE_DIR, "words.json")


def cap_internal_pauses(sig: np.ndarray, sr: int, max_pause_s: float = 0.09, thresh: float = 0.015) -> np.ndarray:
    """Trim any dead-air pause longer than max_pause_s down to max_pause_s (<0.15s per Roblox Storytime Bible)."""
    win = int(0.02 * sr)
    abs_sig = np.abs(sig)
    env = np.convolve(abs_sig, np.ones(win, dtype=np.float32) / win, mode="same")
    silent = env < thresh

    max_keep = int(max_pause_s * sr)
    fade = int(0.006 * sr)
    out = []
    i = 0
    n = len(sig)
    while i < n:
        if silent[i]:
            j = i
            while j < n and silent[j]:
                j += 1
            if (j - i) > max_keep and i > 0 and j < n:
                k1 = max_keep // 2
                k2 = max_keep - k1
                seg_a = sig[i : i + k1].copy()
                seg_b = sig[j - k2 : j].copy()
                if len(seg_a) >= fade:
                    seg_a[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)
                if len(seg_b) >= fade:
                    seg_b[:fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)
                out.append(seg_a)
                out.append(seg_b)
            else:
                out.append(sig[i:j])
            i = j
        else:
            j = i
            while j < n and not silent[j]:
                j += 1
            out.append(sig[i:j])
            i = j
    return np.concatenate(out) if out else sig


async def gen_tts():
    part_wavs = []
    for key, text in SECTIONS:
        part_mp3 = os.path.join(VOICE_DIR, f"{key}.mp3")
        part_wav = os.path.join(VOICE_DIR, f"{key}.wav")
        if not (os.path.exists(part_mp3) and os.path.getsize(part_mp3) > 1000):
            for attempt in range(8):
                try:
                    if os.path.exists(part_mp3):
                        os.remove(part_mp3)
                    comm = edge_tts.Communicate(text, voice="en-AU-WilliamNeural", rate="+7%")
                    await asyncio.wait_for(comm.save(part_mp3), timeout=25)
                    if os.path.exists(part_mp3) and os.path.getsize(part_mp3) > 1000:
                        break
                except Exception as e:
                    print(f"[WARN] {key} attempt {attempt+1} failed: {e}", flush=True)
                    await asyncio.sleep(1.5 * (attempt + 1))
            await asyncio.sleep(0.5)
        subprocess.run(
            ["ffmpeg", "-y", "-i", part_mp3, "-ac", "1", "-ar", "48000", part_wav],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        part_wavs.append((key, part_wav))
        print(f"[OK] Ready {key}", flush=True)

    sr = 48000
    full_chunks = []
    section_spans = {}
    cursor = 0.0
    for key, wpath in part_wavs:
        _, arr = wavfile.read(wpath)
        f = arr.astype(np.float32) / 32768.0
        nz = np.where(np.abs(f) > 0.014)[0]
        if len(nz):
            s_idx = max(0, int(nz[0]) - int(0.015 * sr))
            e_idx = min(len(f), int(nz[-1]) + int(0.045 * sr))
            f = f[s_idx:e_idx]
        f = cap_internal_pauses(f, sr, max_pause_s=0.085)
        gap = np.zeros(int(0.07 * sr), dtype=np.float32) if key != "beat1" else np.zeros(0, dtype=np.float32)
        if len(gap):
            full_chunks.append(gap)
            cursor += len(gap) / sr
        t_start = round(cursor, 3)
        full_chunks.append(f)
        cursor += len(f) / sr
        section_spans[key] = {"start": t_start, "end": round(cursor, 3)}

    joined = np.concatenate(full_chunks)
    joined_wav = os.path.join(VOICE_DIR, "voice_joined.wav")
    wavfile.write(joined_wav, sr, (np.clip(joined, -1.0, 1.0) * 32767.0).astype(np.int16))
    subprocess.run(
        ["ffmpeg", "-y", "-i", joined_wav, "-b:a", "192k", MP3_PATH],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"[OK] Combined TTS -> {MP3_PATH} ({cursor:.2f}s, < 45s cap!)", flush=True)
    return section_spans


def fix_transcript_words(words):
    """Canonicalize Roblox vocabulary (Robux, Obby, Dominus, Noob) if Whisper mishears."""
    out = []
    i = 0
    while i < len(words):
        w = dict(words[i])
        tok = w["w"].strip()
        low = tok.lower().strip(".,!?:;")
        nxt = words[i + 1]["w"].strip() if i + 1 < len(words) else ""
        nxt_low = nxt.lower().strip(".,!?:;")

        if low == "and" and nxt_low == "luckily":
            merged = dict(words[i + 1])
            merged["w"] = "Unluckily,"
            merged["s"] = w["s"]
            out.append(merged)
            i += 2
            continue
        elif low == "work" and nxt_low == "up":
            w["w"] = "woke"
            out.append(w)
            i += 1
            continue
        elif low in ("robots", "robox", "robucks", "robacks", "robux"):
            punct = tok[-1] if tok[-1] in ".,!?" else ""
            w["w"] = "Robux" + punct
            out.append(w)
            i += 1
            continue
        elif low in ("obi", "obby", "hobby", "abby", "abbey", "obby."):
            punct = tok[-1] if tok[-1] in ".,!?" else ""
            w["w"] = "obby" + punct
            out.append(w)
            i += 1
            continue
        elif low in ("dominos", "dominous", "dominant", "dominus"):
            w["w"] = "Dominus"
            out.append(w)
            i += 1
            continue
        elif low == "deflects":
            mid = round(0.5 * (w["s"] + w["e"]), 3)
            out.append({"w": "to", "s": w["s"], "e": mid})
            out.append({"w": "flex", "s": mid, "e": w["e"]})
            i += 1
            continue
        elif low == "but" and len(out) > 0 and out[-1]["w"].lower().strip(".,!?") == "tax":
            w["w"] = "bot"
            out.append(w)
            i += 1
            continue
        elif tok == "4" and nxt == ",000":
            w["w"] = "4,000"
            w["e"] = words[i + 1]["e"]
            out.append(w)
            i += 2
            continue
        elif low == "admin":
            w["w"] = "Admin"
            out.append(w)
            i += 1
            continue
        elif low in ("new", "nube", "noob") and nxt_low == "best":
            w["w"] = "noob"
            out.append(w)
            i += 1
            continue
        elif low in ("roadblocks", "roblox"):
            w["w"] = "Roblox"
            out.append(w)
            i += 1
            continue
        out.append(w)
        i += 1
    return out


def align_words(section_spans):
    wav16 = os.path.join(VOICE_DIR, "voice_16k.wav")
    subprocess.run(
        ["ffmpeg", "-y", "-i", MP3_PATH, "-ac", "1", "-ar", "16000", wav16],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    sr, data = wavfile.read(wav16)
    audio_np = data.astype(np.float32) / 32768.0
    dur = round(float(len(audio_np) / sr), 3)
    os.remove(wav16)

    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_np, word_timestamps=True)
    words = []
    for seg in segments:
        if seg.words:
            for w in seg.words:
                words.append({
                    "w": w.word.strip(),
                    "s": round(float(w.start), 3),
                    "e": round(float(w.end), 3),
                })
    words = fix_transcript_words(words)
    out = {"duration": dur, "sections": section_spans, "words": words}
    with open(WORDS_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"[OK] Aligned {len(words)} words, duration={dur}s -> {WORDS_PATH}", flush=True)
    print("Transcript:", " ".join(x["w"] for x in words), flush=True)
    for key, sp in section_spans.items():
        print(f"  SECTION {key}: {sp['start']:.2f}s -> {sp['end']:.2f}s", flush=True)


if __name__ == "__main__":
    import sys
    if "--fix-only" in sys.argv and os.path.exists(WORDS_PATH):
        d = json.load(open(WORDS_PATH, encoding="utf-8"))
        d["words"] = fix_transcript_words(d["words"])
        json.dump(d, open(WORDS_PATH, "w", encoding="utf-8"), indent=2)
        print("Clean transcript:", " ".join(x["w"] for x in d["words"]))
    else:
        spans = asyncio.run(gen_tts())
        align_words(spans)
