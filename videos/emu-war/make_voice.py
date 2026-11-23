"""Generate per-beat TTS, trim silence, join with short gaps, write voice.wav + beats.json."""
import asyncio, json, subprocess, os, re
import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = "en-AU-WilliamNeural"
SR = 48000
GAP = 0.09          # silence between beats (s)
HEAD = 0.25         # lead-in before first word
TAIL = 0.9          # hold after last word

beats = []
for line in open(os.path.join(HERE, "SCRIPT.md"), encoding="utf-8"):
    m = re.match(r"^\d+\.\s+(.*)$", line.strip())
    if m and "## Beats" in open(os.path.join(HERE, "SCRIPT.md"), encoding="utf-8").read():
        beats.append(m.group(1))

async def tts(i, text):
    import edge_tts
    mp3 = os.path.join(HERE, "voice", f"b{i:02d}.mp3")
    await edge_tts.Communicate(text, VOICE, rate="+4%").save(mp3)
    wav = mp3[:-4] + ".wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), wav], check=True)
    return wav

def trim(x, thr=0.012):
    a = np.abs(x)
    win = int(SR * 0.01)
    env = np.convolve(a, np.ones(win) / win, mode="same")
    idx = np.where(env > thr)[0]
    s, e = max(0, idx[0] - int(SR * 0.02)), min(len(x), idx[-1] + int(SR * 0.04))
    return x[s:e]

async def main():
    os.makedirs(os.path.join(HERE, "voice"), exist_ok=True)
    out = [np.zeros(int(SR * HEAD), np.float32)]
    t = HEAD; info = []
    for i, b in enumerate(beats):
        wav = await tts(i, b)
        sr, x = wavfile.read(wav)
        x = x.astype(np.float32) / 32768.0
        x = trim(x)
        info.append({"i": i, "text": b, "start": round(t, 3), "end": round(t + len(x) / SR, 3)})
        out.append(x); t += len(x) / SR
        g = GAP if i < len(beats) - 1 else TAIL
        out.append(np.zeros(int(SR * g), np.float32)); t += g
    y = np.concatenate(out)
    wavfile.write(os.path.join(HERE, "voice", "voice_raw.wav"), SR, (y * 32767).astype(np.int16))
    json.dump({"total": round(len(y) / SR, 3), "beats": info}, open(os.path.join(HERE, "beats.json"), "w"), indent=1)
    for b in info: print(f'{b["start"]:6.2f} {b["end"]:6.2f}  {b["text"]}')
    print("total", len(y) / SR)

asyncio.run(main())
