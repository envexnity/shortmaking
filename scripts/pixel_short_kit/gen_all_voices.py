"""Batch voice + Whisper word-alignment runner loading Whisper once across all 5 pixel shorts."""
import importlib.util
import os
from faster_whisper import WhisperModel

KIT_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_DIR = os.path.abspath(os.path.join(KIT_DIR, "..", "..", "videos"))

import sys
sys.path.insert(0, KIT_DIR)
from voice_gen import generate_project_voice

TARGETS = [
    "black-hole-8bit-short",
    "sun-touch-8bit-short",
    "dino-time-8bit-short",
    "ocean-bottom-8bit-short",
    "shrinking-atom-8bit-short",
]

def main():
    wmodel = WhisperModel("base.en", device="cpu", compute_type="int8")
    for name in TARGETS:
        pdir = os.path.join(VIDEOS_DIR, name)
        spec = importlib.util.spec_from_file_location(f"mv_{name}", os.path.join(pdir, "make_voice.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        generate_project_voice(pdir, mod.SPEAKER_MAP, mod.CUSTOM_GAPS, wmodel=wmodel)

if __name__ == "__main__":
    main()
