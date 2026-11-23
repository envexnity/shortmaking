"""Voice & word-level timing generator for cb-20261122-1."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "scripts", "pixel_short_kit")))
from voice_gen import generate_project_voice

SPEAKER_MAP = {
    "host": "host",
    "mrbeast": "mrbeast",
    "mc": "mc",
    "cloud": "trickster",
    "volt": "sage",
}

CUSTOM_GAPS = {
    0: 0.14, 1: 0.24, 3: 0.16, 4: 0.16, 6: 0.14,
    8: 0.16, 10: 0.14, 11: 0.12, 12: 0.26, 13: 0.18,
    14: 0.18, 15: 0.06,
}

if __name__ == "__main__":
    generate_project_voice(HERE, SPEAKER_MAP, CUSTOM_GAPS)
