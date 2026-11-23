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

TEXT = (
    "Every stone bridge in this valley was built facing the wrong way. "
    "At sunset, the shadows stretch straight across the river. "
    "Luckily, the lantern still burns on the center arch. "
    "Unluckily, it isn't lighting the path for travelers. "
    "You see, when twilight falls, the river reflections line up with the ancient shrine. "
    "And the fire beneath the cliff wakes up on its own."
)

MP3_PATH = os.path.join(VOICE_DIR, "voice.mp3")
WORDS_PATH = os.path.join(VOICE_DIR, "words.json")


async def gen_tts():
    comm = edge_tts.Communicate(TEXT, voice="en-AU-WilliamNeural", rate="+4%")
    await comm.save(MP3_PATH)
    print(f"[OK] Saved TTS -> {MP3_PATH}")


def align_words():
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

    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_np, word_timestamps=True)
    words = []
    for seg in segments:
        if seg.words:
            for w in seg.words:
                words.append({
                    "w": w.word.strip(),
                    "s": round(float(w.start), 3),
                    "e": round(float(w.end), 3),
                })
    out = {"duration": dur, "words": words}
    with open(WORDS_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"[OK] Aligned {len(words)} words, duration={dur}s -> {WORDS_PATH}")
    for w in words:
        print(f"  {w['s']:5.2f} - {w['e']:5.2f} : {w['w']}")


if __name__ == "__main__":
    asyncio.run(gen_tts())
    align_words()
