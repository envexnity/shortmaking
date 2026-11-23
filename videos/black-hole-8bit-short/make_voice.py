"""Voice & word-level timing generator for black-hole-8bit-short."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "scripts", "pixel_short_kit")))
from voice_gen import generate_project_voice

SPEAKER_MAP = {
    "host": "host",
    "mrbeast": "mrbeast",
    "mc": "mc",
    "singularity": "trickster",
    "warden": "sage",
}

CUSTOM_GAPS = {
    0: 0.16,
    1: 0.28,
    3: 0.20,
    4: 0.20,
    6: 0.18,
    8: 0.18,
    10: 0.16,
    11: 0.14,
    12: 0.30,
    13: 0.22,
    14: 0.22,
    15: 0.06,
}

if __name__ == "__main__":
    generate_project_voice(HERE, SPEAKER_MAP, CUSTOM_GAPS)
