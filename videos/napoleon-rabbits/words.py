"""Extract and align word-level timestamps from voice_raw.wav using faster-whisper + SCRIPT.md verbatim tokens."""
import json
import os
import re
import numpy as np
import scipy.signal as ss
from scipy.io import wavfile
from faster_whisper import WhisperModel

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS_PATH = os.path.join(HERE, "words.json")
BEATS_PATH = os.path.join(HERE, "beats.json")

m = WhisperModel("base.en", device="cpu", compute_type="int8")
sr, x = wavfile.read(os.path.join(HERE, "voice", "voice_raw.wav"))
x16 = ss.resample_poly(x.astype(np.float32) / 32768.0, 1, sr // 16000)

beats = json.load(open(BEATS_PATH, encoding="utf-8"))["beats"]

# Run Whisper per beat slice so every beat's exact script words map 1:1 with zero cross-beat bleed!
all_words = []
for b in beats:
    s0 = max(0, int((b["start"] - 0.03) * 16000))
    s1 = min(len(x16), int((b["end"] + 0.03) * 16000))
    segs, _ = m.transcribe(x16[s0:s1], word_timestamps=True, language="en")
    rec = [
        {"w": w.word.strip(), "s": round(b["start"] - 0.03 + w.start, 3), "e": round(b["start"] - 0.03 + w.end, 3)}
        for sg in segs
        for w in sg.words
    ]
    # Merge split "3" + ",000" if Whisper split it
    merged = []
    i = 0
    while i < len(rec):
        cur = dict(rec[i])
        if cur["w"] == "3" and i + 1 < len(rec) and rec[i + 1]["w"].startswith(",000"):
            cur["w"] = "3" + rec[i + 1]["w"]
            cur["e"] = rec[i + 1]["e"]
            i += 2
        else:
            i += 1
        merged.append(cur)

    # Display tokens from beat text (replacing "three thousand" -> "3,000" for punchy subtitle readability)
    disp_text = b["text"].replace("three thousand", "3,000")
    disp_tokens = disp_text.split()

    if len(merged) == len(disp_tokens):
        for r_tok, d_tok in zip(merged, disp_tokens):
            all_words.append({"w": d_tok, "s": max(b["start"], r_tok["s"]), "e": min(b["end"] + 0.04, r_tok["e"])})
    else:
        # Proportional fallback inside beat window if token count differs (e.g. hyphenated/em-dash)
        dur = b["end"] - b["start"]
        weights = [max(2, len(re.sub(r"\W+", "", t))) for t in disp_tokens]
        tot_w = sum(weights)
        cur_t = b["start"]
        for d_tok, wt in zip(disp_tokens, weights):
            wd = dur * (wt / tot_w)
            all_words.append({"w": d_tok, "s": round(cur_t, 3), "e": round(cur_t + wd, 3)})
            cur_t += wd

with open(WORDS_PATH, "w", encoding="utf-8") as f:
    json.dump(all_words, f, indent=1)

print(f"Aligned {len(all_words)} words across {len(beats)} beats")
print(" ".join(f'{w["w"]}@{w["s"]}' for w in all_words))
