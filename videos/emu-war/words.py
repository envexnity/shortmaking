import json
from faster_whisper import WhisperModel
m = WhisperModel("base.en", device="cpu", compute_type="int8")
import numpy as np, scipy.signal as ss
from scipy.io import wavfile
sr, x = wavfile.read("voice/voice_raw.wav")
x = ss.resample_poly(x.astype(np.float32) / 32768, 1, sr // 16000)
segs, _ = m.transcribe(x, word_timestamps=True, language="en")
words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words]
json.dump(words, open("words.json", "w"), indent=0)
print(" ".join(f'{x["w"]}@{x["s"]}' for x in words))
