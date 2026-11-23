"""Voice & word-level timing generator for cb-20261122-2."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "scripts", "pixel_short_kit")))
from voice_gen import generate_project_voice

SPEAKER_MAP = {
    "host": "host",
    "mrbeast": "mrbeast",
    "mc": "mc",
    "photon": "trickster",
    "einstein": "sage",
}

CUSTOM_GAPS = {
    0: 0.10, 1: 0.20, 3: 0.12, 4: 0.12, 6: 0.10,
    8: 0.12, 10: 0.10, 11: 0.10, 12: 0.22, 13: 0.12,
    14: 0.12, 15: 0.04,
}

if __name__ == "__main__":
    generate_project_voice(HERE, SPEAKER_MAP, CUSTOM_GAPS)
